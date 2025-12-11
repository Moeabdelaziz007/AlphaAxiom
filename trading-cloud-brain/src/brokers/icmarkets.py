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

from typing import Dict, List, Optional
from .base import Broker

try:
    from js import fetch
except ImportError:
    fetch = None

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
        self.env = env
        self.fix_host = str(getattr(env, 'ICMARKETS_FIX_HOST', ''))
        self.fix_port = str(getattr(env, 'ICMARKETS_FIX_PORT', ''))
        self.sender_id = str(getattr(env, 'ICMARKETS_SENDER_ID', ''))
        self.password = str(getattr(env, 'ICMARKETS_PASSWORD', ''))
        self.account_id = str(getattr(env, 'ICMARKETS_ACCOUNT_ID', ''))
        # Initialize logger as per base class
        super().__init__("ICMarkets", env)

    def _map_symbol_to_yahoo(self, symbol: str) -> str:
        """
        Map broker symbol to Yahoo Finance symbol.

        Args:
            symbol: Trading symbol (e.g., "EURUSD", "BTCUSD")

        Returns:
            Mapped symbol (e.g., "EURUSD=X", "BTC-USD")
        """
        symbol = symbol.upper()

        # Crypto mappings
        # Common cryptos usually end with USD in broker but need -USD for Yahoo
        # Check for major crypto prefixes specifically to distinguish from Forex
        crypto_prefixes = ["BTC", "ETH", "LTC", "XRP", "BCH", "SOL", "DOGE", "ADA", "DOT", "LINK"]

        if symbol.endswith("USD"):
             for prefix in crypto_prefixes:
                 if symbol.startswith(prefix):
                     # e.g., BTCUSD -> BTC-USD
                     return f"{symbol[:-3]}-USD"

        # Also catch longer crypto symbols (e.g. SHIBUSD -> SHIB-USD)
        if symbol.endswith("USD") and len(symbol) > 6:
             return f"{symbol[:-3]}-USD"

        # Forex (standard 6 chars, e.g. EURUSD)
        if len(symbol) == 6 and symbol.isalpha():
            return f"{symbol}=X"

        # Indices/Commodities often have specific mappings
        # Default to symbol if no match
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
        """Get OHLCV candles."""
        # TODO: Implement
        return []
    
    async def get_price(self, symbol: str) -> float:
        """
        Get current market price.

        Uses Yahoo Finance as a fallback data source since FIX API
        is primarily for execution, not market data in this context.

        Args:
            symbol: Trading symbol

        Returns:
            float: Current price
        """
        if not fetch:
            self.log.error("Fetch not available (js module missing)")
            return 0.0

        yahoo_symbol = self._map_symbol_to_yahoo(symbol)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?interval=1m&range=1d"

        try:
            response = await fetch(url, {"method": "GET"})
            if not response.ok:
                self.log.error(f"Failed to fetch price for {symbol} from Yahoo: {response.status}")
                return 0.0

            data = await response.json()

            # Parse response
            # data['chart']['result'][0]['meta']['regularMarketPrice']
            result = data.get('chart', {}).get('result', [])
            if not result:
                return 0.0

            price = result[0].get('meta', {}).get('regularMarketPrice')

            # Fallback to last close if regularMarketPrice is missing
            if price is None:
                quotes = result[0].get('indicators', {}).get('quote', [{}])[0]
                closes = quotes.get('close', [])
                if closes:
                    # Get last non-null close
                    for c in reversed(closes):
                        if c is not None:
                            price = c
                            break

            return float(price) if price else 0.0

        except Exception as e:
            self.log.error(f"Error fetching Yahoo price for {symbol}: {str(e)}")
            return 0.0
