# 🚀 Gemini Browser UI - Quick Start

## What is this?

AI-powered browser automation with **3-panel embedded browser interface** using Google's Gemini 2.5 Computer Use API.

**Features:**
- 📱 3-panel layout: History | Chat | Embedded Browser
- 🤖 Natural language browser control
- 🌐 Real-time CDP-based browser embedding
- 💬 ChatGPT-style interface

---

## 🏃 Quick Start (60 seconds)

### 1. Install dependencies

```bash
cd gemini_browser_ui
pip install -r requirements.txt
playwright install chromium
```

### 2. Set API key

**Important:** `.env` file should be in the **project root** (parent directory), not in gemini_browser_ui!

```bash
# File location: AI SNS flow/.env (project root)
GEMINI_API_KEY=your_api_key_here
```

The app will automatically load the .env from the project root directory.

Get your API key: https://aistudio.google.com/apikey

### 3. Run!

```bash
python run.py
```

### 4. Open browser

```
http://localhost:8080
```

---

## 💬 Example Commands

Try these in the web UI:

```
구글에서 바나나모드를 검색해줘
```

```
Go to youtube.com and search for cute cats
```

```
Navigate to github.com and search for "gemini computer use"
```

```
Open reddit.com and scroll down 3 times
```

---

## 📁 Files Overview

```
gemini_browser_ui/
├── run.py                      ← 🎯 Main launcher (3-panel embedded UI)
├── gemini_controller.py        ← Gemini controller with CDP
├── computer_use_wrapper.py     ← Gemini Computer Use agent
├── frontend/
│   ├── templates/
│   │   └── index_embedded.html ← 3-panel layout HTML
│   └── static/
│       ├── css/style.css       ← Styling
│       └── js/app_embedded.js  ← Frontend logic
├── requirements.txt            ← Dependencies
└── README.md                   ← Full documentation
```

---

## 🎮 How to Use

1. **Open browser** → Navigate to http://localhost:8080
2. **See 3-panel layout:**
   - **Left:** Chat history
   - **Center:** Input & AI responses
   - **Right:** Embedded Chromium browser (real-time view)
3. **Enter command** → Type natural language task in center panel
4. **Watch automation** → Browser actions appear in real-time on the right panel
5. **Get response** → AI explanation appears in center chat area

---

## 🐛 Troubleshooting

### "Port 8080 already in use"
```bash
lsof -ti:8080 | xargs kill -9
```

### "GEMINI_API_KEY not found"
Create `.env` file with your API key

### "Browser doesn't start"
```bash
playwright install --force chromium
```

---

## 🎨 UI Layout

```
┌──────────────┬────────────────────┬──────────────────────┐
│   Left       │      Center        │       Right           │
│   History    │   Chat Interface   │    Embedded Browser   │
│              │                    │                       │
│ • Past tasks │ • Prompt input     │ • Real-time view      │
│ • Timestamps │ • AI responses     │ • CDP streaming       │
│ • Quick load │ • Action logs      │ • Live automation     │
└──────────────┴────────────────────┴──────────────────────┘
```

---

**Ready? Just run:**
```bash
python run.py
```

That's it! 🎉
