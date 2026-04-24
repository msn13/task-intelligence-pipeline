from datetime import datetime
import config
from storage.sample_meetings import get_note, NOTES
from extraction.antropic_client import  extract_tasks
from extraction.validator import validate_and_repair
from storage.json_store import save_json


def run_pipeline(note_index: int = 0) -> dict:
    meeting_id = f"meeting-{note_index + 1:03d}"

    meeting = {
        "meeting_id": meeting_id,
        "raw_text": get_note(note_index)
    }

    print(f"🔍 Extracting tasks for {meeting_id}...")
    extracted = extract_tasks(meeting)

    repaired, warnings = validate_and_repair(extracted, meeting_id)
    for w in warnings:
        print(f"  ⚠️  {w}")

    bundle = {
        "schema_version": "1.0",
        "generated_at": datetime.utcnow().isoformat(),
        "meeting_id": meeting_id,
        "summary": repaired.get("summary", ""),
        "tasks": repaired.get("tasks", [])
    }

    save_json(bundle, config.TASKS_BUNDLE)
    print(f"✅ Saved {len(bundle['tasks'])} tasks → {config.TASKS_BUNDLE}")
    return bundle


if __name__ == "__main__":
    run_pipeline(note_index=0)