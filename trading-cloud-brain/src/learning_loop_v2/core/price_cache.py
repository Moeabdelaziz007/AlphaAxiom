"""
Price Caching System for AlphaAxiom Learning Loop v2.0
Efficiently caches price data to reduce API calls and improve performance.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class PriceCache:
    """
    A simple in-memory cache for price data with TTL (Time-To-Live) expiration.
    """
    
    def __init__(self, default_ttl_seconds: int = 60):
        """
        Initialize the price cache.
        
        Args:
            default_ttl_seconds: Default time-to-live for cached 
                items in seconds
        """
        self.default_ttl = timedelta(seconds=default_ttl_seconds)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, datetime] = {}
    
    def _get_cache_key(self, symbol: str, broker: str = "default") -> str:
        """Generate a unique cache key for a symbol and broker combination."""
        return f"{broker}:{symbol}"
    
    def put(self, symbol: str, data: Dict[str, Any], broker: str = "default", 
            ttl_seconds: Optional[int] = None):
        """
        Store price data in the cache.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            data: Price data to cache
            broker: Broker name (e.g., "Binance", "Bybit")
            ttl_seconds: Time-to-live in seconds (overrides default
                if provided)
        """
        key = self._get_cache_key(symbol, broker)
        self._cache[key] = data
        self._access_times[key] = datetime.now()
        
        # Set custom TTL if provided
        if ttl_seconds is not None:
            # We store the TTL with the data for reference
            self._cache[key]["_ttl"] = ttl_seconds
    
    def get(self, symbol: str, broker: str = "default") -> \
            Optional[Dict[str, Any]]:
        """
        Retrieve price data from the cache if it exists and hasn't expired.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            broker: Broker name (e.g., "Binance", "Bybit")
            
        Returns:
            Cached data if available and not expired, None otherwise
        """
        key = self._get_cache_key(symbol, broker)
        
        if key not in self._cache:
            return None
        
        # Check if expired
        access_time = self._access_times[key]
        ttl = self._cache[key].get("_ttl", self.default_ttl.total_seconds())
        expiration_time = access_time + timedelta(seconds=ttl)
        
        if datetime.now() > expiration_time:
            # Expired, remove from cache
            del self._cache[key]
            del self._access_times[key]
            return None
        
        # Update access time
        self._access_times[key] = datetime.now()
        return self._cache[key]
    
    def invalidate(self, symbol: str, broker: str = "default"):
        """
        Remove a specific symbol from the cache.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            broker: Broker name (e.g., "Binance", "Bybit")
        """
        key = self._get_cache_key(symbol, broker)
        if key in self._cache:
            del self._cache[key]
        if key in self._access_times:
            del self._access_times[key]
    
    def clear_expired(self):
        """Remove all expired entries from the cache."""
        now = datetime.now()
        expired_keys = []
        
        for key, access_time in self._access_times.items():
            ttl = self._cache[key].get(
                "_ttl", self.default_ttl.total_seconds())
            expiration_time = access_time + timedelta(seconds=ttl)
            
            if now > expiration_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            del self._access_times[key]
    
    def clear(self):
        """Clear all entries from the cache."""
        self._cache.clear()
        self._access_times.clear()
    
    def size(self) -> int:
        """Return the number of items in the cache."""
        return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        return {
            "size": self.size(),
            "default_ttl_seconds": self.default_ttl.total_seconds()
        }
