# backend/app/services/tradfi_service.py
# ==============================================
# TRADFI ADAPTER - Stocks, Gold, Commodities
# "جسر التمويل التقليدي"
# ==============================================

import yfinance as yf
from datetime import datetime
from typing import Optional, Dict, Any
from app.config import ALPACA_KEY, ALPACA_SECRET, ALPACA_ENDPOINT, DEMO_MODE, ASSET_SYMBOL_MAP

class TradFiAdapter:
    """
    TradFi (Traditional Finance) Adapter
    يتعامل مع الأسهم، الذهب، السلع، و صناديق ETF
    """
    
    def __init__(self):
        self.demo_mode = DEMO_MODE
        self.api = None
        
        # محاولة الاتصال بـ Alpaca (إذا كانت المفاتيح صالحة)
        if not self.demo_mode and ALPACA_KEY != "demo_key":
            try:
                import alpaca_trade_api as tradeapi
                self.api = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_ENDPOINT, api_version='v2')
                print("🏦 TRADFI: Connected to Alpaca API")
            except Exception as e:
                print(f"⚠️ TRADFI: Alpaca connection failed, using Demo Mode: {e}")
                self.demo_mode = True
        else:
            print("🎮 TRADFI: Running in Demo Mode")

    def get_market_price(self, symbol: str) -> Dict[str, Any]:
        """
        جلب السعر الحالي للأصل
        يستخدم yfinance للسرعة والمجانية
        """
        try:
            # تحويل الرمز إذا لزم الأمر
            trade_symbol = ASSET_SYMBOL_MAP.get(symbol.upper(), symbol)
            
            ticker = yf.Ticker(trade_symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                # Fallback to daily data
                hist = ticker.history(period="5d")
            
            if hist.empty:
                return {"error": f"No data for {symbol}"}
            
            current_price = float(hist['Close'].iloc[-1])
            open_price = float(hist['Open'].iloc[0])
            high_price = float(hist['High'].max())
            low_price = float(hist['Low'].min())
            volume = int(hist['Volume'].sum())
            
            change = current_price - open_price
            change_percent = (change / open_price) * 100 if open_price > 0 else 0
            
            return {
                "symbol": symbol,
                "trade_symbol": trade_symbol,
                "price": round(current_price, 2),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ TRADFI: Error fetching price for {symbol}: {e}")
            return {"error": str(e), "symbol": symbol}

    def get_historical_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> list:
        """
        جلب البيانات التاريخية للرسوم البيانية
        """
        try:
            trade_symbol = ASSET_SYMBOL_MAP.get(symbol.upper(), symbol)
            ticker = yf.Ticker(trade_symbol)
            hist = ticker.history(period=period, interval=interval)
            
            data = []
            for index, row in hist.iterrows():
                data.append({
                    "time": int(index.timestamp()),
                    "open": round(float(row['Open']), 2),
                    "high": round(float(row['High']), 2),
                    "low": round(float(row['Low']), 2),
                    "close": round(float(row['Close']), 2),
                    "volume": int(row['Volume'])
                })
            return data
            
        except Exception as e:
            print(f"❌ TRADFI: Error fetching historical data: {e}")
            return []

    def submit_order(
        self, 
        symbol: str, 
        side: str, 
        qty: float,
        sl_price: Optional[float] = None,
        tp_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        تنفيذ أمر شراء/بيع
        يدعم Bracket Orders مع Stop Loss و Take Profit
        """
        trade_symbol = ASSET_SYMBOL_MAP.get(symbol.upper(), symbol)
        
        print(f"🏦 TRADFI: {'[DEMO] ' if self.demo_mode else ''}Placing {side} order for {qty} of {trade_symbol}...")
        
        # في وضع Demo، نعيد استجابة وهمية ناجحة
        if self.demo_mode:
            return {
                "status": "success",
                "mode": "DEMO",
                "order_id": f"demo_{datetime.now().timestamp()}",
                "symbol": trade_symbol,
                "side": side,
                "qty": qty,
                "stop_loss": sl_price,
                "take_profit": tp_price,
                "message": "Order simulated in Demo Mode"
            }
        
        # الاتصال الحقيقي بـ Alpaca
        try:
            order_params = {
                "symbol": trade_symbol,
                "qty": qty,
                "side": side.lower(),
                "type": "market",
                "time_in_force": "gtc"
            }
            
            # إضافة Bracket Order (SL + TP)
            if sl_price and tp_price:
                order_params["order_class"] = "bracket"
                order_params["stop_loss"] = {"stop_price": str(sl_price)}
                order_params["take_profit"] = {"limit_price": str(tp_price)}
            
            order = self.api.submit_order(**order_params)
            
            return {
                "status": "success",
                "mode": "LIVE",
                "order_id": order.id,
                "symbol": trade_symbol,
                "side": side,
                "qty": qty,
                "stop_loss": sl_price,
                "take_profit": tp_price,
                "alpaca_status": order.status
            }
            
        except Exception as e:
            print(f"❌ TRADFI: Order failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_positions(self) -> list:
        """
        جلب الصفقات المفتوحة
        """
        if self.demo_mode:
            # Demo positions
            return [
                {
                    "symbol": "TSLA",
                    "qty": 10,
                    "side": "long",
                    "entry_price": 340.50,
                    "current_price": 352.30,
                    "pnl": 118.00,
                    "pnl_percent": 3.46
                },
                {
                    "symbol": "GLD",
                    "qty": 5,
                    "side": "long",
                    "entry_price": 245.00,
                    "current_price": 248.50,
                    "pnl": 17.50,
                    "pnl_percent": 1.43
                }
            ]
        
        try:
            positions = self.api.list_positions()
            return [
                {
                    "symbol": p.symbol,
                    "qty": float(p.qty),
                    "side": p.side,
                    "entry_price": float(p.avg_entry_price),
                    "current_price": float(p.current_price),
                    "pnl": float(p.unrealized_pl),
                    "pnl_percent": float(p.unrealized_plpc) * 100
                }
                for p in positions
            ]
        except Exception as e:
            print(f"❌ TRADFI: Error fetching positions: {e}")
            return []

    def close_all_positions(self) -> Dict[str, Any]:
        """
        إغلاق جميع الصفقات (زر الطوارئ)
        """
        if self.demo_mode:
            return {"status": "success", "mode": "DEMO", "message": "All positions closed (simulated)"}
        
        try:
            self.api.close_all_positions()
            return {"status": "success", "mode": "LIVE", "message": "All positions closed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
