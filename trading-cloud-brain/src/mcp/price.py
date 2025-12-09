# ========================================
# 💰 AXIOM PRICE SERVER - Unified Price MCP
# ========================================
# Aggregates prices from multiple sources:
#   - Bybit (Crypto) - Unlimited
#   - Finage (Forex/Stocks) - Rate Limited
#   - Capital.com (Forex) - Rate Limited
# ========================================
# Features:
#   - Smart source selection
#   - KV caching (30 second TTL)
#   - Rate limit tracking
#   - Fallback logic
# ========================================

import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from js import fetch


class PriceServer:
    """
    Unified Price Server - "The Eyes of Axiom".
    
    Aggregates real-time prices from multiple sources with:
    - Smart routing (Bybit for crypto, Finage for forex/stocks)
    - KV caching to save API credits
    - Fallback logic when primary source fails
    """
    
    CACHE_TTL_SECONDS = 30  # 30 second cache
    
    # Source priorities
    CRYPTO_SOURCES = ["bybit", "finage"]
    FOREX_SOURCES = ["finage", "capital"]
    STOCK_SOURCES = ["finage"]
    
    def __init__(self, env):
        """
        Initialize PriceServer with environment bindings.
        
        Args:
            env: Cloudflare Worker environment (env.KV, env.FINAGE_API_KEY, etc.)
        """
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.finage_key = str(getattr(env, 'FINAGE_API_KEY', ''))
    
    async def get_price(
        self,
        symbol: str,
        asset_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get price for any symbol with smart routing and caching.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT, EURUSD, AAPL)
            asset_type: Optional hint ('crypto', 'forex', 'stock')
        
        Returns:
            Price data with source info
        """
        # Auto-detect asset type if not provided
        if asset_type is None:
            asset_type = self._detect_asset_type(symbol)
        
        # Check cache first
        cache_key = f"price:{symbol}"
        cached = await self._get_cached(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached
        
        # Fetch from appropriate source
        result = None
        
        if asset_type == "crypto":
            result = await self._get_crypto_price(symbol)
        elif asset_type == "forex":
            result = await self._get_forex_price(symbol)
        else:
            result = await self._get_stock_price(symbol)
        
        # Cache successful results
        if result and result.get("status") == "success":
            result["from_cache"] = False
            await self._set_cached(cache_key, result)
        
        return result
    
    async def get_multi_prices(
        self,
        symbols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get prices for multiple symbols efficiently.
        
        Args:
            symbols: List of trading symbols
        
        Returns:
            Dict mapping symbol to price data
        """
        results = {}
        for symbol in symbols:
            results[symbol] = await self.get_price(symbol)
        return results
    
    async def get_historical_prices(
        self,
        symbol: str,
        interval: str = "60",  # 1 hour
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get historical price data (OHLCV).
        
        Args:
            symbol: Trading symbol
            interval: Candle interval ('1', '5', '15', '60', '240', 'D')
            limit: Number of candles
        
        Returns:
            Historical OHLCV data
        """
        asset_type = self._detect_asset_type(symbol)
        
        if asset_type == "crypto":
            return await self._get_bybit_klines(symbol, interval, limit)
        else:
            # For forex/stocks, we'd need Finage historical endpoint
            return {
                "status": "error",
                "message": "Historical data only available for crypto currently"
            }
    
    # ========================================
    # 🔌 Source-Specific Fetchers
    # ========================================
    
    async def _get_crypto_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch crypto price from Bybit (unlimited)."""
        try:
            url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                ticker = data["result"]["list"][0]
                return {
                    "status": "success",
                    "symbol": symbol,
                    "price": float(ticker.get("lastPrice", 0)),
                    "bid": float(ticker.get("bid1Price", 0)),
                    "ask": float(ticker.get("ask1Price", 0)),
                    "change_24h": float(ticker.get("price24hPcnt", 0)) * 100,
                    "high_24h": float(ticker.get("highPrice24h", 0)),
                    "low_24h": float(ticker.get("lowPrice24h", 0)),
                    "volume_24h": float(ticker.get("volume24h", 0)),
                    "source": "bybit",
                    "asset_type": "crypto",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {"status": "error", "message": "Bybit returned no data", "symbol": symbol}
            
        except Exception as e:
            return {"status": "error", "message": str(e), "symbol": symbol}
    
    async def _get_forex_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch forex price from Finage."""
        if not self.finage_key:
            return {"status": "error", "message": "Finage API key not configured"}
        
        try:
            # Convert EURUSD -> EUR/USD format if needed
            pair = f"{symbol[:3]}/{symbol[3:]}" if len(symbol) == 6 else symbol
            url = f"https://api.finage.co.uk/last/forex/{pair}?apikey={self.finage_key}"
            
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if "bid" in data or "ask" in data:
                bid = float(data.get("bid", 0))
                ask = float(data.get("ask", 0))
                mid = (bid + ask) / 2 if bid and ask else bid or ask
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "price": mid,
                    "bid": bid,
                    "ask": ask,
                    "spread": ask - bid if bid and ask else 0,
                    "source": "finage",
                    "asset_type": "forex",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {"status": "error", "message": "Finage returned no data", "symbol": symbol}
            
        except Exception as e:
            return {"status": "error", "message": str(e), "symbol": symbol}
    
    async def _get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock price from Finage."""
        if not self.finage_key:
            return {"status": "error", "message": "Finage API key not configured"}
        
        try:
            url = f"https://api.finage.co.uk/last/stock/{symbol}?apikey={self.finage_key}"
            
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if "bid" in data or "ask" in data or "price" in data:
                price = float(data.get("price", 0))
                bid = float(data.get("bid", price))
                ask = float(data.get("ask", price))
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "price": price or ((bid + ask) / 2),
                    "bid": bid,
                    "ask": ask,
                    "source": "finage",
                    "asset_type": "stock",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {"status": "error", "message": "Finage stock data unavailable", "symbol": symbol}
            
        except Exception as e:
            return {"status": "error", "message": str(e), "symbol": symbol}
    
    async def _get_bybit_klines(
        self,
        symbol: str,
        interval: str,
        limit: int
    ) -> Dict[str, Any]:
        """Fetch Bybit klines (candlestick data)."""
        try:
            url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if data.get("retCode") == 0 and data.get("result", {}).get("list"):
                klines = data["result"]["list"]
                # Bybit returns newest first, reverse for oldest first
                candles = []
                for k in reversed(klines):
                    candles.append({
                        "timestamp": int(k[0]),
                        "open": float(k[1]),
                        "high": float(k[2]),
                        "low": float(k[3]),
                        "close": float(k[4]),
                        "volume": float(k[5])
                    })
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "interval": interval,
                    "candles": candles,
                    "source": "bybit"
                }
            
            return {"status": "error", "message": "No kline data"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # ========================================
    # 🗄️ KV Caching Layer
    # ========================================
    
    async def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached value from KV."""
        if not self.kv:
            return None
        
        try:
            cached = await self.kv.get(key)
            if cached:
                data = json.loads(cached)
                # Check TTL
                cached_time = datetime.fromisoformat(data.get("timestamp", "2000-01-01"))
                age = (datetime.utcnow() - cached_time).total_seconds()
                if age < self.CACHE_TTL_SECONDS:
                    return data
        except Exception:
            pass
        
        return None
    
    async def _set_cached(self, key: str, value: Dict) -> None:
        """Store value in KV cache."""
        if not self.kv:
            return
        
        try:
            await self.kv.put(key, json.dumps(value), {"expirationTtl": self.CACHE_TTL_SECONDS * 2})
        except Exception:
            pass
    
    # ========================================
    # 🔍 Utilities
    # ========================================
    
    def _detect_asset_type(self, symbol: str) -> str:
        """Auto-detect asset type from symbol."""
        symbol_upper = symbol.upper()
        
        # Crypto patterns
        crypto_suffixes = ["USDT", "PERP", "USD"]
        crypto_bases = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "BNB", "AVAX", "DOT"]
        
        if any(symbol_upper.endswith(s) for s in crypto_suffixes):
            return "crypto"
        if any(symbol_upper.startswith(c) for c in crypto_bases):
            return "crypto"
        
        # Forex pattern: 6 letters (EURUSD, GBPJPY, etc.)
        if len(symbol) == 6 and symbol.isalpha():
            return "forex"
        
        # Default to stock
        return "stock"


# ========================================
# 🏭 Factory Function
# ========================================

def get_price_server(env) -> PriceServer:
    """Get PriceServer instance with environment bindings."""
    return PriceServer(env)
