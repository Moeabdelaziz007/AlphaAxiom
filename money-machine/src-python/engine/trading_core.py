"""
Core trading engine with CCXT integration
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import os


class Portfolio:
    """Manages portfolio state, balance, and positions"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.trades: List[Dict] = []
        self.positions: Dict[str, Any] = {}
    
    def get_balance(self) -> float:
        return self.balance
    
    def get_positions(self) -> Dict:
        return self.positions
    
    def calculate_pnl(self) -> float:
        """Calculate total profit/loss"""
        total_pnl = 0.0
        for position in self.positions.values():
            total_pnl += position.get('pnl', 0.0)
        return total_pnl
    
    def add_trade(self, trade: Dict):
        self.trades.append(trade)
        # Update balance based on trade result
        if 'pnl' in trade:
            self.balance += trade['pnl']


class TradingEngine:
    """Core trading engine with exchange connectivity"""
    
    def __init__(self, config: dict):
        self.config = config
        self.exchange = None
        self.portfolio = Portfolio(config.get('initial_balance', 10000.0))
        self.trading_active = False
        self.market_data_cache = {}
        self.start_time = datetime.now()
        self._connected = False
    
    async def initialize(self):
        """Initialize exchange connection"""
        try:
            # Lazy import ccxt to avoid issues if not installed
            import ccxt.async_support as ccxt
            
            exchange_config = self.config.get('exchange', {})
            exchange_name = exchange_config.get('name', 'binance')
            
            # Create exchange instance
            exchange_class = getattr(ccxt, exchange_name, None)
            if exchange_class:
                self.exchange = exchange_class({
                    'apiKey': exchange_config.get('api_key', ''),
                    'secret': exchange_config.get('secret', ''),
                    'enableRateLimit': True,
                    'sandbox': exchange_config.get('sandbox', True),
                })
                
                # Load markets
                await self.exchange.load_markets()
                self._connected = True
        except ImportError:
            print("CCXT not installed. Running in mock mode.")
            self._connected = False
        except Exception as e:
            print(f"Exchange initialization error: {e}")
            self._connected = False
    
    async def get_market_data(self, symbol: str = "BTC/USDT", 
                             timeframe: str = "5m") -> List[List]:
        """Fetch OHLCV data"""
        if not self.exchange:
            # Return mock data
            return [[datetime.now().timestamp() * 1000, 50000, 50100, 49900, 50050, 100]]
        
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)
            return ohlcv
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return []
    
    async def execute_trade(self, trade_params: dict) -> dict:
        """Execute a trade based on params"""
        if not self.exchange:
            # Mock execution
            return {
                "success": True, 
                "order_id": f"mock_{datetime.now().timestamp()}",
                "message": "Mock execution (no exchange connected)"
            }
        
        try:
            symbol = trade_params['symbol']
            order_type = trade_params['order_type']  # 'buy' or 'sell'
            amount = trade_params['amount']
            price = trade_params.get('price')
            
            if order_type == 'buy':
                if price:
                    order = await self.exchange.create_limit_buy_order(symbol, amount, price)
                else:
                    order = await self.exchange.create_market_buy_order(symbol, amount)
            else:
                if price:
                    order = await self.exchange.create_limit_sell_order(symbol, amount, price)
                else:
                    order = await self.exchange.create_market_sell_order(symbol, amount)
            
            # Update portfolio
            self.portfolio.add_trade(order)
            
            return {"success": True, "order_id": order['id']}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_server_time(self) -> float:
        return datetime.now().timestamp()
    
    def is_connected(self) -> bool:
        return self._connected
    
    def get_uptime(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()
    
    async def update_config(self, new_config: dict):
        """Update configuration on the fly"""
        self.config.update(new_config)
    
    async def close(self):
        """Cleanup resources"""
        if self.exchange:
            await self.exchange.close()
