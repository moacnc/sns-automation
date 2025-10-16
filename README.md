# Instagram Automation - Pure ADB/uiautomator2

> Advanced Instagram automation using pure ADB commands and uiautomator2 with GPT-4 Vision for intelligent content analysis.

## 🎯 Overview

This project provides production-ready Instagram automation with:
- 🚀 **Fast Navigation**: Direct ADB commands with coordinate-based tapping
- 👤 **User Search & Follow**: Smart follow functionality with status detection
- 📊 **Profile Analysis**: GPT-4 Vision OCR for profile information extraction
- 📸 **Story Automation**: Automated story viewing and reposting (coming soon)
- 🎯 **Content Filtering**: AI-powered inappropriate content detection

## ✨ Key Features

- ✅ **Pure ADB/uiautomator2**: No GramAddict dependency, faster and more reliable
- ✅ **Smart Follow System**: Auto-detect follow status, never unfollow
- ✅ **Multi-layer Fallback**: Resource ID → Text → Coordinate-based clicking
- ✅ **Screen Rotation Lock**: Consistent coordinates across sessions
- ✅ **GPT-4 Vision**: Intelligent image analysis and OCR
- ✅ **Comprehensive Testing**: Phase-based test suite with screenshots

## 🏗️ Architecture

```
Test Suite (tests/)
    ├── phase1_infrastructure/    # ADB, UIAutomator2, Instagram launch
    ├── phase2_navigation/         # Tab navigation, user search
    ├── phase3_vision/             # Follow, OCR, content filter
    ├── phase4_integration/        # Profile scraping
    └── phase5_advanced/           # Story automation

Core Navigation (src/gramaddict_wrapper/navigation.py)
    ├── connect()                  # Device connection with auto-detection
    ├── launch_instagram()         # App launch with fallback
    ├── goto_home/search/profile() # Tab navigation (coordinate-based)
    ├── search_username()          # User search with multi-layer fallback
    ├── check_follow_status()      # Detect current follow state
    └── follow_user()              # Smart follow (skip if already following)

Vision Analysis (src/gramaddict_wrapper/vision_analyzer.py)
    └── GPT-4 Vision for profile OCR and content analysis

Device Layer (Pure ADB/uiautomator2)
    ├── ADB (Android Debug Bridge)
    └── uiautomator2 (No third-party frameworks)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Android device** with Instagram app (logged in)
- **ADB installed** and device connected via USB debugging
- **OpenAI API key** (for GPT-4 Vision features)

### Installation

```bash
# Clone repository
git clone https://github.com/moacnc/sns-automation.git
cd sns-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Device Setup

```bash
# 1. Enable USB Debugging on your Android device
#    Settings → About Phone → Tap "Build Number" 7 times
#    Settings → Developer Options → Enable "USB Debugging"

# 2. Connect device and verify
adb devices
# Should show: <DEVICE_ID>    device

# 3. Initialize uiautomator2 service
python3 -m uiautomator2 init
```

### Running Tests

Run tests in sequential order:

```bash
# Phase 1: Infrastructure
python3 tests/phase1_infrastructure/test_device_connection.py
python3 tests/phase1_infrastructure/test_instagram_launch.py

# Phase 2: Navigation
python3 tests/phase2_navigation/test_tab_navigation.py
python3 tests/phase2_navigation/test_search_user.py

# Phase 3: Follow Feature
python3 tests/phase3_vision/test_follow_user.py
```

### Usage Examples

#### 1. Basic Navigation

```python
from src.gramaddict_wrapper import InstagramNavigator

# Initialize and connect
navigator = InstagramNavigator()
navigator.connect()

# Launch Instagram
navigator.launch_instagram()

# Navigate tabs
navigator.goto_home()
navigator.goto_search()
navigator.goto_profile()
```

#### 2. Search and Follow User

```python
from src.gramaddict_wrapper import InstagramNavigator

navigator = InstagramNavigator()
navigator.connect()

# Search for user
navigator.search_username("targetuser")

# Check follow status
status = navigator.check_follow_status()
print(f"Follow status: {status}")
# Returns: "follow", "following", "requested", or "unknown"

# Follow user (skips if already following)
success = navigator.follow_user()
if success:
    print("✅ Follow action completed")
```

#### 3. Profile Scraping with GPT-4 Vision

```python
from src.gramaddict_wrapper import InstagramNavigator, ProfileScraper

navigator = InstagramNavigator()
navigator.connect()
scraper = ProfileScraper(navigator)

# Scrape profile
profile = scraper.scrape_profile("username")
print(f"Username: {profile['username']}")
print(f"Followers: {profile['follower_count']}")
print(f"Bio: {profile['bio']}")
```

## 📊 Test Results

All tests passing with real Android device (Samsung SM-N981N, Android 13, 1080x2400):

✅ **Phase 1.1**: ADB connection
✅ **Phase 1.2**: UIAutomator2 service
✅ **Phase 1.3**: Instagram app launch
✅ **Phase 2.1**: Tab navigation (Home/Search/Profile)
✅ **Phase 2.2**: User search and profile navigation
✅ **Phase 3.3**: Follow user with status detection

Screenshots saved in `tests/phase*/screenshots/`

## 🎯 Accurate Coordinates

| Element | Coordinates (x, y) | Notes |
|---------|-------------------|-------|
| Home Tab | (108, 2165) | Bottom navigation |
| Search Tab | (324, 2165) | Bottom navigation |
| Profile Tab | (972, 2165) | Bottom navigation |
| Search Input | (530, 168) | Top search bar |
| First Search Result | (540, 522) | First user in results |
| Follow Button | (168, 397) | Blue button on profile |

*Coordinates are for 1080x2400 resolution. Screen rotation is locked to portrait.*

## 🔧 Configuration

### Environment Variables (.env)

```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Database (optional)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=instagram_automation
DB_USER=your_user
DB_PASSWORD=your_password
```

### Device Configuration

The navigator automatically:
- Detects connected ADB devices
- Locks screen rotation to portrait
- Initializes uiautomator2 service

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - Development setup and guidelines

## 🛠️ Technology Stack

- **ADB** (Android Debug Bridge) - Device control and input
- **uiautomator2** - UI element detection and interaction
- **OpenAI GPT-4 Vision** - Image analysis and OCR
- **Python 3.8+** - Core language
- **loguru** - Structured logging
- **pytest** - Testing framework

## 🔒 Safety Features

- ✅ **No Unfollow**: Follow function never unfollows existing follows
- ✅ **Status Detection**: Checks follow state before action
- ✅ **Rate Limiting**: Built-in delays to avoid Instagram limits
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Screen Lock**: Prevents coordinate drift from rotation

## 🚧 Current Limitations

- Coordinates are resolution-specific (1080x2400)
- Requires physical device (emulator not tested)
- Instagram UI changes may require coordinate updates
- Requires screen to stay on during automation

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Built with pure ADB and uiautomator2
- GPT-4 Vision by OpenAI
- Custom implementation with no third-party automation frameworks

---

**Repository**: https://github.com/moacnc/sns-automation
