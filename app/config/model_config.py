"""
Model configuration for different Groq models and their limits
"""

import os
from typing import Dict, Any

# Groq model configurations with their rate limits
GROQ_MODELS = {
    "llama-3.1-8b-instant": {
        "tokens_per_minute": 6000,
        "requests_per_minute": 30,
        "cost_per_token": 0.0001,  # Approximate
        "speed": "instant",
        "quality": "good",
        "recommended_for": "development"
    },
    "llama-3.1-70b-versatile": {
        "tokens_per_minute": 12000,
        "requests_per_minute": 30,
        "cost_per_token": 0.0002,  # Approximate
        "speed": "fast",
        "quality": "excellent",
        "recommended_for": "production"
    },
    "llama-3.1-8b-versatile": {
        "tokens_per_minute": 6000,
        "requests_per_minute": 30,
        "cost_per_token": 0.0001,  # Approximate
        "speed": "fast",
        "quality": "good",
        "recommended_for": "development"
    },
    "mixtral-8x7b-32768": {
        "tokens_per_minute": 30000,
        "requests_per_minute": 30,
        "cost_per_token": 0.0003,  # Approximate
        "speed": "fast",
        "quality": "excellent",
        "recommended_for": "high_volume"
    }
}

def get_model_config(model_name: str) -> Dict[str, Any]:
    """Get configuration for a specific model"""
    return GROQ_MODELS.get(model_name, GROQ_MODELS["llama-3.1-8b-instant"])

def get_recommended_model() -> str:
    """Get recommended model based on current usage"""
    # For production, recommend the 70b model for better quality
    # For development/testing, use the 8b instant model
    return "llama-3.1-70b-versatile" if os.getenv("ENVIRONMENT") == "production" else "llama-3.1-8b-instant"

def get_rate_limit_config(model_name: str) -> Dict[str, int]:
    """Get rate limit configuration for a model"""
    config = get_model_config(model_name)
    return {
        "tokens_per_minute": config["tokens_per_minute"],
        "requests_per_minute": config["requests_per_minute"]
    }
