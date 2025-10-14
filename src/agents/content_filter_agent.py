"""
ContentFilterAgent - 스토리 및 포스트 내용 필터링

기능:
- 텍스트 필터링 (정규식 + 불량 단어 검사)
- OpenAI Moderation API를 통한 콘텐츠 검사
- GPT-4 Vision을 통한 이미지 분석 (future)
- 필터링 정책 적용 및 로그 기록
"""

from __future__ import annotations

import re
import os
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

try:
    import openai
    from openai import OpenAI
except ImportError:
    OpenAI = None

from src.utils.logger import get_logger


class FilterAction(Enum):
    """필터링 액션"""
    SKIP = "skip"  # 건너뛰기
    REPORT = "report"  # 신고
    BLOCK = "block"  # 차단


class FilterReason(Enum):
    """필터링 사유"""
    BAD_WORD = "bad_word"  # 불량 단어 포함
    SPAM = "spam"  # 스팸성 내용
    ADULT_CONTENT = "adult_content"  # 성인 콘텐츠
    VIOLENCE = "violence"  # 폭력적 내용
    HATE_SPEECH = "hate_speech"  # 혐오 발언
    HARASSMENT = "harassment"  # 괴롭힘
    SAFE = "safe"  # 안전함


@dataclass
class FilterResult:
    """필터링 결과"""
    is_safe: bool  # 안전 여부
    reason: FilterReason  # 필터링 사유
    action: FilterAction  # 권장 액션
    confidence: float  # 신뢰도 (0.0 - 1.0)
    bad_words_found: List[str]  # 발견된 불량 단어
    moderation_result: Optional[Dict]  # OpenAI Moderation 결과
    details: str  # 상세 설명


class ContentFilterAgent:
    """
    콘텐츠 필터링 Agent

    텍스트와 이미지를 분석하여 부적절한 내용을 필터링합니다.

    Example:
        >>> filter_agent = ContentFilterAgent(
        ...     bad_words=["욕설", "광고", "스팸"],
        ...     use_moderation_api=True
        ... )
        >>>
        >>> # 텍스트 필터링
        >>> result = filter_agent.check_text("이것은 안전한 내용입니다")
        >>> if result.is_safe:
        ...     print("안전한 콘텐츠")
        >>>
        >>> # 이미지 필터링 (future)
        >>> result = filter_agent.check_image("image.jpg")
    """

    def __init__(
        self,
        bad_words: Optional[List[str]] = None,
        use_moderation_api: bool = True,
        api_key: Optional[str] = None,
        filter_action: FilterAction = FilterAction.SKIP
    ):
        """
        ContentFilterAgent 초기화

        Args:
            bad_words: 필터링할 불량 단어 리스트
            use_moderation_api: OpenAI Moderation API 사용 여부
            api_key: OpenAI API Key (None이면 환경변수 사용)
            filter_action: 기본 필터링 액션
        """
        self.logger = get_logger()
        self.bad_words = bad_words or self._get_default_bad_words()
        self.use_moderation_api = use_moderation_api
        self.filter_action = filter_action

        # OpenAI Client 초기화
        self.client = None
        if use_moderation_api:
            if OpenAI is None:
                self.logger.warning("OpenAI 패키지가 설치되지 않았습니다. Moderation API 비활성화")
                self.use_moderation_api = False
            else:
                api_key = api_key or os.getenv('OPENAI_API_KEY')
                if not api_key:
                    self.logger.warning("OPENAI_API_KEY가 설정되지 않았습니다. Moderation API 비활성화")
                    self.use_moderation_api = False
                else:
                    self.client = OpenAI(api_key=api_key)
                    self.logger.info("OpenAI Moderation API 활성화")

        # 정규식 패턴 컴파일
        self.bad_word_patterns = self._compile_bad_word_patterns()

        self.logger.info(f"ContentFilterAgent 초기화 완료 (불량 단어: {len(self.bad_words)}개)")

    def _get_default_bad_words(self) -> List[str]:
        """기본 불량 단어 리스트"""
        return [
            # 욕설
            "욕설", "비속어",

            # 광고/스팸
            "광고", "스팸", "홍보", "판매", "구매",
            "팔로우백", "맞팔", "소통", "선팔",

            # 도박
            "도박", "베팅", "카지노", "슬롯",

            # 성인 콘텐츠
            "성인", "19금", "음란", "야동",

            # 기타
            "사기", "피싱", "해킹", "불법"
        ]

    def _compile_bad_word_patterns(self) -> List[re.Pattern]:
        """불량 단어를 정규식 패턴으로 컴파일"""
        patterns = []
        for word in self.bad_words:
            # 단어 경계를 고려한 패턴
            # 예: "광고" → r'\b광고\b' (공백이나 구두점으로 둘러싸인 경우만 매칭)
            pattern = re.compile(
                rf'\b{re.escape(word)}\b',
                re.IGNORECASE
            )
            patterns.append(pattern)
        return patterns

    def check_text(
        self,
        text: str,
        additional_bad_words: Optional[List[str]] = None
    ) -> FilterResult:
        """
        텍스트 필터링

        Args:
            text: 검사할 텍스트
            additional_bad_words: 추가 불량 단어

        Returns:
            FilterResult: 필터링 결과
        """
        if not text or not text.strip():
            return FilterResult(
                is_safe=True,
                reason=FilterReason.SAFE,
                action=self.filter_action,
                confidence=1.0,
                bad_words_found=[],
                moderation_result=None,
                details="빈 텍스트 (안전)"
            )

        # 1단계: 정규식 기반 불량 단어 검사
        bad_words_found = self._find_bad_words(text, additional_bad_words)

        if bad_words_found:
            return FilterResult(
                is_safe=False,
                reason=FilterReason.BAD_WORD,
                action=self.filter_action,
                confidence=1.0,  # 정규식 매칭은 확실함
                bad_words_found=bad_words_found,
                moderation_result=None,
                details=f"불량 단어 발견: {', '.join(bad_words_found)}"
            )

        # 2단계: OpenAI Moderation API 검사
        if self.use_moderation_api:
            moderation_result = self._check_with_moderation_api(text)

            if moderation_result:
                is_flagged = moderation_result.get('flagged', False)

                if is_flagged:
                    # 위반 카테고리 추출
                    categories = moderation_result.get('categories', {})
                    flagged_categories = [k for k, v in categories.items() if v]

                    # 카테고리를 FilterReason으로 매핑
                    reason = self._map_moderation_category(flagged_categories)

                    # 카테고리별 점수
                    category_scores = moderation_result.get('category_scores', {})
                    max_score = max(category_scores.values()) if category_scores else 0.5

                    return FilterResult(
                        is_safe=False,
                        reason=reason,
                        action=self.filter_action,
                        confidence=max_score,
                        bad_words_found=[],
                        moderation_result=moderation_result,
                        details=f"OpenAI Moderation 위반: {', '.join(flagged_categories)}"
                    )

        # 모든 검사 통과 - 안전
        return FilterResult(
            is_safe=True,
            reason=FilterReason.SAFE,
            action=self.filter_action,
            confidence=0.95,  # 완벽한 확신은 아님
            bad_words_found=[],
            moderation_result=moderation_result if self.use_moderation_api else None,
            details="모든 필터링 검사 통과"
        )

    def _find_bad_words(
        self,
        text: str,
        additional_bad_words: Optional[List[str]] = None
    ) -> List[str]:
        """텍스트에서 불량 단어 찾기"""
        found = []

        # 기본 불량 단어 검사
        for pattern in self.bad_word_patterns:
            if pattern.search(text):
                # 패턴에서 원본 단어 추출
                word = pattern.pattern.replace(r'\b', '').replace('\\', '')
                found.append(word)

        # 추가 불량 단어 검사
        if additional_bad_words:
            for word in additional_bad_words:
                pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
                if pattern.search(text):
                    found.append(word)

        return list(set(found))  # 중복 제거

    def _check_with_moderation_api(self, text: str) -> Optional[Dict]:
        """OpenAI Moderation API로 검사"""
        if not self.client:
            return None

        try:
            response = self.client.moderations.create(input=text)

            # 결과 변환
            result = response.results[0]
            return {
                'flagged': result.flagged,
                'categories': result.categories.model_dump(),
                'category_scores': result.category_scores.model_dump()
            }

        except Exception as e:
            self.logger.error(f"OpenAI Moderation API 호출 실패: {e}")
            return None

    def _map_moderation_category(self, categories: List[str]) -> FilterReason:
        """OpenAI Moderation 카테고리를 FilterReason으로 매핑"""
        # OpenAI Moderation 카테고리:
        # - sexual, hate, harassment, self-harm,
        #   sexual/minors, hate/threatening, violence/graphic, self-harm/intent,
        #   self-harm/instructions, harassment/threatening, violence

        category_mapping = {
            'sexual': FilterReason.ADULT_CONTENT,
            'sexual/minors': FilterReason.ADULT_CONTENT,
            'hate': FilterReason.HATE_SPEECH,
            'hate/threatening': FilterReason.HATE_SPEECH,
            'harassment': FilterReason.HARASSMENT,
            'harassment/threatening': FilterReason.HARASSMENT,
            'violence': FilterReason.VIOLENCE,
            'violence/graphic': FilterReason.VIOLENCE,
        }

        for category in categories:
            if category in category_mapping:
                return category_mapping[category]

        return FilterReason.SPAM  # 기본값

    def check_image(self, image_path: str) -> FilterResult:
        """
        이미지 필터링 (GPT-4 Vision)

        Args:
            image_path: 이미지 파일 경로

        Returns:
            FilterResult: 필터링 결과
        """
        import base64
        from pathlib import Path

        # 이미지 파일 존재 확인
        if not Path(image_path).exists():
            self.logger.error(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            return FilterResult(
                is_safe=False,
                reason=FilterReason.SAFE,
                action=FilterAction.SKIP,
                confidence=0.0,
                bad_words_found=[],
                moderation_result=None,
                details=f"이미지 파일 없음: {image_path}"
            )

        # OpenAI 클라이언트 확인
        if not self.client:
            self.logger.warning("OpenAI 클라이언트가 초기화되지 않아 이미지 필터링 불가")
            return FilterResult(
                is_safe=True,
                reason=FilterReason.SAFE,
                action=self.filter_action,
                confidence=0.5,
                bad_words_found=[],
                moderation_result=None,
                details="OpenAI API 키 없음 - 이미지 필터링 건너뜀"
            )

        try:
            # 이미지를 base64로 인코딩
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # GPT-4 Vision API 호출
            response = self.client.chat.completions.create(
                model="gpt-4o",  # gpt-4-vision-preview 대신 최신 gpt-4o 사용
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """이 이미지를 분석하여 다음 중 하나에 해당하는지 판단해주세요:

1. **성인/음란 콘텐츠**: 노출, 성적 콘텐츠, 19금
2. **폭력**: 피, 무기, 폭력적 장면
3. **혐오/차별**: 인종차별, 혐오 표현
4. **스팸/광고**: 명백한 상업적 광고
5. **안전**: 위 항목에 해당하지 않음

응답 형식 (JSON):
{
  "is_safe": true/false,
  "reason": "adult_content" | "violence" | "hate_speech" | "spam" | "safe",
  "confidence": 0.0-1.0,
  "details": "간단한 설명"
}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "low"  # 비용 절감을 위해 low 사용
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.1  # 일관성 있는 결과를 위해 낮은 temperature
            )

            # 응답 파싱
            import json
            try:
                result_text = response.choices[0].message.content.strip()

                # JSON 블록 추출 (```json ... ``` 형태일 수 있음)
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                vision_result = json.loads(result_text)

                is_safe = vision_result.get("is_safe", True)
                reason_str = vision_result.get("reason", "safe")
                confidence = float(vision_result.get("confidence", 0.8))
                details = vision_result.get("details", "GPT-4 Vision 분석 결과")

                # reason 문자열을 FilterReason으로 변환
                reason_mapping = {
                    "adult_content": FilterReason.ADULT_CONTENT,
                    "violence": FilterReason.VIOLENCE,
                    "hate_speech": FilterReason.HATE_SPEECH,
                    "spam": FilterReason.SPAM,
                    "safe": FilterReason.SAFE
                }
                reason = reason_mapping.get(reason_str, FilterReason.SAFE)

                self.logger.debug(
                    f"GPT-4 Vision 이미지 분석: {image_path} - "
                    f"안전={is_safe}, 이유={reason.value}, 신뢰도={confidence:.2f}"
                )

                return FilterResult(
                    is_safe=is_safe,
                    reason=reason,
                    action=self.filter_action if not is_safe else FilterAction.SKIP,
                    confidence=confidence,
                    bad_words_found=[],
                    moderation_result=vision_result,
                    details=details
                )

            except json.JSONDecodeError as e:
                self.logger.error(f"GPT-4 Vision 응답 파싱 실패: {e}")
                self.logger.debug(f"원본 응답: {response.choices[0].message.content}")

                # 파싱 실패 시 안전한 것으로 간주
                return FilterResult(
                    is_safe=True,
                    reason=FilterReason.SAFE,
                    action=FilterAction.SKIP,
                    confidence=0.5,
                    bad_words_found=[],
                    moderation_result=None,
                    details=f"응답 파싱 실패 (안전으로 간주)"
                )

        except Exception as e:
            self.logger.error(f"GPT-4 Vision API 호출 실패: {e}")

            # 에러 발생 시 안전한 것으로 간주 (false positive보다 false negative 선호)
            return FilterResult(
                is_safe=True,
                reason=FilterReason.SAFE,
                action=FilterAction.SKIP,
                confidence=0.0,
                bad_words_found=[],
                moderation_result=None,
                details=f"API 호출 실패: {str(e)}"
            )

    def add_bad_words(self, words: List[str]):
        """불량 단어 추가"""
        self.bad_words.extend(words)
        self.bad_word_patterns.extend(self._compile_bad_word_patterns())
        self.logger.info(f"불량 단어 {len(words)}개 추가됨 (총: {len(self.bad_words)}개)")

    def remove_bad_words(self, words: List[str]):
        """불량 단어 제거"""
        for word in words:
            if word in self.bad_words:
                self.bad_words.remove(word)

        # 패턴 재컴파일
        self.bad_word_patterns = self._compile_bad_word_patterns()
        self.logger.info(f"불량 단어 {len(words)}개 제거됨 (총: {len(self.bad_words)}개)")

    def get_bad_words(self) -> List[str]:
        """현재 불량 단어 리스트 반환"""
        return self.bad_words.copy()


# CLI 테스트
if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("ContentFilterAgent 테스트")
    print("=" * 60)

    # 1. 기본 테스트
    print("\n[Test 1] 기본 필터링 (정규식)")
    filter_agent = ContentFilterAgent(use_moderation_api=False)

    test_texts = [
        "안녕하세요! 맛있는 카페를 소개합니다.",  # 안전
        "광고입니다! 지금 구매하세요!",  # 불량 단어
        "팔로우백 해주세요 맞팔 소통",  # 불량 단어
        "이것은 깨끗한 내용입니다.",  # 안전
    ]

    for text in test_texts:
        result = filter_agent.check_text(text)
        status = "✅ 안전" if result.is_safe else "❌ 위험"
        print(f"{status} | {text[:30]}... | {result.details}")

    # 2. OpenAI Moderation API 테스트
    if os.getenv('OPENAI_API_KEY'):
        print("\n[Test 2] OpenAI Moderation API")
        filter_agent_with_api = ContentFilterAgent(use_moderation_api=True)

        api_test_texts = [
            "I love this beautiful sunset!",  # 안전
            "You are stupid and I hate you!",  # 혐오 발언
        ]

        for text in api_test_texts:
            result = filter_agent_with_api.check_text(text)
            status = "✅ 안전" if result.is_safe else "❌ 위험"
            print(f"{status} | {text[:30]}... | Confidence: {result.confidence:.2f}")
    else:
        print("\n[Test 2] OPENAI_API_KEY가 설정되지 않아 Moderation API 테스트 생략")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
