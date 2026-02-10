# RapidWhisper

A modern speech-to-text transcription application using Zhipu GLM API, inspired by SuperWhisper.

## Features

- 🎤 **Global Hotkey Activation** - Activate from anywhere with Ctrl+Space
- 🎨 **Modern Floating UI** - Minimalist pill-shaped window with frosted glass effect
- 🌊 **Real-time Waveform** - Animated sound wave visualization during recording
- 🤫 **Smart Silence Detection** - Automatically stops recording after pauses
- ⚡ **Fast Transcription** - 1-2 second turnaround via AI APIs (Groq, OpenAI, GLM, Z.AI)
- 📋 **Auto-Copy** - Results instantly copied to clipboard
- 🧵 **Multi-threaded** - Smooth UI with background processing
- ⚙️ **Settings Window** - Easy configuration through graphical interface
- 🔔 **System Tray** - Runs in background with tray notifications
- 🚫 **Cancel Recording** - Press ESC to cancel recording without transcription
- 🌍 **Multi-language Support** - Interface available in 15 languages with automatic detection
- ✨ **Smart Text Formatting** - Automatically formats text based on active application
- 🌐 **Web Apps Support** - Detects Google Docs, Notion, Office Online, and 20+ web applications in browsers
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

- Python 3.11 or higher
- Microphone access
- Internet connection for AI API
- API key from one of the supported providers:
  - **Groq** (recommended, free): https://console.groq.com/keys
  - **OpenAI**: https://platform.openai.com/api-keys
  - **GLM**: https://open.bigmodel.cn/usercenter/apikeys
  - **Z.AI** (uses GLM API key): https://api.z.ai

## Installation

### For End Users (Windows)

1. Download `RapidWhisper.exe` from releases
2. Run the application
3. Follow the welcome screen instructions
4. Get a free API key from [Groq](https://console.groq.com/keys)
5. Open Settings (tray icon → Settings) and add your API key
6. Done! Press Ctrl+Space to start recording

**All settings are managed through the Settings Window — no manual config editing needed!**

### For Developers

#### 1. Clone the repository

```bash
git clone <repository-url>
cd RapidWhisper
```

#### 2. Set up virtual environment with uv

```bash
# Install uv if you haven't already
pip install uv

# Create and activate virtual environment
uv venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

#### 3. Install dependencies

```bash
uv pip install -e .
```

#### 4. Install development dependencies (optional)

```bash
uv pip install -e ".[dev]"
```

#### 5. Run the application

```bash
python main.py
```

**Configure everything through the Settings Window after first launch.**

## Usage

### Running the Application

```bash
python main.py
```

### Basic Workflow

1. Press **Ctrl+Space** to activate the floating window
2. Speak into your microphone
3. Press **Ctrl+Space** again to stop recording, or wait for automatic silence detection
4. Press **ESC** to cancel recording without transcription
5. Transcribed text is automatically copied to your clipboard
6. Paste anywhere with **Ctrl+V** (or **Cmd+V** on macOS)
7. Notification appears in system tray when transcription is complete

### Settings

All settings are managed through the **Settings Window** — no manual config editing needed!

#### Opening Settings

1. Right-click on the tray icon
2. Select "Settings" (or "Настройки")
3. Customize everything in the graphical interface
4. Changes apply immediately — no restart required!

#### Settings Categories

**🤖 AI Provider**
- Choose between Groq (free & fast), OpenAI, GLM, or Z.AI
- Configure API keys for each provider
- Groq is recommended for beginners (free tier available)
- Z.AI uses the same API key as GLM (no separate key needed)
- **Note**: Z.AI supports only post-processing and formatting, not audio transcription
- Clickable links to get API keys directly in the UI

**⚡ Application**
- Global hotkey (default: Ctrl+Space)
- Silence detection sensitivity and duration
- Window auto-hide delay
- Window position preset (9 presets + custom)

**🎤 Audio**
- Sample rate (default: 16000 Hz, recommended for speech)
- Audio chunk size

See `docs/settings_guide.md` for detailed configuration guide.

## Localization

RapidWhisper supports 15 languages with automatic system language detection:

🇬🇧 English • 🇨🇳 Chinese • 🇮🇳 Hindi • 🇪🇸 Spanish • 🇫🇷 French • 🇸🇦 Arabic • 🇧🇩 Bengali • 🇷🇺 Russian • 🇵🇹 Portuguese • 🇵🇰 Urdu • 🇮🇩 Indonesian • 🇩🇪 German • 🇯🇵 Japanese • 🇹🇷 Turkish • 🇰🇷 Korean

### Changing Language

**Via Settings Window:**
1. Open Settings (tray icon → Settings)
2. Go to "Languages" tab
3. Click your preferred language
4. Click "Save"
5. Interface updates immediately!

**Note**: This changes the interface language only. You can speak any language - the AI auto-detects!

See `docs/LOCALIZATION.md` for:
- Adding new languages
- Translation guidelines
- RTL language support
- Contributing translations

## Text Formatting

RapidWhisper can automatically format transcribed text based on the active application:

### Supported Applications

**Desktop Apps**: Notion, Obsidian, VS Code, Word, LibreOffice, and more

**Web Apps** (detected in browsers):
- 📝 **Google Services**: Docs, Sheets, Slides, Forms, Keep
- 💼 **Microsoft Office Online**: Word, Excel, PowerPoint, Office 365
- 🤝 **Collaboration Tools**: Dropbox Paper, Quip, Coda.io, Airtable
- 📊 **Zoho Office**: Writer, Sheet, Show

## Hooks (Extensions)

RapidWhisper supports **Python hook scripts** that run at specific pipeline events (recording, transcription, formatting, etc.).  
Hooks are managed in the Settings UI and stored in `config/hooks`.

### Minimal Example

```python
HOOK_EVENT = "transcription_received"

def hookHandler(options):
    data = options.get("data") or {}
    text = data.get("text", "")
    data["text"] = text.strip()
    options["data"] = data
    return options
```

See `docs/hooks_guide.md` for a detailed guide, full event list, and a prompt template to generate new hooks.

### Text Formatting

Enable in **Settings → Processing → Formatting**.

**Supported Applications:**

**Desktop Apps**: Notion, Obsidian, VS Code, Word, LibreOffice, and more

**Web Apps** (detected in browsers):
- 📝 **Google Services**: Docs, Sheets, Slides, Forms, Keep
- 💼 **Microsoft Office Online**: Word, Excel, PowerPoint, Office 365
- 🤝 **Collaboration Tools**: Dropbox Paper, Quip, Coda.io, Airtable
- 📊 **Zoho Office**: Writer, Sheet, Show
- 📔 **Note-Taking**: Notion, Obsidian Publish
- ✍️ **Markdown Editors**: HackMD, StackEdit, GitHub.dev, GitLab, Gitpod

See `docs/WEB_APPS_SUPPORT.md` for:
- Complete list of supported web applications
- How browser detection works
- Custom prompts for each application
- Troubleshooting and debugging

## Development

### Building .exe for Distribution

```bash
# Run the build script
build.bat
```

The script will:
1. Check PyInstaller installation
2. Build clean .exe (without development configs)
3. Output: `dist\RapidWhisper.exe`

**Important**:
- First-time users will see a welcome screen with setup instructions
- Only distribute the .exe file, nothing else needed
- All settings are managed through the Settings Window

See `BUILD_QUICK.md` and `DISTRIBUTION_CHECKLIST.md` for details.

### Project Structure

```
RapidWhisper/
├── core/           # Configuration and state management
├── ui/             # PyQt6 user interface components
├── services/       # Audio, API, and service components
├── models/         # Data models
├── utils/          # Utilities and logging
├── tests/          # Unit, property, and integration tests
├── main.py         # Application entry point
└── pyproject.toml  # Project configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only property-based tests
pytest tests/property/
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .
```

## Troubleshooting

### Microphone Issues

**Error: "Микрофон занят другим приложением"**
- Close other applications using the microphone
- Check system audio settings
- Restart the application

### API Issues

**Error: "Check your API key in Settings"**
- Open Settings and verify your API key is correct
- Ensure no extra spaces around the API key
- Check that the selected provider matches your API key

**Error: "Network error, check connection"**
- Check your internet connection
- Verify the API service is accessible
- Check firewall settings

### Hotkey Issues

**Hotkey not working**
- Try a different key in Settings (e.g., F2, F3)
- Check if another application is using the same hotkey
- Run the application with administrator privileges (Windows)
- Grant accessibility permissions (macOS)

## Platform-Specific Notes

### Windows
- Requires Windows 10 or later for blur effects
- May need to run as administrator for global hotkeys

### macOS
- Requires accessibility permissions for global hotkeys
- Go to System Preferences → Security & Privacy → Accessibility
- Add Python or your terminal application to the list

### Linux
- Blur effects depend on compositor (KDE/GNOME)
- May need to install additional audio libraries:
  ```bash
  sudo apt-get install portaudio19-dev python3-pyaudio
  ```

## 🏗️ Building for Multiple Platforms

### Automatic Build (Recommended)

RapidWhisper uses **GitHub Actions** to automatically build for Windows, macOS, and Linux:

1. **Push code to GitHub** - builds start automatically
2. **Download artifacts** from Actions tab
3. **Create release** by pushing a tag: `git tag v1.0.0 && git push origin v1.0.0`

**No Mac required!** GitHub provides free macOS runners.

📖 **Full guide**: See [BUILD_CROSS_PLATFORM.md](BUILD_CROSS_PLATFORM.md) for detailed instructions.

### Manual Build

**Windows:**
```bash
build.bat
```

**macOS/Linux:**
```bash
pyinstaller RapidWhisper.spec --clean
```

## License

**Open Source - Non-Commercial Use**

Copyright (c) 2026 V01GH7

✅ **Allowed:**
- Personal use free of charge
- Use at work for your own tasks
- Use in business for your own productivity
- View and study the source code
- Modify for personal use
- Fork and experiment

❌ **Prohibited:**
- Selling the software or products based on it
- Selling services using this software
- Commercial distribution
- Removing attribution

📧 For commercial licenses, contact the author.

📖 **More Information:** [LICENSE](LICENSE) | [LICENSE_UPDATE.md](LICENSE_UPDATE.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Inspired by [SuperWhisper](https://superwhisper.com/)
- Powered by [Zhipu GLM API](https://open.bigmodel.cn/)
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
