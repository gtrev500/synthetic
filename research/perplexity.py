import os
import aiohttp
import asyncio
import json
from typing import Dict, List, Optional
from pydantic import ValidationError

from research.models import ResearchData


class PerplexityClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
    
    async def search(self, query: str, model: str = "sonar") -> Dict:
        """
        Search using Perplexity API with structured JSON output
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Get the JSON schema from the Pydantic model
        response_schema = ResearchData.model_json_schema()
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant helping gather diverse perspectives and information. Provide structured JSON output adhering to the specified schema."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "schema": response_schema
                }
            },
            "max_tokens": 4000  # Ensure enough tokens for comprehensive responses
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Perplexity API error: {response.status} - {error_text}")
    
    def parse_structured_response(self, response: Dict) -> Dict:
        """
        Parse the structured JSON response from Perplexity API
        """
        try:
            # Extract the content from the response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # Parse and validate the JSON using Pydantic
            research_data = ResearchData.model_validate_json(content)
            
            return {
                'facts': research_data.facts,
                'quotes': research_data.quotes,
                'sources': research_data.sources,
                'raw_content': content
            }
        except ValidationError as e:
            print(f"JSON validation error: {e}")
            # Return fallback data if validation fails
            return {
                'facts': ["Unable to extract facts from research"],
                'quotes': ["Unable to extract quotes from research"],
                'sources': ["Unable to extract sources from research"],
                'raw_content': content if 'content' in locals() else ""
            }
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            # Return fallback data if JSON parsing fails
            return {
                'facts': ["Error parsing research data"],
                'quotes': ["Error parsing research data"],
                'sources': ["Error parsing research data"],
                'raw_content': response.get("choices", [{}])[0].get("message", {}).get("content", "")
            }
            
    def _parse_response(self, response: Dict) -> Dict:
        """
        Legacy parsing method - now redirects to structured parsing
        """
        return self.parse_structured_response(response)