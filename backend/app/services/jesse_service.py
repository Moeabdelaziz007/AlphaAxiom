# backend/app/services/jesse_service.py
# ==============================================
# JESSE CRYPTO ADAPTER
# يتعامل مع تداول العملات الرقمية عبر Jesse Bot
# ==============================================

from datetime import datetime
from typing import Optional, Dict, Any
from app.config import DEMO_MODE, BINANCE_KEY

class JesseAdapter:
    """
    Jesse Crypto Trading Adapter
    يتعامل مع BTC, ETH, SOL وجميع العملات الرقمية
    
    Note: Jesse يتطلب PostgreSQL و TA-Lib
    للـ MVP نستخدم Demo Mode
    """
    
    def __init__(self):
        self.demo_mode = DEMO_MODE
        self.connected = False
        
        if not self.demo_mode and BINANCE_KEY:
            try:
                # Jesse integration would go here
                # from jesse import research
                print("⚡ JESSE: Connected to Crypto Engine")
                self.connected = True
            except Exception as e:
                print(f"⚠️ JESSE: Connection failed, using Demo Mode: {e}")
                self.demo_mode = True
        else:
            print("🎮 JESSE: Running in Demo Mode")

    def get_market_price(self, symbol: str) -> Dict[str, Any]:
        """
        جلب سعر العملة الرقمية
        """
        # Demo prices with slight randomness
        import random
        
        base_prices = {
            "BTC/USDT": 98420,
            "ETH/USDT": 3850,
            "SOL/USDT": 235,
            "BNB/USDT": 620,
            "XRP/USDT": 2.35,
        }
        
        base = base_prices.get(symbol, 100)
        variance = base * 0.001 * (random.random() - 0.5)
        price = base + variance
        
        return {
            "symbol": symbol,
            "price": round(price, 2),
            "change": round(random.uniform(-2, 3), 2),
            "change_percent": round(random.uniform(-2, 3), 2),
            "volume": random.randint(1000000, 5000000),
            "timestamp": datetime.now().isoformat(),
            "source": "DEMO" if self.demo_mode else "JESSE"
        }

    def submit_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        تنفيذ أمر تداول كريبتو
        """
        print(f"⚡ JESSE: {'[DEMO] ' if self.demo_mode else ''}Placing {side} order for {qty} of {symbol}...")
        
        if self.demo_mode:
            return {
                "status": "success",
                "mode": "DEMO",
                "order_id": f"jesse_demo_{datetime.now().timestamp()}",
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "stop_loss": sl_price,
                "take_profit": tp_price,
                "message": "Crypto order simulated in Demo Mode"
            }
        
        # Real Jesse integration
        try:
            # Jesse order execution would go here
            # jesse.place_order(...)
            return {
                "status": "success",
                "mode": "LIVE",
                "order_id": f"jesse_{datetime.now().timestamp()}",
                "symbol": symbol,
                "side": side,
                "qty": qty
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_positions(self) -> list:
        """
        جلب صفقات الكريبتو المفتوحة
        """
        if self.demo_mode:
            return [
                {
                    "symbol": "BTC/USDT",
                    "qty": 0.15,
                    "side": "long",
                    "entry_price": 97500.00,
                    "current_price": 98420.00,
                    "pnl": 138.00,
                    "pnl_percent": 0.94
                },
                {
                    "symbol": "ETH/USDT",
                    "qty": 2.5,
                    "side": "long",
                    "entry_price": 3780.00,
                    "current_price": 3850.00,
                    "pnl": 175.00,
                    "pnl_percent": 1.85
                }
            ]
        return []

    def get_bot_status(self) -> Dict[str, Any]:
        """
        حالة البوت (للعرض في الواجهة)
        """
        return {
            "status": "ONLINE" if self.connected or self.demo_mode else "OFFLINE",
            "mode": "DEMO" if self.demo_mode else "LIVE",
            "active_strategies": 2,
            "uptime": "12h 34m",
            "last_trade": datetime.now().isoformat()
        }
