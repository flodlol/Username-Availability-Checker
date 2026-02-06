from __future__ import annotations

import asyncio
from typing import Any

import httpx

from platforms import PLATFORMS
from suggestions import generate_suggestions

DEFAULT_HEADERS = {
    "User-Agent": "HandleScout/1.0",
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT_SECONDS = 6.0


async def _check_platform(
    platform: dict[str, Any],
    username: str,
    client: httpx.AsyncClient,
) -> dict[str, Any]:
    if platform.get("skip_check"):
        return {
            "platform": platform["name"],
            "url": None,
            "status": "unknown",
            "http_status": None,
            "reason": platform.get("reason", "Not checkable"),
        }

    profile_url = platform["profile_url_template"].format(username=username)
    url = platform.get("check_url_template", platform["profile_url_template"]).format(
        username=username
    )
    method = platform.get("check_method", "GET")
    headers = {**DEFAULT_HEADERS, **platform.get("headers", {})}

    try:
        response = await client.request(method, url, headers=headers)
    except Exception as exc:  # noqa: BLE001
        return {
            "platform": platform["name"],
            "url": url,
            "status": "error",
            "http_status": None,
            "reason": type(exc).__name__,
        }

    status_code = response.status_code
    text_lower = response.text.lower() if response.text else ""
    available_statuses = set(platform.get("available_statuses", []))
    taken_statuses = set(platform.get("taken_statuses", []))
    unknown_statuses = set(platform.get("unknown_statuses", []))

    if status_code in available_statuses:
        return {
            "platform": platform["name"],
            "url": profile_url,
            "status": "available",
            "http_status": status_code,
            "reason": f"Profile returns {status_code} => likely available",
        }

    if status_code in taken_statuses:
        available_markers = platform.get("available_markers", [])
        unknown_markers = platform.get("unknown_markers", [])
        taken_markers = platform.get("taken_markers", [])

        for marker in unknown_markers:
            if marker in text_lower:
                return {
                    "platform": platform["name"],
                    "url": profile_url,
                    "status": "unknown",
                    "http_status": status_code,
                    "reason": "Page requires verification or is blocked",
                }

        for marker in available_markers:
            if marker in text_lower:
                return {
                    "platform": platform["name"],
                    "url": profile_url,
                    "status": "available",
                    "http_status": status_code,
                    "reason": "Page indicates account does not exist",
                }

        for marker in taken_markers:
            if marker.format(username=username).lower() in text_lower:
                return {
                    "platform": platform["name"],
                    "url": profile_url,
                    "status": "taken",
                    "http_status": status_code,
                    "reason": "Page includes username marker",
                }

        if platform.get("assume_taken_on_200"):
            return {
                "platform": platform["name"],
                "url": profile_url,
                "status": "taken",
                "http_status": status_code,
                "reason": "Status 200 without missing markers => likely taken",
            }

    if status_code in taken_statuses and platform.get("ambiguous_on_200"):
        return {
            "platform": platform["name"],
            "url": profile_url,
            "status": "unknown",
            "http_status": status_code,
            "reason": "Status 200 but platform may serve challenges or cached pages",
        }

    if status_code in taken_statuses:
        return {
            "platform": platform["name"],
            "url": profile_url,
            "status": "taken",
            "http_status": status_code,
            "reason": f"Profile returns {status_code} => likely taken",
        }

    if status_code in unknown_statuses:
        return {
            "platform": platform["name"],
            "url": profile_url,
            "status": "unknown",
            "http_status": status_code,
            "reason": f"Status {status_code} => unclear availability",
        }

    return {
        "platform": platform["name"],
        "url": profile_url,
        "status": "unknown",
        "http_status": status_code,
        "reason": f"Unexpected status {status_code}",
    }


async def check_username(username: str) -> dict[str, Any]:
    async with httpx.AsyncClient(
        timeout=TIMEOUT_SECONDS,
        follow_redirects=True,
    ) as client:
        tasks = [
            _check_platform(platform, username, client) for platform in PLATFORMS
        ]
        results = await asyncio.gather(*tasks)

    suggestions = generate_suggestions(username, results)
    return {"results": results, "suggestions": suggestions}
