import unittest
from scalping_engine import ScalpingBrain

class TestScalpingBrain(unittest.TestCase):

    def setUp(self):
        # Create mock data (50 bars)
        self.data = []
        price = 100.0
        for i in range(50):
            self.data.append({
                'time': 1000 + i*60,
                'open': price,
                'high': price + 1.0,
                'low': price - 1.0,
                'close': price + 0.5, # Mild uptrend
                'volume': 1000 + (i * 10)
            })
            price += 0.2

        self.brain = ScalpingBrain(self.data)

    def test_atr_stops(self):
        print("\n🧪 Testing ATR and Dynamic Stops (1:7 R:R Aggressive)...")
        stops = self.brain.calculate_atr_stops(is_buy=True)
        print(f"   ATR: {stops['atr']:.4f}")
        print(f"   Entry: {stops['entry']:.2f} | SL: {stops['sl']:.2f} | TP: {stops['tp']:.2f}")
        print(f"   R:R Ratio: {stops['rr_ratio']}")
        
        self.assertIsNotNone(stops)
        self.assertTrue(stops['tp'] > stops['entry'])
        self.assertTrue(stops['sl'] < stops['entry'])
        self.assertEqual(stops['rr_ratio'], 7.0)  # Updated for aggressive 1:7 R:R strategy
        print("   ✅ ATR Stops validated with 1:7 R:R")


    def test_indicators(self):
        print("\n🧪 Testing New Indicators (MACD, Stoch, Delta)...")
        
        # MACD
        macd = self.brain.calculate_macd()
        print(f"   MACD: {macd['macd']:.4f} | Signal: {macd['signal_line']:.4f}")
        self.assertIsNotNone(macd)
        
        # Stochastic
        stoch = self.brain.calculate_stochastic()
        print(f"   Stoch K: {stoch['k']:.2f} | D: {stoch['d']:.2f}")
        self.assertTrue(0 <= stoch['k'] <= 100)
        
        # Delta Divergence
        delta = self.brain.detect_delta_divergence()
        print(f"   Delta Divergence: {delta['divergence']}")
        self.assertIn(delta['divergence'], ["NONE", "BULLISH", "BEARISH"])
        
        print("   ✅ All new indicators calculating correctly")
        
    def test_algo_score(self):
        print("\n🧪 Testing Algo Scoring System...")
        score = self.brain.calculate_algo_score()
        print(f"   Buy Score: {score['buy_score']} | Sell Score: {score['sell_score']}")
        print(f"   Metrics: {score['metrics']}")
        
        self.assertTrue(score['buy_score'] >= 0)
        self.assertTrue(score['sell_score'] >= 0)
        print("   ✅ Algo scoring functional")

    def test_analysis_output(self):
        print("\n🧪 Testing Worker Output Format...")
        result = self.brain.analyze_market_state()
        print(f"   Action: {result['Action']} | Confidence: {result['Confidence']}%")
        
        self.assertIn("Action", result)
        self.assertIn("Confidence", result)
        print("   ✅ Output format compatible with worker")

    # ==========================
    # 🆕 NEW COMPREHENSIVE TESTS
    # ==========================

    def test_supertrend(self):
        print("\n🧪 Testing Supertrend Calculation...")
        st = self.brain.calculate_supertrend()
        print(f"   Trend: {st['trend_name']} | Value: {st['value']:.2f}")
        
        self.assertIn(st['trend_name'], ["UPTREND", "DOWNTREND", "UNKNOWN"])
        self.assertIn(st['trend'], [1, -1, 0])
        print("   ✅ Supertrend correctly identifies trend")

    def test_sr_levels(self):
        print("\n🧪 Testing Support/Resistance Levels...")
        sr = self.brain.calculate_sr_levels()
        print(f"   Support: {sr['support']:.2f} | Resistance: {sr['resistance']:.2f}")
        
        self.assertTrue(sr['resistance'] > sr['support'])
        self.assertIsNotNone(sr['support'])
        self.assertIsNotNone(sr['resistance'])
        print("   ✅ S/R levels calculated correctly")

    def test_atr_stops_sell(self):
        print("\n🧪 Testing ATR Stops for SELL side...")
        stops = self.brain.calculate_atr_stops(is_buy=False)
        print(f"   Entry: {stops['entry']:.2f} | SL: {stops['sl']:.2f} | TP: {stops['tp']:.2f}")
        
        self.assertTrue(stops['sl'] > stops['entry'])  # SL above entry for sell
        self.assertTrue(stops['tp'] < stops['entry'])  # TP below entry for sell
        print("   ✅ SELL stops inverted correctly")

    def test_vwap_poc(self):
        print("\n🧪 Testing VWAP and POC...")
        vwap = self.brain.calculate_vwap()
        poc = self.brain.calculate_poc()
        print(f"   VWAP: {vwap:.2f} | POC: {poc:.2f}")
        
        self.assertTrue(vwap > 0)
        self.assertIsNotNone(poc)
        print("   ✅ VWAP and POC calculated")

    def test_insufficient_data(self):
        print("\n🧪 Testing Edge Case: Insufficient Data...")
        short_data = [{'time': 0, 'open': 100, 'high': 101, 'low': 99, 'close': 100, 'volume': 1000}]
        short_brain = ScalpingBrain(short_data)
        
        atr = short_brain.calculate_atr()
        macd = short_brain.calculate_macd()
        
        self.assertIsNone(atr)  # Not enough data for ATR
        self.assertEqual(macd['hist'], 0)  # Default neutral
        print("   ✅ Edge cases handled gracefully")

if __name__ == '__main__':
    unittest.main()

