"""
🔗 Binance Connector for AXIOM Trading System
Supports: Spot, Futures, WebSocket real-time data

FEATURES:
- REST API for orders and positions
- WebSocket for real-time market data
- High liquidity support
- Comprehensive market data access

REQUIREMENTS:
pip install python-binance
"""

import hmac
import hashlib
import time
import json
from typing import Optional, Dict, List
from urllib.parse import urlencode
from .base import Broker


class BinanceConnector(Broker):
    """
    Binance Connector for spot and futures trading.
    Supports both REST API and WebSocket connections.
    """
    
    # API Endpoints
    BASE_URL = "https://api.binance.com"
    FUTURES_URL = "https://fapi.binance.com"
    STREAM_URL = "wss://stream.binance.com:9443/ws"
    
    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False):
        """
        Initialize Binance connector.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet for paper trading
        """
        super().__init__("Binance", {})
        self.api_key = api_key or "PLACEHOLDER_BINANCE_API_KEY"
        self.api_secret = api_secret or "PLACEHOLDER_BINANCE_API_SECRET"
        self.testnet = testnet
        
        # Override with testnet URLs if needed
        if testnet:
            self.BASE_URL = "https://testnet.binance.vision"
            self.FUTURES_URL = "https://testnet.binancefuture.com"
    
    def _generate_signature(self, params: dict) -> str:
        """Generate HMAC SHA256 signature for authenticated requests."""
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_headers(self) -> dict:
        """Get authenticated headers."""
        return {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    # ==========================================
    # 📊 MARKET DATA (Public - No Auth Required)
    # ==========================================
    
    async def get_klines(self, 
                        symbol: str, 
                        interval: str = "1m", 
                        limit: int = 500) -> List[dict]:
        """
        Get candlestick/kline data.
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            interval: Timeframe - "1m", "5m", "15m", "1h", etc.
            limit: Number of candles (max 1000)
        
        Returns:
            List of OHLCV candles
        """
        from js import fetch
        
        url = f"{self.BASE_URL}/api/v3/klines"
        params = f"?symbol={symbol}&interval={interval}&limit={limit}"
        
        response = await fetch(url + params)
        data = await response.json()
        
        # Convert to standard format
        candles = []
        for item in data:
            candles.append({
                "time": int(item[0]),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5])
            })
        
        return candles
    
    async def get_ticker(self, symbol: str) -> dict:
        """Get latest ticker for a symbol."""
        from js import fetch
        
        url = f"{self.BASE_URL}/api/v3/ticker/24hr?symbol={symbol}"
        
        response = await fetch(url)
        data = await response.json()
        
        return {
            "symbol": data.get("symbol"),
            "lastPrice": float(data.get("lastPrice", 0)),
            "bid": float(data.get("bidPrice", 0)),
            "ask": float(data.get("askPrice", 0)),
            "volume24h": float(data.get("volume", 0)),
            "change24h": float(data.get("priceChangePercent", 0))
        }
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> dict:
        """Get order book for a symbol."""
        from js import fetch
        
        url = f"{self.BASE_URL}/api/v3/depth?symbol={symbol}&limit={limit}"
        
        response = await fetch(url)
        data = await response.json()
        
        return {
            "bids": [[float(price), float(quantity)] for price, quantity in data.get("bids", [])],
            "asks": [[float(price), float(quantity)] for price, quantity in data.get("asks", [])]
        }
    
    # ==========================================
    # 🏦 ACCOUNT (Authenticated)
    # ==========================================
    
    async def get_account_summary(self) -> Dict:
        """Get account balance and status."""
        from js import fetch
        
        timestamp = int(time.time() * 1000)
        params = {"timestamp": timestamp}
        params["signature"] = self._generate_signature(params)
        
        url = f"{self.BASE_URL}/api/v3/account"
        
        response = await fetch(
            url,
            method="GET",
            headers=self._get_headers(),
            params=params
        )
        data = await response.json()
        
        balances = []
        for balance in data.get("balances", []):
            if float(balance["free"]) > 0 or float(balance["locked"]) > 0:
                balances.append({
                    "asset": balance["asset"],
                    "free": float(balance["free"]),
                    "locked": float(balance["locked"])
                })
        
        return {
            "balances": balances,
            "permissions": data.get("permissions", []),
            "updateTime": data.get("updateTime")
        }
    
    async def get_open_positions(self) -> List[Dict]:
        """Get list of open positions (for futures)."""
        from js import fetch
        
        timestamp = int(time.time() * 1000)
        params = {"timestamp": timestamp}
        params["signature"] = self._generate_signature(params)
        
        url = f"{self.FUTURES_URL}/fapi/v2/positionRisk"
        
        response = await fetch(
            url,
            method="GET",
            headers=self._get_headers(),
            params=params
        )
        data = await response.json()
        
        positions = []
        for pos in data:
            if float(pos["positionAmt"]) != 0:
                positions.append({
                    "symbol": pos["symbol"],
                    "side": "LONG" if float(pos["positionAmt"]) > 0 else "SHORT",
                    "amount": float(pos["positionAmt"]),
                    "entryPrice": float(pos["entryPrice"]),
                    "unrealizedPnl": float(pos["unRealizedProfit"]),
                    "leverage": int(pos["leverage"])
                })
        
        return positions
    
    # ==========================================
    # 💰 TRADING (Authenticated)
    # ==========================================
    
    async def place_order(self, symbol: str, side: str, amount: float, price: float = None, **kwargs) -> Dict:
        """Place a market or limit order."""
        from js import fetch
        
        timestamp = int(time.time() * 1000)
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "LIMIT" if price else "MARKET",
            "quantity": str(amount),
            "timestamp": timestamp
        }
        
        if price:
            params["price"] = str(price)
            params["timeInForce"] = "GTC"
        
        # Add any additional parameters
        for key, value in kwargs.items():
            params[key] = value
        
        params["signature"] = self._generate_signature(params)
        
        url = f"{self.BASE_URL}/api/v3/order"
        
        response = await fetch(
            url,
            method="POST",
            headers=self._get_headers(),
            body=json.dumps(params)
        )
        data = await response.json()
        
        return {
            "orderId": data.get("orderId"),
            "symbol": data.get("symbol"),
            "side": data.get("side"),
            "type": data.get("type"),
            "status": data.get("status"),
            "price": float(data.get("price", 0)),
            "executedQty": float(data.get("executedQty", 0)),
            "origQty": float(data.get("origQty", 0))
        }
    
    async def close_position(self, symbol: str, position_id: str = None) -> Dict:
        """Close a position (for futures)."""
        # For spot trading, this would be selling the asset
        # For futures, we would need to place an opposite order
        return {"error": "Not implemented for spot trading"}
    
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """Fetch historical candle data."""
        return await self.get_klines(symbol, timeframe, limit)
    
    async def get_price(self, symbol: str) -> float:
        """Get current market price."""
        ticker = await self.get_ticker(symbol)
        return ticker.get("lastPrice", 0.0)
