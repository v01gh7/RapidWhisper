# RapidWhisper

<div align="center">

![RapidWhisper](https://img.shields.io/badge/RapidWhisper-v1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-Non--Commercial-orange)

[**Download for Windows / macOS / Linux**](https://v01gh7.github.io/RapidWhisper/) • [Website](https://v01gh7.github.io/RapidWhisper/) • [Discord](https://discord.gg/sZUZKDeq)

A modern speech-to-text transcription application using AI APIs, inspired by SuperWhisper.

</div>

## Features

- 🎤 **Global Hotkey Activation** - Press **Ctrl+Space** to start recording
- 🎨 **Modern Floating UI** - Minimalist pill-shaped window with frosted glass effect
- 🌊 **Real-time Waveform** - Animated sound wave visualization during recording
- 🤫 **Smart Silence Detection** - Automatically stops recording after pauses
- ⚡ **Fast Transcription** - 1-2 second turnaround via AI APIs (Groq, OpenAI, GLM, Z.AI)
- 📋 **Auto-Copy** - Results instantly copied to clipboard
- ⚙️ **Settings Window** - Easy configuration through graphical interface
- 🔔 **System Tray** - Runs in background with tray notifications
- 🌍 **Multi-language Support** - Interface available in 15 languages
- ✨ **Smart Text Formatting** - Automatically formats text based on active application
- 🌐 **Web Apps Support** - Detects Google Docs, Notion, Office Online, and 20+ web applications
- 🪝 **Hook Scripts (Python)** - Extend the pipeline with your own event hooks

---

## 💖 Support the Project

**The program is free, but even a 30-cent donation helps!**

I develop RapidWhisper in my free time and **every donation motivates me to keep improving it**. Even if you can't donate — **just hop into Discord and say that the app helps you**. That feedback alone makes it all worth it!

**Ways to support:**

| Platform | Link |
|----------|------|
| 💰 **Streamlabs** | [streamlabs.com/v01gh7/tip](https://streamlabs.com/v01gh7/tip) |
| 🎁 **Donatex** | [donatex.gg/donate/v01gh7](https://donatex.gg/donate/v01gh7) |
| ☕ **Ko-fi** | [ko-fi.com/v01gh7](https://ko-fi.com/v01gh7) |
| 💬 **Discord** | [discord.gg/sZUZKDeq](https://discord.gg/sZUZKDeq) — drop a message that it helps! |

---

## Requirements

- Microphone access
- Internet connection for AI API
- API key from one of the supported providers:
  - **Groq** (recommended, free): https://console.groq.com/keys
  - **OpenAI**: https://platform.openai.com/api-keys
  - **GLM**: https://open.bigmodel.cn/usercenter/apikeys
  - **Z.AI** (uses GLM API key): https://api.z.ai

## Installation

**For End Users:**

1. Download from [v01gh7.github.io/RapidWhisper](https://v01gh7.github.io/RapidWhisper/)
2. Run the application
3. Follow the welcome screen instructions
4. Get a free API key from [Groq](https://console.groq.com/keys)
5. Open Settings (tray icon → Settings) and add your API key
6. Done! Press Ctrl+Space to start recording

**All settings are managed through the Settings Window — no manual config editing needed!**

## Usage

### Hotkeys

| Action | Hotkey |
|--------|--------|
| 🎤 Start/Stop Recording | `Ctrl+Space` |
| ❌ Cancel Recording | `Esc` |
| 🎨 Format Picker | `Ctrl+Alt+Space` |
| ✨ Manual Formatting | `Ctrl+Shift+Space` |

*All hotkeys can be customized in Settings.*

### Basic Workflow

1. Press **Ctrl+Space** to start recording
2. Speak into your microphone
3. Press **Ctrl+Space** again to stop, or wait for automatic silence detection
4. Press **ESC** to cancel without transcription
5. Text is automatically copied to clipboard
6. Paste anywhere with **Ctrl+V**

### Settings

Right-click the tray icon → Settings. All changes apply immediately without restart.

## Documentation

- 📖 [Settings Guide](docs/settings_guide.md) — Configuration options
- 🌍 [Localization](docs/LOCALIZATION.md) — Adding new languages
- 🌐 [Web Apps Support](docs/WEB_APPS_SUPPORT.md) — Supported browsers and apps
- 🪝 [Hooks Guide](docs/hooks_guide.md) — Python extensions and automation
- 🏗️ [Building](docs/BUILD_CROSS_PLATFORM.md) — Build for multiple platforms
- 📜 [License](LICENSE) — Open Source (Non-Commercial)

## Troubleshooting

**Microphone not working?**
- Close other apps using the microphone
- Check system audio settings
- Restart the application

**Hotkey not working?**
- Try a different key in Settings
- Check if another app is using the same hotkey
- Run as administrator (Windows) or grant accessibility permissions (macOS)

**API errors?**
- Verify your API key in Settings
- Check internet connection
- Ensure the selected provider matches your API key

## License

**Open Source - Non-Commercial Use**

Copyright (c) 2026 V01GH7

✅ Free for personal use, work, and business (as end user)
❌ Commercial use, selling products/services based on it prohibited

📖 [Full License](LICENSE) | [LICENSE_UPDATE.md](LICENSE_UPDATE.md)

## Acknowledgments

- Inspired by [SuperWhisper](https://superwhisper.com/)
- Powered by AI APIs (Groq, OpenAI, GLM, Z.AI)
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
