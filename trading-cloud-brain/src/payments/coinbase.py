# ========================================
# 💰 AXIOM COINBASE INTEGRATION
# ========================================
# Coinbase Advanced Trade API Integration
# Uses CDP (Coinbase Developer Platform) API Keys
# ========================================
# Features:
#   - Market Data (Prices, Order Book, Trades)
#   - Account Info (Balances, Portfolios)
#   - Trading (Market/Limit Orders)
#   - WebSocket for real-time data
# ========================================

import json
import hmac
import hashlib
import time
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List
from js import fetch


class CoinbaseAdvancedTrade:
    """
    Coinbase Advanced Trade API Client.
    
    Uses CDP API Keys for authentication.
    Supports REST API for trading and data.
    """
    
    # API Endpoints
    BASE_URL = "https://api.coinbase.com"
    ADVANCED_TRADE_URL = "https://api.coinbase.com/api/v3/brokerage"
    
    # Sandbox for testing (Demo Mode)
    SANDBOX_URL = "https://api-public.sandbox.exchange.coinbase.com"
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        demo_mode: bool = True
    ):
        """
        Initialize Coinbase client.
        
        Args:
            api_key: CDP API Key
            api_secret: CDP API Secret
            demo_mode: Use sandbox environment
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.demo_mode = demo_mode
        
        # Base URL based on mode
        self.base_url = self.SANDBOX_URL if demo_mode else self.ADVANCED_TRADE_URL
    
    # ========================================
    # 🔐 Authentication
    # ========================================
    
    def _sign_request(
        self,
        method: str,
        path: str,
        body: str = ""
    ) -> Dict[str, str]:
        """
        Create authentication headers for Coinbase API.
        
        Uses HMAC-SHA256 signature as per CDP requirements.
        """
        timestamp = str(int(time.time()))
        
        # Message to sign: timestamp + method + path + body
        message = timestamp + method.upper() + path + body
        
        # HMAC-SHA256 signature
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature_b64,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        }
    
    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Coinbase API.
        """
        body = json.dumps(data) if data else ""
        headers = self._sign_request(method, path, body)
        
        url = f"{self.base_url}{path}"
        
        try:
            options = {
                "method": method,
                "headers": headers
            }
            
            if body:
                options["body"] = body
            
            response = await fetch(url, options)
            response_text = await response.text()
            
            if response.status >= 400:
                return {
                    "status": "error",
                    "code": response.status,
                    "message": response_text
                }
            
            return {
                "status": "success",
                "data": json.loads(response_text) if response_text else {}
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ========================================
    # 📊 Market Data
    # ========================================
    
    async def get_products(self) -> Dict[str, Any]:
        """
        Get list of available trading pairs.
        """
        return await self._request("GET", "/products")
    
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """
        Get details for a specific product.
        
        Args:
            product_id: Trading pair (e.g., "BTC-USD")
        """
        return await self._request("GET", f"/products/{product_id}")
    
    async def get_ticker(self, product_id: str) -> Dict[str, Any]:
        """
        Get current ticker for a product.
        
        Args:
            product_id: Trading pair
        """
        return await self._request("GET", f"/products/{product_id}/ticker")
    
    async def get_order_book(
        self,
        product_id: str,
        level: int = 1
    ) -> Dict[str, Any]:
        """
        Get order book for a product.
        
        Args:
            product_id: Trading pair
            level: Depth level (1, 2, or 3)
        """
        return await self._request(
            "GET", 
            f"/products/{product_id}/book?level={level}"
        )
    
    async def get_candles(
        self,
        product_id: str,
        granularity: str = "ONE_HOUR",
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical candles (OHLCV).
        
        Args:
            product_id: Trading pair
            granularity: ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, 
                        THIRTY_MINUTE, ONE_HOUR, TWO_HOUR, SIX_HOUR, ONE_DAY
            start: Start time (ISO 8601)
            end: End time (ISO 8601)
        """
        params = f"?granularity={granularity}"
        if start:
            params += f"&start={start}"
        if end:
            params += f"&end={end}"
        
        return await self._request(
            "GET",
            f"/products/{product_id}/candles{params}"
        )
    
    # ========================================
    # 💰 Account & Portfolio
    # ========================================
    
    async def get_accounts(self) -> Dict[str, Any]:
        """
        Get all accounts (wallets/balances).
        """
        return await self._request("GET", "/accounts")
    
    async def get_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get specific account details.
        """
        return await self._request("GET", f"/accounts/{account_id}")
    
    async def get_portfolios(self) -> Dict[str, Any]:
        """
        Get all portfolios.
        """
        return await self._request("GET", "/portfolios")
    
    # ========================================
    # 📈 Trading
    # ========================================
    
    async def place_market_order(
        self,
        product_id: str,
        side: str,  # "BUY" or "SELL"
        size: Optional[str] = None,  # Base currency amount
        quote_size: Optional[str] = None  # Quote currency amount
    ) -> Dict[str, Any]:
        """
        Place a market order.
        
        Args:
            product_id: Trading pair (e.g., "BTC-USD")
            side: "BUY" or "SELL"
            size: Amount in base currency (e.g., "0.001" BTC)
            quote_size: Amount in quote currency (e.g., "100" USD)
        
        Note: Specify either size OR quote_size, not both.
        """
        order_config = {"market_market_ioc": {}}
        
        if quote_size:
            order_config["market_market_ioc"]["quote_size"] = quote_size
        elif size:
            order_config["market_market_ioc"]["base_size"] = size
        else:
            return {"status": "error", "message": "Specify size or quote_size"}
        
        order = {
            "client_order_id": self._generate_order_id(),
            "product_id": product_id,
            "side": side.upper(),
            "order_configuration": order_config
        }
        
        return await self._request("POST", "/orders", order)
    
    async def place_limit_order(
        self,
        product_id: str,
        side: str,
        size: str,
        price: str,
        post_only: bool = False
    ) -> Dict[str, Any]:
        """
        Place a limit order.
        
        Args:
            product_id: Trading pair
            side: "BUY" or "SELL"
            size: Amount in base currency
            price: Limit price
            post_only: If True, order will only be placed if it would be a maker order
        """
        order_config = {
            "limit_limit_gtc": {
                "base_size": size,
                "limit_price": price,
                "post_only": post_only
            }
        }
        
        order = {
            "client_order_id": self._generate_order_id(),
            "product_id": product_id,
            "side": side.upper(),
            "order_configuration": order_config
        }
        
        return await self._request("POST", "/orders", order)
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order by ID.
        """
        return await self._request(
            "POST",
            "/orders/batch_cancel",
            {"order_ids": [order_id]}
        )
    
    async def get_orders(
        self,
        product_id: Optional[str] = None,
        status: Optional[str] = None  # "PENDING", "OPEN", "FILLED", "CANCELLED"
    ) -> Dict[str, Any]:
        """
        Get orders list.
        """
        params = []
        if product_id:
            params.append(f"product_id={product_id}")
        if status:
            params.append(f"order_status={status}")
        
        query = "?" + "&".join(params) if params else ""
        return await self._request("GET", f"/orders/historical/batch{query}")
    
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order details by ID.
        """
        return await self._request("GET", f"/orders/historical/{order_id}")
    
    async def get_fills(
        self,
        product_id: Optional[str] = None,
        order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get trade fills (executed portions of orders).
        """
        params = []
        if product_id:
            params.append(f"product_id={product_id}")
        if order_id:
            params.append(f"order_id={order_id}")
        
        query = "?" + "&".join(params) if params else ""
        return await self._request("GET", f"/orders/historical/fills{query}")
    
    # ========================================
    # 🛠️ Utilities
    # ========================================
    
    def _generate_order_id(self) -> str:
        """Generate unique client order ID."""
        import random
        return f"axiom-{int(time.time())}-{random.randint(1000, 9999)}"
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection with a simple request.
        """
        result = await self.get_products()
        
        if result.get("status") == "success":
            return {
                "status": "connected",
                "mode": "sandbox" if self.demo_mode else "live",
                "products_count": len(result.get("data", {}).get("products", []))
            }
        
        return {
            "status": "failed",
            "error": result.get("message", "Unknown error")
        }


# ========================================
# 🏭 Factory Functions
# ========================================

def get_coinbase_client(env, demo_mode: bool = True) -> CoinbaseAdvancedTrade:
    """
    Get Coinbase client from environment.
    
    Expects:
        env.COINBASE_API_KEY
        env.COINBASE_API_SECRET
    """
    api_key = str(getattr(env, 'COINBASE_API_KEY', ''))
    api_secret = str(getattr(env, 'COINBASE_API_SECRET', ''))
    
    return CoinbaseAdvancedTrade(api_key, api_secret, demo_mode)


# ========================================
# 📋 Quick Reference
# ========================================
"""
USAGE EXAMPLE:

```python
# Initialize
coinbase = get_coinbase_client(env, demo_mode=True)

# Test connection
status = await coinbase.test_connection()

# Get BTC price
ticker = await coinbase.get_ticker("BTC-USD")

# Get accounts
accounts = await coinbase.get_accounts()

# Place market buy order ($100 of BTC)
order = await coinbase.place_market_order(
    product_id="BTC-USD",
    side="BUY",
    quote_size="100"  # $100
)

# Place limit order
order = await coinbase.place_limit_order(
    product_id="BTC-USD",
    side="BUY",
    size="0.001",  # 0.001 BTC
    price="40000"  # at $40,000
)
```
"""
