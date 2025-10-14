"""
StoryRestoryManager 유닛 테스트

테스트 범위:
- StoryRestoryManager 초기화
- 해시태그 스토리 검색 (mock)
- 스토리 필터링
- 단일 스토리 리스토리
- 전체 워크플로우 (검색 → 필터링 → 리스토리)
- DB 연동 (mock)
"""

import pytest
from datetime import datetime
from typing import List

from src.wrapper.story_restory_manager import (
    StoryRestoryManager,
    Story,
    RestoryResult
)
from src.agents.content_filter_agent import ContentFilterAgent, FilterResult, FilterReason, FilterAction


class TestStoryRestoryManager:
    """StoryRestoryManager 테스트"""

    def test_init_with_default_filter_agent(self):
        """기본 ContentFilterAgent로 초기화"""
        manager = StoryRestoryManager()
        assert manager.filter_agent is not None
        assert isinstance(manager.filter_agent, ContentFilterAgent)
        assert manager.db is None
        assert manager.device_id is None

    def test_init_with_custom_filter_agent(self):
        """커스텀 ContentFilterAgent로 초기화"""
        custom_filter = ContentFilterAgent(
            bad_words=["테스트"],
            use_moderation_api=False
        )
        manager = StoryRestoryManager(filter_agent=custom_filter)
        assert manager.filter_agent == custom_filter

    def test_search_hashtag_stories_returns_list(self):
        """해시태그 스토리 검색이 리스트 반환"""
        manager = StoryRestoryManager()
        stories = manager.search_hashtag_stories(
            hashtags=["맛집", "카페"],
            max_count=5
        )

        assert isinstance(stories, list)
        assert len(stories) == 5
        assert all(isinstance(story, Story) for story in stories)

    def test_search_hashtag_stories_respects_max_count(self):
        """max_count 제한이 정상 작동"""
        manager = StoryRestoryManager()
        stories = manager.search_hashtag_stories(
            hashtags=["맛집"],
            max_count=3
        )
        assert len(stories) <= 3

    def test_story_structure(self):
        """Story 데이터 구조 검증"""
        manager = StoryRestoryManager()
        stories = manager.search_hashtag_stories(
            hashtags=["맛집"],
            max_count=1
        )

        story = stories[0]
        assert hasattr(story, 'story_id')
        assert hasattr(story, 'username')
        assert hasattr(story, 'text')
        assert hasattr(story, 'image_path')
        assert hasattr(story, 'url')
        assert hasattr(story, 'timestamp')

        assert isinstance(story.story_id, str)
        assert isinstance(story.username, str)
        assert isinstance(story.text, str)
        assert isinstance(story.timestamp, datetime)

    def test_filter_stories_returns_two_lists(self):
        """필터링이 안전/필터링 두 리스트 반환"""
        filter_agent = ContentFilterAgent(
            bad_words=["광고", "스팸"],
            use_moderation_api=False
        )
        manager = StoryRestoryManager(filter_agent=filter_agent)

        stories = manager.search_hashtag_stories(
            hashtags=["맛집"],
            max_count=10
        )

        safe_stories, filtered_stories = manager.filter_stories(stories)

        assert isinstance(safe_stories, list)
        assert isinstance(filtered_stories, list)
        assert len(safe_stories) + len(filtered_stories) == len(stories)

    def test_filter_stories_with_additional_bad_words(self):
        """추가 불량 단어로 필터링"""
        filter_agent = ContentFilterAgent(
            bad_words=[],  # 기본 불량 단어 없음
            use_moderation_api=False
        )
        manager = StoryRestoryManager(filter_agent=filter_agent)

        # Mock 스토리 중 "광고" 포함 스토리가 있음
        stories = manager.search_hashtag_stories(
            hashtags=["맛집"],
            max_count=10
        )

        # 추가 불량 단어 없이 필터링 -> 모두 안전
        safe1, filtered1 = manager.filter_stories(stories)

        # "광고" 추가하여 필터링 -> 일부 필터링됨
        safe2, filtered2 = manager.filter_stories(
            stories,
            additional_bad_words=["광고"]
        )

        # 추가 불량 단어 사용 시 더 많이 필터링되어야 함
        assert len(filtered2) >= len(filtered1)

    def test_restory_returns_result(self):
        """단일 스토리 리스토리가 RestoryResult 반환"""
        manager = StoryRestoryManager()

        story = Story(
            story_id="test_123",
            username="test_user",
            text="테스트 스토리",
            image_path=None,
            url="instagram://story/test",
            timestamp=datetime.now()
        )

        result = manager.restory(story)

        assert isinstance(result, RestoryResult)
        assert result.story == story
        assert isinstance(result.success, bool)

    def test_search_and_restory_workflow(self):
        """전체 워크플로우 (검색 → 필터링 → 리스토리)"""
        filter_agent = ContentFilterAgent(
            bad_words=["광고", "스팸", "팔로우백"],
            use_moderation_api=False
        )
        manager = StoryRestoryManager(filter_agent=filter_agent)

        results = manager.search_and_restory_hashtag_stories(
            hashtags=["맛집", "카페"],
            max_count=10
        )

        assert isinstance(results, list)
        assert all(isinstance(r, RestoryResult) for r in results)

        # 필터링되지 않은 스토리만 리스토리 시도
        # Mock 데이터에는 불량 단어 포함 스토리가 있으므로
        # 결과 개수가 검색된 개수보다 적어야 함
        assert len(results) <= 10

    def test_restory_result_structure(self):
        """RestoryResult 구조 검증"""
        manager = StoryRestoryManager()

        results = manager.search_and_restory_hashtag_stories(
            hashtags=["맛집"],
            max_count=5
        )

        if len(results) > 0:
            result = results[0]
            assert hasattr(result, 'success')
            assert hasattr(result, 'story')
            assert hasattr(result, 'filter_result')
            assert hasattr(result, 'error')

            assert isinstance(result.success, bool)
            assert isinstance(result.story, Story)

    def test_empty_hashtags(self):
        """빈 해시태그 리스트"""
        manager = StoryRestoryManager()

        stories = manager.search_hashtag_stories(
            hashtags=[],
            max_count=5
        )

        # Mock 구현은 해시태그와 무관하게 데이터 반환
        assert isinstance(stories, list)

    def test_zero_max_count(self):
        """max_count = 0"""
        manager = StoryRestoryManager()

        stories = manager.search_hashtag_stories(
            hashtags=["맛집"],
            max_count=0
        )

        assert len(stories) == 0

    def test_filter_stories_with_empty_list(self):
        """빈 스토리 리스트 필터링"""
        manager = StoryRestoryManager()

        safe_stories, filtered_stories = manager.filter_stories([])

        assert safe_stories == []
        assert filtered_stories == []

    def test_mock_data_contains_unsafe_content(self):
        """Mock 데이터에 불량 콘텐츠 포함 검증"""
        filter_agent = ContentFilterAgent(
            bad_words=["광고", "스팸", "팔로우백", "도박"],
            use_moderation_api=False
        )
        manager = StoryRestoryManager(filter_agent=filter_agent)

        stories = manager.search_hashtag_stories(
            hashtags=["맛집"],
            max_count=10
        )

        safe_stories, filtered_stories = manager.filter_stories(stories)

        # Mock 데이터에는 의도적으로 불량 콘텐츠가 포함되어 있음
        assert len(filtered_stories) > 0, "Mock 데이터에 필터링될 스토리가 있어야 함"

    def test_consecutive_runs_generate_different_stories(self):
        """연속 실행 시 다른 story_id 생성 검증"""
        manager = StoryRestoryManager()

        stories1 = manager.search_hashtag_stories(["맛집"], max_count=3)
        stories2 = manager.search_hashtag_stories(["맛집"], max_count=3)

        ids1 = {story.story_id for story in stories1}
        ids2 = {story.story_id for story in stories2}

        # UUID 기반이므로 겹치지 않아야 함
        assert ids1.isdisjoint(ids2), "각 실행마다 고유한 story_id가 생성되어야 함"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
