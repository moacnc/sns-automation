# Instagram Automation - Development Guide

**Version**: 4.0 (Pure ADB/uiautomator2)
**Last Updated**: 2025-10-14
**Goal**: Instagram automation using direct ADB control with AI-powered features

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Quick Start (15 minutes)](#2-quick-start-15-minutes)
3. [System Architecture](#3-system-architecture)
4. [Core Features](#4-core-features)
5. [Development Setup](#5-development-setup)
6. [Testing](#6-testing)
7. [Database Configuration](#7-database-configuration)
8. [Safety & Best Practices](#8-safety--best-practices)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Project Overview

### 1.1 Goals

This system provides Instagram automation with:

#### ✅ Feature 1: User Search and Follow
- Navigate to user profiles
- Detect follow status (follow/following/requested/unknown)
- Smart follow (never unfollow existing follows)

#### ✅ Feature 2: Profile Information Scraping
- Extract profile data using GPT-4 Vision OCR
- Collect followers, following, posts count
- Analyze bio and profile information

#### ✅ Feature 3: Story Automation (Coming Soon)
- View and analyze stories
- Content filtering with AI
- Automated reposting

### 1.2 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Device Control** | ADB | Android Debug Bridge |
| **UI Automation** | uiautomator2 | Element detection and interaction |
| **AI Layer** | OpenAI GPT-4 Vision | Image analysis, OCR, content filtering |
| **Language** | Python 3.8+ | Core implementation |
| **Database** | PostgreSQL/AlloyDB | Session logs, profile data |
| **Logging** | Loguru | Structured logging |

### 1.3 Key Principles

- ✅ **Pure ADB/uiautomator2**: No third-party automation frameworks
- ✅ **Multi-layer Fallback**: Resource ID → Text → Coordinates
- ✅ **GPT Vision for Intelligence**: OCR and analysis, not navigation
- ✅ **Safety First**: Status detection, rate limiting, error handling

---

## 2. Quick Start (15 minutes)

### Step 1: Setup Script (Recommended)

```bash
# Automated setup (recommended)
./scripts/setup_dev.sh
```

This script automatically:
- ✅ Creates Python virtual environment
- ✅ Installs dependencies (uiautomator2, OpenAI SDK, etc.)
- ✅ Creates environment file
- ✅ Starts PostgreSQL (Docker)
- ✅ Tests database connection

### Step 2: Environment Variables

Edit `.env` file and add your API key:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-your-api-key-here

# PostgreSQL (auto-configured)
DB_HOST=127.0.0.1
DB_PORT=5434
DB_NAME=instagram_automation
DB_USER=postgres
DB_PASSWORD=devpassword123
```

### Step 3: Android Device Setup

```bash
# 1. Enable USB Debugging on Android device
#    Settings → About Phone → Tap "Build Number" 7 times
#    Settings → Developer Options → Enable "USB Debugging"

# 2. Connect device and verify
adb devices
# Should show: <DEVICE_ID>    device

# 3. Initialize uiautomator2 service
python3 -m uiautomator2 init

# 4. Test connection
python3 tests/phase1_infrastructure/test_device_connection.py
```

### Step 4: Run Your First Test

```bash
# Test Instagram launch
python3 tests/phase1_infrastructure/test_instagram_launch.py

# Test tab navigation
python3 tests/phase2_navigation/test_tab_navigation.py

# Test user search and follow
python3 tests/phase3_vision/test_follow_user.py
```

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
Application Layer (tests/, examples/)
           ↓
Navigation Wrapper (src/gramaddict_wrapper/)
    ├── InstagramNavigator (navigation.py)
    ├── VisionAnalyzer (vision_analyzer.py)
    ├── ProfileScraper (profile_scraper.py)
    ├── StoryRestory (story_restory.py)
    └── DMSender (dm_sender.py)
           ↓
Core Technologies
    ├── ADB + uiautomator2 (Device control)
    └── OpenAI GPT-4 Vision (AI analysis)
           ↓
Android Device + Instagram App
```

> **Note**: Despite directory name "gramaddict_wrapper", this uses **pure ADB and uiautomator2** with no third-party automation frameworks.

### 3.2 Multi-layer Navigation Fallback

1. **Resource ID** (Primary)
   ```python
   d(resourceId="com.instagram.android:id/search_edit_text")
   ```

2. **Text Matching** (Fallback)
   ```python
   d(text="Search")
   ```

3. **Coordinates** (Final Fallback)
   ```python
   d.click(540, 168)  # Resolution-specific
   ```

---

## 4. Core Features

### 4.1 User Search and Follow

```python
from src.gramaddict_wrapper import InstagramNavigator

# Initialize
nav = InstagramNavigator()
nav.connect()
nav.launch_instagram()

# Search user
nav.search_username("targetuser")

# Check follow status
status = nav.check_follow_status()
print(f"Status: {status}")  # "follow", "following", "requested", "unknown"

# Follow if not already following
if status == "follow":
    success = nav.follow_user()
    print("✅ Followed user" if success else "❌ Failed")
```

### 4.2 Profile Scraping

```python
from src.gramaddict_wrapper import InstagramNavigator, ProfileScraper

nav = InstagramNavigator()
nav.connect()
scraper = ProfileScraper(nav)

# Scrape profile
profile = scraper.scrape_profile("targetuser")
print(f"Username: {profile['username']}")
print(f"Followers: {profile['follower_count']}")
print(f"Following: {profile['following_count']}")
print(f"Bio: {profile['bio']}")
```

### 4.3 Content Analysis with GPT-4 Vision

```python
from src.gramaddict_wrapper import VisionAnalyzer

vision = VisionAnalyzer()

# Analyze profile screenshot
profile_info = vision.analyze_profile_screenshot("profile.png")
print(f"Followers: {profile_info['follower_count']}")

# Check follow status from image
status = vision.check_follow_status("profile.png")
print(f"Follow status: {status}")

# Check content appropriateness
is_safe = vision.check_content_appropriateness("content.png")
print(f"Content is safe: {is_safe}")
```

---

## 5. Development Setup

### 5.1 Manual Setup (Alternative)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# 4. Start PostgreSQL (Docker)
docker run -d \
  --name instagram-postgres \
  -e POSTGRES_PASSWORD=devpassword123 \
  -e POSTGRES_DB=instagram_automation \
  -p 5434:5432 \
  postgres:15-alpine

# 5. Initialize database
python3 scripts/init_db.py
```

### 5.2 Project Structure

```
.
├── src/
│   ├── gramaddict_wrapper/      # Core navigation modules
│   │   ├── navigation.py        # InstagramNavigator
│   │   ├── vision_analyzer.py   # VisionAnalyzer
│   │   ├── profile_scraper.py   # ProfileScraper
│   │   ├── story_restory.py     # StoryRestory
│   │   └── dm_sender.py         # DMSender
│   ├── utils/                   # Utilities
│   │   ├── db_handler.py        # Database operations
│   │   └── logger.py            # Logging setup
│   └── automation/              # Legacy modules
│
├── tests/                       # Phase-based test suite
│   ├── phase1_infrastructure/   # Device & app tests
│   ├── phase2_navigation/       # Navigation tests
│   ├── phase3_vision/           # AI-powered features
│   ├── phase4_integration/      # End-to-end tests
│   └── phase5_advanced/         # Advanced features
│
├── config/                      # Configuration files
├── scripts/                     # Setup and utility scripts
├── docs/                        # Documentation
└── requirements.txt             # Python dependencies
```

### 5.3 Key Dependencies

```txt
# Core automation
uiautomator2>=3.0.0

# AI features
openai>=1.107.1

# Database
psycopg2-binary>=2.9.9

# Utilities
loguru>=0.7.0
pyyaml>=6.0
python-dotenv>=1.0.0
Pillow>=10.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## 6. Testing

### 6.1 Phase-based Test Suite

Run tests sequentially:

```bash
# Phase 1: Infrastructure
python3 tests/phase1_infrastructure/test_device_connection.py
python3 tests/phase1_infrastructure/test_instagram_launch.py

# Phase 2: Navigation
python3 tests/phase2_navigation/test_tab_navigation.py
python3 tests/phase2_navigation/test_search_user.py

# Phase 3: Vision & Actions
python3 tests/phase3_vision/test_follow_user.py
python3 tests/phase3_vision/test_profile_ocr.py
python3 tests/phase3_vision/test_content_filter.py

# Phase 4: Integration
python3 tests/phase4_integration/test_profile_scraping.py

# Phase 5: Advanced (Coming Soon)
python3 tests/phase5_advanced/test_story_restory.py
```

### 6.2 Test Results

All tests passing on Samsung SM-N981N (1080x2400, Android 13):
- ✅ Phase 1: Device connection, Instagram launch
- ✅ Phase 2: Tab navigation, user search
- ✅ Phase 3: Follow with status detection
- 🚧 Phase 4-5: In progress

Screenshots saved in `tests/phase*/screenshots/`

---

## 7. Database Configuration

### 7.1 PostgreSQL Setup (Docker)

```bash
# Start PostgreSQL
docker run -d \
  --name instagram-postgres \
  -e POSTGRES_PASSWORD=devpassword123 \
  -e POSTGRES_DB=instagram_automation \
  -p 5434:5432 \
  postgres:15-alpine

# Stop PostgreSQL
docker stop instagram-postgres

# Remove PostgreSQL
docker rm instagram-postgres
```

### 7.2 Database Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(255),
    account_name VARCHAR(255),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50)
);

-- Actions log table
CREATE TABLE action_logs (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id),
    action_type VARCHAR(100),
    details TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Profiles table
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    follower_count INTEGER,
    following_count INTEGER,
    posts_count INTEGER,
    bio TEXT,
    is_verified BOOLEAN,
    is_private BOOLEAN,
    scraped_at TIMESTAMP
);
```

---

## 8. Safety & Best Practices

### 8.1 Safety Features

1. **Follow Status Detection**: Never unfollow existing follows
2. **Rate Limiting**: Built-in delays between actions
3. **Error Handling**: Comprehensive try-catch blocks
4. **Content Filtering**: AI-powered inappropriate content detection
5. **Session Logging**: All actions logged to database

### 8.2 Best Practices

```python
# ✅ Good: Always check status before action
status = nav.check_follow_status()
if status == "follow":
    nav.follow_user()

# ❌ Bad: Blind action without checking
nav.follow_user()  # Might try to unfollow!

# ✅ Good: Use context manager for cleanup
with InstagramNavigator() as nav:
    nav.connect()
    # Your code here
# Automatic cleanup

# ✅ Good: Add delays for safety
import time
time.sleep(2)  # Human-like behavior
```

### 8.3 Rate Limiting Guidelines

- **Actions per hour**: Max 30
- **Profile views per hour**: Max 50
- **Delay between actions**: 2-5 seconds
- **Delay between sessions**: 30-60 minutes

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Device not found
```bash
# Check ADB connection
adb devices

# If empty, reconnect device and enable USB debugging
# Restart ADB server
adb kill-server
adb start-server
```

#### uiautomator2 not working
```bash
# Reinitialize uiautomator2
python3 -m uiautomator2 init

# Check service status
python3 -c "import uiautomator2 as u2; d = u2.connect(); print(d.info)"
```

#### Instagram not launching
```bash
# Check if Instagram is installed
adb shell pm list packages | grep instagram

# Clear Instagram cache
adb shell pm clear com.instagram.android

# Restart device
adb reboot
```

#### Coordinates not working
```bash
# Check device resolution
adb shell wm size
# Expected: Physical size: 1080x2400

# Lock screen rotation
adb shell settings put system accelerometer_rotation 0
adb shell settings put system user_rotation 0
```

### 9.2 Debug Tips

```python
# Enable debug logging
from loguru import logger
logger.add("debug.log", level="DEBUG")

# Take screenshot for debugging
nav.screenshot("debug_screen.png")

# Check device info
import uiautomator2 as u2
d = u2.connect()
print(d.info)
print(d.window_size())
```

### 9.3 Getting Help

1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for system details
2. Review test files in `tests/` for examples
3. Check logs in `logs/` directory
4. Open issue on GitHub with:
   - Device model and Android version
   - Error message and logs
   - Steps to reproduce

---

## 📚 Additional Resources

- [README.md](README.md) - Project overview and quick start
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system architecture
- [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) - Full documentation index

---

**Last Updated**: 2025-10-14
**Version**: 4.0 (Pure ADB/uiautomator2)
