import unittest
import sys
import json
from unittest.mock import MagicMock, AsyncMock

sys.modules['js'] = MagicMock()

from market_feed import MarketFeed

class MockKV:
    def __init__(self):
        self.store = {}
    
    async def get(self, key):
        return self.store.get(key)
    
    async def put(self, key, value, **kwargs):
        self.store[key] = value

class MockEnv:
    def __init__(self):
        self.BRAIN_MEMORY = MockKV()
        self.FINNHUB_API_KEY = "test_key"

class TestMarketFeed(unittest.TestCase):
    
    def test_init(self):
        env = MockEnv()
        feed = MarketFeed(env)
        self.assertIsNotNone(feed.kv)
        print("✅ MarketFeed init works")
    
    def test_sentiment_analysis_bullish(self):
        env = MockEnv()
        feed = MarketFeed(env)
        
        result = feed._analyze_sentiment("Markets rally as stocks surge to record highs")
        self.assertEqual(result['label'], "BULLISH")
        self.assertGreater(result['score'], 0)
        print(f"✅ Bullish sentiment: {result}")
    
    def test_sentiment_analysis_bearish(self):
        env = MockEnv()
        feed = MarketFeed(env)
        
        result = feed._analyze_sentiment("Markets crash as fear grips investors")
        self.assertEqual(result['label'], "BEARISH")
        self.assertLess(result['score'], 0)
        print(f"✅ Bearish sentiment: {result}")
    
    def test_sentiment_analysis_neutral(self):
        env = MockEnv()
        feed = MarketFeed(env)
        
        result = feed._analyze_sentiment("Markets remain unchanged today")
        self.assertEqual(result['label'], "NEUTRAL")
        print(f"✅ Neutral sentiment: {result}")
    
    def test_is_within_news_window(self):
        env = MockEnv()
        feed = MarketFeed(env)
        
        # Should handle invalid input
        result = feed._is_within_news_window("")
        self.assertFalse(result)
        result = feed._is_within_news_window("invalid")
        self.assertFalse(result)
        print("✅ News window check works")
    
    def test_check_news_impact(self):
        import asyncio
        env = MockEnv()
        feed = MarketFeed(env)
        
        async def test():
            result = await feed.check_news_impact("EURUSD")
            self.assertIn('avoid', result)
            self.assertIn('reason', result)
            print(f"✅ News impact check: avoid={result['avoid']}")
        
        asyncio.run(test())
    
    def test_get_market_context(self):
        import asyncio
        env = MockEnv()
        feed = MarketFeed(env)
        
        async def test():
            result = await feed.get_market_context("EURUSD")
            self.assertIn('symbol', result)
            self.assertIn('sentiment', result)
            self.assertIn('trading_safe', result)
            print(f"✅ Market context: trading_safe={result['trading_safe']}")
        
        asyncio.run(test())

if __name__ == '__main__':
    unittest.main()
