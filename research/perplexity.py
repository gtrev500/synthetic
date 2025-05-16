import os
import aiohttp
import asyncio
from typing import Dict, List, Optional

class PerplexityClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
    
    async def search(self, query: str, model: str = "sonar") -> Dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant helping gather diverse perspectives and information."
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
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
    
    def _parse_response(self, response: Dict) -> Dict:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract structured information
        facts = []
        quotes = []
        sources = []
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith('facts:') or line.lower().startswith('key findings:'):
                current_section = 'facts'
            elif line.lower().startswith('quotes:') or line.lower().startswith('expert opinions:'):
                current_section = 'quotes'
            elif line.lower().startswith('sources:') or line.lower().startswith('references:'):
                current_section = 'sources'
            elif line.startswith('- ') or line.startswith('• '):
                if current_section == 'facts':
                    facts.append(line[2:])
                elif current_section == 'quotes':
                    quotes.append(line[2:])
                elif current_section == 'sources':
                    sources.append(line[2:])
        
        return {
            'facts': facts,
            'quotes': quotes,
            'sources': sources,
            'raw_content': content
        }