from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from checker import check_username

app = FastAPI(title="Handle Scout")
BASE = Path(__file__).parent

app.mount("/public", StaticFiles(directory=BASE / "public"), name="public")


@app.get("/")
async def index():
    return FileResponse(BASE / "index.html")


@app.get("/style.css")
async def css():
    return FileResponse(BASE / "style.css")


@app.get("/app.js")
async def js():
    return FileResponse(BASE / "app.js")


@app.get("/api/check")
async def check(username: str):
    if not username or len(username) < 2 or len(username) > 30:
        raise HTTPException(400, "Username must be 2-30 characters")

    if not all(c.isalnum() or c in "_." for c in username):
        raise HTTPException(400, "Only letters, numbers, underscore, dot allowed")

    results = await check_username(username)
    return JSONResponse({
        "username": username,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results["results"],
        "suggestions": results["suggestions"],
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
