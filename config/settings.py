import os
import yaml
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

class Settings:
    def __init__(self, config_path: str = None):
        load_dotenv()
        
        self.config_path = config_path or "config/settings.yaml"
        self.config = self._load_config()
        
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        
        # Paths
        self.db_path = self.config.get("database", {}).get("path", "synthetic_essays.db")
        self.output_dir = self.config.get("output", {}).get("directory", "output")
        
        # Model configurations
        self.models = self.config.get("models", [])
        
        # Generation settings
        self.default_num_essays = self.config.get("generation", {}).get("default_num_essays", 60)
        self.batch_size = self.config.get("generation", {}).get("batch_size", 5)
        self.base_max_tokens = self.config.get("generation", {}).get("base_max_tokens", 1500)
        
    def _load_config(self) -> Dict:
        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_default_config(self) -> Dict:
        default_config = {
            "database": {
                "path": "synthetic_essays.db"
            },
            "output": {
                "directory": "output"
            },
            "models": [
                {
                    "name": "ChatGPT 4o",
                    "model": "gpt-4o",
                    "provider": "openai",
                    "temperature": 0.8,
                    "max_tokens": 1500
                },
                {
                    "name": "Gemini 2.5 Pro",
                    "model": "gemini-2.5-pro-preview",
                    "provider": "gemini",
                    "temperature": 0.8,
                    "max_tokens": 1500
                },
                {
                    "name": "Claude 3.7 Sonnet",
                    "model": "claude-3-7-sonnet",
                    "provider": "anthropic",
                    "temperature": 1.0,
                    "max_tokens": 1500
                }
            ],
            "generation": {
                "default_num_essays": 60,
                "batch_size": 5,
                "base_max_tokens": 1500
            },
            "research": {
                "num_seeds": 10,
                "perplexity_model": "llama-2-70b"
            }
        }
        
        # Create config directory if it doesn't exist
        Path(os.path.dirname(self.config_path)).mkdir(exist_ok=True)
        
        # Save default config
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return default_config