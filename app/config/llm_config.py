"""
LLM Configuration for CrewAI Quiz System
Supports Gemini and Groq LLM providers
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class LLMConfig:
    """Configuration for LLM providers"""
    
    # Provider settings
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Default models
    GEMINI_MODEL = "gemini-pro"
    GROQ_MODEL = "llama3-8b-8192"  # Fast and efficient for quiz generation
    
    # Fallback settings
    ENABLE_FALLBACK = True
    FALLBACK_PROVIDER = "gemini" if GOOGLE_API_KEY else "groq"
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available LLM providers"""
        providers = []
        if cls.GOOGLE_API_KEY:
            providers.append("gemini")
        if cls.GROQ_API_KEY:
            providers.append("groq")
        return providers
    
    @classmethod
    def get_primary_provider(cls) -> str:
        """Get the primary LLM provider"""
        if cls.GOOGLE_API_KEY:
            return "gemini"
        elif cls.GROQ_API_KEY:
            return "groq"
        else:
            raise ValueError("No LLM API keys configured")
    
    @classmethod
    def get_provider_config(cls, provider: str) -> Dict[str, Any]:
        """Get configuration for specific provider"""
        configs = {
            "gemini": {
                "api_key": cls.GOOGLE_API_KEY,
                "model": cls.GEMINI_MODEL,
                "max_tokens": 2048,
                "temperature": 0.7
            },
            "groq": {
                "api_key": cls.GROQ_API_KEY,
                "model": cls.GROQ_MODEL,
                "max_tokens": 2048,
                "temperature": 0.7
            }
        }
        return configs.get(provider, {})
    
    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """Check if provider is available"""
        return provider in cls.get_available_providers()
