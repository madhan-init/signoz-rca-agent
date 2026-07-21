import os
from dotenv import load_dotenv

load_dotenv()

_REQUIRED_VARS = [
    "SIGNOZ_QUERY_URL",
    "SIGNOZ_TOKEN",
    "ANTHROPIC_API_KEY",
    "SLACK_WEBHOOK_URL",
]

_missing = [var for var in _REQUIRED_VARS if not os.environ.get(var)]
if _missing:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        "Please check your .env file."
    )

SIGNOZ_QUERY_URL: str = os.environ["SIGNOZ_QUERY_URL"]
SIGNOZ_TOKEN: str = os.environ["SIGNOZ_TOKEN"]
ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
SLACK_WEBHOOK_URL: str = os.environ["SLACK_WEBHOOK_URL"]
