# 📚 Documentation Index

Complete documentation for Instagram Automation project.

---

## ⭐ Essential Documentation

### 1. [README.md](../README.md) ★★★★★
**8KB | Project Overview**

**Start here first!**

#### Contents:
- ✅ Project overview and key features
- ✅ Pure ADB/uiautomator2 architecture
- ✅ Quick start guide
- ✅ Installation instructions
- ✅ Usage examples
- ✅ Coordinate-based navigation system
- ✅ Safety features

#### For:
- First-time users
- Quick setup and testing
- Understanding project capabilities

---

### 2. [ARCHITECTURE.md](../ARCHITECTURE.md) ★★★★★
**14KB | System Architecture**

**Comprehensive technical documentation**

#### Contents:
- ✅ Architecture diagram and layers
- ✅ Module structure and API reference
- ✅ Pure ADB/uiautomator2 implementation details
- ✅ Multi-layer fallback system
- ✅ Technology stack
- ✅ Coordinate system (1080x2400)
- ✅ Safety features

#### For:
- Developers
- Architects
- Understanding system design
- API reference

---

### 3. [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) ★★★★★
**17KB | Development Guide**

**Complete development workflow**

#### Contents:
- ✅ Project goals and principles
- ✅ 15-minute quick start
- ✅ System architecture overview
- ✅ Core features with code examples
- ✅ Development setup (automated & manual)
- ✅ Phase-based testing guide
- ✅ Database configuration
- ✅ Safety best practices
- ✅ Troubleshooting

#### For:
- New developers
- Setting up development environment
- Learning core features
- Debugging issues

---

## 📖 Key Technologies

### Pure ADB/uiautomator2
- **No GramAddict** - Custom implementation using only ADB and uiautomator2
- **Multi-layer Fallback** - Resource ID → Text → Coordinates
- **Resolution-specific** - Tested on 1080x2400 (Samsung SM-N981N)

### GPT-4 Vision
- Profile OCR and data extraction
- Follow status detection from screenshots
- Content appropriateness checking
- NOT used for navigation (cost-effective design)

---

## 🗃️ Archived Documentation

Located in `docs/archive/` - Historical reference only.

### [개발문서.md](archive/개발문서.md)
**26KB | Original Development Document (Korean)**
- Initial 3-stage development strategy
- Stage-by-stage architecture plans
- Risk analysis

> **Note**: Contains outdated GramAddict references. Use DEVELOPMENT_GUIDE.md instead.

### [AGENTS_USAGE_GUIDE.md](archive/AGENTS_USAGE_GUIDE.md)
**19KB | AI Agents Guide**
- OpenAI Agents SDK usage
- Agent types and APIs
- Real-world examples

### [PROJECT_ARCHITECTURE.md](archive/PROJECT_ARCHITECTURE.md)
**20KB | Detailed Architecture**
- System architecture diagrams
- Feature workflows
- Database ER diagrams
- Implementation plans

> **Note**: Contains outdated GramAddict references. Use ARCHITECTURE.md instead.

### [Local_Development.md](archive/Local_Development.md)
**6.6KB | Local Development Setup**
- Quick start guides
- Makefile usage
- Development scripts

### [PostgreSQL_Setup.md](archive/PostgreSQL_Setup.md)
**7.9KB | Database Setup**
- PostgreSQL installation (macOS, Linux, Windows)
- AlloyDB configuration (Google Cloud)
- Database migration

---

## 🔍 Documentation Selection Guide

### 🚀 First Time Setup
1. **[README.md](../README.md)** - Understand what this project does
2. **[DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - Section 2 (Quick Start)
3. Run tests and verify setup

### 💻 Development Work
1. **[DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - Section 4 (Core Features)
2. **[ARCHITECTURE.md](../ARCHITECTURE.md)** - API reference
3. Check `tests/` for code examples

### 🔧 Troubleshooting
1. **[DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - Section 9 (Troubleshooting)
2. Check logs in `logs/` directory
3. Review test files for working examples

### 🏗️ Architecture Understanding
1. **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Complete system design
2. **[DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - Section 3 (Architecture)

---

## 📊 Documentation Statistics

| Document | Size | Status | Priority | Updated |
|----------|------|--------|----------|---------|
| README.md | 8KB | ✅ Current | ⭐⭐⭐⭐⭐ | 2025-10-14 |
| ARCHITECTURE.md | 14KB | ✅ Current | ⭐⭐⭐⭐⭐ | 2025-10-14 |
| DEVELOPMENT_GUIDE.md | 17KB | ✅ Current | ⭐⭐⭐⭐⭐ | 2025-10-14 |
| archive/개발문서.md | 26KB | 🗃️ Archive | ⭐ | 2025-10-10 |
| archive/AGENTS_USAGE_GUIDE.md | 19KB | 🗃️ Archive | ⭐ | 2025-10-10 |
| archive/PROJECT_ARCHITECTURE.md | 20KB | 🗃️ Archive | ⭐ | 2025-10-10 |
| archive/Local_Development.md | 6.6KB | 🗃️ Archive | ⭐ | 2025-10-10 |
| archive/PostgreSQL_Setup.md | 7.9KB | 🗃️ Archive | ⭐ | 2025-10-10 |

**Total**: 8 documents
**Core**: 3 documents (39KB) - **These are all you need!**
**Archive**: 5 documents (99KB) - Historical reference

---

## 🎯 Recommended Reading Order

### For New Developers (1-2 hours)
1. **README.md** (15 min) - Project overview
2. **DEVELOPMENT_GUIDE.md** (45 min) - Sections 1, 2, 4
3. Run test suite (30 min) - Hands-on practice

### For Experienced Developers (30 min)
1. **README.md** (5 min) - Quick overview
2. **ARCHITECTURE.md** (15 min) - System design
3. **DEVELOPMENT_GUIDE.md** Section 4 (10 min) - Core features

### For Architects/Technical Leads (1 hour)
1. **ARCHITECTURE.md** (30 min) - Complete system design
2. **DEVELOPMENT_GUIDE.md** Sections 3, 8 (20 min) - Architecture & safety
3. Review `src/gramaddict_wrapper/` code (10 min) - Implementation

---

## 🚨 Important Notes

### No GramAddict Dependency
Despite the directory name `src/gramaddict_wrapper/`, this project uses **pure ADB and uiautomator2** with no third-party automation frameworks.

- ✅ Direct ADB commands
- ✅ uiautomator2 for element detection
- ✅ GPT-4 Vision for image analysis only
- ❌ NO GramAddict installation required

### Archived Documents
Documents in `docs/archive/` contain **outdated GramAddict references**. They are kept for historical purposes only. Always refer to the three main documents for current information.

---

## 📝 Quick Reference

### Core Technologies
```
Device Control: ADB + uiautomator2
AI Analysis: OpenAI GPT-4 Vision
Language: Python 3.8+
Database: PostgreSQL/AlloyDB
Testing: pytest
```

### Key Modules
```python
from src.gramaddict_wrapper import (
    InstagramNavigator,    # Navigation and control
    VisionAnalyzer,        # GPT-4 Vision analysis
    ProfileScraper,        # Profile data extraction
    StoryRestory,          # Story automation
    DMSender              # Direct messaging
)
```

### Test Phases
```
Phase 1: Infrastructure (Device, ADB, Instagram)
Phase 2: Navigation (Tabs, Search)
Phase 3: Vision & Actions (Follow, OCR, Filter)
Phase 4: Integration (Profile scraping)
Phase 5: Advanced (Story automation)
```

---

**Last Updated**: 2025-10-14
**Documentation Version**: 4.0 (Pure ADB/uiautomator2)

---

**Need Help?**
1. Start with [README.md](../README.md)
2. Check [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) Section 9 (Troubleshooting)
3. Review test files in `tests/` for examples
4. Check logs in `logs/` directory
