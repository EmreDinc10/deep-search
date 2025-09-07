#!/usr/bin/env python3
"""
Minimal Azure OpenAI Test for o3-mini model
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

async def test_minimal_o3_mini():
    """Test with minimal parameters supported by o3-mini"""
    logger.info("=== Testing o3-mini with MINIMAL supported parameters ===")
    
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
        # Test with absolutely minimal parameters
        logger.info("Testing with minimal parameters (no temperature, no max_tokens)...")
        response = await client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": "Hello"}]
            # No temperature, no max_completion_tokens - just the bare minimum
        )
        
        result = response.choices[0].message.content
        logger.info("✅ Minimal test successful!")
        logger.info(f"Response: {result}")
        
        # Test with max_completion_tokens but no temperature
        logger.info("\nTesting with max_completion_tokens only...")
        response2 = await client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "user", "content": "Explain Azure OpenAI in one sentence."}],
            max_completion_tokens=50
        )
        
        result2 = response2.choices[0].message.content
        logger.info("✅ Max completion tokens test successful!")
        logger.info(f"Response: {result2}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def main():
    """Run the minimal test"""
    print("🚀 Testing o3-mini with Minimal Parameters...")
    print("=" * 60)
    
    success = await test_minimal_o3_mini()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULT: o3-mini works with minimal parameters!")
        print("   Key findings:")
        print("   - Use max_completion_tokens instead of max_tokens")
        print("   - Don't use temperature parameter")
        print("   - o3-mini has different parameter requirements than other models")
    else:
        print("❌ RESULT: Still having issues with o3-mini model.")

if __name__ == "__main__":
    asyncio.run(main())
