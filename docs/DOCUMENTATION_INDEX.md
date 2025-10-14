# 📚 문서 인덱스

프로젝트의 모든 문서를 한 눈에 파악할 수 있습니다.

---

## ⭐ 필수 문서

### 1. [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) ★★★★★
**28KB | 완전 통합 개발 가이드**

**이 문서 하나로 모든 것을 파악하세요!**

#### 포함 내용:
- ✅ 프로젝트 개요 (목표, 기술 스택)
- ✅ 빠른 시작 (15분 설정)
- ✅ 시스템 아키텍처
- ✅ 핵심 기능 구현 (스토리 리스토리, 프로필 수집 + DM)
- ✅ 개발 환경 설정
- ✅ AI Agents 사용법
- ✅ 데이터베이스 설정
- ✅ 안전성 및 리스크 관리
- ✅ 구현 로드맵 (Phase 1-4)
- ✅ 문제 해결

#### 대상:
- 신규 개발자
- 기능 구현 담당자
- 전체 시스템 이해 필요한 모든 사람

---

### 2. [README.md](../README.md) ★★★★
**13KB | 프로젝트 개요**

#### 포함 내용:
- 프로젝트 소개
- 주요 기능
- 빠른 시작
- 설치 방법
- 안전 사용 가이드

#### 대상:
- 처음 프로젝트를 접하는 사람
- 빠른 시작이 필요한 사람

---

## 📖 핵심 문서

### 3. [IMPROVEMENTS.md](../IMPROVEMENTS.md) ★★★
**6.8KB | 개선 사항 로그**

#### 포함 내용:
- DB 재연결 로직
- 세션 동시성 제어
- 로그 파싱 패턴 개선
- 타입 힌팅
- 유닛 테스트

#### 대상:
- 기여자
- 코드 리뷰어

---

### 4. [OPENAI_AGENTS_INTEGRATION.md](../OPENAI_AGENTS_INTEGRATION.md) ★★★★
**14KB | AI 통합 계획**

#### 포함 내용:
- 통합 가능성 분석 (95%)
- 5가지 통합 영역
- 아키텍처 설계
- 5단계 구현 계획
- ROI 분석

#### 대상:
- AI 기능 구현 담당자
- 아키텍처 설계자

---

### 5. [OPENAI_AGENTS_IMPLEMENTATION_COMPLETE.md](../OPENAI_AGENTS_IMPLEMENTATION_COMPLETE.md) ★★★
**14KB | AI 통합 완료 보고서**

#### 포함 내용:
- 구현된 Agent (ConfigGenerator, Planning)
- 사용 예제
- 테스트 방법
- 성과 지표

#### 대상:
- AI Agent 사용자
- QA 담당자

---

## 🗃️ 아카이브 문서 (참고용)

아래 문서들은 **DEVELOPMENT_GUIDE.md**에 통합되었습니다.
상세 정보가 필요할 때만 참고하세요.

### [개발문서.md](archive/개발문서.md)
**26KB | 초기 개발 문서**
- 3단계 개발 전략 (GramAddict → 네이티브 → Appium)
- Stage별 아키텍처
- 리스크 분석

### [AGENTS_USAGE_GUIDE.md](archive/AGENTS_USAGE_GUIDE.md)
**19KB | Agents 상세 가이드**
- 프로젝트 목표별 사용법
- Agent 종류 및 API
- 실전 예제 코드

### [PROJECT_ARCHITECTURE.md](archive/PROJECT_ARCHITECTURE.md)
**20KB | 아키텍처 상세**
- 시스템 아키텍처 다이어그램
- 기능별 워크플로우
- DB 스키마 (ER Diagram)
- 구현 계획

### [Local_Development.md](archive/Local_Development.md)
**6.6KB | 로컬 개발 환경**
- 빠른 시작 (자동/수동)
- Makefile 사용법
- 개발 스크립트

### [PostgreSQL_Setup.md](archive/PostgreSQL_Setup.md)
**7.9KB | DB 설정 상세**
- PostgreSQL 설치 (macOS, Linux, Windows)
- AlloyDB 설정 (Google Cloud)
- 마이그레이션

---

## 🔍 문서 선택 가이드

### 처음 시작하는 경우
1. [README.md](../README.md) - 프로젝트 이해
2. **[DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - 전체 파악 ⭐

### 기능 구현하는 경우
1. **[DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - Section 4 (핵심 기능 구현)
2. [OPENAI_AGENTS_INTEGRATION.md](../OPENAI_AGENTS_INTEGRATION.md) - AI 기능 필요시

### 문제 해결하는 경우
1. **[DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - Section 10 (문제 해결)
2. [archive/Local_Development.md](archive/Local_Development.md) - 환경 설정 이슈

### 기여하는 경우
1. [IMPROVEMENTS.md](../IMPROVEMENTS.md) - 최근 개선 사항
2. **[DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)** - Section 9 (로드맵)

---

## 📊 문서 통계

| 문서 | 크기 | 상태 | 우선순위 |
|------|------|------|----------|
| DEVELOPMENT_GUIDE.md | 28KB | ✅ 최신 | ⭐⭐⭐⭐⭐ |
| README.md | 13KB | ✅ 최신 | ⭐⭐⭐⭐ |
| OPENAI_AGENTS_INTEGRATION.md | 14KB | ✅ 최신 | ⭐⭐⭐⭐ |
| OPENAI_AGENTS_IMPLEMENTATION_COMPLETE.md | 14KB | ✅ 최신 | ⭐⭐⭐ |
| IMPROVEMENTS.md | 6.8KB | ✅ 최신 | ⭐⭐⭐ |
| archive/개발문서.md | 26KB | 🗃️ 아카이브 | ⭐⭐ |
| archive/AGENTS_USAGE_GUIDE.md | 19KB | 🗃️ 아카이브 | ⭐⭐ |
| archive/PROJECT_ARCHITECTURE.md | 20KB | 🗃️ 아카이브 | ⭐⭐ |
| archive/Local_Development.md | 6.6KB | 🗃️ 아카이브 | ⭐ |
| archive/PostgreSQL_Setup.md | 7.9KB | 🗃️ 아카이브 | ⭐ |

**총 문서**: 10개 (메인 5개 + 아카이브 5개)
**총 크기**: ~135KB

---

## 🎯 추천 읽기 순서

### 신규 개발자
1. README.md (10분)
2. **DEVELOPMENT_GUIDE.md - Section 1, 2** (30분)
3. **DEVELOPMENT_GUIDE.md - Section 5** (환경 설정, 20분)
4. **DEVELOPMENT_GUIDE.md - 전체** (2시간)

### 기존 개발자
1. **DEVELOPMENT_GUIDE.md - Section 4** (기능 구현)
2. **DEVELOPMENT_GUIDE.md - Section 9** (로드맵 확인)
3. IMPROVEMENTS.md (최근 변경 사항)

### 아키텍트
1. **DEVELOPMENT_GUIDE.md - Section 3** (시스템 아키텍처)
2. OPENAI_AGENTS_INTEGRATION.md (AI 통합 계획)
3. archive/PROJECT_ARCHITECTURE.md (상세 설계)

---

**최종 업데이트**: 2025-10-10
**문서 버전**: 3.0 (통합 완료)
