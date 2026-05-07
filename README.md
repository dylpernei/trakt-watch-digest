# 🎬 Trakt Watch Digest

I love to track the movies and tv shows that I watch, which over the years I've used a variety of tools for. For this, I use Trakt. My watchlist became too big to browse, so I built this to give me an opinionated daily digest powered by Claude.

## What It Does

Pulls three data sources from Trakt (watchlist, in-progress shows, recent history), feeds them to Claude, and emails a curated "what to watch tonight" digest via Resend. The `/trigger` endpoint is the entry point — hit it manually or wire it up to a cron/scheduler.

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
                     │   Resend (email)   │
                     └────────────────────┘
```

## Live Deployment

**Base URL:** `https://trakt-watch-digest-production.up.railway.app`

| Action | Command |
|--------|---------|
| Check status | `GET https://trakt-watch-digest-production.up.railway.app/status` |
| Preview digest (no email) | `GET https://trakt-watch-digest-production.up.railway.app/preview` |
| Trigger digest + send email | `POST https://trakt-watch-digest-production.up.railway.app/trigger` |

## Endpoints

| Endpoint   | Method | Description                                               |
|------------|--------|-----------------------------------------------------------|
| `/`        | GET    | API info and available endpoints                          |
| `/trigger` | POST   | Fetch data, generate digest, send email                   |
| `/preview` | GET    | Same as trigger but returns digest as JSON (no email sent)|
| `/status`  | GET    | Health check — shows configured services and Trakt user   |

## Setup

### Prerequisites

- Python 3.11+
- Trakt account + app registered at [trakt.tv/oauth/applications](https://trakt.tv/oauth/applications)
- Resend account + verified domain at [resend.com](https://resend.com)
- Anthropic API key

### Local Setup

```bash
git clone https://github.com/dylpernei/trakt-watch-digest
cd trakt-watch-digest

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Fill in your values in .env

uvicorn main:app --reload
```

Then hit `GET /status` to confirm all services are configured, and `GET /preview` to test without sending an email.

### Environment Variables

| Variable            | Description                        | Where to get it                                    |
|---------------------|------------------------------------|----------------------------------------------------|
| `TRAKT_CLIENT_ID`   | Your Trakt app's client ID         | trakt.tv/oauth/applications → your app → Client ID |
| `TRAKT_USERNAME`    | Your Trakt username                | Your Trakt profile URL                             |
| `ANTHROPIC_API_KEY` | Anthropic API key                  | console.anthropic.com/settings/api-keys            |
| `RESEND_API_KEY`    | Resend API key                     | resend.com/api-keys                                |
| `RESEND_FROM`       | Sender address (verified domain)   | e.g. `Digest <digest@yourdomain.com>`              |
| `RESEND_TO`         | Recipient email address            | Your email                                         |

## Deployment (Railway)

```bash
brew install railway
railway login
railway init
railway service
railway up
railway domain
```

Then add your environment variables in the Railway dashboard under **Variables**.

## Assumptions

- Trakt account is public — no OAuth token required for read endpoints. If private, a full OAuth flow would be needed (not implemented).
- Resend domain is verified and DNS records are propagated.
- Claude summarizes based on show/movie titles only; no episode-level metadata is passed.

## What I'd Add Next

- Scheduled daily runs via Railway cron
- OAuth flow for private Trakt accounts
- Per-show "next episode" lookup for richer context
- Webhook auth (HMAC signature validation)
