import asyncio
from typing import List, Optional
from abc import ABC, abstractmethod
import logging

# Import search libraries
from duckduckgo_search import DDGS
import wikipedia
import praw

from models import SearchResult, SearchSource

logger = logging.getLogger(__name__)

class SearchModule(ABC):
    """Abstract base class for search modules"""
    
    def __init__(self, source: SearchSource):
        self.source = source
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Perform search and return results"""
        pass

class GoogleSearchModule(SearchModule):
    """Google search using multiple fallback strategies"""
    
    def __init__(self):
        super().__init__(SearchSource.GOOGLE)
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            import os
            import json
            import httpx
            from urllib.parse import quote_plus
            
            results = []
            loop = asyncio.get_event_loop()
            
            # Strategy 1: Google Custom Search API (if credentials available)
            async def try_google_api():
                google_api_key = os.getenv('GOOGLE_API_KEY')
                google_cse_id = os.getenv('GOOGLE_CSE_ID')
                
                if google_api_key and google_cse_id:
                    try:
                        api_url = "https://www.googleapis.com/customsearch/v1"
                        params = {
                            'key': google_api_key,
                            'cx': google_cse_id,
                            'q': query,
                            'num': min(max_results, 10)
                        }
                        
                        async with httpx.AsyncClient(timeout=10) as client:
                            response = await client.get(api_url, params=params)
                            
                        if response.status_code == 200:
                            data = response.json()
                            api_results = []
                            
                            for item in data.get('items', [])[:max_results]:
                                api_results.append(SearchResult(
                                    source=self.source,
                                    title=item.get('title', 'Google Result'),
                                    url=item.get('link', ''),
                                    snippet=item.get('snippet', 'No snippet available')
                                ))
                            
                            logger.info(f"Google API search successful: {len(api_results)} results")
                            return api_results
                    except Exception as e:
                        logger.warning(f"Google API search failed: {e}")
                return []
            
            # Strategy 2: SerpAPI (alternative Google search API)
            async def try_serpapi():
                serpapi_key = os.getenv('SERPAPI_KEY')
                
                if serpapi_key:
                    try:
                        serpapi_url = "https://serpapi.com/search"
                        params = {
                            'api_key': serpapi_key,
                            'engine': 'google',
                            'q': query,
                            'num': max_results
                        }
                        
                        async with httpx.AsyncClient(timeout=10) as client:
                            response = await client.get(serpapi_url, params=params)
                        
                        if response.status_code == 200:
                            data = response.json()
                            serp_results = []
                            
                            for item in data.get('organic_results', [])[:max_results]:
                                serp_results.append(SearchResult(
                                    source=self.source,
                                    title=item.get('title', 'Google Result'),
                                    url=item.get('link', ''),
                                    snippet=item.get('snippet', 'No snippet available')
                                ))
                            
                            logger.info(f"SerpAPI search successful: {len(serp_results)} results")
                            return serp_results
                    except Exception as e:
                        logger.warning(f"SerpAPI search failed: {e}")
                return []
            
            # Strategy 3: Improved web scraping with rotating user agents
            def try_web_scraping():
                try:
                    import requests
                    import random
                    from urllib.parse import quote_plus
                    import re
                    import time
                    
                    user_agents = [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
                    ]
                    
                    headers = {
                        'User-Agent': random.choice(user_agents),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    }
                    
                    # Try different Google domains
                    domains = ['www.google.com', 'www.google.co.uk', 'www.google.ca']
                    
                    for domain in domains:
                        try:
                            search_url = f"https://{domain}/search?q={quote_plus(query)}&num={max_results}&hl=en"
                            
                            response = requests.get(search_url, headers=headers, timeout=8)
                            
                            if response.status_code == 200:
                                html = response.text
                                
                                # Enhanced regex patterns for different Google result formats
                                patterns = [
                                    r'<a href="/url\?q=([^&]+)&amp;sa=U.*?<h3.*?>(.*?)</h3>.*?<span.*?>(.*?)</span>',
                                    r'<a.*?href="([^"]*)".*?<h3.*?>(.*?)</h3>.*?<div.*?>(.*?)</div>',
                                    r'<div class="g">.*?<a href="([^"]*)".*?<h3.*?>(.*?)</h3>.*?<span.*?>(.*?)</span>'
                                ]
                                
                                scrape_results = []
                                
                                for pattern in patterns:
                                    matches = re.findall(pattern, html, re.DOTALL)
                                    
                                    for i, match in enumerate(matches[:max_results]):
                                        if len(match) >= 2:
                                            url = match[0]
                                            title = re.sub(r'<[^>]+>', '', match[1])[:100]
                                            snippet = re.sub(r'<[^>]+>', '', match[2] if len(match) > 2 else '')[:200]
                                            
                                            if url.startswith('http') and title:
                                                scrape_results.append({
                                                    'title': title,
                                                    'url': url,
                                                    'snippet': snippet or f"Google search result for: {query}"
                                                })
                                    
                                    if scrape_results:
                                        logger.info(f"Web scraping successful from {domain}: {len(scrape_results)} results")
                                        return scrape_results[:max_results]
                            
                            time.sleep(1)  # Rate limiting between domains
                        except Exception as e:
                            logger.warning(f"Scraping failed for {domain}: {e}")
                            continue
                    
                    return []
                    
                except Exception as e:
                    logger.warning(f"Web scraping approach failed: {e}")
                    return []
            
            # Strategy 4: Fallback to original googlesearch library
            def try_googlesearch_library():
                try:
                    from googlesearch import search as google_search
                    urls = list(google_search(query, num_results=max_results, sleep_interval=2, pause=1))
                    
                    lib_results = []
                    for i, url in enumerate(urls[:max_results]):
                        lib_results.append({
                            'title': f'Google Result {i+1}',
                            'url': url,
                            'snippet': f'Google search result for: {query}'
                        })
                    
                    if lib_results:
                        logger.info(f"Googlesearch library successful: {len(lib_results)} results")
                    return lib_results
                except Exception as e:
                    logger.warning(f"Googlesearch library failed: {e}")
                    return []
            
            # Try strategies in order of preference
            search_data = await try_google_api()
            
            if not search_data:
                search_data = await try_serpapi()
            
            if not search_data:
                search_data = await loop.run_in_executor(None, try_web_scraping)
            
            if not search_data:
                search_data = await loop.run_in_executor(None, try_googlesearch_library)
            
            # Convert results to SearchResult objects
            for item in search_data:
                if isinstance(item, SearchResult):
                    results.append(item)
                elif isinstance(item, dict):
                    results.append(SearchResult(
                        source=self.source,
                        title=item.get('title', 'Google Result'),
                        url=item.get('url', ''),
                        snippet=item.get('snippet', f"Google search result for: {query}")
                    ))
                elif isinstance(item, str):  # URL only
                    results.append(SearchResult(
                        source=self.source,
                        title=f'Google Result {len(results)+1}',
                        url=item,
                        snippet=f"Google search result for: {query}"
                    ))
            
            if results:
                logger.info(f"Google search successful: {len(results)} results for '{query}'")
            else:
                logger.warning(f"All Google search strategies failed for query: {query}")
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []

class DuckDuckGoSearchModule(SearchModule):
    """DuckDuckGo search using duckduckgo-search library with enhanced configuration"""
    
    def __init__(self):
        super().__init__(SearchSource.DUCKDUCKGO)
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            results = []
            loop = asyncio.get_event_loop()
            
            # Enhanced DuckDuckGo search with better configuration
            def run_ddgs_search():
                try:
                    # Use DDGS with custom headers and settings
                    ddgs = DDGS(
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        },
                        timeout=10
                    )
                    
                    # Perform search with region and safesearch settings
                    search_results = ddgs.text(
                        query, 
                        max_results=max_results,
                        region='us-en',
                        safesearch='moderate',
                        timelimit=None
                    )
                    
                    return list(search_results)
                    
                except Exception as e:
                    logger.warning(f"DuckDuckGo search attempt failed: {e}")
                    # Try with minimal configuration as fallback
                    try:
                        simple_ddgs = DDGS()
                        return list(simple_ddgs.text(query, max_results=max_results))
                    except Exception as e2:
                        logger.warning(f"DuckDuckGo fallback search also failed: {e2}")
                        return []
            
            ddgs_results = await loop.run_in_executor(None, run_ddgs_search)
            
            if not ddgs_results:
                logger.warning("DuckDuckGo search returned no results")
                return []
            
            for item in ddgs_results:
                if isinstance(item, dict):
                    results.append(SearchResult(
                        source=self.source,
                        title=item.get('title', 'No title'),
                        url=item.get('href', item.get('link', '')),
                        snippet=item.get('body', item.get('snippet', 'No snippet available'))
                    ))
            
            logger.info(f"DuckDuckGo search successful: {len(results)} results for '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []

class WikipediaSearchModule(SearchModule):
    """Wikipedia search using wikipedia library"""
    
    def __init__(self):
        super().__init__(SearchSource.WIKIPEDIA)
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            results = []
            loop = asyncio.get_event_loop()
            
            # Search Wikipedia
            search_results = await loop.run_in_executor(
                None,
                lambda: wikipedia.search(query, results=max_results)
            )
            
            for title in search_results[:max_results]:
                try:
                    # Get page summary
                    summary = await loop.run_in_executor(
                        None,
                        lambda t=title: wikipedia.summary(t, sentences=2, auto_suggest=False)
                    )
                    
                    page_url = await loop.run_in_executor(
                        None,
                        lambda t=title: wikipedia.page(t, auto_suggest=False).url
                    )
                    
                    results.append(SearchResult(
                        source=self.source,
                        title=title,
                        url=page_url,
                        snippet=summary
                    ))
                except wikipedia.exceptions.DisambiguationError as e:
                    # Take the first option from disambiguation
                    if e.options:
                        try:
                            first_option = e.options[0]
                            summary = await loop.run_in_executor(
                                None,
                                lambda: wikipedia.summary(first_option, sentences=2, auto_suggest=False)
                            )
                            page_url = await loop.run_in_executor(
                                None,
                                lambda: wikipedia.page(first_option, auto_suggest=False).url
                            )
                            results.append(SearchResult(
                                source=self.source,
                                title=first_option,
                                url=page_url,
                                snippet=summary
                            ))
                        except Exception:
                            continue
                except Exception:
                    continue
            
            return results
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return []

class ParallelSearchManager:
    """Manager for coordinating parallel searches across multiple modules"""
    
    def __init__(self):
        self.modules = {}
        self.setup_modules()
    
    def setup_modules(self):
        """Initialize search modules"""
        self.modules[SearchSource.GOOGLE] = GoogleSearchModule()
        self.modules[SearchSource.DUCKDUCKGO] = DuckDuckGoSearchModule()
        self.modules[SearchSource.WIKIPEDIA] = WikipediaSearchModule()
    
    async def search_parallel(self, query: str, sources: List[SearchSource], max_results_per_source: int = 5) -> dict:
        """Execute parallel searches across selected sources with timeout handling"""
        tasks = []
        
        for source in sources:
            if source in self.modules:
                # Wrap each search with timeout
                async def search_with_timeout(src, mod):
                    try:
                        # Set timeout per source (Google might need more time due to sleep intervals)
                        timeout = 30 if src == SearchSource.GOOGLE else 15
                        return await asyncio.wait_for(
                            mod.search(query, max_results_per_source),
                            timeout=timeout
                        )
                    except asyncio.TimeoutError:
                        logger.warning(f"Search timeout for {src.value} after {timeout}s")
                        return []
                    except Exception as e:
                        logger.error(f"Search error for {src.value}: {e}")
                        return []
                
                task = asyncio.create_task(
                    search_with_timeout(source, self.modules[source]),
                    name=f"search_{source.value}"
                )
                tasks.append((source, task))
        
        results = {}
        
        # Execute all searches in parallel
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for i, (source, task) in enumerate(tasks):
            try:
                if isinstance(completed_tasks[i], Exception):
                    logger.error(f"Search failed for {source}: {completed_tasks[i]}")
                    results[source] = []
                else:
                    search_results = completed_tasks[i]
                    results[source] = search_results if search_results else []
                    logger.info(f"{source.value} search completed: {len(results[source])} results")
            except Exception as e:
                logger.error(f"Error processing results for {source}: {e}")
                results[source] = []
        
        return results
