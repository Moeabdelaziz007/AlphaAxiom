"""
🔵 IC Markets Provider
cTrader FIX API / MT5 integration for IC Markets broker.

RESEARCH FINDINGS:
- Uses cTrader FIX API or MT5
- Python library: ejtraderCT for FIX API
- MetaTrader5 package for MT5
- FIX API requires enabled in cTrader settings

For full implementation, requires:
1. IC Markets cTrader or MT5 account
2. FIX API credentials (host, port, SenderCompID)
3. Or MT5 login credentials
"""

import json
from typing import Dict, List, Optional
from .base import Broker

# Try to import fetch from js (Cloudflare Workers)
# Fallback to httpx if not available (Local testing)
try:
    from js import fetch, Headers
except ImportError:
    # Use dummy fetch for local testing unless mocked, but we will handle it in _fetch
    fetch = None
    Headers = None

class ICMarketsProvider(Broker):
    """
    IC Markets broker integration via cTrader FIX API.
    
    Environment Variables:
        ICMARKETS_FIX_HOST: FIX server host
        ICMARKETS_FIX_PORT: FIX server port
        ICMARKETS_SENDER_ID: SenderCompID
        ICMARKETS_PASSWORD: FIX password
        ICMARKETS_ACCOUNT_ID: Account number
    """
    
    def __init__(self, env):
        """
        Initialize IC Markets provider.
        
        Args:
            env: Cloudflare Worker environment
        """
        super().__init__("ICMARKETS", env)
        self.fix_host = str(getattr(env, 'ICMARKETS_FIX_HOST', ''))
        self.fix_port = str(getattr(env, 'ICMARKETS_FIX_PORT', ''))
        self.sender_id = str(getattr(env, 'ICMARKETS_SENDER_ID', ''))
        self.password = str(getattr(env, 'ICMARKETS_PASSWORD', ''))
        self.account_id = str(getattr(env, 'ICMARKETS_ACCOUNT_ID', ''))

        # Yahoo Finance mapping
        self.timeframe_map = {
            "M1": "1m",
            "M5": "5m",
            "M15": "15m",
            "M30": "30m",
            "H1": "60m",
            "H4": "1d", # Yahoo 4h is tricky, fallback to 1d or handle aggregation
            "D1": "1d",
            "W1": "1wk",
            "MN": "1mo"
        }

    async def _fetch(self, url: str) -> Dict:
        """Helper to fetch JSON data."""
        if fetch:
            # Cloudflare Workers environment
            try:
                headers = Headers.new()
                headers.set("User-Agent", "Mozilla/5.0")
                response = await fetch(url, headers=headers)
                if not response.ok:
                    self.log.error(f"Fetch failed: {response.status}")
                    return {}
                return await response.json()
            except Exception as e:
                self.log.error(f"Fetch error: {e}")
                return {}
        else:
            # Local environment fallback (using httpx if available)
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                    response.raise_for_status()
                    return response.json()
            except ImportError:
                self.log.error("httpx not found for local fetch")
                return {}
            except Exception as e:
                self.log.error(f"Local fetch error: {e}")
                return {}

    def _map_symbol(self, symbol: str) -> str:
        """Map generic symbol to Yahoo Finance symbol."""
        # Crypto - Specific checks first
        if symbol in ["BTCUSD", "ETHUSD"]:
            return f"{symbol[:3]}-USD"

        # Gold/Silver
        if symbol == "XAUUSD":
            return "GC=F" # Gold Futures
        if symbol == "XAGUSD":
            return "SI=F" # Silver Futures

        # Common Forex (length 6 and alpha)
        if len(symbol) == 6 and symbol.isalpha():
            return f"{symbol}=X"

        return symbol

    async def get_account_summary(self) -> Dict:
        """
        Get account summary.
        
        Returns:
            dict: {balance, equity, margin, profit}
        """
        # TODO: Implement FIX API call
        return {
            "broker": "ICMARKETS",
            "balance": 0.0,
            "equity": 0.0,
            "margin_used": 0.0,
            "margin_available": 0.0,
            "unrealized_pnl": 0.0,
            "status": "STUB_NOT_IMPLEMENTED"
        }
    
    async def get_open_positions(self) -> List[Dict]:
        """Get open positions."""
        # TODO: Implement
        return []
    
    async def place_order(self, symbol: str, side: str, units: float, 
                         order_type: str = "MARKET", price: float = None,
                         stop_loss: float = None, take_profit: float = None) -> Dict:
        """
        Place order via FIX API.
        
        Args:
            symbol: Trading symbol
            side: "BUY" or "SELL"
            units: Position size
            order_type: "MARKET" or "LIMIT"
            price: Limit price (if LIMIT order)
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            dict: Order result
        """
        # TODO: Implement FIX order placement
        return {
            "broker": "ICMARKETS",
            "status": "STUB_NOT_IMPLEMENTED",
            "message": "IC Markets FIX integration pending"
        }
    
    async def close_position(self, position_id: str) -> Dict:
        """Close position."""
        # TODO: Implement
        return {"status": "STUB_NOT_IMPLEMENTED"}
    
    async def get_candles(self, symbol: str, timeframe: str = "M1", 
                         count: int = 100) -> List[Dict]:
        """
        Get OHLCV candles via Yahoo Finance as fallback.

        Args:
            symbol: Trading pair (e.g., "EURUSD")
            timeframe: Timeframe code (M1, M5, H1, D1)
            count: Number of candles
        """
        yf_symbol = self._map_symbol(symbol)
        interval = self.timeframe_map.get(timeframe, "1m")

        # Calculate range approximately based on count * interval
        # Yahoo supports range like 1d, 5d, 1mo, 1y.
        # Simple heuristic:
        range_param = "1d"
        if interval == "1m":
            if count > 1400: range_param = "5d"
            else: range_param = "1d"
        elif interval == "5m":
            if count > 200: range_param = "5d"
            else: range_param = "1d"
        elif interval == "15m":
            range_param = "5d"
        elif interval == "60m" or interval == "1h":
            range_param = "1mo"
        elif interval == "1d":
            range_param = "1y" # Approx

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_symbol}?interval={interval}&range={range_param}"

        data = await self._fetch(url)

        candles = []
        try:
            result = data.get("chart", {}).get("result", [])
            if not result:
                return []

            quote = result[0]
            timestamps = quote.get("timestamp", [])
            indicators = quote.get("indicators", {}).get("quote", [{}])[0]

            opens = indicators.get("open", [])
            highs = indicators.get("high", [])
            lows = indicators.get("low", [])
            closes = indicators.get("close", [])
            volumes = indicators.get("volume", [])

            for i in range(len(timestamps)):
                # Skip incomplete candles
                if opens[i] is None: continue

                candles.append({
                    "time": timestamps[i], # Unix timestamp
                    "open": float(opens[i]),
                    "high": float(highs[i]),
                    "low": float(lows[i]),
                    "close": float(closes[i]),
                    "volume": int(volumes[i] if volumes[i] else 0)
                })

            # Filter to count
            if count and len(candles) > count:
                candles = candles[-count:]

            return candles

        except Exception as e:
            self.log.error(f"Error parsing candles for {symbol}: {e}")
            return []
    
    async def get_price(self, symbol: str) -> float:
        """
        Get current mid price.
        Uses get_candles(M1, 1) as proxy.
        """
        candles = await self.get_candles(symbol, "M1", 1)
        if candles:
            last = candles[-1]
            return last["close"]
        return 0.0
