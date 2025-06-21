import asyncio
import time
from typing import Dict, List
from datetime import datetime, timedelta


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60, burst_limit: int = 10):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.requests = []
        self.burst_count = 0
        self.last_reset = datetime.now()
    
    async def wait(self):
        """Wait if necessary to respect rate limits"""
        now = datetime.now()
        
        # Reset burst counter every minute
        if now - self.last_reset > timedelta(minutes=1):
            self.burst_count = 0
            self.last_reset = now
        
        # Remove old requests (older than 1 minute)
        cutoff_time = now - timedelta(minutes=1)
        self.requests = [req_time for req_time in self.requests if req_time > cutoff_time]
        
        # Check if we need to wait
        if len(self.requests) >= self.requests_per_minute:
            # Wait until the oldest request is more than 1 minute old
            oldest_request = min(self.requests)
            wait_time = 60 - (now - oldest_request).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Check burst limit
        if self.burst_count >= self.burst_limit:
            await asyncio.sleep(1)  # Wait 1 second between bursts
            self.burst_count = 0
        
        # Record this request
        self.requests.append(now)
        self.burst_count += 1


class GlobalRateLimiter:
    """Global rate limiter to manage multiple API rate limits"""
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
    
    def get_limiter(self, api_name: str, requests_per_minute: int = 60, burst_limit: int = 10) -> RateLimiter:
        """Get or create a rate limiter for a specific API"""
        if api_name not in self.limiters:
            self.limiters[api_name] = RateLimiter(requests_per_minute, burst_limit)
        return self.limiters[api_name]
    
    async def wait_for_api(self, api_name: str):
        """Wait for a specific API rate limiter"""
        if api_name in self.limiters:
            await self.limiters[api_name].wait()


# Global instance
global_rate_limiter = GlobalRateLimiter()