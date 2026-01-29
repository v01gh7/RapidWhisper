# RapidWhisper

A modern speech-to-text transcription application using Zhipu GLM API, inspired by SuperWhisper.

## Features

- 🎤 **Global Hotkey Activation** - Activate from anywhere with F1
- 🎨 **Modern Floating UI** - Minimalist pill-shaped window with frosted glass effect
- 🌊 **Real-time Waveform** - Animated sound wave visualization during recording
- 🤫 **Smart Silence Detection** - Automatically stops recording after pauses
- ⚡ **Fast Transcription** - 1-2 second turnaround via GLM API
- 📋 **Auto-Copy** - Results instantly copied to clipboard
- 🧵 **Multi-threaded** - Smooth UI with background processing

## Requirements

- Python 3.11 or higher
- Microphone access
- Internet connection for GLM API
- Zhipu GLM API key ([Get one here](https://open.bigmodel.cn/))

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd RapidWhisper
```

### 2. Set up virtual environment with uv

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

### 3. Install dependencies

```bash
uv pip install -e .
```

### 4. Install development dependencies (optional)

```bash
uv pip install -e ".[dev]"
```

### 5. Configure API key

Copy the example environment file and add your GLM API key:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
GLM_API_KEY=your_api_key_here
```

## Usage

### Running the Application

```bash
python main.py
```

### Basic Workflow

1. Press **F1** to activate the floating window
2. Speak into your microphone
3. The app automatically detects when you stop speaking
4. Transcribed text is copied to your clipboard
5. Paste anywhere with **Ctrl+V** (or **Cmd+V** on macOS)

### Configuration

All settings can be customized in the `.env` file:

- `HOTKEY` - Global activation key (default: F1)
- `SILENCE_THRESHOLD` - Sensitivity for silence detection (default: 0.02)
- `SILENCE_DURATION` - How long to wait before stopping (default: 1.5 seconds)
- `AUTO_HIDE_DELAY` - Window auto-hide delay (default: 2.5 seconds)
- `WINDOW_WIDTH` / `WINDOW_HEIGHT` - Window dimensions

See `.env.example` for all available options.

## Development

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

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Inspired by [SuperWhisper](https://superwhisper.com/)
- Powered by [Zhipu GLM API](https://open.bigmodel.cn/)
- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
