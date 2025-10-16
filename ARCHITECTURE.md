# Instagram Automation Architecture

## 🎯 Overview

This project provides advanced Instagram automation using:
- **Pure ADB/uiautomator2** for reliable device control
- **GPT-4 Vision** for intelligent image analysis and OCR
- **Coordinate-based navigation** with multi-layer fallback system

## 📐 Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          Test Suite (tests/)                             │ │
│  │          - Phase 1: Infrastructure                        │ │
│  │          - Phase 2: Navigation                            │ │
│  │          - Phase 3: Vision & Actions                      │ │
│  │          - Phase 4: Integration                           │ │
│  │          - Phase 5: Advanced Features                     │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                   Navigation Wrapper Layer                      │
│                    (src/gramaddict_wrapper/)                    │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  navigation.py   │  │ vision_analyzer  │                   │
│  │  ──────────────  │  │  ──────────────  │                   │
│  │  · connect()     │  │  · analyze_      │                   │
│  │  · launch_       │  │    profile_      │                   │
│  │    instagram()   │  │    screenshot()  │                   │
│  │  · goto_home()   │  │  · check_        │                   │
│  │  · goto_search() │  │    follow_       │                   │
│  │  · search_       │  │    status()      │                   │
│  │    username()    │  │  · analyze_      │                   │
│  │  · follow_user() │  │    content()     │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ profile_scraper  │  │  story_restory   │                   │
│  │  ──────────────  │  │  ──────────────  │                   │
│  │  · scrape_       │  │  · view_story()  │                   │
│  │    profile()     │  │  · restory()     │                   │
│  │  · extract_      │  │  · filter_       │                   │
│  │    info()        │  │    content()     │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │   dm_sender.py   │                                           │
│  │  ──────────────  │                                           │
│  │  · send_dm()     │                                           │
│  │  · personalize() │                                           │
│  └──────────────────┘                                           │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                      Core Technologies                          │
│                                                                  │
│  ┌─────────────────────┐         ┌─────────────────────┐       │
│  │   ADB + uiautomator2 │         │    OpenAI APIs      │       │
│  │  ─────────────────   │         │  ─────────────────  │       │
│  │  · Device control    │         │  · GPT-4 Vision     │       │
│  │  · Screen capture    │         │    (gpt-4o)         │       │
│  │  · Input simulation  │         │  · Image analysis   │       │
│  │  · Element finding   │         │  · OCR              │       │
│  │  · Coordinate tap    │         │  · Content filter   │       │
│  └─────────────────────┘         └─────────────────────┘       │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                        Device Layer                             │
│                 Android Device + Instagram App                  │
└────────────────────────────────────────────────────────────────┘
```

## 🗂️ Module Structure

### src/gramaddict_wrapper/

> **Note**: Despite the directory name "gramaddict_wrapper", this module uses **pure ADB and uiautomator2** with no GramAddict dependency.

#### 1. **navigation.py** - Instagram Navigation

**Purpose**: Direct device control using ADB commands and uiautomator2

**Key Methods**:
- `connect()`: Connect to Android device via uiautomator2
- `launch_instagram()`: Launch Instagram app
- `goto_home()`, `goto_search()`, `goto_profile()`: Tab navigation using coordinates
- `search_username(username)`: Search user with multi-layer fallback
- `check_follow_status()`: Detect current follow state (follow/following/requested)
- `follow_user()`: Smart follow (skips if already following)
- `screenshot(path)`: Capture screen

**Navigation Strategy**:
1. **Resource ID matching** (primary)
2. **Text matching** (fallback)
3. **Coordinate-based tapping** (final fallback)

**Usage Example**:
```python
from src.gramaddict_wrapper import InstagramNavigator

nav = InstagramNavigator()
nav.connect()
nav.launch_instagram()
nav.search_username("targetuser")
nav.follow_user()
```

---

#### 2. **vision_analyzer.py** - GPT-4 Vision Image Analysis

**Purpose**: Intelligent image analysis using GPT-4 Vision

**Key Methods**:
- `analyze_profile_screenshot(image_path)`: Extract profile info via OCR
- `check_follow_status(image_path)`: Detect follow button state
- `analyze_story_content(image_path)`: Analyze story content
- `check_content_appropriateness(image_path)`: Content safety check

**Usage Example**:
```python
from src.gramaddict_wrapper import VisionAnalyzer

vision = VisionAnalyzer()
profile_info = vision.analyze_profile_screenshot("profile.png")
print(f"Followers: {profile_info['follower_count']}")
```

---

#### 3. **profile_scraper.py** - Profile Information Scraper

**Purpose**: Combine navigation + GPT Vision for profile data extraction

**Key Methods**:
- `scrape_profile(username)`: Full profile scraping
- `get_follower_count(username)`: Quick follower count
- `is_verified(username)`: Check verification status
- `is_private(username)`: Check privacy status

**Usage Example**:
```python
from src.gramaddict_wrapper import InstagramNavigator, ProfileScraper

nav = InstagramNavigator()
nav.connect()
scraper = ProfileScraper(nav)

profile = scraper.scrape_profile("username")
print(f"Username: {profile['username']}")
print(f"Followers: {profile['follower_count']}")
print(f"Bio: {profile['bio']}")
```

---

#### 4. **story_restory.py** - Story Automation

**Purpose**: Automated story viewing and reposting with content filtering

**Key Methods**:
- `view_story(username)`: View user's story
- `restory_from_user(username, max_stories)`: Repost stories
- `filter_inappropriate_content(image_path)`: AI content filtering

**Usage Example**:
```python
from src.gramaddict_wrapper import InstagramNavigator, StoryRestory

nav = InstagramNavigator()
nav.connect()
restory = StoryRestory(nav)

result = restory.restory_from_user(
    username="targetuser",
    max_stories=5
)
print(f"Reposted: {result['stories_reposted']}")
```

---

#### 5. **dm_sender.py** - Direct Message Automation

**Purpose**: Send personalized DMs using GPT-4

**Key Methods**:
- `send_personalized_dm(username, context)`: Send DM with AI-generated content

**Usage Example**:
```python
from src.gramaddict_wrapper import InstagramNavigator, DMSender

nav = InstagramNavigator()
nav.connect()
dm_sender = DMSender(nav)

result = dm_sender.send_personalized_dm(
    username="targetuser",
    campaign_context="Collaboration opportunity..."
)
```

---

## 🔑 Key Design Principles

### 1. **Pure ADB/uiautomator2 Implementation**
- ✅ **Direct device control**: No third-party automation frameworks
- ✅ **Fast and reliable**: Minimal overhead
- ✅ **Simple dependencies**: Only ADB and uiautomator2

### 2. **Multi-layer Fallback System**
1. **Resource ID** → `d(resourceId="com.instagram.android:id/search_edit_text")`
2. **Text matching** → `d(text="Search")`
3. **Coordinates** → `d.click(540, 168)`

### 3. **GPT Vision for Intelligence, Not Navigation**
- ❌ **NOT used for**: Finding buttons, navigation
- ✅ **Used for**: OCR, content analysis, follow status detection

### 4. **Screen Rotation Lock**
- Always lock to portrait mode for consistent coordinates
- Resolution-specific coordinates (1080x2400)

---

## 📊 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Device Control** | ADB | Android Debug Bridge |
| **UI Automation** | uiautomator2 | Element detection and interaction |
| **AI Analysis** | GPT-4 Vision | Image analysis and OCR |
| **Language** | Python 3.8+ | Core implementation |
| **Logging** | loguru | Structured logging |
| **Testing** | pytest | Test framework |

---

## 🧪 Test Architecture

### Phase-based Testing

```
tests/
├── phase1_infrastructure/    # Device & app verification
│   ├── test_device_connection.py
│   └── test_instagram_launch.py
├── phase2_navigation/         # Tab navigation & search
│   ├── test_tab_navigation.py
│   └── test_search_user.py
├── phase3_vision/             # AI-powered features
│   ├── test_follow_user.py
│   ├── test_profile_ocr.py
│   └── test_content_filter.py
├── phase4_integration/        # End-to-end workflows
│   └── test_profile_scraping.py
└── phase5_advanced/           # Advanced features
    └── test_story_restory.py
```

### Test Results
All tests passing on Samsung SM-N981N (1080x2400, Android 13):
- ✅ Phase 1: Infrastructure (ADB, uiautomator2, Instagram launch)
- ✅ Phase 2: Navigation (Tabs, user search)
- ✅ Phase 3: Follow with status detection
- 🚧 Phase 4-5: In progress

---

## 🎯 Coordinate System

### Screen Resolution: 1080x2400 (portrait locked)

| Element | Coordinates (x, y) | Method |
|---------|-------------------|--------|
| Home Tab | (108, 2165) | Bottom navigation bar |
| Search Tab | (324, 2165) | Bottom navigation bar |
| Profile Tab | (972, 2165) | Bottom navigation bar |
| Search Input | (530, 168) | Top search bar |
| First Result | (540, 522) | First search result |
| Follow Button | (168, 397) | Profile screen button |

> **Important**: Coordinates are resolution-specific. For different resolutions, coordinates must be recalibrated.

---

## 🔐 Safety Features

1. **Follow Status Detection**: Never unfollow existing follows
2. **Rate Limiting**: Built-in delays between actions
3. **Error Handling**: Comprehensive try-catch blocks
4. **Content Filtering**: AI-powered inappropriate content detection
5. **Session Logging**: All actions logged to database

---

## 🚀 Quick Start

```python
from src.gramaddict_wrapper import InstagramNavigator

# Initialize
navigator = InstagramNavigator()
navigator.connect()
navigator.launch_instagram()

# Navigate and search
navigator.goto_search()
navigator.search_username("targetuser")

# Check and follow
status = navigator.check_follow_status()
if status == "follow":
    navigator.follow_user()
    print("✅ Followed user")
else:
    print(f"ℹ️ Status: {status}")
```

---

## 📝 Dependencies

Core dependencies (from requirements.txt):
```
uiautomator2>=3.0.0
openai>=1.107.1
loguru>=0.7.0
Pillow>=10.0.0
pytest>=7.4.0
```

No GramAddict or other automation frameworks required.

---

## 🔧 Future Enhancements

- [ ] Multi-resolution coordinate adaptation
- [ ] Enhanced OCR accuracy
- [ ] Story automation with AI filtering
- [ ] Bulk DM campaigns
- [ ] Analytics dashboard

---

**Last Updated**: 2025-10-14
**Architecture Version**: 2.0 (Pure ADB/uiautomator2)
