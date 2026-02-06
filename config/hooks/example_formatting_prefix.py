"""
Example hook: prepend a simple title before formatting.

Rename the file to remove the "__" prefix to enable it.
"""

HOOK_EVENT = "formatting_step"

def hookHandler(options):
    data = options.get("data") or {}
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        return options

    if not text.lstrip().startswith("#"):
        data["text"] = "# Draft\n\n" + text
        options["data"] = data
    return options
