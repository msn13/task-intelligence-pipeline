PRIORITY_VALUES = {"low", "medium", "high"}
STATUS_VALUES = {"not_started", "in_progress", "completed", "blocked"}
RISK_VALUES = {"low", "medium", "high", "unknown"}
DATE_FORMAT = "%Y-%m-%d"

REQUIRED_FIELDS = ["task_id", "meeting_id", "description", "priority", "status"]
NULLABLE_FIELDS = ["owner", "due_date"]

DEFAULTS = {
    "priority": "medium",
    "status": "not_started",
    "risk": "unknown",
}