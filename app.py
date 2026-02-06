from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from checker import check_username

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
PUBLIC_DIR = BASE_DIR / "public"

app = FastAPI(title="Handle Scout", version="0.1.0")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")

RATE_LIMIT_SECONDS = 1.0
_last_request_by_ip: dict[str, float] = {}


def _rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    now = time()
    last = _last_request_by_ip.get(client_host, 0.0)
    if now - last < RATE_LIMIT_SECONDS:
        raise HTTPException(status_code=429, detail="slow down")
    _last_request_by_ip[client_host] = now


def _validate_username(username: str) -> None:
    if not (2 <= len(username) <= 30):
        raise HTTPException(status_code=400, detail="Username must be 2-30 chars")
    for ch in username:
        if not (ch.isalnum() or ch in {"_", "."}):
            raise HTTPException(
                status_code=400,
                detail="Username may contain letters, numbers, underscore, dot",
            )


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/style.css")
async def style_css() -> FileResponse:
    return FileResponse(STATIC_DIR / "style.css")


@app.get("/app.js")
async def app_js() -> FileResponse:
    return FileResponse(STATIC_DIR / "app.js")


@app.get("/api/check")
async def api_check(username: str, request: Request) -> JSONResponse:
    _rate_limit(request)
    _validate_username(username)

    results = await check_username(username)
    payload = {
        "username": username,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "results": results["results"],
        "suggestions": results["suggestions"],
    }
    return JSONResponse(payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
