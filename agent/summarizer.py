import json
import logging
from typing import Any, Dict
import httpx
from .config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

# Single source of truth for Claude model string
CLAUDE_MODEL: str = "claude-sonnet-4-6"

PROMPT_TEMPLATE: str = """You are a senior Site Reliability Engineer summarizing a production incident for an executive-facing Slack channel.

Alert:
{alert_json}

Telemetry from the 15 minutes around the alert (logs + relevant metric series):
{telemetry_json}

Respond in under 150 words using a highly professional, clinical, and formal tone. Avoid conversational language, jargon, or emojis. Format for Slack (*bold* for emphasis, bullet points):
- Incident Summary: A concise, objective description of the event.
- Root Cause Analysis: A professional assessment of the likely cause based on the telemetry. State if evidence is inconclusive.
- Recommended Mitigation: The immediate steps required to resolve the issue.
- Severity Assessment: (P1-P5) with a brief, formal justification.
"""


async def summarize(alert: Dict[str, Any], telemetry: Dict[str, Any]) -> str:
    """Send alert context and telemetry to Claude and return formatted summary."""
    logger.info("Generating incident summary with Claude model %s", CLAUDE_MODEL)
    prompt = PROMPT_TEMPLATE.format(
        alert_json=json.dumps(alert, indent=2),
        telemetry_json=json.dumps(telemetry, indent=2),
    )
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": CLAUDE_MODEL,
                    "max_tokens": 400,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            content = resp.json()["content"][0]["text"]
            return content
    except httpx.HTTPStatusError as exc:
        logger.error("Anthropic API returned HTTP error status %s: %s", exc.response.status_code, exc.response.text)
        raise
    except httpx.RequestError as exc:
        logger.error("Network error while connecting to Anthropic API: %s", str(exc))
        raise
