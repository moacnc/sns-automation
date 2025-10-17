#!/usr/bin/env python3
"""
Search Agent - Google Search Grounding Specialist

Uses Google's official Search Grounding API to perform web searches
without bot detection issues. Returns summarized results with source URLs.
"""

import os
from typing import Optional, Dict, Any, List, Callable
from loguru import logger
from google import genai
from google.genai import types


class SearchAgent:
    """
    Search Agent using Google Search Grounding

    This agent specializes in web searches using Google's official API,
    avoiding bot detection issues that plague direct browser-based searches.
    """

    def __init__(self, api_key: Optional[str] = None, progress_callback: Optional[Callable] = None):
        """
        Initialize Search Agent

        Args:
            api_key: Google AI API key (or uses GEMINI_API_KEY env var)
            progress_callback: Optional callback for progress updates
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Model for search grounding
        self.model_name = "gemini-2.0-flash-exp"

        # Google Search Grounding tool
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Progress callback
        self.progress_callback = progress_callback

        logger.info(f"🔍 SearchAgent initialized with model: {self.model_name}")

    def search(self, query: str, language: str = "ko") -> Dict[str, Any]:
        """
        Perform Google Search using Search Grounding

        Args:
            query: Search query
            language: Language for search results (default: Korean)

        Returns:
            Dictionary containing:
            - query: Original search query
            - summary: AI-generated summary of results
            - sources: List of source URLs with titles
            - search_queries: Actual search queries used by Gemini
            - grounding_metadata: Full grounding metadata
        """
        try:
            logger.info(f"🔍 Searching: {query}")

            if self.progress_callback:
                self.progress_callback({
                    'agent': 'search',
                    'type': 'info',
                    'message': f'🔍 Google Search 시작: "{query}"'
                })

            # Build search prompt optimized for Korean/English
            search_prompt = self._build_search_prompt(query, language)

            # Configure with Google Search Grounding
            config = types.GenerateContentConfig(
                tools=[self.grounding_tool],
                temperature=0.3,  # Lower temperature for factual searches
            )

            if self.progress_callback:
                self.progress_callback({
                    'agent': 'search',
                    'type': 'info',
                    'message': '⏳ Google Search Grounding API 호출 중...'
                })

            # Call Gemini with Search Grounding
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=search_prompt,
                config=config
            )

            # Extract grounding metadata
            grounding_metadata = response.candidates[0].grounding_metadata if hasattr(response, 'candidates') else None

            # Extract search queries used
            search_queries = []
            if grounding_metadata and hasattr(grounding_metadata, 'web_search_queries'):
                search_queries = grounding_metadata.web_search_queries
                logger.info(f"📋 Search queries used: {search_queries}")

            # Extract sources
            sources = self._extract_sources(grounding_metadata)

            # Get summary text
            summary = response.text if hasattr(response, 'text') else "검색 결과를 가져올 수 없습니다."

            logger.info(f"✅ Search completed: {len(sources)} sources found")

            if self.progress_callback:
                self.progress_callback({
                    'agent': 'search',
                    'type': 'info',
                    'message': f'✅ 검색 완료: {len(sources)}개 소스 발견'
                })

                # Send summary as gemini_text
                self.progress_callback({
                    'agent': 'search',
                    'type': 'gemini_text',
                    'message': f'💭 검색 결과 요약:\n{summary[:500]}...'
                })

            result = {
                'query': query,
                'summary': summary,
                'sources': sources,
                'search_queries': search_queries,
                'grounding_metadata': grounding_metadata,
                'source_count': len(sources)
            }

            return result

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")

            if self.progress_callback:
                self.progress_callback({
                    'agent': 'search',
                    'type': 'error',
                    'message': f'❌ 검색 실패: {str(e)}'
                })

            return {
                'query': query,
                'summary': f"검색 중 오류 발생: {str(e)}",
                'sources': [],
                'search_queries': [],
                'grounding_metadata': None,
                'source_count': 0,
                'error': str(e)
            }

    def _build_search_prompt(self, query: str, language: str) -> str:
        """
        Build optimized search prompt

        Args:
            query: User's search query
            language: Target language

        Returns:
            Optimized prompt for search grounding
        """
        if language == "ko":
            prompt = f"""다음 주제에 대해 웹 검색을 수행하고 요약해주세요:

검색어: {query}

요구사항:
1. 최신 정보를 우선 검색 (2024-2025)
2. 신뢰할 수 있는 출처 우선
3. 한국어 결과 우선 (있는 경우)
4. 핵심 정보를 3-5문장으로 요약
5. 각 정보의 출처를 명시

검색 결과를 다음 형식으로 정리해주세요:

## 요약
[핵심 정보 3-5문장]

## 주요 소스
1. [소스명] - [URL]
2. [소스명] - [URL]
...

## 추가 정보
[필요시 추가 세부사항]
"""
        else:
            prompt = f"""Search and summarize information about: {query}

Requirements:
1. Prioritize recent information (2024-2025)
2. Use reliable sources
3. Summarize key information in 3-5 sentences
4. Cite sources clearly

Format the results as:

## Summary
[Key information in 3-5 sentences]

## Main Sources
1. [Source name] - [URL]
2. [Source name] - [URL]
...

## Additional Information
[Details if needed]
"""

        return prompt

    def _extract_sources(self, grounding_metadata) -> List[Dict[str, str]]:
        """
        Extract source URLs and titles from grounding metadata

        Args:
            grounding_metadata: Grounding metadata from Gemini response

        Returns:
            List of dicts with 'title' and 'url' keys
        """
        sources = []

        if not grounding_metadata:
            return sources

        try:
            # Extract grounding chunks (web sources)
            if hasattr(grounding_metadata, 'grounding_chunks'):
                for chunk in grounding_metadata.grounding_chunks:
                    if hasattr(chunk, 'web'):
                        web = chunk.web
                        source = {
                            'title': getattr(web, 'title', 'Untitled'),
                            'url': getattr(web, 'uri', '')
                        }
                        if source['url']:
                            sources.append(source)

            # Remove duplicates while preserving order
            seen_urls = set()
            unique_sources = []
            for source in sources:
                if source['url'] not in seen_urls:
                    seen_urls.add(source['url'])
                    unique_sources.append(source)

            logger.info(f"📚 Extracted {len(unique_sources)} unique sources")

            return unique_sources

        except Exception as e:
            logger.error(f"❌ Failed to extract sources: {e}")
            return []

    def search_and_extract_urls(self, query: str) -> List[str]:
        """
        Quick search to extract only URLs (for orchestrator)

        Args:
            query: Search query

        Returns:
            List of URLs
        """
        result = self.search(query)
        return [source['url'] for source in result.get('sources', [])]

    def multi_search(self, queries: List[str]) -> Dict[str, Any]:
        """
        Perform multiple searches and combine results

        Args:
            queries: List of search queries

        Returns:
            Combined search results
        """
        all_results = []
        all_sources = []

        for query in queries:
            result = self.search(query)
            all_results.append(result)
            all_sources.extend(result.get('sources', []))

        # Deduplicate sources
        seen_urls = set()
        unique_sources = []
        for source in all_sources:
            if source['url'] not in seen_urls:
                seen_urls.add(source['url'])
                unique_sources.append(source)

        return {
            'queries': queries,
            'results': all_results,
            'combined_sources': unique_sources,
            'total_sources': len(unique_sources)
        }


# Test function
if __name__ == "__main__":
    """Test SearchAgent"""

    # Test 1: Simple search
    agent = SearchAgent()
    result = agent.search("한국 유명 뷰티 유튜버 2025")

    print("\n" + "="*60)
    print("SEARCH RESULTS")
    print("="*60)
    print(f"\nQuery: {result['query']}")
    print(f"\nSummary:\n{result['summary']}")
    print(f"\nSources ({result['source_count']}):")
    for i, source in enumerate(result['sources'][:5], 1):
        print(f"{i}. {source['title']}")
        print(f"   {source['url']}")

    # Test 2: Multiple searches
    print("\n" + "="*60)
    print("MULTI-SEARCH TEST")
    print("="*60)

    multi_result = agent.multi_search([
        "삼성전자 주가 2025",
        "AI 트렌드 2025"
    ])

    print(f"\nTotal unique sources: {multi_result['total_sources']}")
