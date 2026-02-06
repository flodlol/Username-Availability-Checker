import asyncio
import httpx
from platforms import PLATFORMS

TIMEOUT = 5
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; UsernameChecker/1.0)"}


async def check_platform(name: str, url: str, client: httpx.AsyncClient) -> dict:
    try:
        resp = await client.get(url, headers=HEADERS)
        if resp.status_code == 404:
            return {"platform": name, "url": url, "status": "available"}
        elif resp.status_code == 200:
            return {"platform": name, "url": url, "status": "taken"}
        else:
            return {"platform": name, "url": url, "status": "unknown"}
    except Exception:
        return {"platform": name, "url": url, "status": "error"}


async def check_username(username: str) -> dict:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        tasks = [
            check_platform(p["name"], p["url"].format(username=username), client)
            for p in PLATFORMS
        ]
        results = await asyncio.gather(*tasks)

    suggestions = generate_suggestions(username, results)
    return {"results": list(results), "suggestions": suggestions}


def generate_suggestions(username: str, results: list) -> list:
    if all(r["status"] == "available" for r in results):
        return []

    suffixes = ["dev", "hq", "app", "official", "real", "the"]
    suggestions = []

    for suffix in suffixes:
        suggestions.append(f"{username}_{suffix}")
        suggestions.append(f"{username}{suffix}")

    for n in ["1", "01", "2", "99"]:
        suggestions.append(f"{username}{n}")

    return suggestions[:12]
