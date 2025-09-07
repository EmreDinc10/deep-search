from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import json
import time
from typing import Dict
import logging

from models import SearchRequest, SearchResponse, SearchProgress, SearchSource, SearchResult
from search_modules import ParallelSearchManager
from azure_openai_client import AzureOpenAIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Deep Search API",
    description="Parallel search across multiple sources with AI synthesis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
search_manager = ParallelSearchManager()
openai_client = AzureOpenAIClient()

# Store for tracking search progress
search_progress: Dict[str, Dict[SearchSource, SearchProgress]] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Deep Search API is running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "available_sources": [source.value for source in SearchSource]
    }

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables (for troubleshooting)"""
    import os
    
    return {
        "azure_openai_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "NOT_SET"),
        "azure_openai_deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "NOT_SET"),
        "azure_openai_api_version": os.getenv("AZURE_OPENAI_API_VERSION", "NOT_SET"),
        "azure_openai_api_key_exists": "YES" if os.getenv("AZURE_OPENAI_API_KEY") else "NO",
        "azure_openai_api_key_length": len(os.getenv("AZURE_OPENAI_API_KEY", "")) if os.getenv("AZURE_OPENAI_API_KEY") else 0
    }

@app.get("/debug/azure-openai")
async def debug_azure_openai():
    """Debug endpoint to test Azure OpenAI connection"""
    try:
        # Test AI synthesis with simple data
        test_results = {
            SearchSource.WIKIPEDIA: [
                SearchResult(
                    source=SearchSource.WIKIPEDIA,
                    title="Test Article",
                    url="https://example.com",
                    snippet="This is a test snippet for debugging Azure OpenAI integration."
                )
            ]
        }
        
        synthesis_result = await openai_client.synthesize_results("test query", test_results)
        
        return {
            "status": "success",
            "message": "Azure OpenAI connection working",
            "synthesis_length": len(synthesis_result),
            "synthesis_preview": synthesis_result[:200] + "..." if len(synthesis_result) > 200 else synthesis_result
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Perform parallel search across multiple sources"""
    start_time = time.time()
    search_id = f"search_{int(start_time * 1000)}"
    
    logger.info(f"Starting search {search_id} for query: {request.query}")
    
    # Initialize progress tracking
    search_progress[search_id] = {}
    for source in request.sources:
        search_progress[search_id][source] = SearchProgress(
            source=source,
            status="started"
        )
    
    try:
        # Execute parallel search
        results = await search_manager.search_parallel(
            query=request.query,
            sources=request.sources,
            max_results_per_source=request.max_results_per_source
        )
        
        # Update progress
        for source, source_results in results.items():
            if source in search_progress[search_id]:
                search_progress[search_id][source].status = "completed"
                search_progress[search_id][source].results_count = len(source_results)
        
        # Convert results to response format
        formatted_results = {}
        total_results = 0
        
        for source in request.sources:
            source_results = results.get(source, [])
            formatted_results[source] = source_results
            total_results += len(source_results)
        
        # Generate AI synthesis
        ai_synthesis = None
        if total_results > 0:
            try:
                ai_synthesis = await openai_client.synthesize_results(request.query, formatted_results)
            except Exception as e:
                logger.error(f"AI synthesis failed: {e}")
                ai_synthesis = "AI synthesis unavailable"
        
        search_duration = time.time() - start_time
        
        # Clean up progress tracking
        if search_id in search_progress:
            del search_progress[search_id]
        
        response = SearchResponse(
            query=request.query,
            results=formatted_results,
            ai_synthesis=ai_synthesis,
            search_duration=search_duration,
            total_results=total_results
        )
        
        logger.info(f"Search {search_id} completed in {search_duration:.2f}s with {total_results} results")
        return response
        
    except Exception as e:
        logger.error(f"Search {search_id} failed: {e}")
        # Update progress with error
        for source in request.sources:
            if source in search_progress[search_id]:
                search_progress[search_id][source].status = "error"
                search_progress[search_id][source].error_message = str(e)
        
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/search/progress/{search_id}")
async def get_search_progress(search_id: str):
    """Get progress of a running search"""
    if search_id not in search_progress:
        raise HTTPException(status_code=404, detail="Search not found")
    
    return search_progress[search_id]

@app.get("/search/stream/{query}")
async def stream_search(query: str, sources: str = "google,duckduckgo,wikipedia"):
    """Stream search results as they come in"""
    
    # Parse sources
    source_list = []
    for source_name in sources.split(","):
        try:
            source_list.append(SearchSource(source_name.strip().lower()))
        except ValueError:
            continue
    
    if not source_list:
        source_list = [SearchSource.GOOGLE, SearchSource.DUCKDUCKGO, SearchSource.WIKIPEDIA]
    
    async def generate_stream():
        search_id = f"stream_{int(time.time() * 1000)}"
        
        # Send initial message
        yield f"data: {json.dumps({'type': 'start', 'search_id': search_id, 'query': query})}\n\n"
        
        try:
            # Execute searches and stream results
            tasks = []
            for source in source_list:
                if source in search_manager.modules:
                    task = asyncio.create_task(
                        search_manager.modules[source].search(query, 5),
                        name=f"search_{source.value}"
                    )
                    tasks.append((source, task))
            
            # Stream results as they complete
            for source, task in tasks:
                try:
                    results = await task
                    yield f"data: {json.dumps({'type': 'results', 'source': source.value, 'results': [r.dict() for r in results]})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'source': source.value, 'error': str(e)})}\n\n"
            
            # Send completion message
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/sources")
async def list_sources():
    """List available search sources"""
    return {
        "sources": [
            {
                "name": source.value,
                "display_name": source.value.title(),
                "available": source in search_manager.modules
            }
            for source in SearchSource
        ]
    }

@app.post("/analyze")
async def analyze_results(request: SearchRequest):
    """Get AI insights about search results without full synthesis"""
    try:
        # Execute search
        results = await search_manager.search_parallel(
            query=request.query,
            sources=request.sources,
            max_results_per_source=request.max_results_per_source
        )
        
        # Generate insights
        insights = await openai_client.generate_search_insights(request.query, results)
        
        return {
            "query": request.query,
            "insights": insights,
            "total_results": sum(len(source_results) for source_results in results.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
