"""
Token calculation utilities for managing model-specific token limits.
"""

def calculate_max_tokens(base_tokens: int, multiplier: float, min_tokens: int = 500, max_tokens: int = 10000) -> int:
    """
    Calculate the maximum tokens for a model based on base value and multiplier.
    
    Args:
        base_tokens: Base token count
        multiplier: Model-specific multiplier
        min_tokens: Minimum allowed tokens
        max_tokens: Maximum allowed tokens
    
    Returns:
        Calculated token limit within bounds
    """
    calculated = int(base_tokens * multiplier)
    return max(min_tokens, min(calculated, max_tokens))

def estimate_words_from_tokens(tokens: int, provider: str) -> int:
    """
    Estimate word count from token count based on provider.
    
    Different providers have different tokenization strategies:
    - OpenAI: ~1.3 tokens per word
    - Gemini: ~1.3 tokens per word (but includes thinking tokens)
    - Anthropic: ~1.4 tokens per word
    
    Args:
        tokens: Number of tokens
        provider: Model provider name
    
    Returns:
        Estimated word count
    """
    ratios = {
        "openai": 1.3,
        "gemini": 1.3,
        "anthropic": 1.4,
    }
    
    ratio = ratios.get(provider.lower(), 1.3)  # Default to OpenAI ratio
    
    # For Gemini, account for thinking tokens (roughly 50% of total)
    if provider.lower() == "gemini":
        tokens = tokens * 0.5
    
    return int(tokens / ratio)

def estimate_tokens_from_words(words: int, provider: str) -> int:
    """
    Estimate token count from word count based on provider.
    
    Args:
        words: Number of words
        provider: Model provider name
    
    Returns:
        Estimated token count
    """
    ratios = {
        "openai": 1.3,
        "gemini": 1.3,
        "anthropic": 1.4,
    }
    
    ratio = ratios.get(provider.lower(), 1.3)
    tokens = int(words * ratio)
    
    # For Gemini, account for thinking tokens overhead
    if provider.lower() == "gemini":
        tokens = int(tokens * 2)  # Double for thinking overhead
    
    return tokens

def get_model_token_config(model_config: dict, base_tokens: int) -> dict:
    """
    Get complete token configuration for a model.
    
    Args:
        model_config: Model configuration dictionary
        base_tokens: Base token count from settings
    
    Returns:
        Dictionary with token configuration
    """
    multiplier = model_config.get("token_multiplier", 1.0)
    max_tokens = model_config.get("max_tokens")
    
    # If max_tokens is explicitly set, use it
    if max_tokens is not None:
        calculated_tokens = max_tokens
    else:
        calculated_tokens = calculate_max_tokens(base_tokens, multiplier)
    
    provider = model_config.get("provider", "openai")
    estimated_words = estimate_words_from_tokens(calculated_tokens, provider)
    
    return {
        "max_tokens": calculated_tokens,
        "base_tokens": base_tokens,
        "multiplier": multiplier,
        "estimated_words": estimated_words,
        "provider": provider
    }