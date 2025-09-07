import asyncio
from typing import List, Optional
from abc import ABC, abstractmethod
import logging

# Import search libraries
from googlesearch import search as google_search
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
    """Google search using googlesearch-python library with enhanced error handling"""
    
    def __init__(self):
        super().__init__(SearchSource.GOOGLE)
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            results = []
            loop = asyncio.get_event_loop()
            
            # Enhanced Google search with better parameters
            def run_google_search():
                try:
                    # Use more conservative settings to avoid rate limiting
                    return list(google_search(
                        query, 
                        num_results=max_results,
                        sleep_interval=2,  # Increased sleep interval
                        lang='en',
                        safe='off',
                        pause=2.0  # Additional pause parameter
                    ))
                except Exception as e:
                    logger.warning(f"Google search attempt failed: {e}")
                    return []
            
            urls = await loop.run_in_executor(None, run_google_search)
            
            if not urls:
                logger.warning("Google search returned no results - might be rate limited")
                return []
            
            for i, url in enumerate(urls[:max_results]):
                results.append(SearchResult(
                    source=self.source,
                    title=f"Google Result {i+1}",
                    url=url,
                    snippet=f"Search result from Google for: {query}"
                ))
            
            logger.info(f"Google search successful: {len(results)} results for '{query}'")
            return results
            
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
