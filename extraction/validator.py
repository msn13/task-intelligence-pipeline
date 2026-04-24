from datetime import datetime
from schemas import PRIORITY_VALUES, STATUS_VALUES, RISK_VALUES, DEFAULTS, DATE_FORMAT


def validate_and_repair(extracted: dict, meeting_id: str) -> tuple[dict, list[str]]:
    """Returns (repaired_extracted, warnings)"""
    warnings = []
    tasks = extracted.get("tasks", [])

    for i, task in enumerate(tasks):
        # --- normalize casing ---
        for field in ("priority", "status", "risk"):
            if isinstance(task.get(field), str):
                task[field] = task[field].strip().lower()

        # --- repair invalid enum values ---
        if task.get("priority") not in PRIORITY_VALUES:
            warnings.append(f"Task {i}: invalid priority '{task.get('priority')}' → default")
            task["priority"] = DEFAULTS["priority"]

        if task.get("status") not in STATUS_VALUES:
            warnings.append(f"Task {i}: invalid status '{task.get('status')}' → default")
            task["status"] = DEFAULTS["status"]

        if task.get("risk") not in RISK_VALUES:
            warnings.append(f"Task {i}: invalid risk '{task.get('risk')}' → default")
            task["risk"] = DEFAULTS["risk"]

        # --- validate date format ---
        if task.get("due_date"):
            try:
                datetime.strptime(task["due_date"], DATE_FORMAT)
            except ValueError:
                warnings.append(f"Task {i}: unparseable date '{task['due_date']}' → null")
                task["due_date"] = None

        # --- ensure IDs ---
        if not task.get("meeting_id"):
            task["meeting_id"] = meeting_id

        if not task.get("task_id"):
            task["task_id"] = f"task-{meeting_id}-{i:03d}"

    extracted["tasks"] = tasks
    return extracted, warnings