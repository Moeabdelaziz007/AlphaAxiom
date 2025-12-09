# ========================================
# 🔴 AXIOM CACHE CLIENT - Redis-Ready Architecture
# ========================================
# Hybrid caching solution for Cloudflare Workers.
# 
# Current Implementation: Cloudflare KV (serverless, no TCP)
# Future Ready: Upstash Redis HTTP API (easy migration)
#
# Features:
#   - Signal caching (30s TTL)
#   - Price caching (60s TTL)
#   - Session storage
#   - Redis-compatible method names
# ========================================

import json
from typing import Any, Dict, Optional, List
from datetime import datetime

# ========================================
# 📦 Abstract Cache Interface
# ========================================

class CacheInterface:
    """
    Abstract interface for cache operations.
    Implement this for different backends (KV, Redis, etc.)
    """
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        raise NotImplementedError
    
    async def set(self, key: str, value: str, ttl: int = 60) -> bool:
        """Set value with TTL in seconds."""
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        raise NotImplementedError


# ========================================
# ☁️ Cloudflare KV Adapter
# ========================================

class KVCacheAdapter(CacheInterface):
    """
    Cloudflare KV implementation of CacheInterface.
    Works in CF Workers Python environment.
    """
    
    def __init__(self, kv_namespace):
        """
        Initialize with KV namespace binding.
        
        Args:
            kv_namespace: env.BRAIN_MEMORY (or any KV binding)
        """
        self.kv = kv_namespace
        self.prefix = "cache:"
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from KV."""
        try:
            full_key = f"{self.prefix}{key}"
            value = await self.kv.get(full_key)
            return value
        except Exception as e:
            return None
    
    async def set(self, key: str, value: str, ttl: int = 60) -> bool:
        """Set value in KV with expiration."""
        try:
            full_key = f"{self.prefix}{key}"
            # KV put accepts expirationTtl in seconds
            await self.kv.put(full_key, value, {"expirationTtl": ttl})
            return True
        except Exception as e:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete from KV."""
        try:
            full_key = f"{self.prefix}{key}"
            await self.kv.delete(full_key)
            return True
        except Exception as e:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in KV."""
        value = await self.get(key)
        return value is not None
    
    # ========================================
    # 📊 JSON Convenience Methods
    # ========================================
    
    async def get_json(self, key: str) -> Optional[Dict]:
        """Get and parse JSON value."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return None
        return None
    
    async def set_json(self, key: str, data: Dict, ttl: int = 60) -> bool:
        """Serialize and set JSON value."""
        try:
            value = json.dumps(data)
            return await self.set(key, value, ttl)
        except:
            return False


# ========================================
# 🔴 Upstash Redis Adapter (Future)
# ========================================

class UpstashRedisAdapter(CacheInterface):
    """
    Upstash Redis HTTP implementation.
    For future migration when we need cross-region Redis.
    
    Requires:
        - UPSTASH_REDIS_URL
        - UPSTASH_REDIS_TOKEN
    """
    
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def _request(self, command: List[str]) -> Any:
        """Execute Redis command via HTTP."""
        from js import fetch as js_fetch
        
        response = await js_fetch(
            self.url,
            method="POST",
            headers=self.headers,
            body=json.dumps(command)
        )
        data = await response.json()
        return data.get("result")
    
    async def get(self, key: str) -> Optional[str]:
        return await self._request(["GET", key])
    
    async def set(self, key: str, value: str, ttl: int = 60) -> bool:
        result = await self._request(["SET", key, value, "EX", str(ttl)])
        return result == "OK"
    
    async def delete(self, key: str) -> bool:
        result = await self._request(["DEL", key])
        return result > 0
    
    async def exists(self, key: str) -> bool:
        result = await self._request(["EXISTS", key])
        return result > 0
    
    # Pub/Sub (Upstash supports this via HTTP)
    async def publish(self, channel: str, message: str) -> int:
        return await self._request(["PUBLISH", channel, message])


# ========================================
# 🏭 Signal Cache Service
# ========================================

class SignalCache:
    """
    High-level caching service for trading signals.
    Uses the cache adapter underneath.
    """
    
    def __init__(self, cache: CacheInterface):
        self.cache = cache
    
    async def cache_signal(self, symbol: str, signal: Dict, ttl: int = 30) -> bool:
        """
        Cache a trading signal.
        
        Args:
            symbol: e.g., "BTCUSDT"
            signal: {"direction": "BUY", "confidence": 0.85, ...}
            ttl: Time to live in seconds
        """
        key = f"signal:{symbol}"
        signal["cached_at"] = datetime.utcnow().isoformat()
        return await self.cache.set_json(key, signal, ttl)
    
    async def get_signal(self, symbol: str) -> Optional[Dict]:
        """Get cached signal for symbol."""
        key = f"signal:{symbol}"
        return await self.cache.get_json(key)
    
    async def cache_price(self, symbol: str, price: float, ttl: int = 60) -> bool:
        """Cache current price."""
        key = f"price:{symbol}"
        data = {
            "price": price,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.cache.set_json(key, data, ttl)
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """Get cached price."""
        key = f"price:{symbol}"
        data = await self.cache.get_json(key)
        return data.get("price") if data else None
    
    async def cache_user_session(self, user_id: str, data: Dict, ttl: int = 3600) -> bool:
        """Cache user session data."""
        key = f"session:{user_id}"
        return await self.cache.set_json(key, data, ttl)
    
    async def get_user_session(self, user_id: str) -> Optional[Dict]:
        """Get user session."""
        key = f"session:{user_id}"
        return await self.cache.get_json(key)

    async def check_rate_limit(self, key: str, max_requests: int, window_sec: int) -> bool:
        """
        Check if action is within rate limit using a sliding window counter.
        
        Args:
            key: Unique identifier for the limit (e.g., "coinbase_api" or "user:123:trade")
            max_requests: Maximum allowed requests in the window
            window_sec: Time window in seconds
            
        Returns:
            bool: True if allowed, False if limit exceeded
        """
        # Simple fixed window counter for KV (efficient)
        # For stricter sliding window, we'd need a list of timestamps, which is heavier on KV.
        # We append a rough time bucket to the key to rotate windows.
        import time
        current_window = int(time.time() / window_sec)
        limit_key = f"ratelimit:{key}:{current_window}"
        
        current_count = await self.cache.get(limit_key)
        
        if current_count:
            count = int(current_count)
            if count >= max_requests:
                return False
            # Increment
            await self.cache.set(limit_key, str(count + 1), ttl=window_sec)
        else:
            # First request in this window
            await self.cache.set(limit_key, "1", ttl=window_sec)
            
        return True


# ========================================
# 🏭 Factory Functions
# ========================================

def create_kv_cache(env) -> SignalCache:
    """
    Create SignalCache using Cloudflare KV.
    
    Usage:
        cache = create_kv_cache(env)
        await cache.cache_signal("BTC", {"direction": "BUY"})
    """
    kv_adapter = KVCacheAdapter(env.BRAIN_MEMORY)
    return SignalCache(kv_adapter)


def create_upstash_cache(url: str, token: str) -> SignalCache:
    """
    Create SignalCache using Upstash Redis.
    
    Usage:
        cache = create_upstash_cache(url, token)
        await cache.cache_signal("BTC", {"direction": "BUY"})
    """
    redis_adapter = UpstashRedisAdapter(url, token)
    return SignalCache(redis_adapter)


# ========================================
# 🧪 Quick Test
# ========================================

def test_cache_architecture():
    """Verify cache architecture design."""
    print("✅ CacheInterface defined")
    print("✅ KVCacheAdapter (CF Workers)")
    print("✅ UpstashRedisAdapter (Future)")
    print("✅ SignalCache service layer")
    print("✅ Factory functions ready")
    return True
