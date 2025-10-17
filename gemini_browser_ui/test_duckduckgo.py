#!/usr/bin/env python3
"""
DuckDuckGo + Playwright 테스트
reCAPTCHA 없이 검색이 가능한지 확인
"""

import asyncio
from playwright.async_api import async_playwright
import json
from loguru import logger

async def test_duckduckgo_search(query: str):
    """DuckDuckGo 검색 테스트"""

    logger.info(f"🦆 DuckDuckGo 검색 테스트: {query}")

    async with async_playwright() as p:
        # 브라우저 시작
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # Anti-detection 스크립트
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = await context.new_page()

        try:
            # DuckDuckGo 접속
            logger.info("1️⃣  DuckDuckGo 접속 중...")
            await page.goto("https://duckduckgo.com", wait_until="domcontentloaded", timeout=30000)
            logger.info("✅ DuckDuckGo 로드 완료")

            # reCAPTCHA 체크
            has_captcha = await page.query_selector('iframe[src*="recaptcha"]')
            if has_captcha:
                logger.error("❌ reCAPTCHA 감지됨!")
                return None
            else:
                logger.info("✅ reCAPTCHA 없음!")

            # 검색창 찾기
            logger.info("2️⃣  검색창 찾는 중...")
            search_input = await page.query_selector('input[name="q"]')
            if not search_input:
                logger.error("❌ 검색창을 찾을 수 없음")
                return None

            logger.info("✅ 검색창 발견")

            # 검색어 입력
            logger.info(f"3️⃣  검색어 입력: {query}")
            await search_input.fill(query)
            await asyncio.sleep(0.5)

            # Enter 키 누르기
            logger.info("4️⃣  검색 실행...")
            await search_input.press("Enter")

            # 결과 페이지 대기
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            await asyncio.sleep(2)  # 결과 로드 대기

            # reCAPTCHA 재확인
            has_captcha = await page.query_selector('iframe[src*="recaptcha"]')
            if has_captcha:
                logger.error("❌ 검색 후 reCAPTCHA 나타남!")
                return None

            logger.info("✅ 검색 후에도 reCAPTCHA 없음!")

            # 검색 결과 추출
            logger.info("5️⃣  검색 결과 추출 중...")

            results = []

            # DuckDuckGo의 검색 결과 셀렉터
            # 일반 결과: article[data-testid="result"]
            result_elements = await page.query_selector_all('article[data-testid="result"]')

            logger.info(f"📊 발견된 결과: {len(result_elements)}개")

            for i, element in enumerate(result_elements[:10]):  # 상위 10개만
                try:
                    # 제목
                    title_elem = await element.query_selector('h2')
                    title = await title_elem.inner_text() if title_elem else "No title"

                    # URL
                    link_elem = await element.query_selector('a[href]')
                    url = await link_elem.get_attribute('href') if link_elem else ""

                    # 요약
                    snippet_elem = await element.query_selector('div[data-result="snippet"]')
                    snippet = await snippet_elem.inner_text() if snippet_elem else ""

                    results.append({
                        'title': title.strip(),
                        'url': url.strip(),
                        'snippet': snippet.strip()
                    })

                    logger.info(f"  {i+1}. {title[:60]}...")
                    logger.info(f"     {url[:80]}...")

                except Exception as e:
                    logger.warning(f"⚠️  결과 {i+1} 파싱 실패: {e}")
                    continue

            # 스크린샷 저장
            screenshot_path = "/tmp/duckduckgo_test.png"
            await page.screenshot(path=screenshot_path)
            logger.info(f"📸 스크린샷 저장: {screenshot_path}")

            logger.info(f"\n✅ 총 {len(results)}개 결과 추출 완료!")

            return results

        except Exception as e:
            logger.error(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

            # 오류 시 스크린샷
            await page.screenshot(path="/tmp/duckduckgo_error.png")
            logger.info("📸 오류 스크린샷: /tmp/duckduckgo_error.png")

            return None

        finally:
            await browser.close()

async def main():
    """메인 테스트"""

    logger.info("=" * 70)
    logger.info("🧪 DuckDuckGo + Playwright 테스트")
    logger.info("=" * 70)

    test_queries = [
        "Anthropic Claude AI",
        "Python tutorial",
        "인공지능 최신 트렌드"
    ]

    for query in test_queries:
        logger.info(f"\n{'='*70}")
        logger.info(f"테스트 쿼리: {query}")
        logger.info(f"{'='*70}\n")

        results = await test_duckduckgo_search(query)

        if results:
            logger.info(f"\n✅ 성공! {len(results)}개 결과:")
            for i, r in enumerate(results[:3], 1):
                logger.info(f"\n{i}. {r['title']}")
                logger.info(f"   URL: {r['url']}")
                logger.info(f"   요약: {r['snippet'][:100]}...")
        else:
            logger.error(f"\n❌ 실패: {query}")

        logger.info("\n" + "="*70)
        await asyncio.sleep(3)  # 쿼리 간 대기

    logger.info("\n🎉 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
