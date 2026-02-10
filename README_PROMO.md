# RapidWhisper

Release README for repositories with prebuilt binaries.

RapidWhisper is a speech-to-text application with hotkey recording, fast AI transcription, and automatic text formatting for desktop and web apps.

## Features

- Global hotkey activation (`Ctrl+Space`)
- Floating UI with real-time waveform
- Automatic stop on silence
- Fast transcription via AI providers (Groq, OpenAI, GLM, Z.AI)
- Automatic clipboard copy of final text
- Text formatting by active app/tab context
- Manual formatting mode for selected target format
- Hook scripts (Python) for pipeline extensions
- Multi-language interface (15 languages)

## Quick Start (Prebuilt)

1. Download the latest binary from Releases.
2. Launch the app.
3. Open Settings from tray icon.
4. Add API key for your provider.
5. Press `Ctrl+Space` to start recording.

No local build or source installation is required in this repository.

## Basic Workflow

1. Press `Ctrl+Space` to start recording.
2. Speak into microphone.
3. Press `Ctrl+Space` again to stop (or wait for silence auto-stop).
4. Press `Esc` to cancel current recording.
5. Final text is copied to clipboard automatically.
6. Paste into any app.

## Settings Overview

Main configuration is managed in the Settings window:

- AI provider and API keys
- Recording and silence detection
- Global hotkeys
- Window behavior and theme
- Text formatting rules and prompts
- Hooks and pipeline actions
- Interface language

## Localization

Supported UI languages:

English, Chinese, Hindi, Spanish, French, Arabic, Bengali, Russian, Portuguese, Urdu, Indonesian, German, Japanese, Turkish, Korean.

Language switching is available in Settings and applies immediately.

## Text Formatting

RapidWhisper supports:

- Auto-format by active app or browser tab
- Manual format selection via dedicated hotkey
- Custom prompts per application format

Supported targets include:

- Notion
- Obsidian
- Markdown
- Word
- LibreOffice
- BBCode
- WhatsApp
- Universal fallback

## Hooks (Extensions)

Python hooks can run on pipeline events such as:

- `before_recording`
- `after_recording`
- `transcription_received`
- `formatting_step`
- `post_formatting_step`
- `task_completed`

Hooks are managed in Settings and stored in `config/hooks`.

## Troubleshooting

### Microphone issues

- Ensure microphone access is granted in OS settings.
- Close other apps that exclusively lock the microphone.

### API issues

- Verify provider API key in Settings.
- Check internet access and provider status.

### Hotkey issues

- Rebind hotkey in Settings if conflict exists.
- On macOS, ensure accessibility permissions are granted.

## Platform Notes

### Windows

- Recommended: Windows 10+
- Admin rights may be needed for some global hotkey environments

### macOS

- Accessibility permission is required for global hotkeys

### Linux

- Behavior can depend on desktop compositor/window manager

## License

Proprietary software. Free for personal and business end-user productivity usage under project license terms.

See:

- `LICENSE`
- `LICENSE_EXPLAINED.md`
- `LICENSE_CLARIFICATION.md`

## Acknowledgments

- Inspired by SuperWhisper
- Built with PyQt6
