"""
StoryRestoryManager - 해시태그 스토리 검색 및 리스토리 관리

기능:
- 해시태그 기반 스토리 검색
- 스토리 내용 수집 (텍스트, 이미지)
- ContentFilterAgent와 통합하여 필터링
- 안전한 스토리만 자동 리스토리
- DB에 세션 기록
"""

from __future__ import annotations

import uuid
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.db_handler import DatabaseHandler
from src.agents.content_filter_agent import ContentFilterAgent, FilterResult


@dataclass
class Story:
    """스토리 데이터"""
    story_id: str  # 스토리 고유 ID
    username: str  # 작성자 username
    text: str  # 스토리 텍스트 내용
    image_path: Optional[str]  # 이미지 경로 (스크린샷)
    url: str  # 스토리 URL (딥링크)
    timestamp: datetime  # 수집 시간


@dataclass
class RestoryResult:
    """리스토리 결과"""
    success: bool  # 성공 여부
    story: Story  # 대상 스토리
    filter_result: Optional[FilterResult]  # 필터링 결과
    error: Optional[str]  # 에러 메시지


class StoryRestoryManager:
    """
    스토리 리스토리 관리자

    해시태그 기반으로 스토리를 검색하고, ContentFilterAgent로 필터링한 후
    안전한 스토리만 리스토리합니다.

    Example:
        >>> from src.agents.content_filter_agent import ContentFilterAgent
        >>> from src.wrapper.story_restory_manager import StoryRestoryManager
        >>>
        >>> filter_agent = ContentFilterAgent(bad_words=["광고", "스팸"])
        >>> manager = StoryRestoryManager(filter_agent=filter_agent)
        >>>
        >>> # 해시태그 스토리 검색 및 리스토리
        >>> results = manager.search_and_restory_hashtag_stories(
        ...     hashtags=["맛집", "카페"],
        ...     max_count=20
        ... )
        >>>
        >>> print(f"총 리스토리: {len([r for r in results if r.success])}")
    """

    def __init__(
        self,
        filter_agent: Optional[ContentFilterAgent] = None,
        db_handler: Optional[DatabaseHandler] = None,
        device_id: Optional[str] = None
    ):
        """
        StoryRestoryManager 초기화

        Args:
            filter_agent: ContentFilterAgent 인스턴스
            db_handler: DatabaseHandler 인스턴스
            device_id: Android 디바이스 ID
        """
        self.logger = get_logger()
        self.filter_agent = filter_agent or ContentFilterAgent(use_moderation_api=False)
        self.db = db_handler
        self.device_id = device_id

        self.logger.info("StoryRestoryManager 초기화 완료")

    def search_hashtag_stories(
        self,
        hashtags: List[str],
        max_count: int = 20
    ) -> List[Story]:
        """
        해시태그 기반 스토리 검색

        Args:
            hashtags: 검색할 해시태그 리스트
            max_count: 최대 수집 개수

        Returns:
            List[Story]: 검색된 스토리 리스트

        Note:
            현재는 Mock 데이터 반환. 실제 구현은 GramAddict 연동 필요.
        """
        self.logger.info(f"해시태그 스토리 검색: {hashtags}, 최대 {max_count}개")

        # TODO: GramAddict를 사용한 실제 스토리 검색 구현
        # 1. GramAddict로 Instagram 앱 실행
        # 2. 해시태그 검색
        # 3. 스토리 탭 이동
        # 4. 스토리 목록 수집
        # 5. 각 스토리의 텍스트 및 이미지 추출

        # 임시 Mock 데이터
        mock_stories = self._generate_mock_stories(hashtags, max_count)

        self.logger.info(f"총 {len(mock_stories)}개 스토리 검색 완료")
        return mock_stories

    def _generate_mock_stories(self, hashtags: List[str], count: int) -> List[Story]:
        """Mock 스토리 데이터 생성 (테스트용)"""
        stories = []

        mock_texts = [
            "맛있는 카페를 소개합니다! #맛집 #카페",
            "광고입니다! 지금 구매하세요! #광고",
            "팔로우백 해주세요 맞팔 소통 #소통",
            "오늘의 일상 #daily #life",
            "서울 카페 추천 #서울카페",
            "이것은 스팸 메시지입니다",
            "아름다운 풍경 #여행 #travel",
            "도박 사이트 홍보",
            "좋은 아침입니다! #goodmorning",
            "불법 판매 #불법"
        ]

        for i in range(min(count, len(mock_texts))):
            story = Story(
                story_id=f"story_{uuid.uuid4().hex[:8]}",
                username=f"user_{i}",
                text=mock_texts[i],
                image_path=None,  # 실제 구현 시 스크린샷 경로
                url=f"instagram://story/{uuid.uuid4().hex}",
                timestamp=datetime.now()
            )
            stories.append(story)

        return stories

    def filter_stories(
        self,
        stories: List[Story],
        additional_bad_words: Optional[List[str]] = None,
        check_images: bool = False
    ) -> tuple[List[Story], List[Story]]:
        """
        스토리 필터링

        Args:
            stories: 필터링할 스토리 리스트
            additional_bad_words: 추가 불량 단어
            check_images: 이미지 필터링 활성화 여부 (GPT-4 Vision)

        Returns:
            tuple: (안전한 스토리, 필터링된 스토리)
        """
        safe_stories = []
        filtered_stories = []

        for story in stories:
            is_safe = True
            filter_result = None

            # 1단계: 텍스트 필터링
            text_filter_result = self.filter_agent.check_text(
                story.text,
                additional_bad_words=additional_bad_words
            )

            if not text_filter_result.is_safe:
                is_safe = False
                filter_result = text_filter_result
                self.logger.debug(
                    f"❌ 텍스트 필터링: {story.username} - {text_filter_result.details}"
                )

            # 2단계: 이미지 필터링 (옵션)
            if is_safe and check_images and story.image_path:
                image_filter_result = self.filter_agent.check_image(story.image_path)

                if not image_filter_result.is_safe:
                    is_safe = False
                    filter_result = image_filter_result
                    self.logger.debug(
                        f"❌ 이미지 필터링: {story.username} - {image_filter_result.details}"
                    )

            # 결과 분류
            if is_safe:
                safe_stories.append(story)
                self.logger.debug(f"✅ 안전: {story.username} - {story.text[:30]}")
            else:
                filtered_stories.append(story)

                # DB에 필터링 기록 저장
                if self.db and filter_result:
                    self._log_filtered_story(story, filter_result)

        self.logger.info(
            f"필터링 완료: 안전 {len(safe_stories)}개, 필터링 {len(filtered_stories)}개"
        )

        return safe_stories, filtered_stories

    def restory(self, story: Story) -> RestoryResult:
        """
        단일 스토리 리스토리

        Args:
            story: 리스토리할 스토리

        Returns:
            RestoryResult: 리스토리 결과

        Note:
            현재는 Mock 구현. 실제 GramAddict 연동 필요.
        """
        self.logger.info(f"리스토리 실행: {story.username} - {story.text[:30]}")

        # TODO: GramAddict를 사용한 실제 리스토리 구현
        # 1. 스토리 열기 (URL 또는 UI 탐색)
        # 2. 공유 버튼 클릭
        # 3. "스토리에 추가" 선택
        # 4. 확인

        # 임시 Mock 결과
        import random
        success = random.choice([True, True, True, False])  # 75% 성공률

        result = RestoryResult(
            success=success,
            story=story,
            filter_result=None,
            error=None if success else "Mock error: 리스토리 실패"
        )

        if success:
            self.logger.info(f"✅ 리스토리 성공: {story.story_id}")
        else:
            self.logger.warning(f"❌ 리스토리 실패: {story.story_id}")

        return result

    def search_and_restory_hashtag_stories(
        self,
        hashtags: List[str],
        max_count: int = 20,
        additional_bad_words: Optional[List[str]] = None,
        check_images: bool = False
    ) -> List[RestoryResult]:
        """
        해시태그 스토리 검색 → 필터링 → 리스토리 (전체 워크플로우)

        Args:
            hashtags: 검색할 해시태그
            max_count: 최대 리스토리 개수
            additional_bad_words: 추가 불량 단어
            check_images: 이미지 필터링 활성화 여부 (GPT-4 Vision)

        Returns:
            List[RestoryResult]: 리스토리 결과 리스트
        """
        session_id = str(uuid.uuid4())
        self.logger.info("=" * 60)
        self.logger.info(f"스토리 리스토리 세션 시작: {session_id}")
        self.logger.info(f"해시태그: {hashtags}, 최대 {max_count}개")
        self.logger.info("=" * 60)

        # DB 세션 생성
        if self.db:
            self._create_restory_session(session_id, hashtags, max_count)

        # 1단계: 스토리 검색
        stories = self.search_hashtag_stories(hashtags, max_count)

        # 2단계: 필터링
        safe_stories, filtered_stories = self.filter_stories(
            stories,
            additional_bad_words=additional_bad_words,
            check_images=check_images
        )

        # 3단계: 리스토리
        results = []
        for story in safe_stories:
            result = self.restory(story)
            results.append(result)

            # DB에 결과 기록
            if self.db:
                self._log_restory_result(session_id, result)

        # DB 세션 업데이트
        if self.db:
            self._update_restory_session(
                session_id,
                total_viewed=len(stories),
                total_restoried=len([r for r in results if r.success]),
                total_filtered=len(filtered_stories)
            )

        # 결과 요약
        success_count = len([r for r in results if r.success])
        self.logger.info("=" * 60)
        self.logger.info("스토리 리스토리 세션 완료")
        self.logger.info("=" * 60)
        self.logger.info(f"총 조회: {len(stories)}개")
        self.logger.info(f"필터링: {len(filtered_stories)}개")
        self.logger.info(f"리스토리 시도: {len(safe_stories)}개")
        self.logger.info(f"리스토리 성공: {success_count}개")

        return results

    def _create_restory_session(
        self,
        session_id: str,
        hashtags: List[str],
        max_count: int
    ):
        """DB에 리스토리 세션 생성"""
        if not self.db:
            return

        try:
            # filter_agent의 설정을 JSONB로 저장
            filter_settings = {
                "bad_words": self.filter_agent.bad_words,
                "use_moderation_api": self.filter_agent.use_moderation_api,
                "filter_action": self.filter_agent.filter_action.value
            }

            query = """
                INSERT INTO restory_sessions (
                    session_id, username, device_id, target_hashtags, max_count,
                    filter_settings, start_time, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            params = (
                session_id,
                "unknown",  # TODO: 실제 username 전달
                self.device_id,
                hashtags,
                max_count,
                json.dumps(filter_settings),  # JSON 문자열로 변환
                datetime.now(),
                "running"
            )

            self.db.execute_query(query, params)
            self.logger.debug(f"DB 세션 생성 완료: {session_id}")

        except Exception as e:
            self.logger.error(f"DB 세션 생성 실패: {e}")

    def _update_restory_session(
        self,
        session_id: str,
        total_viewed: int,
        total_restoried: int,
        total_filtered: int
    ):
        """DB 세션 업데이트"""
        if not self.db:
            return

        try:
            query = """
                UPDATE restory_sessions
                SET total_viewed = %s,
                    total_restoried = %s,
                    total_filtered = %s,
                    end_time = %s,
                    status = %s
                WHERE session_id = %s
            """
            params = (
                total_viewed,
                total_restoried,
                total_filtered,
                datetime.now(),
                "completed",
                session_id
            )

            self.db.execute_query(query, params)
            self.logger.debug(
                f"DB 세션 업데이트 완료: {session_id} - "
                f"조회 {total_viewed}, 리스토리 {total_restoried}, 필터링 {total_filtered}"
            )

        except Exception as e:
            self.logger.error(f"DB 세션 업데이트 실패: {e}")

    def _log_filtered_story(self, story: Story, filter_result: FilterResult):
        """필터링된 스토리 DB 기록"""
        if not self.db:
            return

        try:
            # session_id를 어디선가 가져와야 함 - 현재는 filter_stories에서 호출되므로 추적 불가
            # 대신 최신 세션을 찾아서 연결
            session_query = """
                SELECT session_id FROM restory_sessions
                WHERE status = 'running'
                ORDER BY start_time DESC
                LIMIT 1
            """
            session_result = self.db.fetch_query(session_query)

            if not session_result:
                self.logger.warning("실행 중인 세션이 없어 필터링 기록 불가")
                return

            session_id = session_result[0]['session_id']

            query = """
                INSERT INTO filtered_stories (
                    session_id, story_id, username, text, image_path, url,
                    filter_reason, filter_action, bad_words_found, confidence,
                    moderation_result, filter_details, timestamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            params = (
                session_id,
                story.story_id,
                story.username,
                story.text,
                story.image_path,
                story.url,
                filter_result.reason.value,
                filter_result.action.value,
                filter_result.bad_words_found,
                filter_result.confidence,
                json.dumps(filter_result.moderation_result) if filter_result.moderation_result else None,
                filter_result.details,
                story.timestamp
            )

            self.db.execute_query(query, params)
            self.logger.debug(f"필터링 기록 완료: {story.story_id} - {filter_result.reason.value}")

        except Exception as e:
            self.logger.error(f"필터링 기록 실패: {e}")

    def _log_restory_result(self, session_id: str, result: RestoryResult):
        """리스토리 결과 DB 기록"""
        if not self.db:
            return

        try:
            query = """
                INSERT INTO restory_results (
                    session_id, story_id, username, text, image_path, url,
                    success, error_message, timestamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            params = (
                session_id,
                result.story.story_id,
                result.story.username,
                result.story.text,
                result.story.image_path,
                result.story.url,
                result.success,
                result.error,
                result.story.timestamp
            )

            self.db.execute_query(query, params)

            status = "성공" if result.success else "실패"
            self.logger.debug(f"리스토리 기록 완료: {result.story.story_id} - {status}")

        except Exception as e:
            self.logger.error(f"리스토리 기록 실패: {e}")


# CLI 테스트
if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("StoryRestoryManager 테스트")
    print("=" * 60)

    # ContentFilterAgent 초기화
    filter_agent = ContentFilterAgent(
        bad_words=["광고", "스팸", "팔로우백", "맞팔", "소통", "도박", "불법"],
        use_moderation_api=False
    )

    # StoryRestoryManager 초기화
    manager = StoryRestoryManager(filter_agent=filter_agent)

    # 해시태그 스토리 검색 및 리스토리
    print("\n[Test] 해시태그 스토리 리스토리")
    results = manager.search_and_restory_hashtag_stories(
        hashtags=["맛집", "카페", "여행"],
        max_count=10,
        additional_bad_words=["도박"]
    )

    # 결과 출력
    print("\n" + "=" * 60)
    print("리스토리 결과 상세")
    print("=" * 60)

    for i, result in enumerate(results, 1):
        status = "✅ 성공" if result.success else "❌ 실패"
        print(f"{i}. {status} | {result.story.username} | {result.story.text[:40]}")
        if result.error:
            print(f"   에러: {result.error}")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
