"""
GPT-4 Vision 이미지 필터링 테스트

테스트용 이미지를 생성하고 ContentFilterAgent.check_image()를 테스트합니다.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

from src.agents.content_filter_agent import ContentFilterAgent

# 환경변수 로드
load_dotenv()

# 테스트 이미지 디렉토리
TEST_IMAGES_DIR = "test_images"
os.makedirs(TEST_IMAGES_DIR, exist_ok=True)


def create_test_image(text: str, filename: str, color: str = "white", bg_color: str = "black"):
    """
    텍스트가 포함된 테스트 이미지 생성

    Args:
        text: 이미지에 표시할 텍스트
        filename: 저장할 파일명
        color: 텍스트 색상
        bg_color: 배경 색상
    """
    # 이미지 생성 (Instagram 스토리 비율: 1080x1920)
    img = Image.new('RGB', (540, 960), color=bg_color)
    draw = ImageDraw.Draw(img)

    # 폰트 설정 (시스템 기본 폰트 사용)
    try:
        # macOS 기본 폰트
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        # 폴백: PIL 기본 폰트
        font = ImageFont.load_default()

    # 텍스트를 이미지 중앙에 배치
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((540 - text_width) / 2, (960 - text_height) / 2)
    draw.text(position, text, fill=color, font=font)

    # 이미지 저장
    filepath = os.path.join(TEST_IMAGES_DIR, filename)
    img.save(filepath)
    print(f"✅ 테스트 이미지 생성: {filepath}")

    return filepath


def main():
    print("=" * 60)
    print("GPT-4 Vision 이미지 필터링 테스트")
    print("=" * 60)

    # ContentFilterAgent 초기화 (OpenAI API 사용)
    print("\n[1] ContentFilterAgent 초기화...")
    agent = ContentFilterAgent(use_moderation_api=True)
    print("✅ 초기화 완료")

    # 테스트 이미지 생성
    print("\n[2] 테스트 이미지 생성...")

    test_cases = [
        {
            "text": "Beautiful\nCafe ☕",
            "filename": "safe_cafe.jpg",
            "color": "white",
            "bg_color": "navy",
            "expected": "safe",
            "description": "안전한 카페 이미지"
        },
        {
            "text": "🌸 Spring\nFlowers 🌸",
            "filename": "safe_flowers.jpg",
            "color": "pink",
            "bg_color": "lightgreen",
            "expected": "safe",
            "description": "안전한 꽃 이미지"
        },
        {
            "text": "BUY NOW!\n50% OFF",
            "filename": "spam_ad.jpg",
            "color": "red",
            "bg_color": "yellow",
            "expected": "spam",
            "description": "스팸/광고 이미지"
        }
    ]

    created_images = []
    for case in test_cases:
        filepath = create_test_image(
            text=case["text"],
            filename=case["filename"],
            color=case["color"],
            bg_color=case["bg_color"]
        )
        created_images.append((filepath, case["expected"], case["description"]))

    # GPT-4 Vision으로 이미지 필터링 테스트
    print("\n[3] GPT-4 Vision 이미지 필터링 테스트...")
    print(f"    (OpenAI API 키: {'✅ 설정됨' if os.getenv('OPENAI_API_KEY') else '❌ 없음'})")

    results = []
    for image_path, expected, description in created_images:
        print(f"\n📷 테스트: {description}")
        print(f"   파일: {image_path}")
        print(f"   예상: {expected}")

        result = agent.check_image(image_path)

        print(f"   결과: {'안전' if result.is_safe else '불안전'}")
        print(f"   이유: {result.reason.value}")
        print(f"   신뢰도: {result.confidence:.2f}")
        print(f"   상세: {result.details}")

        results.append({
            "image": image_path,
            "description": description,
            "expected": expected,
            "is_safe": result.is_safe,
            "reason": result.reason.value,
            "confidence": result.confidence,
            "details": result.details
        })

    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)

    for i, r in enumerate(results, 1):
        status = "✅" if (r["expected"] == "safe" and r["is_safe"]) or (r["expected"] != "safe" and not r["is_safe"]) else "⚠️"
        print(f"{i}. {status} {r['description']}")
        print(f"   - 예상: {r['expected']}, 결과: {'safe' if r['is_safe'] else r['reason']}")
        print(f"   - 신뢰도: {r['confidence']:.2f}")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

    # 비용 안내
    print("\n💰 참고: GPT-4o Vision API 사용 시 비용이 발생합니다.")
    print("   - 이미지당 약 $0.001-0.003 (detail=low)")
    print("   - 총 테스트 이미지: 3개")


if __name__ == "__main__":
    main()
