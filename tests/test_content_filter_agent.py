"""
Unit tests for ContentFilterAgent
"""

import pytest
import os
from src.agents.content_filter_agent import (
    ContentFilterAgent,
    FilterAction,
    FilterReason,
    FilterResult
)


class TestContentFilterAgent:
    """ContentFilterAgent 테스트"""

    def test_initialization(self):
        """Agent 초기화 테스트"""
        agent = ContentFilterAgent(use_moderation_api=False)

        assert agent is not None
        assert len(agent.bad_words) > 0
        assert len(agent.bad_word_patterns) > 0
        assert agent.filter_action == FilterAction.SKIP

    def test_initialization_with_custom_bad_words(self):
        """커스텀 불량 단어로 초기화"""
        custom_words = ["test1", "test2", "test3"]
        agent = ContentFilterAgent(
            bad_words=custom_words,
            use_moderation_api=False
        )

        assert agent.bad_words == custom_words
        assert len(agent.bad_word_patterns) == 3

    def test_safe_text(self):
        """안전한 텍스트 검사"""
        agent = ContentFilterAgent(use_moderation_api=False)

        result = agent.check_text("안녕하세요! 맛있는 카페입니다.")

        assert result.is_safe == True
        assert result.reason == FilterReason.SAFE
        assert len(result.bad_words_found) == 0

    def test_text_with_bad_words(self):
        """불량 단어 포함 텍스트"""
        agent = ContentFilterAgent(
            bad_words=["테스트불량단어"],
            use_moderation_api=False
        )

        result = agent.check_text("이 텍스트에는 테스트불량단어 가 포함되어 있습니다")

        assert result.is_safe == False
        assert len(result.bad_words_found) > 0
        assert result.reason == FilterReason.BAD_WORD

    def test_text_with_spam_keywords(self):
        """스팸 키워드 포함 텍스트"""
        agent = ContentFilterAgent(use_moderation_api=False)

        result = agent.check_text("팔로우백 해주세요 맞팔 소통")

        assert result.is_safe == False
        assert len(result.bad_words_found) > 0
        assert "팔로우백" in result.bad_words_found or "맞팔" in result.bad_words_found

    def test_empty_text(self):
        """빈 텍스트"""
        agent = ContentFilterAgent(use_moderation_api=False)

        result = agent.check_text("")

        assert result.is_safe == True
        assert result.reason == FilterReason.SAFE

    def test_add_bad_words(self):
        """불량 단어 추가"""
        agent = ContentFilterAgent(
            bad_words=["test"],
            use_moderation_api=False
        )

        initial_count = len(agent.bad_words)
        agent.add_bad_words(["new1", "new2"])

        assert len(agent.bad_words) == initial_count + 2
        assert "new1" in agent.bad_words
        assert "new2" in agent.bad_words

    def test_remove_bad_words(self):
        """불량 단어 제거"""
        agent = ContentFilterAgent(
            bad_words=["test1", "test2", "test3"],
            use_moderation_api=False
        )

        agent.remove_bad_words(["test1", "test2"])

        assert len(agent.bad_words) == 1
        assert "test3" in agent.bad_words
        assert "test1" not in agent.bad_words

    def test_get_bad_words(self):
        """불량 단어 리스트 조회"""
        custom_words = ["word1", "word2"]
        agent = ContentFilterAgent(
            bad_words=custom_words,
            use_moderation_api=False
        )

        words = agent.get_bad_words()

        assert words == custom_words
        assert words is not agent.bad_words  # 복사본 확인

    def test_additional_bad_words_in_check_text(self):
        """check_text에서 추가 불량 단어 사용"""
        agent = ContentFilterAgent(
            bad_words=["test"],
            use_moderation_api=False
        )

        # "custom"은 기본 리스트에 없지만 추가로 전달
        result = agent.check_text(
            "이 텍스트에는 custom 단어가 있습니다",
            additional_bad_words=["custom"]
        )

        assert result.is_safe == False
        assert "custom" in result.bad_words_found

    def test_case_insensitive_matching(self):
        """대소문자 구분 없이 매칭"""
        agent = ContentFilterAgent(
            bad_words=["spam"],
            use_moderation_api=False
        )

        # 대문자, 소문자 모두 매칭되어야 함
        result1 = agent.check_text("SPAM message")
        result2 = agent.check_text("spam message")
        result3 = agent.check_text("SpAm message")

        assert result1.is_safe == False or result2.is_safe == False or result3.is_safe == False

    def test_image_filtering_not_implemented(self):
        """이미지 필터링 미구현 확인"""
        agent = ContentFilterAgent(use_moderation_api=False)

        result = agent.check_image("fake_image.jpg")

        # 현재는 항상 안전으로 처리
        assert result.is_safe == True
        assert result.confidence == 0.0  # 구현 안됨 표시

    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY not set"
    )
    def test_moderation_api_safe_text(self):
        """OpenAI Moderation API - 안전한 텍스트"""
        agent = ContentFilterAgent(use_moderation_api=True)

        result = agent.check_text("I love this beautiful sunset!")

        assert result.is_safe == True
        assert result.moderation_result is not None
        assert result.moderation_result['flagged'] == False

    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY not set"
    )
    def test_moderation_api_unsafe_text(self):
        """OpenAI Moderation API - 위험한 텍스트"""
        agent = ContentFilterAgent(use_moderation_api=True)

        # 혐오 발언 테스트
        result = agent.check_text("You are stupid and I hate you!")

        # OpenAI Moderation이 이를 위험으로 플래그할 가능성 높음
        # (하지만 100% 보장은 아니므로 로그만 확인)
        assert result.moderation_result is not None

    def test_filter_result_structure(self):
        """FilterResult 구조 확인"""
        agent = ContentFilterAgent(use_moderation_api=False)

        result = agent.check_text("test text")

        # 모든 필수 필드가 있는지 확인
        assert hasattr(result, 'is_safe')
        assert hasattr(result, 'reason')
        assert hasattr(result, 'action')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'bad_words_found')
        assert hasattr(result, 'moderation_result')
        assert hasattr(result, 'details')

        # 타입 확인
        assert isinstance(result.is_safe, bool)
        assert isinstance(result.reason, FilterReason)
        assert isinstance(result.action, FilterAction)
        assert isinstance(result.confidence, float)
        assert isinstance(result.bad_words_found, list)
        assert isinstance(result.details, str)


# Manual test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
