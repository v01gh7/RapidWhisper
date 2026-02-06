# Hooks System Plan

## Summary
Implement a hook system for RapidWhisper with:
- Event-based hooks at key pipeline steps
- Per-hook enable/disable and background execution
- Unified hook chain for all formats, with format info in options
- UI to reorder hooks and toggle settings
- Dedicated Hooks log with rotation at 5MB

## Goals
- Allow Python hook scripts to run at each pipeline step
- Preserve data flow across hooks (options in/out shape is identical)
- Provide a UI to manage hook order and execution settings
- Add logs with rotation for both `rapidwhisper.log` and `hooks.log`

## Hook Events
- before_recording
- after_recording
- transcription_received
- formatting_step
- post_formatting_step
- task_completed

## Hook Contract
Each hook script must expose:
```
HOOK_EVENT = "transcription_received"

def hookHandler(options: dict) -> dict:
    ...
    return options
```
Rules:
- Must return the same structural shape as received
- Can modify values inside `options`
- `HOOK_EVENT` must be one of the supported events (one hook file = one event)

## options Structure (schema)
Required keys in the payload passed to `hookHandler`:
- `event`: string hook event name
- `session_id`: string or null
- `timestamps`: object with `event_time` (UTC ISO string)
- `data`: event-specific payload (see table below)
- `hooks`: list of hook execution results (appended by the manager)
- `errors`: list of hook errors (appended by the manager)

Example payload:
```
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

### Event data payloads
| Event | `data` keys | Notes |
| --- | --- | --- |
| `before_recording` | *(empty)* | Can be used to set defaults in `data`. |
| `after_recording` | `audio_file_path` | Hook may replace `audio_file_path` to point to a new file. |
| `transcription_received` | `text`, `audio_file_path` | Hook may edit `text`. |
| `formatting_step` | `text`, `format_type`, `combined` | `format_type` can be `null` or a string (e.g., `fallback`). |
| `post_formatting_step` | `text`, `format_type`, `combined` | Same keys as `formatting_step`. |
| `task_completed` | `text` | Final text before display. |

## Config (config.jsonc)
Add:
```
"hooks": {
  "enabled": true,
  "paths": ["config/hooks"],
  "order": {
    "before_recording": ["hook_a", "hook_b"],
    "after_recording": [],
    "transcription_received": [],
    "formatting_step": [],
    "post_formatting_step": [],
    "task_completed": []
  },
  "disabled": {
    "before_recording": [],
    "after_recording": [],
    "transcription_received": [],
    "formatting_step": [],
    "post_formatting_step": [],
    "task_completed": []
  },
  "background": {
    "before_recording": [],
    "after_recording": [],
    "transcription_received": [],
    "formatting_step": [],
    "post_formatting_step": [],
    "task_completed": []
  },
  "log": {
    "enabled": true,
    "max_entries": 500
  }
}
```

## Hook Discovery
- Recursively scan paths (max depth 5)
- Register scripts containing `hookHandler`
- Ignore others
- Example hooks are stored in `config/hooks` with a `__` prefix to keep them disabled by default. Rename to enable.
- Hooks missing `HOOK_EVENT` are skipped

## HookManager
New service, e.g. `services/hooks_manager.py`
Responsibilities:
- Discover/load hooks
- Execute hooks in config order
- Run only hooks whose `HOOK_EVENT` matches the current event
- Skip disabled hooks
- If background: run async (side-effects only)
- Log errors and continue

## Pipeline Integration
- before_recording: StateManager.on_hotkey_pressed()
- after_recording: main.py::_on_recording_stopped()
- transcription_received: TranscriptionThread.run() after ASR
- formatting_step: ProcessingCoordinator.process_transcription() before formatting
- post_formatting_step: ProcessingCoordinator post-processing path
- task_completed: StateManager.on_transcription_complete() before display

## UI Changes
### Hooks Tab
- Event selector (dropdown)
- List of hooks for the selected event
- Per-hook:
  - Enabled checkbox
  - Background checkbox
  - Up/Down buttons (and drag/drop)
- Reload hooks button

### Logs Tab
- Table: time, event, hook, status, duration, summary
- Filter by event/hook
- Max entries from config

## Background Hooks (Async)
- Only side-effects, no changes to pipeline
- Results are logged only

## Log Rotation
- If `rapidwhisper.log` > 5MB: delete
- If `hooks.log` > 5MB: delete
- Check at logger initialization and HookManager startup

## Tests / Scenarios
- Hook discovery
- Order persistence
- Disabled hooks skipped
- Background hooks run async
- Log entries appear and rotate
