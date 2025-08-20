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
    """Google search using googlesearch-python library"""
    
    def __init__(self):
        super().__init__(SearchSource.GOOGLE)
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            results = []
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            urls = await loop.run_in_executor(
                None, 
                lambda: list(google_search(query, num_results=max_results, sleep_interval=1))
            )
            
            for i, url in enumerate(urls[:max_results]):
                results.append(SearchResult(
                    source=self.source,
                    title=f"Google Result {i+1}",
                    url=url,
                    snippet=f"Search result from Google for: {query}"
                ))
            
            return results
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []

class DuckDuckGoSearchModule(SearchModule):
    """DuckDuckGo search using duckduckgo-search library"""
    
    def __init__(self):
        super().__init__(SearchSource.DUCKDUCKGO)
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            results = []
            loop = asyncio.get_event_loop()
            
            # Run DuckDuckGo search in thread pool
            ddgs_results = await loop.run_in_executor(
                None,
                lambda: DDGS().text(query, max_results=max_results)
            )
            
            for item in ddgs_results:
                results.append(SearchResult(
                    source=self.source,
                    title=item.get('title', 'No title'),
                    url=item.get('href', ''),
                    snippet=item.get('body', 'No snippet available')
                ))
            
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
        """Execute parallel searches across selected sources"""
        tasks = []
        
        for source in sources:
            if source in self.modules:
                task = asyncio.create_task(
                    self.modules[source].search(query, max_results_per_source),
                    name=f"search_{source.value}"
                )
                tasks.append((source, task))
        
        results = {}
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for i, (source, task) in enumerate(tasks):
            try:
                if isinstance(completed_tasks[i], Exception):
                    logger.error(f"Search failed for {source}: {completed_tasks[i]}")
                    results[source] = []
                else:
                    results[source] = completed_tasks[i]
            except Exception as e:
                logger.error(f"Error processing results for {source}: {e}")
                results[source] = []
        
        return results
