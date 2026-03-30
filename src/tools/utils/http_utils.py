"""HTTP utilities for API calls with rate limiting and caching."""

import time
import hashlib
import json
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import requests
from cachetools import TTLCache


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, calls_per_period: int, period_seconds: float):
        """Initialize rate limiter.

        Args:
            calls_per_period: Number of allowed calls per period
            period_seconds: Period duration in seconds
        """
        self.calls_per_period = calls_per_period
        self.period_seconds = period_seconds
        self.calls = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove old calls outside the window
        self.calls = [call_time for call_time in self.calls
                     if now - call_time < self.period_seconds]

        # Check if we need to wait
        if len(self.calls) >= self.calls_per_period:
            sleep_time = self.period_seconds - (now - self.calls[0]) + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)
                now = time.time()
                self.calls = []

        # Record this call
        self.calls.append(now)


class CacheManager:
    """TTL-based caching with persistence support."""

    def __init__(self, ttl: int = 3600, maxsize: int = 1000, cache_dir: Optional[str] = None):
        """Initialize cache manager.

        Args:
            ttl: Time to live in seconds (default: 1 hour)
            maxsize: Maximum cache size
            cache_dir: Optional directory for persistent cache
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.cache_dir = Path(cache_dir) if cache_dir else None

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Try memory cache first
        if key in self.cache:
            return self.cache[key]

        # Try persistent cache
        if self.cache_dir:
            cache_file = self.cache_dir / self._hash_key(key)
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        # Check if expired
                        if time.time() - data['timestamp'] < data['ttl']:
                            value = data['value']
                            self.cache[key] = value
                            return value
                        else:
                            cache_file.unlink()  # Remove expired cache
                except Exception:
                    pass

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL
        """
        # Store in memory cache
        self.cache[key] = value

        # Store in persistent cache
        if self.cache_dir:
            cache_file = self.cache_dir / self._hash_key(key)
            try:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'key': key,
                        'value': value,
                        'timestamp': time.time(),
                        'ttl': ttl or 3600
                    }, f)
            except Exception:
                pass

    def _hash_key(self, key: str) -> str:
        """Generate hash for cache key."""
        return hashlib.md5(key.encode()).hexdigest() + '.json'

    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        if self.cache_dir and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()


def make_api_call(
    url: str,
    method: str = 'GET',
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 10,
    max_retries: int = 3,
    rate_limiter: Optional[RateLimiter] = None,
    cache_manager: Optional[CacheManager] = None,
    cache_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Make API call with retry logic and caching.

    Args:
        url: API endpoint URL
        method: HTTP method (GET, POST, etc.)
        params: Query parameters
        json_data: JSON body for POST/PUT
        headers: HTTP headers
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        rate_limiter: Optional rate limiter
        cache_manager: Optional cache manager
        cache_key: Cache key (required if cache_manager provided)

    Returns:
        Response JSON or None on failure
    """
    # Check cache first (only for GET requests)
    if method == 'GET' and cache_manager and cache_key:
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result

    # Apply rate limiting
    if rate_limiter:
        rate_limiter.wait_if_needed()

    # Retry with exponential backoff
    for attempt in range(max_retries):
        try:
            if method == 'GET':
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
            elif method == 'POST':
                response = requests.post(
                    url,
                    params=params,
                    json=json_data,
                    headers=headers,
                    timeout=timeout
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            result = response.json()

            # Cache successful result
            if method == 'GET' and cache_manager and cache_key:
                cache_manager.set(cache_key, result)

            return result

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limit
                wait_time = min(2 ** attempt, 60)  # Max 60 seconds
                time.sleep(wait_time)
                continue
            elif response.status_code >= 500:  # Server error
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            return None

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None

        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None

        except Exception:
            return None

    return None
