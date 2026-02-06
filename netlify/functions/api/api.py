from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

import httpx


# ========== PLATFORMS ==========
PLATFORMS = [
    {
        "name": "GitHub",
        "profile_url_template": "https://github.com/{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
    },
    {
        "name": "Reddit",
        "profile_url_template": "https://www.reddit.com/user/{username}",
        "check_url_template": "https://www.reddit.com/user/{username}/about.json",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
        "headers": {
            "User-Agent": "Mozilla/5.0 (compatible; HandleScout/1.0; +https://example.com)",
        },
    },
    {
        "name": "TikTok",
        "profile_url_template": "https://www.tiktok.com/@{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
        "unknown_markers": [
            "verify you are human",
            "captcha",
            "unusual traffic",
            "something went wrong",
        ],
        "available_markers": [
            "couldn't find this account",
            "couldn't find this user",
            "user not found",
        ],
        "taken_markers": ["\"uniqueId\":\"{username}\""],
        "ambiguous_on_200": True,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    },
    {
        "name": "X",
        "profile_url_template": "https://x.com/{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
        "unknown_markers": [
            "something went wrong",
            "unusual activity",
            "retry",
            "access denied",
        ],
        "available_markers": [
            "this account doesn't exist",
            "account doesn't exist",
        ],
        "ambiguous_on_200": True,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    },
    {
        "name": "GitLab",
        "profile_url_template": "https://gitlab.com/{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
    },
    {
        "name": "Bitbucket",
        "profile_url_template": "https://bitbucket.org/{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
    },
    {
        "name": "Dev.to",
        "profile_url_template": "https://dev.to/{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
    },
    {
        "name": "CodePen",
        "profile_url_template": "https://codepen.io/{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
    },
    {
        "name": "Dribbble",
        "profile_url_template": "https://dribbble.com/{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
    },
    {
        "name": "Behance",
        "profile_url_template": "https://www.behance.net/{username}",
        "check_method": "GET",
        "available_statuses": [404],
        "taken_statuses": [200],
        "unknown_statuses": [429, 403, 401],
    },
]

# ========== SUGGESTIONS ==========
def _is_valid(candidate: str) -> bool:
    if not (2 <= len(candidate) <= 30):
        return False
    for ch in candidate:
        if not (ch.isalnum() or ch in {"_", "."}):
            return False
    return True


def generate_suggestions(username: str, results: list[dict[str, Any]]) -> list[str]:
    key_platforms = {
        "GitHub", "Reddit", "TikTok", "X", "GitLab",
        "Bitbucket", "Dev.to", "CodePen", "Dribbble", "Behance",
    }
    needs_suggestions = any(
        r["platform"] in key_platforms and r["status"] != "available" for r in results
    )
    if not needs_suggestions:
        return []

    suffixes = ["hq", "dev", "app", "io", "official", "real"]
    separators = ["_", ".", "-"]
    numbers = ["01", "1", "2", "3"]
    candidates: list[str] = []
    seen = set()

    def push(value: str) -> None:
        if value in seen or not _is_valid(value):
            return
        seen.add(value)
        candidates.append(value)

    for suffix in suffixes:
        push(f"{username}{suffix}")
        for sep in separators:
            push(f"{username}{sep}{suffix}")
    for num in numbers:
        push(f"{username}{num}")
        for sep in separators:
            push(f"{username}{sep}{num}")
    push(f"its{username}")
    push(f"the{username}")
    push(f"{username}_dev")
    return candidates[:18]


# ========== CHECKER ==========
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
    url = platform.get("check_url_template", platform["profile_url_template"]).format(username=username)
    method = platform.get("check_method", "GET")
    headers = {**DEFAULT_HEADERS, **platform.get("headers", {})}

    try:
        response = await client.request(method, url, headers=headers)
    except Exception as exc:
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

        if platform.get("ambiguous_on_200"):
            return {
                "platform": platform["name"],
                "url": profile_url,
                "status": "unknown",
                "http_status": status_code,
                "reason": "200 but no definitive marker found",
            }

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
            "reason": f"Status {status_code} => blocked or rate-limited",
        }

    return {
        "platform": platform["name"],
        "url": profile_url,
        "status": "unknown",
        "http_status": status_code,
        "reason": f"Unexpected {status_code}",
    }


async def check_username(username: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
        tasks = [_check_platform(p, username, client) for p in PLATFORMS]
        results = await asyncio.gather(*tasks)
    suggestions = generate_suggestions(username, results)
    return {"results": results, "suggestions": suggestions}


# ========== HANDLER ==========
def _validate_username(username: str) -> str | None:
    if not username:
        return "Username is required"
    if not (2 <= len(username) <= 30):
        return "Username must be 2-30 chars"
    for ch in username:
        if not (ch.isalnum() or ch in {"_", "."}):
            return "Username may contain letters, numbers, underscore, dot"
    return None


def _json_response(body: dict, status_code: int = 200) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
        },
        "body": json.dumps(body),
    }


def handler(event, context):
    """Netlify Function handler."""
    http_method = event.get("httpMethod", "GET")
    
    # Handle CORS preflight
    if http_method == "OPTIONS":
        return _json_response({})
    
    # Parse path and query
    path = event.get("path", "")
    query = event.get("queryStringParameters") or {}
    
    # Route: /api/check
    if "/check" in path or path.endswith("/api"):
        username = query.get("username", "")
        
        error = _validate_username(username)
        if error:
            return _json_response({"error": error}, 400)
        
        # Run async check
        try:
            results = asyncio.run(check_username(username))
        except RuntimeError:
            # Fallback for environments with existing event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(check_username(username))
            finally:
                loop.close()
        
        payload = {
            "username": username,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "results": results["results"],
            "suggestions": results["suggestions"],
        }
        return _json_response(payload)
    
    return _json_response({"error": "Not found"}, 404)
