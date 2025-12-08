"""
🚀 Multi-Timeframe Scalper for 100% Weekly ROI
Combines 1M, 5M, 15M analysis for high-probability trades.

STRATEGY:
- 15M: Trend direction (EMA 9/21 + SuperTrend)
- 5M: Momentum confirmation (Fast RSI + Stochastic)
- 1M: Precise entry (MACD + Rejection Candles)

TARGET: 100% Weekly ROI with 100x Leverage
"""

from scalping_engine import ScalpingBrain


class MultiTimeframeScalper:
    """
    Multi-Timeframe Scalping Strategy for Crypto Derivatives.
    
    Flow:
    1. Check 15M trend (only trade in trend direction)
    2. Wait for 5M momentum confirmation
    3. Enter on 1M precise signal
    4. Exit on ATR-based TP/SL (1:2.5 R:R)
    """
    
    # Leverage Settings
    DEFAULT_LEVERAGE = 100
    MAX_POSITION_PCT = 0.20  # 20% of account per trade
    MAX_DAILY_LOSS = 0.25    # 25% max daily drawdown
    
    def __init__(self, data_1m: list, data_5m: list, data_15m: list):
        """
        Initialize with data from all three timeframes.
        
        Args:
            data_1m: List of 1-minute candles
            data_5m: List of 5-minute candles  
            data_15m: List of 15-minute candles
        """
        self.tf_1m = ScalpingBrain(data_1m)
        self.tf_5m = ScalpingBrain(data_5m)
        self.tf_15m = ScalpingBrain(data_15m)
        
        self.current_price = data_1m[-1]['close'] if data_1m else 0
    
    def get_aligned_signal(self, leverage: int = None) -> dict:
        """
        Generate trading signal only when all timeframes align.
        
        Returns:
            dict: {
                'signal': 'LONG' | 'SHORT' | 'NEUTRAL',
                'confidence': 0-100,
                'entry': float,
                'stop_loss': float,
                'take_profit': float,
                'leverage': int,
                'analysis': dict
            }
        """
        leverage = leverage or self.DEFAULT_LEVERAGE
        
        # Step 1: 15M Trend
        trend_15m = self.tf_15m.get_trend()
        ema_15m = self.tf_15m.calculate_ema_crossover()
        
        # Step 2: 5M Momentum
        momentum_5m = self.tf_5m.get_momentum_signal()
        rsi_5m = self.tf_5m.calculate_fast_rsi()
        
        # Step 3: 1M Entry
        entry_1m = self.tf_1m.get_entry_signal()
        macd_1m = self.tf_1m.calculate_macd()
        
        # Build analysis object
        analysis = {
            "15m": {
                "trend": trend_15m,
                "ema_trend": ema_15m['trend'],
                "ema_gap": ema_15m['gap_pct']
            },
            "5m": {
                "momentum": momentum_5m,
                "rsi": rsi_5m['rsi'],
                "rsi_signal": rsi_5m['signal']
            },
            "1m": {
                "entry": entry_1m,
                "macd_bullish": macd_1m['bullish'],
                "macd_bearish": macd_1m['bearish']
            }
        }
        
        # Alignment Check
        signal = "NEUTRAL"
        confidence = 0
        
        # LONG Signal: All bullish alignment
        if trend_15m == "BULL" and momentum_5m in ["BULL", "NEUTRAL"] and entry_1m == "BULL":
            signal = "LONG"
            confidence = self._calculate_confidence(trend_15m, momentum_5m, entry_1m, "BULL")
            
        # SHORT Signal: All bearish alignment
        elif trend_15m == "BEAR" and momentum_5m in ["BEAR", "NEUTRAL"] and entry_1m == "BEAR":
            signal = "SHORT"
            confidence = self._calculate_confidence(trend_15m, momentum_5m, entry_1m, "BEAR")
        
        # Calculate stops
        stops = self._calculate_stops(signal, leverage)
        
        return {
            "signal": signal,
            "confidence": confidence,
            "entry": stops["entry"],
            "stop_loss": stops["stop_loss"],
            "take_profit": stops["take_profit"],
            "leverage": leverage,
            "position_size_pct": self.MAX_POSITION_PCT if confidence >= 70 else self.MAX_POSITION_PCT * 0.5,
            "analysis": analysis,
            "aligned": signal != "NEUTRAL"
        }
    
    def _calculate_confidence(self, trend: str, momentum: str, entry: str, direction: str) -> int:
        """Calculate confidence score 0-100 based on alignment quality."""
        score = 0
        
        # Trend alignment (40 points max)
        if trend == direction:
            score += 40
        
        # Momentum alignment (30 points max)
        if momentum == direction:
            score += 30
        elif momentum == "NEUTRAL":
            score += 15
        
        # Entry alignment (30 points max)
        if entry == direction:
            score += 30
        
        return min(100, score)
    
    def _calculate_stops(self, signal: str, leverage: int) -> dict:
        """Calculate entry, stop-loss, and take-profit levels."""
        if signal == "NEUTRAL":
            return {"entry": 0, "stop_loss": 0, "take_profit": 0}
        
        atr_stops = self.tf_1m.calculate_atr_stops(is_buy=(signal == "LONG"))
        
        if not atr_stops:
            return {"entry": self.current_price, "stop_loss": 0, "take_profit": 0}
        
        return {
            "entry": atr_stops["entry"],
            "stop_loss": atr_stops["sl"],
            "take_profit": atr_stops["tp"],
            "atr": atr_stops["atr"],
            "rr_ratio": atr_stops["rr_ratio"]
        }
    
    def get_quick_scalp(self, direction: str = None) -> dict:
        """
        Get a quick scalp opportunity without waiting for perfect alignment.
        Uses 1M and 5M only for faster signals.
        
        Args:
            direction: 'LONG' or 'SHORT' - force direction based on higher TF
        """
        momentum = self.tf_5m.get_momentum_signal()
        entry = self.tf_1m.get_entry_signal()
        rsi = self.tf_1m.calculate_fast_rsi()
        
        signal = "NEUTRAL"
        confidence = 0
        
        if direction == "LONG" or (momentum == "BULL" and entry == "BULL"):
            if rsi['is_oversold'] or rsi['signal'] == "WEAK_OVERSOLD":
                signal = "LONG"
                confidence = 60 + (30 - rsi['rsi']) if rsi['rsi'] < 30 else 60
                
        elif direction == "SHORT" or (momentum == "BEAR" and entry == "BEAR"):
            if rsi['is_overbought'] or rsi['signal'] == "WEAK_OVERBOUGHT":
                signal = "SHORT"
                confidence = 60 + (rsi['rsi'] - 70) if rsi['rsi'] > 70 else 60
        
        stops = self._calculate_stops(signal, self.DEFAULT_LEVERAGE)
        
        return {
            "signal": signal,
            "confidence": min(100, int(confidence)),
            "type": "QUICK_SCALP",
            **stops
        }


class HighLeverageRiskManager:
    """
    Risk Manager for 100x Leverage Trading.
    Tracks daily P&L and enforces circuit breakers.
    """
    
    def __init__(self, account_balance: float, max_daily_loss: float = 0.25):
        self.initial_balance = account_balance
        self.current_balance = account_balance
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0
        self.trades_today = 0
        self.wins = 0
        self.losses = 0
    
    def can_trade(self) -> bool:
        """Check if trading is allowed (daily loss limit not hit)."""
        return self.daily_pnl > -self.max_daily_loss
    
    def calculate_position_size(self, 
                                 leverage: int = 100,
                                 max_position_pct: float = 0.20,
                                 confidence: int = 70) -> dict:
        """
        Calculate optimal position size with Kelly-like adjustment.
        """
        # Adjust position based on confidence
        confidence_multiplier = confidence / 100
        adjusted_pct = max_position_pct * confidence_multiplier
        
        # Cap at max
        position_pct = min(adjusted_pct, max_position_pct)
        
        # Calculate amounts
        margin = self.current_balance * position_pct
        notional = margin * leverage
        
        return {
            "margin_usd": round(margin, 2),
            "notional_usd": round(notional, 2),
            "position_pct": round(position_pct * 100, 2),
            "leverage": leverage,
            "max_loss_usd": round(margin, 2),  # Max loss = margin (liquidation)
            "trading_allowed": self.can_trade()
        }
    
    def record_trade(self, pnl_pct: float):
        """Record a completed trade."""
        self.daily_pnl += pnl_pct
        self.trades_today += 1
        
        if pnl_pct > 0:
            self.wins += 1
        else:
            self.losses += 1
        
        self.current_balance *= (1 + pnl_pct)
    
    def get_stats(self) -> dict:
        """Get current session statistics."""
        win_rate = (self.wins / self.trades_today * 100) if self.trades_today > 0 else 0
        
        return {
            "initial_balance": self.initial_balance,
            "current_balance": round(self.current_balance, 2),
            "daily_pnl_pct": round(self.daily_pnl * 100, 2),
            "trades_today": self.trades_today,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": round(win_rate, 1),
            "can_trade": self.can_trade(),
            "remaining_risk": round((self.max_daily_loss + self.daily_pnl) * 100, 2)
        }
    
    def reset_daily(self):
        """Reset daily counters (call at start of each trading day)."""
        self.initial_balance = self.current_balance
        self.daily_pnl = 0
        self.trades_today = 0
        self.wins = 0
        self.losses = 0
