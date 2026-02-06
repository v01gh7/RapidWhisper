"""
Example hook: clean up whitespace right after transcription.

Rename the file to remove the "__" prefix to enable it.
"""

HOOK_EVENT = "transcription_received"


def hookHandler(options):
    data = options.get("data") or {}
    text = data.get("text")
    if not isinstance(text, str):
        return options

    # Trim each line and normalize outer whitespace without touching content.
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(lines).strip()
    data["text"] = cleaned
    options["data"] = data
    return options
