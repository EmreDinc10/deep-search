#!/usr/bin/env python3
"""
Local Azure OpenAI Connection Test with Fixed Parameters
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

async def test_fixed_parameters():
    """Test with the correct parameters for o3-mini model"""
    logger.info("=== Testing with FIXED parameters (max_completion_tokens) ===")
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    try:
        # Test basic connection with correct parameter
        logger.info("Testing basic connection with max_completion_tokens...")
        response = await client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": "Hello, can you respond with 'Connection successful'?"}],
            max_completion_tokens=20,  # Using max_completion_tokens instead of max_tokens
            temperature=0
        )
        
        result = response.choices[0].message.content
        logger.info(f"✅ Basic connection test successful!")
        logger.info(f"Response: {result}")
        
        # Test synthesis simulation
        logger.info("\nTesting synthesis simulation...")
        synthesis_response = await client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful research assistant that synthesizes information from multiple sources."},
                {"role": "user", "content": "Synthesize this test data: Wikipedia says 'Azure OpenAI is a cloud service.' Please provide a brief summary."}
            ],
            max_completion_tokens=100,  # Using max_completion_tokens
            temperature=0.7
        )
        
        synthesis_result = synthesis_response.choices[0].message.content
        logger.info(f"✅ Synthesis test successful!")
        logger.info(f"Synthesis result: {synthesis_result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def main():
    """Run the fixed test"""
    print("🚀 Testing Azure OpenAI with Fixed Parameters...")
    print("=" * 60)
    
    success = await test_fixed_parameters()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULT: Azure OpenAI works with max_completion_tokens!")
        print("   The issue was using max_tokens instead of max_completion_tokens for o3-mini model.")
        print("   Now we need to update the backend code to use the correct parameter.")
    else:
        print("❌ RESULT: Still having issues even with fixed parameters.")

if __name__ == "__main__":
    asyncio.run(main())
