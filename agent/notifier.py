import logging
import httpx
from .config import SLACK_WEBHOOK_URL

logger = logging.getLogger(__name__)


async def post_to_slack(summary: str) -> None:
    """Post incident summary to Slack incoming webhook."""
    logger.info("Posting summary to Slack incoming webhook")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                SLACK_WEBHOOK_URL,
                json={"text": summary},
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
            resp.raise_for_status()
            logger.info("Successfully posted summary to Slack")
    except httpx.HTTPStatusError as exc:
        logger.error("Slack webhook returned HTTP error status %s: %s", exc.response.status_code, exc.response.text)
        raise
    except httpx.RequestError as exc:
        logger.error("Network error while connecting to Slack webhook: %s", str(exc))
        raise
