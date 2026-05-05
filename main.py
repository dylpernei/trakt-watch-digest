import asyncio
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv(override=True)

from services.trakt import get_watchlist, get_up_next, get_recent_history
from services.claude import generate_digest
from services.email import post_digest

app = FastAPI(title="Trakt Watch Digest")


@app.get("/")
async def root():
    return {"message": "Trakt Watch Digest API", "endpoints": ["/trigger", "/preview", "/status"]}


@app.post("/trigger")
async def trigger():
    try:
        watchlist, up_next, history = await asyncio.gather(
            get_watchlist(),
            get_up_next(),
            get_recent_history(),
        )
        digest = generate_digest(watchlist, up_next, history)
        await post_digest(digest)
        return {"status": "success", "emailed": True}
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, detail=f"Upstream API error: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/preview")
async def preview():
    """Returns the digest as JSON without sending email. Useful for testing."""
    try:
        watchlist, up_next, history = await asyncio.gather(
            get_watchlist(),
            get_up_next(),
            get_recent_history(),
        )
        digest = generate_digest(watchlist, up_next, history)
        return {"status": "success", "digest": digest}
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, detail=f"Upstream API error: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@app.get("/status")
async def status():
    return {
        "status": "healthy",
        "trakt_user": os.environ.get("TRAKT_USERNAME", "not set"),
        "services": {
            "trakt": bool(os.environ.get("TRAKT_CLIENT_ID")),
            "claude": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "resend": bool(os.environ.get("RESEND_API_KEY")),
        },
    }
