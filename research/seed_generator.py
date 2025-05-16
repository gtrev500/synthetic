import asyncio
from typing import List, Dict

from research.perplexity import PerplexityClient

class ResearchSeedGenerator:
    def __init__(self, api_key: str):
        self.client = PerplexityClient(api_key)
        
    async def generate_seeds(self, topic: str, num_seeds: int = 10) -> List[Dict]:
        angles = [
            f"current debates about {topic}",
            f"controversial aspects of {topic}",
            f"future implications of {topic}",
            f"historical context of {topic}",
            f"economic impacts of {topic}",
            f"social justice perspectives on {topic}",
            f"technological aspects of {topic}",
            f"environmental considerations of {topic}",
            f"cultural differences in {topic}",
            f"ethical dilemmas of {topic}",
            f"legal challenges surrounding {topic}",
            f"educational implications of {topic}"
        ]
        
        seeds = []
        tasks = []
        
        for angle in angles[:num_seeds]:
            task = self._generate_seed(angle, topic)
            tasks.append(task)
        
        seed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(seed_results):
            if isinstance(result, Exception):
                print(f"Error generating seed for angle '{angles[i]}': {result}")
                continue
            seeds.append(result)
        
        return seeds
    
    async def _generate_seed(self, angle: str, topic: str) -> Dict:
        query = f"""
        Research the following aspect of {topic}: {angle}
        
        Please provide:
        1. Key Facts: List 5-7 specific, relevant facts
        2. Expert Quotes: Include 2-3 quotes from experts or studies
        3. Sources: List credible sources and references
        
        Focus on providing diverse, specific information that would help a student write an essay.
        """
        
        try:
            response = await self.client.search(query)
            parsed_data = self.client._parse_response(response)
            
            return {
                'angle': angle,
                'topic': topic,
                'facts': parsed_data['facts'],
                'quotes': parsed_data['quotes'],
                'sources': parsed_data['sources']
            }
        except Exception as e:
            print(f"Error in research seed generation for '{angle}': {e}")
            # Return a basic seed structure even on failure
            return {
                'angle': angle,
                'topic': topic,
                'facts': [f"General fact about {angle}"],
                'quotes': [f"Expert opinion on {angle}"],
                'sources': ["Academic source"]
            }