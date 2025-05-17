import asyncio
import hashlib
import time
import random
import logging
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

import litellm
from litellm import acompletion, RateLimitError

from .token_calculator import get_model_token_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self, models_config: List[Dict], base_tokens: int = 1500):
        self.models = models_config
        self.base_tokens = base_tokens
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Configure litellm
        litellm.drop_params = True
        litellm.set_verbose = True
        
        # Provider backoff state: {provider: {'backoff_seconds': float, 'last_failure': timestamp}}
        self.provider_backoff = {}
        self.max_backoff = 300  # 5 minutes max
        self.initial_backoff = 1  # Start with 1 second
        self.backoff_multiplier = 2  # Double on each retry
        
        logger.info(f"Initialized LLMManager with {len(models_config)} models")
    
    def _get_provider_backoff_time(self, provider: str) -> float:
        """Calculate current backoff time for a provider."""
        if provider not in self.provider_backoff:
            return 0
        
        state = self.provider_backoff[provider]
        time_since_failure = time.time() - state['last_failure']
        
        # If enough time has passed, reset the backoff
        if time_since_failure > state['backoff_seconds'] * 2:
            del self.provider_backoff[provider]
            return 0
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 0.1) * state['backoff_seconds']
        return state['backoff_seconds'] + jitter
    
    def _update_provider_backoff(self, provider: str):
        """Update backoff state for a provider after a rate limit error."""
        if provider not in self.provider_backoff:
            self.provider_backoff[provider] = {
                'backoff_seconds': self.initial_backoff,
                'last_failure': time.time()
            }
        else:
            # Exponential backoff with max limit
            current_backoff = self.provider_backoff[provider]['backoff_seconds']
            new_backoff = min(current_backoff * self.backoff_multiplier, self.max_backoff)
            self.provider_backoff[provider] = {
                'backoff_seconds': new_backoff,
                'last_failure': time.time()
            }
    
    async def generate_essay(self, prompt: str, model_config: Dict, metadata: Dict) -> Optional[Dict]:
        """Generate a single essay using specified model with rate limit handling."""
        provider = model_config.get('provider', 'unknown')
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                # Check if we need to wait due to backoff
                backoff_time = self._get_provider_backoff_time(provider)
                if backoff_time > 0:
                    logger.warning(f"Provider {provider} is backing off for {backoff_time:.2f} seconds")
                    await asyncio.sleep(backoff_time)
                
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
                if attempt == 0:  # Only log on first attempt
                    logger.debug(f"Token config for {model_config['name']}: max_tokens={token_config['max_tokens']}, "
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
                    logger.error(f"LLM {model_config['name']} returned None content for prompt")
                    logger.debug(f"Failing prompt: {prompt[:200]}...")
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
                
            except RateLimitError as e:
                logger.warning(f"Rate limit error for {model_config['name']} (provider: {provider}): {e}")
                self._update_provider_backoff(provider)
                
                if attempt < max_retries - 1:
                    backoff_time = self._get_provider_backoff_time(provider)
                    logger.info(f"Retrying after {backoff_time:.2f} seconds (attempt {attempt + 1}/{max_retries})")
                else:
                    logger.error(f"Max retries exceeded for {model_config['name']} after {max_retries} attempts")
                    return None
                    
            except Exception as e:
                logger.error(f"Error generating essay with {model_config['name']}: {e}", exc_info=True)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying after error (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(1)  # Brief pause before retry
                else:
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
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                prompt_index = i % len(prompts)
                model_index = i // len(prompts)
                logger.error(f"Task exception for prompt {prompt_index}, model {models[model_index]['name']}: {result}")
                continue
            if result is not None:
                essays.append(result)
        
        logger.info(f"Generated {len(essays)} essays out of {len(tasks)} attempted")
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
    
    def get_backoff_status(self) -> Dict[str, Dict]:
        """Get current backoff status for all providers."""
        status = {}
        for provider, state in self.provider_backoff.items():
            time_since_failure = time.time() - state['last_failure']
            remaining_backoff = max(0, state['backoff_seconds'] - time_since_failure)
            
            status[provider] = {
                'backoff_seconds': state['backoff_seconds'],
                'time_since_failure': time_since_failure,
                'remaining_backoff': remaining_backoff,
                'is_backed_off': remaining_backoff > 0
            }
        
        return status