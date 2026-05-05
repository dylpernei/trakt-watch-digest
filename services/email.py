import os
import re
import httpx

RESEND_API_URL = "https://api.resend.com/emails"

def _slack_to_html(text: str) -> str:
    text = re.sub(r"\*(.+?)\*", r"<strong>\1</strong>", text)
    text = text.replace("\n", "<br>")
    return text

async def post_digest(digest: str) -> None:
    html_body = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
        <h2 style="margin-bottom: 20px;">🎬 Tonight's Watch Digest</h2>
        <div style="line-height: 1.7; font-size: 15px;">
            {_slack_to_html(digest)}
        </div>
        <hr style="margin-top: 32px; border: none; border-top: 1px solid #eee;">
        <p style="color: #999; font-size: 12px;">Powered by Trakt + Claude</p>
    </div>
    """

    payload = {
        "from": os.environ["RESEND_FROM"],
        "to": [os.environ["RESEND_TO"]],
        "subject": "🎬 Tonight's Watch Digest",
        "html": html_body,
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            RESEND_API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {os.environ['RESEND_API_KEY']}"},
        )
    r.raise_for_status()
