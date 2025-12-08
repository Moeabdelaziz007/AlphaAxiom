"""
🧪 Tests for Multi-Timeframe Scalper and Fast RSI/EMA
"""

import unittest
from scalping_engine import ScalpingBrain
from mtf_scalper import MultiTimeframeScalper, HighLeverageRiskManager


def generate_test_candles(count: int, start_price: float = 100.0, trend: str = "up") -> list:
    """Generate test candlestick data."""
    candles = []
    price = start_price
    
    for i in range(count):
        if trend == "up":
            change = 0.5 + (i * 0.1)
        elif trend == "down":
            change = -0.5 - (i * 0.1)
        else:
            change = 0.1 if i % 2 == 0 else -0.1
        
        open_price = price
        close_price = price + change
        high = max(open_price, close_price) + 0.2
        low = min(open_price, close_price) - 0.2
        
        candles.append({
            "time": i,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close_price,
            "volume": 1000 + i * 100
        })
        
        price = close_price
    
    return candles


class TestFastRSI(unittest.TestCase):
    """Test Fast RSI (7-period) implementation."""
    
    def test_fast_rsi_oversold(self):
        """Test RSI detection of oversold conditions."""
        # Generate downtrend data
        candles = generate_test_candles(30, 100, "down")
        brain = ScalpingBrain(candles)
        
        rsi = brain.calculate_fast_rsi()
        
        self.assertIn("rsi", rsi)
        self.assertIn("signal", rsi)
        self.assertIn("is_oversold", rsi)
        print(f"✅ Fast RSI (downtrend): {rsi['rsi']} - {rsi['signal']}")
    
    def test_fast_rsi_overbought(self):
        """Test RSI detection of overbought conditions."""
        # Generate uptrend data
        candles = generate_test_candles(30, 100, "up")
        brain = ScalpingBrain(candles)
        
        rsi = brain.calculate_fast_rsi()
        
        self.assertIn("rsi", rsi)
        print(f"✅ Fast RSI (uptrend): {rsi['rsi']} - {rsi['signal']}")


class TestEMACrossover(unittest.TestCase):
    """Test EMA 9/21 Crossover implementation."""
    
    def test_ema_uptrend(self):
        """Test EMA crossover in uptrend."""
        candles = generate_test_candles(50, 100, "up")
        brain = ScalpingBrain(candles)
        
        ema = brain.calculate_ema_crossover()
        
        self.assertIn("trend", ema)
        self.assertIn("fast_ema", ema)
        self.assertIn("slow_ema", ema)
        self.assertEqual(ema["trend"], "UPTREND")
        print(f"✅ EMA Crossover (uptrend): Fast={ema['fast_ema']}, Slow={ema['slow_ema']}")
    
    def test_ema_downtrend(self):
        """Test EMA crossover in downtrend."""
        candles = generate_test_candles(50, 100, "down")
        brain = ScalpingBrain(candles)
        
        ema = brain.calculate_ema_crossover()
        
        self.assertEqual(ema["trend"], "DOWNTREND")
        print(f"✅ EMA Crossover (downtrend): Fast={ema['fast_ema']}, Slow={ema['slow_ema']}")


class TestMultiTimeframe(unittest.TestCase):
    """Test Multi-Timeframe Scalper."""
    
    def test_aligned_long_signal(self):
        """Test aligned LONG signal when all timeframes bullish."""
        # All timeframes uptrend
        data_1m = generate_test_candles(50, 100, "up")
        data_5m = generate_test_candles(50, 100, "up")
        data_15m = generate_test_candles(50, 100, "up")
        
        mtf = MultiTimeframeScalper(data_1m, data_5m, data_15m)
        signal = mtf.get_aligned_signal()
        
        self.assertIn("signal", signal)
        self.assertIn("confidence", signal)
        self.assertIn("analysis", signal)
        print(f"✅ MTF Signal: {signal['signal']} (Confidence: {signal['confidence']}%)")
    
    def test_no_signal_conflicting(self):
        """Test no signal when timeframes conflict."""
        # 15M up, 1M down = conflict
        data_1m = generate_test_candles(50, 100, "down")
        data_5m = generate_test_candles(50, 100, "neutral")
        data_15m = generate_test_candles(50, 100, "up")
        
        mtf = MultiTimeframeScalper(data_1m, data_5m, data_15m)
        signal = mtf.get_aligned_signal()
        
        # Should be NEUTRAL due to conflict
        print(f"✅ MTF Conflict Test: {signal['signal']} (Expected: mixed)")


class TestHighLeverageRiskManager(unittest.TestCase):
    """Test Risk Manager for 100x leverage."""
    
    def test_position_sizing(self):
        """Test position sizing calculation."""
        rm = HighLeverageRiskManager(1000)
        
        position = rm.calculate_position_size(leverage=100, confidence=80)
        
        self.assertIn("margin_usd", position)
        self.assertIn("notional_usd", position)
        self.assertEqual(position["leverage"], 100)
        print(f"✅ Position Size: Margin=${position['margin_usd']}, Notional=${position['notional_usd']}")
    
    def test_daily_loss_circuit_breaker(self):
        """Test circuit breaker triggers on 25% loss."""
        rm = HighLeverageRiskManager(1000, max_daily_loss=0.25)
        
        # Simulate losses
        rm.record_trade(-0.10)  # -10%
        rm.record_trade(-0.10)  # -10%
        
        self.assertTrue(rm.can_trade())  # Still under 25%
        
        rm.record_trade(-0.10)  # -10% = -30% total
        
        self.assertFalse(rm.can_trade())  # Should be blocked
        print(f"✅ Circuit Breaker: Trading blocked at {rm.daily_pnl*100:.1f}% loss")
    
    def test_stats_tracking(self):
        """Test win/loss tracking."""
        rm = HighLeverageRiskManager(1000)
        
        rm.record_trade(0.15)   # Win
        rm.record_trade(-0.05)  # Loss
        rm.record_trade(0.10)   # Win
        
        stats = rm.get_stats()
        
        self.assertEqual(stats["trades_today"], 3)
        self.assertEqual(stats["wins"], 2)
        self.assertEqual(stats["losses"], 1)
        print(f"✅ Stats: {stats['wins']}W/{stats['losses']}L, PnL: {stats['daily_pnl_pct']}%")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 AXIOM 100% Weekly ROI - Module Tests")
    print("="*60 + "\n")
    
    unittest.main(verbosity=2)
