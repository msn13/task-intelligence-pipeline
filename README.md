# Task Intelligence Pipeline

> An AI-powered system that extracts structured action items from wellness team meeting notes, validates them against a
strict schema, and surfaces them in an interactive dashboard.

Built as an internship interview demo targeting real business pain: action plans falling through the cracks, no
leadership visibility, and no accountability layer in resident care workflows.

---

## The Problem It Solves

Wellness teams currently hand-write meeting notes, generate action plans verbally, and track follow-through manually.
The result:

- Action items live in someone's notebook or memory
- No standardized format across staff members
- Leadership has no visibility until something goes wrong
- Follow-through is assumed, not verified

This pipeline takes a raw, messy meeting note written in plain prose and produces a structured, validated, persisted
task record — automatically.

---

## Demo Flow

1. Select a meeting note from the dropdown (5 realistic wellness check-in notes)
2. Click **Extract Tasks**
3. Claude Haiku reads the note and returns structured JSON
4. The validator repairs any malformed fields against the schema
5. Results are saved to `data/tasks_bundle.json`
6. The dashboard renders a task table with owner, deadline, priority, status, and risk

---

## Architecture

```
ingestion/sample_meetings.py  (realistic injected meeting prose)
        │
        ▼
extraction/prompts.py  (builds structured extraction prompt)
        │
        ▼
extraction/anthropic_client.py  (calls Claude Haiku → strips fences → parses JSON)
        │
        ▼
extraction/validator.py  (repairs + validates against schemas.py)
        │
        ▼
storage/json_store.py  (writes tasks_bundle.json via pathlib.Path)
        │
        ▼
ui/dashboard.py  (Streamlit — thin render layer, no business logic)
```

Every stage is a pure Python function. `app.py` is the orchestrator — it calls them in order and owns no logic of its
own. The UI just calls `run_pipeline()` and renders what comes back.

---

## Tech Stack

| Layer               | Technology                                           |
|---------------------|------------------------------------------------------|
| Language            | Python 3.14                                          |
| AI Model            | Anthropic Claude Haiku (`claude-haiku-4-5-20251001`) |
| UI                  | Streamlit                                            |
| Package Manager     | uv                                                   |
| Virtual Environment | uv-managed `.venv/`                                  |
| Config              | `.env` via `python-dotenv`                           |
| Persistence         | Local JSON (`pathlib.Path` throughout)               |
| IDE                 | IntelliJ IDEA Ultimate                               |

---

## Project Structure

```
task-intelligence-pipeline/
├── .env                          ← API key (never committed)
├── app.py                        ← pipeline orchestrator
├── config.py                     ← loads env, single Anthropic client, all Path constants
│
├── extraction/
│   ├── __init__.py
│   ├── anthropic_client.py       ← calls Claude, strips markdown fences, parses JSON
│   ├── prompts.py                ← builds extraction prompt from meeting text
│   └── validator.py              ← repairs + validates model output
│
├── storage/
│   ├── __init__.py
│   ├── json_store.py             ← save_json / load_json utilities
│   └── schemas.py                ← single source of truth: enums, required fields, defaults
│
├── ui/
│   └── dashboard.py              ← Streamlit dashboard
│
└── data/
    ├── tasks_bundle.json         ← pipeline output
    └── sample_output/
        └── tasks_bundle.json     ← saved good run for demo fallback
```

---

## Setup

**Prerequisites:** Python 3.9+, [uv](https://github.com/astral-sh/uv)

```powershell
# 1. Install uv (Windows)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Clone the repo
git clone <repo-url>
cd task-intelligence-pipeline

# 3. Activate virtual environment (Windows)
.venv\Scripts\activate

# 4. Install dependencies
uv add anthropic streamlit python-dotenv requests pandas

# 5. Create .env file at project root
echo ANTHROPIC_API_KEY=your_key_here > .env

# 6. Verify
python -c "import anthropic, streamlit, dotenv, requests, pandas; print('OK')"
```

---

## Running the App

**Pipeline only (terminal output, no UI):**

```bash
python app.py
```

Inspect `data/tasks_bundle.json` to verify extraction quality.

**Full dashboard:**

```bash
streamlit run ui/dashboard.py
```

**Demo fallback** (if API is unavailable):
Check "Use saved demo data" in the sidebar — loads from `data/sample_output/tasks_bundle.json` with no API call.

---

## Key Design Decisions

**Why `schemas.py` as a single source of truth?**
The extraction prompt, the validator, and eventually Go structs all need to agree on field names, enum values, and date
formats. Defining them once and importing everywhere prevents silent drift — the most common integration bug in
multi-stage pipelines.

**Why strip markdown fences from Claude's response?**
Even with an explicit prompt instruction to return only JSON, Claude occasionally wraps the response in ` ```json ``` `
fences. The client strips them with regex before parsing so the validator always receives clean input regardless of
model behavior variance.

**Why is the Streamlit layer kept thin?**
Streamlit reruns the entire script on every user interaction. Business logic inside the UI creates hard-to-debug state
bugs. All pipeline logic lives in plain Python modules — Streamlit only calls `run_pipeline()` and renders what it
returns.

**Why `pathlib.Path` instead of string paths?**
String paths with backslashes break silently on different OS configurations. `pathlib.Path` constructs OS-correct paths
automatically and keeps all file locations centrally defined in `config.py` — nothing is hardcoded anywhere else.

**Why one `config.client` instead of instantiating Anthropic per call?**
The client holds the API key and connection pool. Instantiating it once at import time and sharing it across modules
avoids repeated key loading, is easier to mock in tests, and mirrors how production SDK usage is structured.

---

## Schema Contract

All output written to `tasks_bundle.json` conforms to this structure:

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-04-24T12:00:00",
  "meeting_id": "meeting-001",
  "summary": "One sentence summary of the meeting.",
  "tasks": [
    {
      "task_id": "task-meeting-001-000",
      "meeting_id": "meeting-001",
      "description": "Schedule follow-up appointment for resident Callahan",
      "owner": "Dr. Patel",
      "due_date": "2026-05-02",
      "priority": "high",
      "status": "not_started",
      "risk": "medium"
    }
  ]
}
```

Field rules enforced by `validator.py`, sourced from `schemas.py`:

| Field      | Allowed Values                                       |
|------------|------------------------------------------------------|
| `priority` | `low`, `medium`, `high`                              |
| `status`   | `not_started`, `in_progress`, `completed`, `blocked` |
| `risk`     | `low`, `medium`, `high`, `unknown`                   |
| `due_date` | `YYYY-MM-DD` or `null`                               |
| `owner`    | name string or `null`                                |

Any value outside these constraints is repaired to the schema default and logged as a warning. The pipeline never
crashes on bad model output.

---

## Sample Meeting Notes

The five injected meeting notes are intentionally messy — each tests a different extraction challenge:

| Note              | Challenge                                                                                                 |
|-------------------|-----------------------------------------------------------------------------------------------------------|
| Mrs. Callahan     | Action item buried at end, owner is ambiguous ("me"), soft deadline                                       |
| Mr. Okafor        | Multiple owners, hedged timeframe ("if her schedule allows"), one unowned item                            |
| Resident Flores   | Informal tone, urgency implied not stated, one item with no owner                                         |
| Resident Thompson | One task explicitly unassigned, deadline implied by escalation logic                                      |
| Mrs. Delacroix    | Emotional context dominates, action items feel like afterthoughts, prescription urgency in final sentence |

The variation is intentional — a system that only works on clean, well-formatted input isn't solving a real problem.

---

## Where This Goes Next

The demo pipeline proves the core concept. The full system extends it in three directions:

### 1. Go Concurrent Analyzer

A compiled Go binary (`go_analyzer/main.go`) that Python invokes via `subprocess.run()`. It reads `tasks_bundle.json`,
spins up a worker pool using goroutines and channels, and scores each task for urgency based on due date proximity,
priority, and risk level. Output: `alerts.json` (flagged high-risk tasks) and `ranked_tasks.json` (all tasks sorted by
urgency score).

Go is the right tool here not for performance at demo scale — the dataset is small — but because a worker pool with
bounded concurrency is the *correct pattern* for this kind of batch analysis at production scale. Python's GIL makes
true parallelism awkward for CPU-bound scoring; Go goroutines are cheap, and the channel-based data flow is explicit and
safe. The `tasks_bundle.json` file is the shared contract between the two runtimes — Python writes it, Go reads it,
neither needs to know how the other works internally.

### 2. Real Data Integration

Replace JSONPlaceholder stubs with a live Smartsheet or Google Forms integration. The ingestion layer is already
isolated behind `sample_meetings.py` — swapping the data source means changing one module, not touching the extraction
or validation pipeline.

### 3. Accountability and Alerting Layer

The core business requirement that motivated this project: leadership needs to know when action plans aren't followed
through. Completing this means:

- Storing task state across time — requires moving from local JSON to a real database (PostgreSQL or SQLite)
- A scheduled job that checks task status against due dates
- A notification layer (email or Slack webhook) that fires when tasks are overdue by a defined threshold
- A role-based view so senior leadership sees only flagged items without needing to understand the full pipeline

This is where the project stops being a demo and becomes a production system.