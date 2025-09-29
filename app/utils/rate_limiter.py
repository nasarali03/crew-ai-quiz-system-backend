"""
Advanced rate limiter utility for Groq API calls with token tracking and retry mechanisms
"""

import asyncio
import time
import random
from typing import Dict, Any, Optional
import logging
from app.config.model_config import get_rate_limit_config, get_recommended_model

class AdvancedGroqRateLimiter:
    def __init__(self, model_name: str = None):
        """
        Initialize advanced rate limiter for Groq API
        
        Args:
            model_name: Groq model name (default: auto-detect)
        """
        self.model_name = model_name or get_recommended_model()
        config = get_rate_limit_config(self.model_name)
        
        self.tokens_per_minute = config["tokens_per_minute"]
        self.requests_per_minute = config["requests_per_minute"]
        
        # Token tracking
        self.token_usage = []  # List of (timestamp, tokens_used)
        self.request_times = []  # List of request timestamps
        self.lock = asyncio.Lock()
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0
        self.max_delay = 60.0
        
        # Safety margins
        self.token_safety_margin = 0.8  # Use only 80% of limit
        self.request_safety_margin = 0.9  # Use only 90% of request limit
        
        print(f"🚀 Advanced Rate Limiter initialized for {self.model_name}")
        print(f"📊 Limits: {self.tokens_per_minute} TPM, {self.requests_per_minute} RPM")
        
    async def wait_if_needed(self, estimated_tokens: int = 1000):
        """
        Advanced wait mechanism with safety margins and retry logic
        
        Args:
            estimated_tokens: Estimated tokens for the next request
        """
        async with self.lock:
            current_time = time.time()
            
            # Clean old entries (older than 1 minute)
            self.token_usage = [(t, tokens) for t, tokens in self.token_usage if current_time - t < 60]
            self.request_times = [t for t in self.request_times if current_time - t < 60]
            
            # Calculate current usage
            total_tokens = sum(tokens for _, tokens in self.token_usage)
            current_requests = len(self.request_times)
            
            # Apply safety margins
            safe_token_limit = int(self.tokens_per_minute * self.token_safety_margin)
            safe_request_limit = int(self.requests_per_minute * self.request_safety_margin)
            
            # Check if we need to wait
            wait_time = 0
            
            # Token limit check
            if total_tokens + estimated_tokens > safe_token_limit:
                if self.token_usage:
                    oldest_token_time = min(t for t, _ in self.token_usage)
                    wait_time = max(wait_time, 60 - (current_time - oldest_token_time))
                else:
                    wait_time = max(wait_time, 1.0)  # Minimum 1 second wait
            
            # Request limit check
            if current_requests >= safe_request_limit:
                if self.request_times:
                    oldest_request_time = min(self.request_times)
                    wait_time = max(wait_time, 60 - (current_time - oldest_request_time))
                else:
                    wait_time = max(wait_time, 1.0)
            
            # Wait if necessary
            if wait_time > 0:
                print(f"⏳ Rate limit protection: Waiting {wait_time:.1f}s")
                print(f"📊 Current usage: {total_tokens}/{safe_token_limit} tokens, {current_requests}/{safe_request_limit} requests")
                await asyncio.sleep(wait_time)
                
                # Clean up after waiting
                current_time = time.time()
                self.token_usage = [(t, tokens) for t, tokens in self.token_usage if current_time - t < 60]
                self.request_times = [t for t in self.request_times if current_time - t < 60]
            
            # Record this request
            self.token_usage.append((current_time, estimated_tokens))
            self.request_times.append(current_time)
            
            # Add jittered delay between requests to avoid thundering herd
            delay = 0.5 + random.uniform(0, 0.5)
            await asyncio.sleep(delay)
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with automatic retry on rate limit errors
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if "rate_limit" in str(e).lower() or "rate limit" in str(e).lower():
                    if attempt < self.max_retries:
                        # Exponential backoff with jitter
                        delay = min(self.base_delay * (2 ** attempt) + random.uniform(0, 1), self.max_delay)
                        print(f"🔄 Rate limit hit, retrying in {delay:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        print(f"❌ Max retries exceeded for rate limit")
                        raise
                else:
                    # Re-raise non-rate-limit errors immediately
                    raise
        
        raise Exception("Unexpected retry loop exit")

# Global rate limiter instance
rate_limiter = AdvancedGroqRateLimiter()

async def apply_rate_limit(estimated_tokens: int = 1000):
    """Apply advanced rate limiting before making API calls"""
    await rate_limiter.wait_if_needed(estimated_tokens)

async def execute_with_rate_limit(func, *args, estimated_tokens: int = 1000, **kwargs):
    """Execute function with automatic rate limiting and retry"""
    await apply_rate_limit(estimated_tokens)
    return await rate_limiter.execute_with_retry(func, *args, **kwargs)
