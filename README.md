# 🎬 Trakt Watch Digest

I've been tracking everything I watch for years — currently hundreds of shows and movies in Trakt. My watchlist became too big to browse, so I built this to give me an opinionated daily digest powered by Claude.

## What It Does

Pulls three data sources from Trakt (watchlist, in-progress shows, recent history), feeds them to Claude, and posts a curated "what to watch tonight" digest to Slack. The `/trigger` endpoint is the entry point — hit it manually or wire it up to a cron/scheduler.

## Architecture

```
                     ┌─────────────┐
                     │  /trigger   │
                     └──────┬──────┘
                            │
              ┌─────────────▼──────────────┐
              │          FastAPI           │
              └──┬──────────┬──────────┬───┘
                 │          │          │
        ┌────────▼───┐      │    ┌─────▼──────┐
        │ Trakt API  │      │    │ Claude API │
        │ (3 calls)  │      │    │  (digest)  │
        └────────────┘      │    └─────┬──────┘
                            │          │
                     ┌──────▼──────────▼──┐
                     │   Slack Webhook    │
                     └────────────────────┘
```

## Endpoints

| Endpoint   | Method | Description                                              |
|------------|--------|----------------------------------------------------------|
| `/`        | GET    | API info and available endpoints                         |
| `/trigger` | POST   | Fetch data, generate digest, post to Slack               |
| `/preview` | GET    | Same as trigger but returns digest as JSON (no Slack post)|
| `/status`  | GET    | Health check — shows configured services and Trakt user  |

## Setup

### Prerequisites

- Python 3.11+
- Trakt account + app registered at [trakt.tv/oauth/applications](https://trakt.tv/oauth/applications)
- Slack webhook URL from a Slack app
- Anthropic API key

### Local Setup

```bash
git clone <this-repo>
cd trakt-watch-digest

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Fill in your values in .env

uvicorn main:app --reload
```

### Environment Variables

| Variable            | Description                          | Where to get it                                      |
|---------------------|--------------------------------------|------------------------------------------------------|
| `TRAKT_CLIENT_ID`   | Your Trakt app's client ID           | trakt.tv/oauth/applications → your app → Client ID   |
| `TRAKT_USERNAME`    | Your Trakt username                  | Your Trakt profile URL                               |
| `ANTHROPIC_API_KEY` | Anthropic API key                    | console.anthropic.com/settings/api-keys              |
| `SLACK_WEBHOOK_URL` | Incoming webhook URL for your channel| api.slack.com/apps → your app → Incoming Webhooks    |

## Deployment (Railway)

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

Then add your environment variables in the Railway dashboard under **Variables**.

## Assumptions

- Trakt account is public or auth token not required for read endpoints. If your account is private, a full OAuth flow is needed — not implemented here.
- Slack webhook is pre-configured and pointed at your desired channel.
- Claude summarizes based on show/movie titles only; no episode-level metadata is passed.

## What I'd Add Next

- Scheduled daily runs via Railway cron
- OAuth flow for private Trakt accounts
- Per-show "next episode" lookup for richer context
- Webhook auth (HMAC signature validation)
