# Instagram Automation Architecture (GramAddict-based)

## 🎯 Overview

This project provides advanced Instagram automation by combining:
- **GramAddict** for reliable UI navigation
- **GPT-4 Vision** for image analysis (OCR, content understanding)
- **GPT-4o** for personalized text generation

## 📐 Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          examples/test_new_architecture.py               │ │
│  │          - Profile Scraping Test                          │ │
│  │          - Story Restory Test                             │ │
│  │          - DM Sending Test                                │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                   GramAddict Wrapper Layer                      │
│                    (src/gramaddict_wrapper/)                    │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │  navigation.py   │  │ vision_analyzer  │                   │
│  │  ──────────────  │  │  ──────────────  │                   │
│  │  · goto_home()   │  │  · analyze_      │                   │
│  │  · goto_search() │  │    profile_      │                   │
│  │  · search_       │  │    screenshot()  │                   │
│  │    username()    │  │  · analyze_      │                   │
│  └──────────────────┘  │    story_        │                   │
│                         │    content()     │                   │
│  ┌──────────────────┐  └──────────────────┘                   │
│  │ profile_scraper  │                                           │
│  │  ──────────────  │  ┌──────────────────┐                   │
│  │  · scrape_       │  │  story_restory   │                   │
│  │    profile()     │  │  ──────────────  │                   │
│  │  · get_follower_ │  │  · restory_from_ │                   │
│  │    count()       │  │    user()        │                   │
│  │  · is_verified() │  │  · filter_       │                   │
│  └──────────────────┘  │    inappropriate │                   │
│                         │    _content()    │                   │
│  ┌──────────────────┐  └──────────────────┘                   │
│  │   dm_sender.py   │                                           │
│  │  ──────────────  │                                           │
│  │  · send_         │                                           │
│  │    personalized_ │                                           │
│  │    dm()          │                                           │
│  └──────────────────┘                                           │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                      Core Libraries                             │
│                                                                  │
│  ┌─────────────────────┐         ┌─────────────────────┐       │
│  │    GramAddict        │         │    OpenAI APIs      │       │
│  │  ─────────────────   │         │  ─────────────────  │       │
│  │  · TabBarView        │         │  · GPT-4 Vision     │       │
│  │    - navigateToHome  │         │    (gpt-4o)         │       │
│  │    - navigateToSearch│         │  · GPT-4o           │       │
│  │  · SearchView        │         │  · Moderation API   │       │
│  │    - navigate_to_    │         │                     │       │
│  │      target()        │         │                     │       │
│  │  · ProfileView       │         │                     │       │
│  │  · DeviceFacade      │         │                     │       │
│  │    - find()          │         │                     │       │
│  │    - screenshot()    │         │                     │       │
│  └─────────────────────┘         └─────────────────────┘       │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│                        Device Layer                             │
│                 UIAutomator2 + ADB + Instagram                  │
└────────────────────────────────────────────────────────────────┘
```

## 🗂️ Module Structure

### src/gramaddict_wrapper/

#### 1. **navigation.py** - Instagram Navigation
- **Purpose**: High-level navigation wrapper for GramAddict
- **Key Methods**:
  - `connect()`: Connect to Android device
  - `goto_home()`, `goto_search()`, `goto_profile()`: Tab navigation
  - `search_username(username)`: Search and navigate to user profile
  - `go_back()`: Navigate back
  - `screenshot(path)`: Capture screenshot

**Usage Example**:
```python
from src.gramaddict_wrapper import InstagramNavigator

nav = InstagramNavigator(device_id="R3CN70D9ZBY")
nav.connect()
nav.search_username("liowish")  # Navigate to @liowish profile
```

---

#### 2. **vision_analyzer.py** - GPT-4 Vision Image Analysis
- **Purpose**: Image analysis using GPT-4 Vision (NOT for navigation)
- **Key Methods**:
  - `analyze_profile_screenshot(image_path)`: Extract profile info via OCR
  - `analyze_story_content(image_path)`: Analyze story content
  - `check_content_appropriateness(image_path)`: Content safety check

**Usage Example**:
```python
from src.gramaddict_wrapper import VisionAnalyzer

vision = VisionAnalyzer()
profile_info = vision.analyze_profile_screenshot("profile.png")
print(profile_info['follower_count'])  # "1.2K"
```

---

#### 3. **profile_scraper.py** - Profile Information Scraper
- **Purpose**: Combine GramAddict navigation + GPT Vision OCR
- **Key Methods**:
  - `scrape_profile(username)`: Full profile scraping
  - `get_follower_count(username)`: Quick follower count
  - `is_verified(username)`: Check verification
  - `is_private(username)`: Check privacy status

**Usage Example**:
```python
from src.gramaddict_wrapper import InstagramNavigator, ProfileScraper

nav = InstagramNavigator()
nav.connect()
scraper = ProfileScraper(nav)

profile = scraper.scrape_profile("liowish")
print(f"Followers: {profile['follower_count']}")
```

---

#### 4. **story_restory.py** - Story Reposting
- **Purpose**: Automated story reposting with content filtering
- **Key Methods**:
  - `restory_from_user(username, filter_inappropriate, max_stories)`: Repost stories

**Usage Example**:
```python
from src.gramaddict_wrapper import InstagramNavigator, StoryRestory

nav = InstagramNavigator()
nav.connect()
restory = StoryRestory(nav)

result = restory.restory_from_user(
    username="liowish",
    filter_inappropriate=True,
    max_stories=5
)
print(f"Reposted: {result['stories_reposted']}")
```

---

#### 5. **dm_sender.py** - Personalized DM Automation
- **Purpose**: Send personalized DMs using GPT-4o
- **Key Methods**:
  - `send_personalized_dm(username, campaign_context, use_profile_info)`: Send DM

**Usage Example**:
```python
from src.gramaddict_wrapper import InstagramNavigator, DMSender

nav = InstagramNavigator()
nav.connect()
dm_sender = DMSender(nav)

result = dm_sender.send_personalized_dm(
    username="liowish",
    campaign_context="Collaboration opportunity...",
    use_profile_info=True
)
```

---

## 🔑 Key Design Principles

### 1. **Separation of Concerns**
- ✅ **GramAddict**: UI navigation, element finding, interactions
- ✅ **GPT-4 Vision**: Image analysis ONLY (profiles, stories, content)
- ✅ **GPT-4o**: Text generation (personalized DMs)

### 2. **No More Coordinate-based Navigation**
- ❌ **Before**: `device.tap(0.3, 0.97)` → unreliable, resolution-dependent
- ✅ **After**: `search_view.navigate_to_target("liowish", "blogger")` → selector-based, robust

### 3. **GPT Vision for Image Understanding Only**
- ❌ **Before**: GPT Vision for finding coordinates → expensive, slow, inaccurate
- ✅ **After**: GPT Vision for OCR and content analysis → appropriate use case

### 4. **Cost Efficiency**
- **Before**: GPT Vision API call for every navigation action
- **After**: GPT Vision API call only for actual image analysis
- **Estimated Cost Reduction**: 70-80%

---

## 📊 Comparison: Old vs New Architecture

| Aspect | Old (instagram_core) | New (gramaddict_wrapper) |
|--------|----------------------|--------------------------|
| **Navigation** | Coordinate-based (`tap(x, y)`) | Selector-based (`find(resourceId=...)`) |
| **Reliability** | Low (coordinates change) | High (selectors stable) |
| **Resolution Independence** | ❌ No | ✅ Yes |
| **GPT Vision Usage** | Navigation + Analysis | Analysis only |
| **API Costs** | High | Low (70% reduction) |
| **Code Complexity** | High (manual coordinate debugging) | Low (GramAddict handles it) |
| **Maintainability** | Low | High |
| **Instagram Updates** | Breaks often | Resilient |

---

## 🧪 Testing

### Run Tests
```bash
cd "/Users/kyounghogwack/MOAcnc/Dev/PantaRheiX/AI SNS flow"
source gramaddict-env/bin/activate
python3 examples/test_new_architecture.py
```

### Test Coverage
1. ✅ Profile Scraping (@liowish)
2. ✅ Story Restory (with content filtering)
3. ✅ Personalized DM Sending

---

## 🚀 Quick Start

```python
from src.gramaddict_wrapper import (
    InstagramNavigator,
    VisionAnalyzer,
    ProfileScraper,
    StoryRestory,
    DMSender
)

# Initialize
navigator = InstagramNavigator(device_id="R3CN70D9ZBY")
navigator.connect()

# Example 1: Scrape Profile
scraper = ProfileScraper(navigator)
profile = scraper.scrape_profile("liowish")
print(f"Followers: {profile['follower_count']}")

# Example 2: Restory Stories
restory = StoryRestory(navigator)
result = restory.restory_from_user("liowish", max_stories=3)

# Example 3: Send Personalized DM
dm_sender = DMSender(navigator, scraper)
dm_sender.send_personalized_dm(
    username="liowish",
    campaign_context="Partnership opportunity..."
)
```

---

## 📝 Dependencies

- **GramAddict** 3.2.12 (Instagram automation)
- **UIAutomator2** (Android device control)
- **OpenAI Python SDK** (GPT-4 Vision, GPT-4o)
- **Loguru** (Logging)
- **Python 3.9+**

---

## 🔐 Environment Variables

Create `.env` file:
```
OPENAI_API_KEY=sk-...
```

---

## 📌 Notes

- Device must be connected via ADB
- Instagram app must be installed
- UIAutomator2 service must be running on device
- GPT-4 Vision is used ONLY for image analysis, not navigation
- All navigation uses GramAddict's robust UI selectors

---

## 🎉 Benefits of New Architecture

1. ✅ **Stable**: Uses GramAddict's battle-tested selectors
2. ✅ **Cost-effective**: 70% reduction in GPT API calls
3. ✅ **Fast**: No waiting for GPT Vision on every navigation
4. ✅ **Maintainable**: Clean separation of concerns
5. ✅ **Scalable**: Easy to add new features
6. ✅ **Resolution-independent**: Works on any screen size

---

*Last updated: 2025-10-10*
