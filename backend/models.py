from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class SearchSource(str, Enum):
    GOOGLE = "google"
    DUCKDUCKGO = "duckduckgo"  
    WIKIPEDIA = "wikipedia"
    REDDIT = "reddit"

class SearchResult(BaseModel):
    source: SearchSource
    title: str
    url: str
    snippet: str
    timestamp: Optional[str] = None
    score: Optional[float] = None

class SearchRequest(BaseModel):
    query: str
    sources: List[SearchSource] = [SearchSource.GOOGLE, SearchSource.DUCKDUCKGO, SearchSource.WIKIPEDIA]
    max_results_per_source: int = 5

class SearchResponse(BaseModel):
    query: str
    results: Dict[SearchSource, List[SearchResult]]
    ai_synthesis: Optional[str] = None
    search_duration: float
    total_results: int

class SearchProgress(BaseModel):
    source: SearchSource
    status: str  # "started", "completed", "error"
    results_count: int = 0
    error_message: Optional[str] = None
