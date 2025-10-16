# Gemini Browser UI

**AI-powered browser automation with embedded live view**

A standalone micro-project that provides a web interface for controlling browsers using Google's Gemini 2.5 Computer Use API. Features real-time browser streaming and natural language control.

![Gemini Browser UI](https://img.shields.io/badge/Gemini-2.5%20Computer%20Use-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🤖 **AI Browser Control** - Natural language commands powered by Gemini 2.5
- 📺 **Live Browser View** - Real-time embedded browser with CDP (Chrome DevTools Protocol)
- 💬 **Chat Interface** - Intuitive chat-style prompts
- 🎯 **Computer Use API** - Full support for all 14+ Gemini Computer Use functions:
  - Navigation: `navigate`, `go_back`, `go_forward`, `search`
  - Mouse: `click_at`, `hover_at`, `drag_and_drop`
  - Keyboard: `type_text_at`, `key_combination`
  - Scrolling: `scroll_document`, `scroll_at`
  - Utilities: `wait_5_seconds`, `open_web_browser`

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### Installation

1. **Clone or navigate to this directory**
   ```bash
   cd gemini_browser_ui
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**

   Create a `.env` file:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Open your browser**
   ```
   http://localhost:8080
   ```

## 📁 Project Structure

```
gemini_browser_ui/
├── computer_use_wrapper.py      # Core Gemini Computer Use agent
├── web_ui/
│   ├── backend/
│   │   ├── app.py              # Flask backend (embedded version)
│   │   └── gemini_controller.py # Gemini controller with CDP
│   └── frontend/
│       └── templates/
│           └── index_embedded.html  # Web UI with embedded browser
├── requirements.txt              # Python dependencies
├── run.py                       # Launcher script
└── README.md                    # This file
```

## 🎮 Usage

### Starting the Browser

1. Click **"Start Browser"** button
2. Browser will initialize with Google homepage
3. Embedded view will show live browser content

### Sending Commands

Type natural language commands in the chat input:

```
"Navigate to instagram.com"
"Click on the search box and type 'AI news'"
"Scroll down the page"
"Go to github.com and search for 'gemini computer use'"
```

### Example Commands

| Command | Description |
|---------|-------------|
| `Go to reddit.com` | Navigate to Reddit |
| `Search for 'machine learning'` | Open search and type query |
| `Click on the first result` | Click element |
| `Scroll to the bottom` | Scroll page down |
| `Take a screenshot` | Capture current view |

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional
PORT=8080                        # Server port (default: 8080)
HEADLESS=false                   # Run browser in headless mode
```

### Browser Settings

Edit [gemini_controller.py](web_ui/backend/gemini_controller.py):

```python
# Viewport size
viewport_size=(1280, 800)

# CDP port
remote_debugging_port=9222

# Browser launch args
args=['--disable-blink-features=AutomationControlled']
```

## 🛠️ Development

### Running Tests

```bash
# Test computer_use_wrapper directly
python computer_use_wrapper.py

# Test with specific task
python -c "
from computer_use_wrapper import GeminiComputerUseAgent

with GeminiComputerUseAgent() as agent:
    result = agent.execute_task('Navigate to google.com and search for AI')
    print(result)
"
```

### Debugging

Enable debug logging in [gemini_controller.py](web_ui/backend/gemini_controller.py):

```python
logger.add(sys.stdout, level="DEBUG")
```

## 📚 API Reference

### GeminiComputerUseAgent

Main agent class for browser automation.

```python
from computer_use_wrapper import GeminiComputerUseAgent

agent = GeminiComputerUseAgent(api_key="your_key")
agent.start_browser(headless=False)

# Execute task
result = agent.execute_task("Navigate to github.com", max_steps=5)

# Navigate directly
agent.navigate_to("https://example.com")

# Get page info
info = agent.get_page_info()

# Cleanup
agent.close_browser()
```

### GeminiController

Web UI controller with CDP streaming.

```python
from web_ui.backend.gemini_controller import GeminiController

controller = GeminiController(
    api_key="your_key",
    headless=False,
    viewport_size=(1280, 800),
    remote_debugging_port=9222
)

controller.start_browser()
result = controller.execute_task("Search for AI news", max_steps=10)
```

## 🔍 Troubleshooting

### Port 8080 already in use

```bash
# Kill existing process
lsof -ti:8080 | xargs kill -9

# Or use different port
PORT=8081 python run.py
```

### Browser doesn't start

```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

### Gemini API errors

- Check API key is valid
- Ensure you have Computer Use API access
- Check rate limits: [Google AI Studio](https://aistudio.google.com)

### CDP connection issues

- Ensure port 9222 is available
- Check firewall settings
- Try different port in `gemini_controller.py`

## 📝 License

MIT License - feel free to use in your projects!

## 🙏 Credits

- Built with [Google Gemini 2.5 Computer Use API](https://ai.google.dev/gemini-api/docs/computer-use)
- Browser automation via [Playwright](https://playwright.dev/)
- Web framework: [Flask](https://flask.palletsprojects.com/) + [Socket.IO](https://socket.io/)

## 🚧 Roadmap

- [ ] Multi-tab support
- [ ] Session recording/replay
- [ ] Custom action macros
- [ ] Mobile device emulation
- [ ] Docker containerization
- [ ] Instagram automation presets

---

**Need help?** Open an issue or check the [documentation](https://ai.google.dev/gemini-api/docs/computer-use)
