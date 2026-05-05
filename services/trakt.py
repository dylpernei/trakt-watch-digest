import asyncio
import os
import httpx

BASE_URL = "https://api.trakt.tv"

def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "trakt-api-version": "2",
        "trakt-api-key": os.environ["TRAKT_CLIENT_ID"],
    }

async def get_watchlist() -> dict:
    username = os.environ["TRAKT_USERNAME"]
    async with httpx.AsyncClient(headers=_headers()) as client:
        shows_req = client.get(f"{BASE_URL}/users/{username}/watchlist/shows")
        movies_req = client.get(f"{BASE_URL}/users/{username}/watchlist/movies")
        shows_resp, movies_resp = await asyncio.gather(shows_req, movies_req)
    shows_resp.raise_for_status()
    movies_resp.raise_for_status()
    return {
        "shows": shows_resp.json()[:10],
        "movies": movies_resp.json()[:10],
    }

async def get_up_next() -> list:
    username = os.environ["TRAKT_USERNAME"]
    async with httpx.AsyncClient(headers=_headers()) as client:
        r = await client.get(
            f"{BASE_URL}/users/{username}/watched/shows",
            params={"extended": "noseasons"},
        )
    r.raise_for_status()
    return r.json()[:15]

async def get_recent_history() -> list:
    username = os.environ["TRAKT_USERNAME"]
    async with httpx.AsyncClient(headers=_headers()) as client:
        r = await client.get(
            f"{BASE_URL}/users/{username}/history",
            params={"limit": 10},
        )
    r.raise_for_status()
    return r.json()
