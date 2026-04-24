from storage.schemas import PRIORITY_VALUES, STATUS_VALUES, RISK_VALUES


def build_extraction_prompt(text: str, meeting_id: str) -> str:
    return f"""You are extracting action items from a wellness team meeting note.

Return ONLY a valid JSON object. No explanation. No markdown. No code fences.

Required format:
{{
  "summary": "one sentence summary of the meeting",
  "tasks": [
    {{
      "task_id": "task-{meeting_id}-000",
      "meeting_id": "{meeting_id}",
      "description": "clear description of what needs to be done",
      "owner": "person responsible or null",
      "due_date": "YYYY-MM-DD or null",
      "priority": "low or medium or high",
      "status": "not_started",
      "risk": "low or medium or high or unknown"
    }}
  ]
}}

Rules:
- priority must be exactly one of: {sorted(PRIORITY_VALUES)}
- status must always be: not_started
- risk must be exactly one of: {sorted(RISK_VALUES)}
- due_date must be YYYY-MM-DD format or null — never a relative date like "next week"
- owner must be a name string or null — never "unassigned" or "TBD"
- Return an empty tasks array [] if there are truly no action items
- Increment task_id suffix for each task: task-{meeting_id}-000, task-{meeting_id}-001, etc.

Today's date is 2026-04-24. Use this to resolve relative dates like "by Friday" or "next week".

Meeting note:
{text}"""