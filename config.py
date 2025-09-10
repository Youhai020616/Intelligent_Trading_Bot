"""
Configuration management for the Intelligent Trading Bot system.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Central configuration class for the trading bot system."""
    
    def __init__(self):
        self.config = self._load_config()
        self._ensure_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables with defaults."""
        return {
            # Directory settings
            "results_dir": os.getenv("RESULTS_DIR", "./results"),
            "data_cache_dir": os.getenv("DATA_CACHE_DIR", "./data_cache"),
            "memory_db_path": os.getenv("MEMORY_DB_PATH", "./memory_db"),
            "log_file": os.getenv("LOG_FILE", "./logs/trading_bot.log"),
            
            # LLM settings
            "llm_provider": "openai",
            "deep_think_llm": os.getenv("DEEP_THINK_LLM", "gpt-4o"),
            "quick_think_llm": os.getenv("QUICK_THINK_LLM", "gpt-4o-mini"),
            "backend_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1")),
            
            # Debate and discussion settings
            "max_debate_rounds": int(os.getenv("MAX_DEBATE_ROUNDS", "2")),
            "max_risk_discuss_rounds": int(os.getenv("MAX_RISK_DISCUSS_ROUNDS", "1")),
            "max_recur_limit": int(os.getenv("MAX_RECUR_LIMIT", "100")),
            
            # Tool settings
            "online_tools": os.getenv("ONLINE_TOOLS", "true").lower() == "true",
            "use_cache": os.getenv("USE_CACHE", "true").lower() == "true",
            
            # API Keys
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "finnhub_api_key": os.getenv("FINNHUB_API_KEY"),
            "tavily_api_key": os.getenv("TAVILY_API_KEY"),
            "langsmith_api_key": os.getenv("LANGSMITH_API_KEY"),
            
            # LangSmith settings
            "langsmith_tracing": os.getenv("LANGSMITH_TRACING", "true").lower() == "true",
            "langsmith_project": os.getenv("LANGSMITH_PROJECT", "Intelligent-Trading-Bot"),
            
            # Logging
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
        }
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.config["results_dir"],
            self.config["data_cache_dir"],
            self.config["memory_db_path"],
            Path(self.config["log_file"]).parent,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to config."""
        return self.config[key]
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present."""
        required_keys = {
            "openai_api_key": "OpenAI API Key",
            "finnhub_api_key": "Finnhub API Key", 
            "tavily_api_key": "Tavily API Key"
        }
        
        validation_results = {}
        for key, description in required_keys.items():
            value = self.config.get(key)
            validation_results[description] = bool(value and value.strip())
        
        return validation_results
    
    def setup_langsmith(self):
        """Setup LangSmith environment variables if configured."""
        if self.config.get("langsmith_api_key"):
            os.environ["LANGSMITH_API_KEY"] = self.config["langsmith_api_key"]
            
        if self.config.get("langsmith_tracing"):
            os.environ["LANGSMITH_TRACING"] = "true"
            
        if self.config.get("langsmith_project"):
            os.environ["LANGSMITH_PROJECT"] = self.config["langsmith_project"]

# Global configuration instance
config = Config()
