#!/usr/bin/env python3
"""
Test script to query each LLM with "test" prompt.
"""

import asyncio
import os
from dotenv import load_dotenv
from generation.llm_manager import LLMManager
from config.settings import Settings

# Load environment variables from both .env and api-keys.txt files
load_dotenv()

# Load from api-keys.txt if it exists (fallback for benchmark.py compatibility)
if os.path.exists("api-keys.txt"):
    with open("api-keys.txt", "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                value = value.strip('"')
                os.environ[key] = value

# Ensure Gemini API key is properly set
if os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

async def test_all_llms():
    """Test each LLM with a simple 'test' query."""
    
    # Initialize settings
    settings = Settings()
    
    # Initialize LLM manager
    llm_manager = LLMManager(settings.models)
    
    # Check API keys
    print("API Key Status:")
    key_status = llm_manager.validate_api_keys()
    for provider, status in key_status.items():
        print(f"  {provider}: {'✓' if status else '✗'}")
    print()
    
    # Test prompt
    test_prompt = "test"
    
    print(f"Testing all models with prompt: '{test_prompt}'")
    print("-" * 50)
    
    for model in settings.models:
        print(f"\nTesting: {model['name']} ({model['model']})")
        print(f"Provider: {model['provider']}")
        
        try:
            result = await llm_manager.generate_essay(
                prompt=test_prompt,
                model_config=model,
                metadata={'test': True}
            )
            
            if result:
                print(f"✓ Success!")
                print(f"  Response: {result['content'][:100]}...")
                print(f"  Word count: {result['word_count']}")
            else:
                print("✗ Failed - returned None")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "-" * 50)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_all_llms())