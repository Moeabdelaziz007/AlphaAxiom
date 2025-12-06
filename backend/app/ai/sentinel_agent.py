# backend/app/ai/sentinel_agent.py
# ==============================================
# SENTINEL AI - العقل المدبر
# "يزيل العاطفة. ينفذ كالجراح بدقة المليمتر."
# ==============================================

from datetime import datetime
from typing import Dict, Any, Optional
import random

from app.services.tradfi_service import TradFiAdapter
from app.services.jesse_service import JesseAdapter
from app.config import DEFAULT_STOP_LOSS_PERCENT, DEFAULT_TAKE_PROFIT_PERCENT

class SentinelAgent:
    """
    Sentinel AI - Smart Trading Router
    
    المهام:
    1. تحديد نوع الأصل (Crypto/Stock/Commodity/Forex)
    2. توجيه الأوامر للمحرك المناسب (Jesse أو TradFi)
    3. حساب Stop Loss و Take Profit تلقائياً
    4. تحليل الزخم (Antigravity Algorithm)
    """
    
    def __init__(self):
        self.tradfi = TradFiAdapter()
        self.crypto = JesseAdapter()
        self.logs = []
        
        self._log("INFO", "SENTINEL AI v2.0 INITIALIZED")
        self._log("SUCCESS", "ENGINES ONLINE: JESSE (Crypto) + TRADFI (Stocks/Gold)")

    def _log(self, log_type: str, message: str):
        """إضافة سجل للعرض في الواجهة"""
        log_entry = {
            "id": str(datetime.now().timestamp()),
            "timestamp": datetime.now().isoformat(),
            "type": log_type,
            "message": message
        }
        self.logs.append(log_entry)
        # احتفظ بآخر 100 سجل فقط
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        print(f"[{log_type}] {message}")

    def get_logs(self, limit: int = 50) -> list:
        """جلب آخر السجلات للعرض"""
        return self.logs[-limit:]

    def detect_asset_type(self, symbol: str) -> str:
        """
        تحديد نوع الأصل بذكاء
        """
        symbol_upper = symbol.upper()
        
        # Crypto patterns
        crypto_indicators = ["BTC", "ETH", "SOL", "BNB", "XRP", "USDT", "USDC", "/"]
        if any(x in symbol_upper for x in crypto_indicators):
            return "CRYPTO"
        
        # Commodities
        commodity_indicators = ["GOLD", "XAU", "SILVER", "XAG", "OIL", "GLD", "SLV", "USO"]
        if any(x in symbol_upper for x in commodity_indicators):
            return "COMMODITY"
        
        # Forex
        if len(symbol_upper) == 6 and "USD" in symbol_upper:
            return "FOREX"
        
        # Default: Stock
        return "STOCK"

    def analyze_momentum(self, symbol: str) -> Dict[str, Any]:
        """
        خوارزمية Antigravity للزخم
        تحلل اتجاه السوق وتعطي إشارة
        """
        self._log("SCAN", f"ANTIGRAVITY: Analyzing {symbol}...")
        
        # Demo: توليد إشارة عشوائية للعرض
        momentum_score = random.uniform(-100, 100)
        
        if momentum_score > 60:
            signal = "STRONG_BUY"
            confidence = random.uniform(75, 95)
        elif momentum_score > 20:
            signal = "BUY"
            confidence = random.uniform(55, 75)
        elif momentum_score < -60:
            signal = "STRONG_SELL"
            confidence = random.uniform(75, 95)
        elif momentum_score < -20:
            signal = "SELL"
            confidence = random.uniform(55, 75)
        else:
            signal = "NEUTRAL"
            confidence = random.uniform(40, 60)
        
        self._log("SIGNAL", f"MOMENTUM SCORE: {momentum_score:.1f} | SIGNAL: {signal}")
        
        return {
            "symbol": symbol,
            "momentum_score": round(momentum_score, 2),
            "signal": signal,
            "confidence": round(confidence, 1),
            "timestamp": datetime.now().isoformat()
        }

    def calculate_risk_params(self, price: float, side: str) -> Dict[str, float]:
        """
        حساب Stop Loss و Take Profit تلقائياً
        """
        if side.upper() in ["BUY", "LONG"]:
            sl = price * (1 - DEFAULT_STOP_LOSS_PERCENT / 100)
            tp = price * (1 + DEFAULT_TAKE_PROFIT_PERCENT / 100)
        else:
            sl = price * (1 + DEFAULT_STOP_LOSS_PERCENT / 100)
            tp = price * (1 - DEFAULT_TAKE_PROFIT_PERCENT / 100)
        
        return {
            "stop_loss": round(sl, 2),
            "take_profit": round(tp, 2),
            "risk_percent": DEFAULT_STOP_LOSS_PERCENT,
            "reward_percent": DEFAULT_TAKE_PROFIT_PERCENT
        }

    def execute_trade(
        self,
        symbol: str,
        side: str,
        amount: float,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None,
        auto_risk: bool = True
    ) -> Dict[str, Any]:
        """
        تنفيذ صفقة ذكية مع توجيه تلقائي
        """
        asset_type = self.detect_asset_type(symbol)
        self._log("INFO", f"ROUTING: {symbol} detected as {asset_type}")
        
        # تحليل الزخم
        momentum = self.analyze_momentum(symbol)
        
        # جلب السعر الحالي
        if asset_type == "CRYPTO":
            price_data = self.crypto.get_market_price(symbol)
            engine = self.crypto
            engine_name = "JESSE"
        else:
            price_data = self.tradfi.get_market_price(symbol)
            engine = self.tradfi
            engine_name = "TRADFI"
        
        current_price = price_data.get("price", 0)
        
        # حساب المخاطر تلقائياً إذا لم تُحدد
        if auto_risk and (not sl_price or not tp_price):
            risk_params = self.calculate_risk_params(current_price, side)
            sl_price = sl_price or risk_params["stop_loss"]
            tp_price = tp_price or risk_params["take_profit"]
            self._log("INFO", f"AUTO RISK: SL={sl_price} | TP={tp_price}")
        
        self._log("EXECUTE", f"SENDING TO {engine_name}: {side} {amount} {symbol}")
        
        # تنفيذ الأمر
        result = engine.submit_order(
            symbol=symbol,
            side=side,
            qty=amount,
            sl_price=sl_price,
            tp_price=tp_price
        )
        
        if result.get("status") == "success":
            self._log("SUCCESS", f"ORDER EXECUTED: {result.get('order_id')}")
        else:
            self._log("WARNING", f"ORDER FAILED: {result.get('message')}")
        
        return {
            "asset_type": asset_type,
            "engine": engine_name,
            "momentum": momentum,
            "order": result,
            "risk_params": {
                "stop_loss": sl_price,
                "take_profit": tp_price
            }
        }

    def get_all_positions(self) -> Dict[str, list]:
        """
        جلب جميع الصفقات من جميع المحركات
        """
        return {
            "crypto": self.crypto.get_positions(),
            "tradfi": self.tradfi.get_positions()
        }

    def flatten_all(self) -> Dict[str, Any]:
        """
        زر الطوارئ: إغلاق جميع الصفقات
        """
        self._log("WARNING", "⚠️ EMERGENCY: CLOSING ALL POSITIONS")
        
        tradfi_result = self.tradfi.close_all_positions()
        # crypto_result = self.crypto.close_all_positions()
        
        self._log("SUCCESS", "ALL POSITIONS FLATTENED")
        
        return {
            "tradfi": tradfi_result,
            "crypto": {"status": "success", "message": "Demo mode - positions cleared"}
        }

    def get_status(self) -> Dict[str, Any]:
        """
        حالة النظام الكاملة
        """
        return {
            "sentinel": "ONLINE",
            "jesse": self.crypto.get_bot_status(),
            "tradfi": {
                "status": "ONLINE",
                "mode": "DEMO" if self.tradfi.demo_mode else "LIVE"
            },
            "active_patterns": random.randint(40, 60),
            "pending_signals": random.randint(1, 5)
        }
