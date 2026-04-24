import json
import config
from prompts import build_extraction_prompt


def extract_tasks(meeting: dict) -> dict:
    """
    meeting: {"meeting_id": str, "raw_text": str}
    returns: {"summary": str, "tasks": [...]}
    """
    prompt = build_extraction_prompt(
        text=meeting["raw_text"],
        meeting_id=meeting["meeting_id"]
    )

    response = config.client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    # removes ``` wrapping from claude response so it's pure json
    raw = response.content[0].text
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    raw = raw.rsplit("```", 1)[0]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("❌ Claude returned non-JSON:\n", raw)
        raise


# at the bottom of anthropic_client.py temporarily for testing without ui
# if __name__ == "__main__":
#     from storage.sample_meetings import get_note
#
#     result = extract_tasks({"meeting_id": "meeting-001", "raw_text": get_note(0)})
#     print(result)