import asyncio
import hashlib
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

import litellm
from litellm import acompletion

from .token_calculator import get_model_token_config

class LLMManager:
    def __init__(self, models_config: List[Dict], base_tokens: int = 1500):
        self.models = models_config
        self.base_tokens = base_tokens
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Configure litellm
        litellm.drop_params = True
        litellm.set_verbose = True
    
    async def generate_essay(self, prompt: str, model_config: Dict, metadata: Dict) -> Optional[Dict]:
        """Generate a single essay using specified model."""
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": "You are an experienced student writer. Follow the instructions precisely to create an authentic academic essay."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Calculate model-specific token configuration
            token_config = get_model_token_config(model_config, self.base_tokens)
            
            # Log token configuration for debugging
            print(f"Token config for {model_config['name']}: max_tokens={token_config['max_tokens']}, "
                  f"estimated_words={token_config['estimated_words']}, provider={token_config['provider']}")
            
            # Model-specific adjustments
            kwargs = {
                "model": model_config["model"],
                "messages": messages,
                "temperature": model_config.get("temperature", 0.8),
                "max_tokens": token_config["max_tokens"]
            }
            
            # Add provider-specific parameters
            if model_config["provider"] == "anthropic" and "claude-3-7" in model_config["model"]:
                # Enable Claude's thinking mode if available
                if "temperature" in kwargs and kwargs["temperature"] == 1.0:
                    kwargs["reasoning_effort"] = "low"
            elif model_config["provider"] == "gemini":
                kwargs["reasoning_effort"] = "low"
            
            # Make the API call
            response = await acompletion(**kwargs)
            
            content = response.choices[0].message.content

            if content is None:
                print(f"LLM {model_config['name']} returned None content for prompt. Failing prompt:\n{prompt}")
                return None
            
            # Calculate prompt hash for tracking
            prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
            
            return {
                'content': content,
                'model_name': model_config['name'],
                'model_id': model_config['model'],
                'temperature': model_config.get('temperature', 0.8),
                'word_count': len(content.split()),
                'prompt_hash': prompt_hash,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"Error generating essay with {model_config['name']}: {e}")
            return None
    
    async def generate_batch(self, prompts: List[Dict], models: Optional[List[Dict]] = None) -> List[Dict]:
        """Generate essays for multiple prompts across multiple models."""
        if models is None:
            models = self.models
        
        tasks = []
        
        for prompt_data in prompts:
            prompt = prompt_data['prompt']
            metadata = prompt_data['metadata']
            
            for model_config in models:
                task = self.generate_essay(prompt, model_config, metadata)
                tasks.append(task)
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        essays = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Task exception: {result}")
                continue
            if result is not None:
                essays.append(result)
        
        return essays
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured."""
        import os
        
        key_status = {
            'openai': bool(os.getenv('OPENAI_API_KEY')),
            'anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
            'google': bool(os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')),
            'perplexity': bool(os.getenv('PERPLEXITY_API_KEY'))
        }
        
        return key_status