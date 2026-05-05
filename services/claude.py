import os
import anthropic

def _extract_title(item: dict, media_type: str) -> str:
    return item.get(media_type, {}).get("title", "Unknown")

def generate_digest(watchlist: dict, up_next: list, history: list) -> str:
    recently_watched = ", ".join(
        _extract_title(item, "show") if "show" in item else _extract_title(item, "movie")
        for item in history[:5]
    )
    in_progress = ", ".join(
        item.get("show", {}).get("title", "Unknown") for item in up_next[:10]
    )
    watchlist_shows = ", ".join(
        item.get("show", {}).get("title", "Unknown") for item in watchlist["shows"][:8]
    )
    watchlist_movies = ", ".join(
        item.get("movie", {}).get("title", "Unknown") for item in watchlist["movies"][:5]
    )

    prompt = f"""You're helping Dylan figure out what to watch. He's a busy SF-based engineer who tracks everything he watches obsessively.

Currently in progress:
{in_progress}

Recently watched:
{recently_watched}

Watchlist — shows to start:
{watchlist_shows}

Watchlist — movies:
{watchlist_movies}

Generate a concise, opinionated Slack digest with:
1. *Tonight's Pick* — one show or movie with a punchy one-line reason
2. *Up Next* — 2-3 in-progress shows to continue (prioritize momentum)
3. *Off The Bench* — one watchlist title worth starting now
4. *Pattern Watch* — one brief observation about his watching habits if anything stands out

Tone: like a friend who knows his taste really well. Use Slack markdown (*bold*, not **bold**). Keep it under 250 words.
"""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
