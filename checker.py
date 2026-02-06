import asyncio
import httpx
from platforms import PLATFORMS

TIMEOUT = 5
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


async def check_platform(platform: dict, username: str, client: httpx.AsyncClient) -> dict:
    url = platform["url"].format(username=username)
    profile_url = url.replace("/about.json", "")  # Clean URL for display
    
    # Unreliable platforms (JS-heavy) - mark as unknown, user should check manually
    if platform.get("unreliable"):
        return {"platform": platform["name"], "url": profile_url, "status": "unknown"}
    
    try:
        resp = await client.get(url, headers=HEADERS)
        
        # 404 = available
        if resp.status_code == 404:
            return {"platform": platform["name"], "url": profile_url, "status": "available"}
        
        # 200 = taken
        if resp.status_code == 200:
            return {"platform": platform["name"], "url": profile_url, "status": "taken"}
        
        return {"platform": platform["name"], "url": profile_url, "status": "unknown"}
    except Exception:
        return {"platform": platform["name"], "url": profile_url, "status": "error"}


async def check_username(username: str) -> list:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        tasks = [check_platform(p, username, client) for p in PLATFORMS]
        results = await asyncio.gather(*tasks)
    return list(results)
