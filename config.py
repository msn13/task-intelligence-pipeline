"""Config file for project; use the same client and directories everywhere by importing config.client"""

import os
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if ANTHROPIC_API_KEY is None:
    raise ValueError("ANTHROPIC_API_KEY not set in .env")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

RAW_MEETINGS = DATA_DIR / "raw_meetings.json"
TASKS_BUNDLE = DATA_DIR / "tasks_bundle.json"
SAMPLE_OUTPUT = DATA_DIR / "sample_output"