#!/usr/bin/env python3
"""
Test Azure OpenAI with Exact Same Parameters as Debug Endpoint
"""

import os
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from openai import AsyncAzureOpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_synthesis_exact():
    """Test with exact same logic as the debug endpoint"""
    logger.info("=== Testing exact synthesis logic from debug endpoint ===")
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    logger.info(f"API Key length: {len(api_key) if api_key else 0}")
    logger.info(f"API Key preview: {api_key[:10]}...{api_key[-10:] if api_key and len(api_key) > 20 else 'N/A'}")
    
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    # Create test results that match the debug endpoint structure
    from models import SearchSource, SearchResult
    
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
    
    try:
        # Mimic the exact synthesis call from azure_openai_client.py
        logger.info("Creating synthesis with exact backend logic...")
        
        # Format results like the backend does
        formatted_results = []
        for source, source_results in test_results.items():
            if source_results:
                formatted_results.append(f"\n{source.value.upper()} RESULTS:")
                for i, result in enumerate(source_results[:3], 1):
                    formatted_results.append(f"{i}. {result.title}")
                    formatted_results.append(f"   {result.snippet}")
                    formatted_results.append(f"   Source: {result.url}")
        
        system_prompt = """
        You are an expert research assistant. Your task is to analyze and synthesize information from multiple search sources to provide a comprehensive, well-structured response to the user's query.

        Guidelines:
        1. Provide a clear, comprehensive answer based on the search results
        2. Cite sources when making specific claims
        3. Identify patterns and connections across different sources
        4. Highlight any conflicting information found
        5. Structure your response with clear sections if appropriate
        6. Be objective and factual
        7. If information is limited, acknowledge the limitations
        
        Format your response in a clear, readable manner with proper sections and bullet points where appropriate.
        """
        
        user_prompt = f"""
        Query: test query
        
        Search Results from Multiple Sources:
        {chr(10).join(formatted_results)}
        
        Please analyze and synthesize this information to provide a comprehensive answer to the query. Include insights from the different sources and identify key themes or patterns.
        """
        
        logger.info(f"Making API call with system prompt length: {len(system_prompt)}")
        logger.info(f"Making API call with user prompt length: {len(user_prompt)}")
        
        response = await client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=2000
        )
        
        result = response.choices[0].message.content
        logger.info("✅ Synthesis successful!")
        logger.info(f"Result length: {len(result)}")
        logger.info(f"Result preview: {result[:200]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Synthesis failed: {e}")
        return False

async def main():
    """Run the exact synthesis test"""
    print("🚀 Testing Exact Synthesis Logic...")
    print("=" * 60)
    
    success = await test_synthesis_exact()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULT: Local synthesis works perfectly!")
        print("   This confirms the issue is with Render's environment, not our code.")
        print("   The API key on Render might be corrupted or have extra characters.")
    else:
        print("❌ RESULT: Synthesis fails locally too.")
        print("   This suggests there might be another issue.")

if __name__ == "__main__":
    asyncio.run(main())
