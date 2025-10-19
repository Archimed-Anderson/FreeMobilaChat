"""
Rate limiting utilities for API calls
Implements token bucket and sliding window rate limiting
"""

import asyncio
import time
from typing import Dict, Optional, Any
from collections import deque
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Async rate limiter using token bucket algorithm
    Ensures API calls don't exceed specified limits
    """
    
    def __init__(self, max_calls: int, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds (default: 60s)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        self.lock = asyncio.Lock()
        
        logger.info(f"Rate limiter initialized: {max_calls} calls per {time_window}s")
    
    async def acquire(self) -> None:
        """
        Acquire permission to make an API call
        Blocks if rate limit would be exceeded
        """
        async with self.lock:
            now = time.time()
            
            # Remove old calls outside the time window
            while self.calls and self.calls[0] <= now - self.time_window:
                self.calls.popleft()
            
            # Check if we can make a call
            if len(self.calls) >= self.max_calls:
                # Calculate how long to wait
                oldest_call = self.calls[0]
                wait_time = oldest_call + self.time_window - now
                
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    
                    # Remove the old call after waiting
                    if self.calls and self.calls[0] <= time.time() - self.time_window:
                        self.calls.popleft()
            
            # Record this call
            self.calls.append(time.time())
    
    def get_remaining_calls(self) -> int:
        """Get number of remaining calls in current window"""
        now = time.time()
        
        # Remove old calls
        while self.calls and self.calls[0] <= now - self.time_window:
            self.calls.popleft()
        
        return max(0, self.max_calls - len(self.calls))
    
    def get_reset_time(self) -> Optional[float]:
        """Get time when rate limit resets (Unix timestamp)"""
        if not self.calls:
            return None
        
        return self.calls[0] + self.time_window
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        now = time.time()
        
        # Clean old calls
        while self.calls and self.calls[0] <= now - self.time_window:
            self.calls.popleft()
        
        return {
            'max_calls': self.max_calls,
            'time_window': self.time_window,
            'current_calls': len(self.calls),
            'remaining_calls': self.get_remaining_calls(),
            'reset_time': self.get_reset_time(),
            'utilization_percent': (len(self.calls) / self.max_calls) * 100
        }


class MultiProviderRateLimiter:
    """
    Rate limiter for multiple API providers
    Manages different rate limits for different services
    """
    
    def __init__(self):
        """Initialize multi-provider rate limiter"""
        self.limiters: Dict[str, RateLimiter] = {}
        
        # Default rate limits for different providers
        self.default_limits = {
            'openai': {'max_calls': 60, 'time_window': 60},  # 60 calls per minute
            'mistral': {'max_calls': 30, 'time_window': 60},  # 30 calls per minute (free tier)
            'anthropic': {'max_calls': 50, 'time_window': 60},  # 50 calls per minute
        }
    
    def add_provider(self, provider: str, max_calls: int, time_window: int = 60):
        """
        Add a rate limiter for a specific provider
        
        Args:
            provider: Provider name
            max_calls: Maximum calls allowed
            time_window: Time window in seconds
        """
        self.limiters[provider] = RateLimiter(max_calls, time_window)
        logger.info(f"Added rate limiter for {provider}: {max_calls} calls per {time_window}s")
    
    def get_or_create_limiter(self, provider: str) -> RateLimiter:
        """
        Get existing limiter or create with default settings
        
        Args:
            provider: Provider name
            
        Returns:
            RateLimiter instance
        """
        if provider not in self.limiters:
            if provider in self.default_limits:
                limits = self.default_limits[provider]
                self.add_provider(provider, limits['max_calls'], limits['time_window'])
            else:
                # Default fallback
                self.add_provider(provider, 30, 60)
        
        return self.limiters[provider]
    
    async def acquire(self, provider: str) -> None:
        """
        Acquire permission for specific provider
        
        Args:
            provider: Provider name
        """
        limiter = self.get_or_create_limiter(provider)
        await limiter.acquire()
    
    def get_stats(self, provider: str = None) -> Dict[str, any]:
        """
        Get statistics for provider(s)
        
        Args:
            provider: Specific provider or None for all
            
        Returns:
            Statistics dictionary
        """
        if provider:
            if provider in self.limiters:
                return {provider: self.limiters[provider].get_stats()}
            else:
                return {provider: "Not configured"}
        else:
            return {
                name: limiter.get_stats() 
                for name, limiter in self.limiters.items()
            }


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts based on API responses
    Reduces rate when hitting limits, increases when successful
    """
    
    def __init__(self, initial_rate: int = 30, min_rate: int = 5, max_rate: int = 100):
        """
        Initialize adaptive rate limiter
        
        Args:
            initial_rate: Starting rate limit
            min_rate: Minimum rate limit
            max_rate: Maximum rate limit
        """
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.limiter = RateLimiter(initial_rate, 60)
        self.consecutive_successes = 0
        self.consecutive_failures = 0
        
        logger.info(f"Adaptive rate limiter initialized: {initial_rate} calls/min")
    
    async def acquire(self) -> None:
        """Acquire permission with current rate"""
        await self.limiter.acquire()
    
    def report_success(self):
        """Report successful API call"""
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        
        # Increase rate after multiple successes
        if self.consecutive_successes >= 10 and self.current_rate < self.max_rate:
            old_rate = self.current_rate
            self.current_rate = min(self.max_rate, int(self.current_rate * 1.2))
            
            if self.current_rate != old_rate:
                self.limiter = RateLimiter(self.current_rate, 60)
                logger.info(f"Rate limit increased: {old_rate} -> {self.current_rate} calls/min")
                self.consecutive_successes = 0
    
    def report_failure(self, is_rate_limit_error: bool = False):
        """
        Report failed API call
        
        Args:
            is_rate_limit_error: Whether failure was due to rate limiting
        """
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        
        # Decrease rate on rate limit errors or multiple failures
        if is_rate_limit_error or self.consecutive_failures >= 3:
            if self.current_rate > self.min_rate:
                old_rate = self.current_rate
                self.current_rate = max(self.min_rate, int(self.current_rate * 0.7))
                
                if self.current_rate != old_rate:
                    self.limiter = RateLimiter(self.current_rate, 60)
                    logger.warning(f"Rate limit decreased: {old_rate} -> {self.current_rate} calls/min")
                    self.consecutive_failures = 0
    
    def get_current_rate(self) -> int:
        """Get current rate limit"""
        return self.current_rate
    
    def get_stats(self) -> Dict[str, any]:
        """Get adaptive limiter statistics"""
        base_stats = self.limiter.get_stats()
        base_stats.update({
            'adaptive_rate': self.current_rate,
            'min_rate': self.min_rate,
            'max_rate': self.max_rate,
            'consecutive_successes': self.consecutive_successes,
            'consecutive_failures': self.consecutive_failures
        })
        return base_stats


# Global rate limiter instances
_global_limiter = None
_multi_provider_limiter = None


def get_rate_limiter(max_calls: int = 30, time_window: int = 60) -> RateLimiter:
    """
    Get global rate limiter instance
    
    Args:
        max_calls: Maximum calls per time window
        time_window: Time window in seconds
        
    Returns:
        RateLimiter instance
    """
    global _global_limiter
    
    if _global_limiter is None:
        _global_limiter = RateLimiter(max_calls, time_window)
    
    return _global_limiter


def get_multi_provider_limiter() -> MultiProviderRateLimiter:
    """
    Get global multi-provider rate limiter
    
    Returns:
        MultiProviderRateLimiter instance
    """
    global _multi_provider_limiter
    
    if _multi_provider_limiter is None:
        _multi_provider_limiter = MultiProviderRateLimiter()
    
    return _multi_provider_limiter
