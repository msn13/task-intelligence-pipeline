import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()
API_KEY = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
if API_KEY is None:
    raise ValueError("API key not set")

DATA_DIR = Path("data")
RAW_MEETINGS = DATA_DIR / "raw_meetings.json"