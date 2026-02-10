# RapidWhisper Hooks Creation Guide

This is a document you can pass to a contractor. It describes how hooks work, what events exist, what data structure they receive, and how to write correct scripts.

## 1. What is a hook
A hook is a Python script that runs at a specific step of the pipeline.
One file = one hook = one event.

A hook receives `options` (a dictionary) and **must return a dictionary** of the same structure for the chain to continue.

## 2. Where to store hooks
Hook scripts are stored by default in:
```
config/hooks
```

Files with the `__` prefix are ignored.
To enable an example — remove `__` from the filename.

## 3. Required file structure
Minimal hook file:
```python
HOOK_EVENT = "transcription_received"

def hookHandler(options):
    # your code
    return options
```

**Required:**
- The file must have `HOOK_EVENT` (a string).
- The file must have a function `hookHandler(options)`.
- `hookHandler` returns the `options` dictionary.

If `HOOK_EVENT` is missing or invalid — the file **will not be registered**.

## 4. List of available events
- `before_recording` — before recording starts
- `after_recording` — after recording (audio file is saved)
- `transcription_received` — text received from ASR
- `formatting_step` — formatting step
- `post_formatting_step` — post-formatting step
- `task_completed` — final text before display

## 5. Structure of `options`
Example of a typical payload:
```json
{
  "event": "transcription_received",
  "session_id": "session_123",
  "timestamps": {
    "event_time": "2026-02-06T20:11:22.123456"
  },
  "data": {
    "audio_file_path": "D:/recordings/clip.wav",
    "text": "Raw text from ASR"
  },
  "hooks": [
    {
      "name": "normalize_text",
      "event": "transcription_received",
      "status": "ok",
      "duration_ms": 12,
      "background": false
    }
  ],
  "errors": [
    {"hook": "foo", "event": "transcription_received", "error": "Traceback..."}
  ]
}
```

### `data` keys by event
| Event | `data` keys | What can be modified |
| --- | --- | --- |
| `before_recording` | *(empty)* | You can add your own fields |
| `after_recording` | `audio_file_path` | Can replace the path |
| `transcription_received` | `text`, `audio_file_path` | Can modify `text` |
| `formatting_step` | `text`, `format_type`, `combined` | Can modify `text` |
| `post_formatting_step` | `text`, `format_type`, `combined` | Can modify `text` |
| `task_completed` | `text` | Can modify `text` |

## 6. Background hooks
In the UI you can mark a hook as **"Background"**.
In this case:
- the hook runs asynchronously
- the main chain doesn't wait for its result
- the hook result doesn't affect the text

Use background hooks **only for side effects**: logging, statistics, sending to external services, etc.

## 7. Examples

### Example 1 — Trim whitespace after transcription
```python
HOOK_EVENT = "transcription_received"

def hookHandler(options):
    data = options.get("data") or {}
    text = data.get("text")
    if not isinstance(text, str):
        return options

    lines = [line.strip() for line in text.splitlines()]
    data["text"] = "\n".join(lines).strip()
    options["data"] = data
    return options
```

### Example 2 — Add metadata after recording
```python
import os

HOOK_EVENT = "after_recording"

def hookHandler(options):
    data = options.get("data") or {}
    audio_path = data.get("audio_file_path")
    if isinstance(audio_path, str) and audio_path:
        data["audio_basename"] = os.path.basename(audio_path)
    options["data"] = data
    return options
```

### Example 3 — Add heading before formatting
```python
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
```

## 8. AI prompt template (to generate a hook)
Copy and paste this prompt into the model:

```text
You are a Python developer. Generate a hook file for RapidWhisper.

Requirements:
- One file = one hook
- File must have HOOK_EVENT
- Function hookHandler(options) returns options
- Only modify options["data"]
- Don't break the options structure

Event: <INSERT_EVENT>
My task: <DESCRIBE_WHAT_HOOK_SHOULD_DO>

Write clean code, add type checks and safe conditions.
Return only the file code without explanations.
```

## 9. Testing and enabling
1. Save the file to `config/hooks/`
2. Make sure there's no `__` prefix
3. In the UI, enable hooks and select the event
4. Verify the hook appears in the list and is enabled
