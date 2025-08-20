#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/emredinc/projects/deep-search/backend/venv/lib/python3.13/site-packages')

# Test imports
try:
    from models import SearchSource, SearchResult
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Models import failed: {e}")

try:
    from search_modules import ParallelSearchManager
    print("✅ Search modules imported successfully")
except Exception as e:
    print(f"❌ Search modules import failed: {e}")

try:
    from azure_openai_client import AzureOpenAIClient
    print("✅ Azure OpenAI client imported successfully")
except Exception as e:
    print(f"❌ Azure OpenAI client import failed: {e}")

try:
    import uvicorn
    print("✅ Uvicorn imported successfully")
except Exception as e:
    print(f"❌ Uvicorn import failed: {e}")

# Test basic functionality
async def test_search():
    try:
        manager = ParallelSearchManager()
        print("✅ Search manager created successfully")
        print(f"Available sources: {list(manager.modules.keys())}")
    except Exception as e:
        print(f"❌ Search manager creation failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_search())
