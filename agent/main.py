import logging
from typing import Any, Dict
from fastapi import FastAPI, Request, HTTPException
from .telemetry import fetch_telemetry_window
from .summarizer import summarize
from .notifier import post_to_slack

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("agent.main")

app = FastAPI(title="SigNoz Incident Summarizer Agent")


@app.post("/alert")
async def handle_alert(request: Request) -> Dict[str, str]:
    """Receive SigNoz alert webhook, fetch telemetry, generate summary, and notify Slack."""
    try:
        alert: Dict[str, Any] = await request.json()
    except Exception as exc:
        logger.error("Failed to parse alert JSON payload: %s", str(exc))
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    logger.info("Received SigNoz alert notification")
    
    telemetry = await fetch_telemetry_window(alert)
    summary = await summarize(alert, telemetry)
    await post_to_slack(summary)
    
    return {"status": "posted"}
