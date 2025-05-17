import asyncio
import time
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from generation.llm_manager import LLMManager
from litellm import RateLimitError

class TestRateLimitBackoff:
    """Test the exponential backoff mechanism for rate limit errors."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.models_config = [
            {
                "model": "openai/gpt-4o",
                "name": "ChatGPT 4o",
                "provider": "openai",
                "temperature": 0.8
            },
            {
                "model": "gemini/gemini-2.5-pro",
                "name": "Gemini 2.5",
                "provider": "gemini",
                "temperature": 0.8
            }
        ]
        self.llm_manager = LLMManager(self.models_config)
    
    def test_backoff_state_initialization(self):
        """Test that backoff state is properly initialized."""
        assert self.llm_manager.provider_backoff == {}
        assert self.llm_manager.initial_backoff == 1
        assert self.llm_manager.max_backoff == 300
        assert self.llm_manager.backoff_multiplier == 2
    
    def test_update_provider_backoff(self):
        """Test that provider backoff is updated correctly."""
        # First failure
        self.llm_manager._update_provider_backoff("openai")
        assert "openai" in self.llm_manager.provider_backoff
        assert self.llm_manager.provider_backoff["openai"]["backoff_seconds"] == 1
        
        # Second failure - exponential increase
        self.llm_manager._update_provider_backoff("openai")
        assert self.llm_manager.provider_backoff["openai"]["backoff_seconds"] == 2
        
        # Third failure
        self.llm_manager._update_provider_backoff("openai")
        assert self.llm_manager.provider_backoff["openai"]["backoff_seconds"] == 4
    
    def test_max_backoff_limit(self):
        """Test that backoff doesn't exceed the maximum."""
        provider = "openai"
        
        # Simulate many failures
        for _ in range(20):
            self.llm_manager._update_provider_backoff(provider)
        
        # Should not exceed max_backoff
        assert self.llm_manager.provider_backoff[provider]["backoff_seconds"] <= self.llm_manager.max_backoff
    
    def test_get_provider_backoff_time(self):
        """Test getting backoff time for a provider."""
        # No backoff for new provider
        assert self.llm_manager._get_provider_backoff_time("openai") == 0
        
        # After failure, should have backoff
        self.llm_manager._update_provider_backoff("openai")
        backoff_time = self.llm_manager._get_provider_backoff_time("openai")
        
        # Should be around 1 second with some jitter
        assert 0.9 < backoff_time < 1.2
    
    def test_backoff_reset_after_time(self):
        """Test that backoff resets after sufficient time has passed."""
        provider = "openai"
        
        # Set up a backoff
        self.llm_manager._update_provider_backoff(provider)
        assert provider in self.llm_manager.provider_backoff
        
        # Simulate time passing
        original_time = self.llm_manager.provider_backoff[provider]["last_failure"]
        self.llm_manager.provider_backoff[provider]["last_failure"] = original_time - 10
        
        # Should reset backoff
        backoff_time = self.llm_manager._get_provider_backoff_time(provider)
        assert backoff_time == 0
        assert provider not in self.llm_manager.provider_backoff
    
    @pytest.mark.asyncio
    @patch('generation.llm_manager.acompletion')
    @patch('generation.llm_manager.get_model_token_config')
    async def test_rate_limit_retry(self, mock_token_config, mock_acompletion):
        """Test that rate limit errors trigger retries with backoff."""
        # Mock token config
        mock_token_config.return_value = {
            'max_tokens': 1500,
            'estimated_words': 1000,
            'provider': 'openai'
        }
        
        # Create a mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test essay content"
        
        # Create the RateLimitError with required arguments
        rate_limit_error = RateLimitError(
            message="Rate limit exceeded",
            llm_provider="openai",
            model="gpt-4o"
        )
        
        # First call fails with rate limit, second succeeds
        mock_acompletion.side_effect = [
            rate_limit_error,
            mock_response
        ]
        
        model_config = self.models_config[0]
        result = await self.llm_manager.generate_essay(
            "Test prompt", 
            model_config, 
            {"assignment": "test"}
        )
        
        # Should succeed after retry
        assert result is not None
        assert result['content'] == "Test essay content"
        
        # Should have called twice
        assert mock_acompletion.call_count == 2
        
        # Should have updated backoff state
        assert "openai" in self.llm_manager.provider_backoff
    
    @pytest.mark.asyncio
    @patch('generation.llm_manager.acompletion')
    @patch('generation.llm_manager.get_model_token_config')
    async def test_max_retries_exceeded(self, mock_token_config, mock_acompletion):
        """Test that max retries are respected."""
        # Mock token config
        mock_token_config.return_value = {
            'max_tokens': 1500,
            'estimated_words': 1000,
            'provider': 'openai'
        }
        
        # Always fail with rate limit
        rate_limit_error = RateLimitError(
            message="Rate limit exceeded",
            llm_provider="openai",
            model="gpt-4o"
        )
        mock_acompletion.side_effect = rate_limit_error
        
        model_config = self.models_config[0]
        result = await self.llm_manager.generate_essay(
            "Test prompt", 
            model_config, 
            {"assignment": "test"}
        )
        
        # Should fail after max retries
        assert result is None
        
        # Should have tried 5 times
        assert mock_acompletion.call_count == 5
    
    @pytest.mark.asyncio
    @patch('asyncio.sleep')
    @patch('generation.llm_manager.acompletion')
    @patch('generation.llm_manager.get_model_token_config')
    async def test_concurrent_provider_backoff(self, mock_token_config, mock_acompletion, mock_sleep):
        """Test that different providers have independent backoff states."""
        # Mock token config
        def token_config_side_effect(model_config, base_tokens):
            return {
                'max_tokens': 1500,
                'estimated_words': 1000,
                'provider': model_config['provider']
            }
        mock_token_config.side_effect = token_config_side_effect
        
        # Mock sleep to not actually wait
        mock_sleep.return_value = None
        
        # Create success responses
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test essay content"
        
        # Create the RateLimitError for OpenAI
        rate_limit_error = RateLimitError(
            message="Rate limit exceeded",
            llm_provider="openai",
            model="gpt-4o"
        )
        
        # Set up different behaviors for different providers
        call_count = 0
        def acompletion_side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            
            # OpenAI fails once, then succeeds
            if kwargs['model'] == 'openai/gpt-4o' and call_count == 1:
                raise rate_limit_error
            
            # Gemini always succeeds
            return mock_response
        
        mock_acompletion.side_effect = acompletion_side_effect
        
        # Test both providers concurrently
        tasks = [
            self.llm_manager.generate_essay("Test prompt", self.models_config[0], {}),
            self.llm_manager.generate_essay("Test prompt", self.models_config[1], {})
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Both should succeed
        assert results[0] is not None
        assert results[1] is not None
        
        # Only OpenAI should have backoff state
        assert "openai" in self.llm_manager.provider_backoff
        assert "gemini" not in self.llm_manager.provider_backoff
    
    def test_get_backoff_status(self):
        """Test the backoff status reporting method."""
        # Initially no backoff
        status = self.llm_manager.get_backoff_status()
        assert status == {}
        
        # Add backoff for openai
        self.llm_manager._update_provider_backoff("openai")
        
        # Check status
        status = self.llm_manager.get_backoff_status()
        assert "openai" in status
        assert status["openai"]["backoff_seconds"] == 1
        assert status["openai"]["is_backed_off"] == True
        assert status["openai"]["remaining_backoff"] > 0
        
        # Simulate time passing
        self.llm_manager.provider_backoff["openai"]["last_failure"] -= 2
        
        # Should no longer be backed off
        status = self.llm_manager.get_backoff_status()
        assert status["openai"]["is_backed_off"] == False
        assert status["openai"]["remaining_backoff"] == 0