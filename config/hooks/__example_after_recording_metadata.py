"""
Example hook: attach metadata after recording is saved.

Rename the file to remove the "__" prefix to enable it.
"""

import os

HOOK_EVENT = "after_recording"

def hookHandler(options):
    data = options.get("data") or {}
    audio_path = data.get("audio_file_path")
    if isinstance(audio_path, str) and audio_path:
        data["audio_basename"] = os.path.basename(audio_path)
    options["data"] = data
    return options
