"""
StoryRestoryManager DB 연동 테스트

실제 DatabaseHandler와 함께 StoryRestoryManager를 실행하여
DB에 데이터가 제대로 저장되는지 확인합니다.
"""

import os
from dotenv import load_dotenv

from src.utils.db_handler import DatabaseHandler
from src.agents.content_filter_agent import ContentFilterAgent
from src.wrapper.story_restory_manager import StoryRestoryManager

# 환경변수 로드
load_dotenv()

print("=" * 60)
print("StoryRestoryManager DB 연동 테스트")
print("=" * 60)

# DatabaseHandler 초기화 (__init__ 시 자동 연결)
print("\n[1] DatabaseHandler 초기화...")
db = DatabaseHandler()
print("✅ DB 연결 성공")

# ContentFilterAgent 초기화
print("\n[2] ContentFilterAgent 초기화...")
filter_agent = ContentFilterAgent(
    bad_words=["광고", "스팸", "팔로우백", "맞팔", "소통", "도박", "불법"],
    use_moderation_api=False
)
print("✅ ContentFilterAgent 초기화 완료")

# StoryRestoryManager 초기화 (DB 연동)
print("\n[3] StoryRestoryManager 초기화 (DB 연동)...")
manager = StoryRestoryManager(
    filter_agent=filter_agent,
    db_handler=db,
    device_id="test_device_001"
)
print("✅ StoryRestoryManager 초기화 완료")

# 해시태그 스토리 검색 및 리스토리 (DB 기록 포함)
print("\n[4] 해시태그 스토리 리스토리 실행...")
print("    - DB에 세션, 필터링, 리스토리 결과 기록됨")
results = manager.search_and_restory_hashtag_stories(
    hashtags=["맛집", "카페", "여행"],
    max_count=10,
    additional_bad_words=["도박"]
)
print(f"✅ 리스토리 완료: {len(results)}개")

# DB 데이터 확인
print("\n[5] DB 데이터 확인...")

# restory_sessions 확인
session_query = """
    SELECT session_id, username, target_hashtags, total_viewed,
           total_restoried, total_filtered, status
    FROM restory_sessions
    ORDER BY start_time DESC
    LIMIT 1
"""
session_data = db.fetch_query(session_query)
if session_data:
    print("\n✅ restory_sessions 테이블:")
    s = session_data[0]
    print(f"   - session_id: {s['session_id']}")
    print(f"   - username: {s['username']}")
    print(f"   - target_hashtags: {s['target_hashtags']}")
    print(f"   - total_viewed: {s['total_viewed']}")
    print(f"   - total_restoried: {s['total_restoried']}")
    print(f"   - total_filtered: {s['total_filtered']}")
    print(f"   - status: {s['status']}")

# filtered_stories 확인
filtered_query = """
    SELECT COUNT(*) as count
    FROM filtered_stories
    WHERE session_id = (
        SELECT session_id FROM restory_sessions
        ORDER BY start_time DESC LIMIT 1
    )
"""
filtered_count = db.fetch_query(filtered_query)
if filtered_count:
    print(f"\n✅ filtered_stories: {filtered_count[0]['count']}개 기록")

# restory_results 확인
results_query = """
    SELECT COUNT(*) as total,
           SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as success_count
    FROM restory_results
    WHERE session_id = (
        SELECT session_id FROM restory_sessions
        ORDER BY start_time DESC LIMIT 1
    )
"""
results_count = db.fetch_query(results_query)
if results_count:
    r = results_count[0]
    print(f"\n✅ restory_results: 총 {r['total']}개 (성공 {r['success_count']}개)")

# DB 연결 종료
print("\n[6] DB 연결 종료...")
db.close()
print("✅ DB 연결 종료 완료")

print("\n" + "=" * 60)
print("테스트 완료!")
print("=" * 60)
print("\n💡 Tip: pgAdmin (http://localhost:5050)에서 데이터를 확인할 수 있습니다.")
print("   Email: admin@localhost.com")
print("   Password: admin123")
