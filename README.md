# AI Meeting → Task Pipeline
> A business AI demo that extracts structured action items from meeting notes using Claude, validates them, and surfaces them in a lightweight dashboard.

---

## What It Does

Wellness teams currently hand-write meeting notes, action plans fall through the cracks, and leadership has no visibility into follow-through. This system:

1. Ingests meeting notes (via JSONPlaceholder stubs + realistic injected text)
2. Sends them to **Claude Haiku** for structured task extraction
3. Validates and normalizes the output against a strict schema
4. Persists results as local JSON
5. Displays extracted tasks in a **Streamlit** dashboard

---

## Architecture

```
JSONPlaceholder API (post stubs: id, title, userId)
        │
        ▼
sample_meetings.py  ← injects realistic wellness meeting text
        │
        ▼
ingestion/normalizer.py  ← maps to internal meeting schema
        │
        ▼
extraction/anthropic_client.py  ← Claude Haiku extracts tasks as JSON
        │
        ▼
extraction/validator.py  ← repairs + validates against schemas.py
        │
        ▼
storage/json_store.py  ← writes tasks_bundle.json
        │
        ▼
ui/dashboard.py  ← Streamlit dashboard displays results
```

> **Planned next layer:** A Go concurrent analyzer (`go_analyzer/`) that reads `tasks_bundle.json`, runs a worker pool to score and rank tasks for urgency, and writes `alerts.json` + `ranked_tasks.json`. Python calls it via `subprocess.run()` and surfaces any Go errors directly in the UI.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| AI Model | Anthropic Claude Haiku |
| UI | Streamlit |
| Package Manager | uv |
| Config | `.env` via `python-dotenv` |
| Persistence | Local JSON files |
| File Paths | `pathlib.Path` throughout |
| External API | JSONPlaceholder (stub layer) |

---

## Project Structure

```
project/
├── .env                        ← API key (never committed)
├── app.py                      ← pipeline orchestrator
├── config.py                   ← loads env, defines all Path constants
│
├── ingestion/
│   ├── api_client.py           ← fetches post stubs from JSONPlaceholder
│   ├── normalizer.py           ← maps raw post → internal meeting schema
│   └── sample_meetings.py      ← realistic meeting note strings + get_note()
│
├── extraction/
│   ├── anthropic_client.py     ← calls Claude, parses JSON response
│   ├── prompts.py              ← builds structured extraction prompt
│   └── validator.py            ← repairs + validates model output
│
├── storage/
│   ├── json_store.py           ← save_json / load_json utilities
│   └── schemas.py              ← single source of truth: field names, enums, defaults
│
├── ui/
│   └── dashboard.py            ← Streamlit UI (thin — no business logic)
│
├── data/
│   ├── tasks_bundle.json       ← Python output, Go input
│   └── sample_output/          ← saved good run for demo fallback
│
└── go_analyzer/                ← (planned) concurrent task analyzer
    └── main.go
```

---

## Setup

**Prerequisites:** Python 3.9+, [uv](https://github.com/astral-sh/uv)

```bash
# 1. Clone the repo
git clone <repo-url>
cd project

# 2. Activate virtual environment
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
uv add anthropic streamlit python-dotenv requests

# 4. Add your API key
# Create a .env file:
ANTHROPIC_API_KEY=your_key_here

# 5. Verify imports
python -c "import anthropic, streamlit, dotenv, requests"
```

---

## Running the App

**Pipeline only (no UI):**
```bash
python app.py
```
Outputs `data/tasks_bundle.json` — open it to inspect extracted tasks.

**Full dashboard:**
```bash
streamlit run ui/dashboard.py
```

**Demo fallback** (no API call needed):
Toggle "Use saved demo data" in the UI to load from `data/sample_output/`.

---

## Key Design Decisions

**Why inject sample text into JSONPlaceholder?**
JSONPlaceholder bodies are lorem ipsum. Claude would produce meaningless output from them. We use JSONPlaceholder for real HTTP integration (proving API client code), but replace the body with realistic meeting notes before any downstream processing touches it. The pipeline is trivially upgradeable to a real meeting source.

**Why `schemas.py` as a single source of truth?**
The extraction prompt, validator, and (eventually) Go structs all need to agree on field names, enum values, and date formats. Defining them once and importing everywhere prevents silent drift — the most common integration bug in multi-stage pipelines.

**Why is Streamlit kept thin?**
Streamlit reruns the entire script on every interaction. Business logic inside the UI file creates hard-to-debug state bugs. All pipeline functions live in plain Python modules; Streamlit only calls them and renders results.

**Why `pathlib.Path` instead of string paths?**
String paths with backslashes are fragile on Windows. `pathlib.Path` constructs OS-correct paths automatically and makes all file locations centrally defined in `config.py`.

**Why a Go worker pool for the analyzer (planned)?**
Not for performance at demo scale — the dataset is small. The worker pool demonstrates bounded concurrency and correct channel-based data flow: the pattern that is safe and correct at scale. Go is also a natural fit for a compiled, statically-typed analyzer that produces deterministic scoring output.

---

## Schema Contract

All tasks written to `tasks_bundle.json` conform to this structure:

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-04-23T12:00:00",
  "mode": "single",
  "tasks": [
    {
      "task_id": "task-meeting-001-000",
      "meeting_id": "meeting-001",
      "description": "Schedule follow-up appointment for resident",
      "owner": "Dr. Rivera",
      "due_date": "2026-04-30",
      "priority": "high",
      "status": "not_started",
      "risk": "medium"
    }
  ]
}
```

Field rules enforced by `validator.py`:
- `priority`: `low | medium | high`
- `status`: `not_started | in_progress | completed | blocked`
- `risk`: `low | medium | high | unknown`
- `due_date`: `YYYY-MM-DD` or `null`
- `owner`: string or `null`

---

## What's Next

- **Go concurrent analyzer** — worker pool scoring urgency and generating `alerts.json`
- **Real meeting source** — replace JSONPlaceholder with a Smartsheet or Google Forms integration
- **Role-based alerts** — notify leadership only when tasks are overdue by a defined threshold
- **Database persistence** — replace local JSON with PostgreSQL for multi-user support
- **Audit log** — append-only trail of all pipeline runs and extracted tasks
