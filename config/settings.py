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
            raise FileNotFoundError(f"Settings file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
