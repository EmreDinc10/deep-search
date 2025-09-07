#!/usr/bin/env python3
"""
Local Azure OpenAI Connection Test
This script tests the Azure OpenAI connection using the same configuration
as the deployed application to isolate whether issues are with Render or Azure.
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

class LocalAzureOpenAITest:
    def __init__(self):
        """Initialize Azure OpenAI client with local environment"""
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        logger.info("=== Local Azure OpenAI Configuration Test ===")
        logger.info(f"Endpoint: {self.endpoint}")
        logger.info(f"Deployment: {self.deployment_name}")
        logger.info(f"API Version: {self.api_version}")
        logger.info(f"API Key exists: {bool(self.api_key)}")
        logger.info(f"API Key length: {len(self.api_key) if self.api_key else 0}")
        logger.info(f"API Key preview: {self.api_key[:10]}...{self.api_key[-10:] if self.api_key and len(self.api_key) > 20 else 'N/A'}")
        
        if not all([self.api_key, self.endpoint, self.deployment_name, self.api_version]):
            missing = []
            if not self.api_key: missing.append("AZURE_OPENAI_API_KEY")
            if not self.endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
            if not self.deployment_name: missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")
            if not self.api_version: missing.append("AZURE_OPENAI_API_VERSION")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        try:
            self.client = AsyncAzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            logger.info("✅ Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure OpenAI client: {e}")
            raise

    async def test_basic_connection(self):
        """Test basic connectivity with a simple request"""
        logger.info("\n=== Testing Basic Connection ===")
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Hello, can you respond with 'Connection successful'?"}],
                max_tokens=20,
                temperature=0
            )
            
            result = response.choices[0].message.content
            logger.info(f"✅ Basic connection test successful!")
            logger.info(f"Response: {result}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Basic connection test failed: {e}")
            self._analyze_error(e)
            return False

    async def test_synthesis_simulation(self):
        """Test the synthesis functionality similar to the actual application"""
        logger.info("\n=== Testing Synthesis Simulation ===")
        try:
            test_prompt = """Analyze and synthesize the following search results for the query: "test query"

WIKIPEDIA RESULTS:
1. Test Article
   This is a test snippet for debugging Azure OpenAI integration.
   Source: https://example.com

Please provide a comprehensive summary that:
1. Identifies key themes and patterns across sources
2. Highlights the most important information
3. Notes any conflicting information
4. Provides actionable insights
5. Maintains objectivity and cites sources appropriately

Synthesis:"""

            logger.info(f"Making synthesis call with prompt length: {len(test_prompt)}")
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful research assistant that synthesizes information from multiple sources."},
                    {"role": "user", "content": test_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            logger.info(f"✅ Synthesis test successful!")
            logger.info(f"Response length: {len(result)} characters")
            logger.info(f"Response preview: {result[:200]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Synthesis test failed: {e}")
            self._analyze_error(e)
            return False

    async def test_different_api_versions(self):
        """Test different API versions to see if version is the issue"""
        logger.info("\n=== Testing Different API Versions ===")
        versions_to_test = [
            "2024-12-01-preview",
            "2024-02-01", 
            "2023-12-01-preview",
            "2023-05-15"
        ]
        
        for version in versions_to_test:
            try:
                logger.info(f"Testing API version: {version}")
                test_client = AsyncAzureOpenAI(
                    api_key=self.api_key,
                    api_version=version,
                    azure_endpoint=self.endpoint
                )
                
                response = await test_client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=10
                )
                
                logger.info(f"✅ API version {version} works!")
                return version
                
            except Exception as e:
                logger.info(f"❌ API version {version} failed: {str(e)[:100]}...")
                
        logger.error("❌ No API versions worked")
        return None

    def _analyze_error(self, error):
        """Analyze the error to provide specific guidance"""
        error_str = str(error)
        
        if "401" in error_str:
            if "subscription key" in error_str.lower():
                logger.error("🔍 DIAGNOSIS: Invalid subscription key")
                logger.error("   - Check if your Azure OpenAI API key is correct")
                logger.error("   - Verify the key hasn't expired")
                logger.error("   - Ensure you're using the correct key for this resource")
            elif "endpoint" in error_str.lower():
                logger.error("🔍 DIAGNOSIS: Invalid endpoint")
                logger.error("   - Check if your Azure OpenAI endpoint URL is correct")
                logger.error("   - Verify the resource exists and is accessible")
            else:
                logger.error("🔍 DIAGNOSIS: Authentication error (401)")
                logger.error("   - Could be invalid credentials or wrong configuration")
                
        elif "404" in error_str:
            logger.error("🔍 DIAGNOSIS: Resource not found (404)")
            logger.error("   - Check if the deployment name is correct")
            logger.error(f"   - Verify '{self.deployment_name}' exists in your Azure OpenAI resource")
            logger.error("   - Check if the endpoint URL is correct")
            
        elif "429" in error_str:
            logger.error("🔍 DIAGNOSIS: Rate limit exceeded (429)")
            logger.error("   - Your Azure OpenAI resource may have hit rate limits")
            logger.error("   - Wait a moment and try again")
            
        elif "403" in error_str:
            logger.error("🔍 DIAGNOSIS: Forbidden (403)")
            logger.error("   - Your subscription may not have access to this resource")
            logger.error("   - Check your Azure permissions")
            
        else:
            logger.error(f"🔍 DIAGNOSIS: Other error: {error_str}")

async def main():
    """Run all tests"""
    print("🚀 Starting Local Azure OpenAI Connection Tests...")
    print("=" * 60)
    
    try:
        # Initialize tester
        tester = LocalAzureOpenAITest()
        
        # Run tests
        basic_success = await tester.test_basic_connection()
        
        if basic_success:
            synthesis_success = await tester.test_synthesis_simulation()
        else:
            # Try different API versions if basic connection fails
            working_version = await tester.test_different_api_versions()
            if working_version:
                logger.info(f"\n🎉 Found working API version: {working_version}")
                logger.info("Consider updating your AZURE_OPENAI_API_VERSION environment variable")
        
        print("\n" + "=" * 60)
        if basic_success:
            print("🎉 LOCAL TEST RESULT: Azure OpenAI connection works locally!")
            print("   This suggests the issue might be with Render's environment configuration.")
        else:
            print("❌ LOCAL TEST RESULT: Azure OpenAI connection fails locally too.")
            print("   This suggests the issue is with the Azure OpenAI configuration itself.")
            
    except Exception as e:
        logger.error(f"Test setup failed: {e}")
        print(f"\n❌ TEST SETUP FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
