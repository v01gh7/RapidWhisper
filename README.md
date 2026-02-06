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

**Note**: Settings are automatically saved in `%APPDATA%\RapidWhisper\.env`

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

#### 5. Configure API key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and configure your preferred AI provider:

```env
# Choose your AI provider (groq, openai, or glm)
AI_PROVIDER=groq

# Add your API key for the chosen provider
GROQ_API_KEY=your_groq_key_here
# OPENAI_API_KEY=your_openai_key_here
# GLM_API_KEY=your_glm_key_here
```

**Or use the Settings Window** after first launch to configure through GUI.

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

### Configuration

Settings are automatically saved in:
- **Windows**: `%APPDATA%\RapidWhisper\.env`
- **macOS**: `~/Library/Application Support/RapidWhisper/.env`
- **Linux**: `~/.config/RapidWhisper/.env`

All settings can be customized through the **Settings Window** (no restart required!):

#### Opening Settings Window

1. Right-click on the tray icon
2. Select "Настройки" (Settings)
3. Modify settings in the graphical interface
4. Click "💾 Сохранить" to save
5. Settings apply immediately without restart!

#### Settings Categories

**🤖 AI Provider**
- Choose between Groq (free & fast), OpenAI, GLM, or Z.AI
- Configure API keys for each provider
- Groq is recommended for beginners (free tier available)
- Z.AI uses the same API key as GLM (no separate key needed)
- **Note**: Z.AI supports only post-processing and formatting, not audio transcription
- Clickable links to get API keys

**⚡ Application**
- `HOTKEY` - Global activation key (default: ctrl+space)
- `SILENCE_THRESHOLD` - Sensitivity for silence detection (default: 0.02)
- `SILENCE_DURATION` - How long to wait before stopping (default: 1.5 seconds)
- `AUTO_HIDE_DELAY` - Window auto-hide delay (default: 2.5 seconds)

**🎤 Audio**
- `SAMPLE_RATE` - Audio sample rate (default: 16000 Hz, recommended for speech)
- `CHUNK_SIZE` - Audio chunk size (default: 1024 frames)

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

**Via Configuration:**
```env
# In .env file
INTERFACE_LANGUAGE=en-us  # or ru, zh, es, fr, etc.
```

**Note**: This changes the interface language only. You can speak any language - Whisper auto-detects!

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
- 📔 **Note-Taking**: Notion, Obsidian Publish
- ✍️ **Markdown Editors**: HackMD, StackEdit, GitHub.dev, GitLab, Gitpod

### Configuration

Enable in Settings → Processing → Formatting, or via `.env`:

```env
FORMATTING_ENABLED=true
FORMATTING_PROVIDER=groq
FORMATTING_APPLICATIONS=word,notion,obsidian,markdown
```

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
2. Save your development .env
3. Build clean .exe (without .env files)
4. Restore your development .env

Output: `dist\RapidWhisper.exe`

**Important**: 
- The .exe contains NO .env files
- Settings are saved in `%APPDATA%\RapidWhisper\.env`
- First-time users will see a welcome screen with setup instructions
- Only distribute the .exe file, nothing else needed

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

**Error: "Проверьте GLM_API_KEY в .env файле"**
- Verify your API key is correct in `.env`
- Check that `.env` file exists in the project root
- Ensure no extra spaces around the API key

**Error: "Ошибка сети, проверьте подключение"**
- Check your internet connection
- Verify GLM API service is accessible
- Check firewall settings

### Hotkey Issues

**Hotkey not working**
- Try a different key in `.env` (e.g., F2, F3)
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

**Proprietary Software - Free for Personal & Business Use**

Copyright (c) 2026 V01GH7 - All Rights Reserved

✅ **Allowed:**
- Personal use free of charge
- Use at work for your own tasks
- Use in business for your own productivity
- Use anywhere as long as YOU are the end user

❌ **Prohibited:**
- Viewing or accessing source code
- Selling the software or its copies
- Selling services based on the software
- Distribution or sharing binaries
- Modification or reverse engineering
- Resale or sublicensing

📧 For commercial licenses (selling services/products based on this software), contact the author.

📖 **More Information:**
- Full License: [LICENSE](LICENSE)
- Detailed Explanation: [LICENSE_EXPLAINED.md](LICENSE_EXPLAINED.md)
- Business Use Clarification: [LICENSE_CLARIFICATION.md](LICENSE_CLARIFICATION.md)

**Note:** This is proprietary software. Source code is not available for viewing or modification.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Inspired by [SuperWhisper](https://superwhisper.com/)
- Powered by [Zhipu GLM API](https://open.bigmodel.cn/)
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
