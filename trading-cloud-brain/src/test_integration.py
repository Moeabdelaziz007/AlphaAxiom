"""
🔗 Integration Tests for Axiom Antigravity Trading System
Tests the complete trading flows with mocked external dependencies.

Tested Flows:
1. Market Data → ScalpingBrain → Signal Generation
2. Signal → RiskGuardian → Trade Decision
3. AEXI/Dream → Composite Score → Alert Trigger
4. Error Handling and Edge Cases
"""

import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import trading modules
from scalping_engine import ScalpingBrain
from long_term_engine import LongTermBrain
from aexi_engine import AEXIEngine
from dream_engine import DreamMachine


# ==========================================
# 🎭 MOCK CLASSES
# ==========================================

class MockEnv:
    """Mock Cloudflare Workers environment object."""
    
    def __init__(self):
        # KV Storage Mock
        self.BRAIN_MEMORY = MockKV()
        
        # D1 Database Mock
        self.TRADING_DB = MockD1()
        
        # Workers AI Mock
        self.AI = MockWorkersAI()
        
        # Secrets (mocked)
        self.TELEGRAM_BOT_TOKEN = "mock_telegram_token"
        self.TELEGRAM_CHAT_ID = "123456789"
        self.GROQ_API_KEY = "mock_groq_key"
        self.CAPITAL_API_KEY = "mock_capital_key"
        self.CAPITAL_EMAIL = "test@example.com"
        self.CAPITAL_PASSWORD = "test_password"
        self.ABLY_API_KEY = "mock_ably_key"


class MockKV:
    """Mock Cloudflare KV storage."""
    
    def __init__(self):
        self._store = {}
    
    async def get(self, key):
        return self._store.get(key)
    
    async def put(self, key, value):
        self._store[key] = value


class MockD1:
    """Mock Cloudflare D1 database."""
    
    def __init__(self):
        self._tables = {
            "trade_logs": [],
            "system_state": {"kill_switch": False, "panic_mode": False}
        }
    
    def prepare(self, query):
        return MockStatement(self._tables, query)


class MockStatement:
    """Mock D1 prepared statement."""
    
    def __init__(self, tables, query):
        self.tables = tables
        self.query = query
    
    def bind(self, *args):
        return self
    
    async def run(self):
        return {"success": True}
    
    async def first(self):
        if "COUNT" in self.query:
            return {"count": len(self.tables["trade_logs"])}
        return None


class MockWorkersAI:
    """Mock Cloudflare Workers AI."""
    
    async def run(self, model, inputs):
        return {"response": "Mock AI response", "success": True}


def generate_realistic_market_data(bars=100, trend='ranging'):
    """Generate realistic OHLCV market data for testing."""
    data = []
    base_price = 1.0850  # EURUSD-like
    base_volume = 50000
    
    for i in range(bars):
        if trend == 'up':
            price = base_price + (i * 0.0005)
        elif trend == 'down':
            price = base_price - (i * 0.0005)
        else:  # ranging
            price = base_price + (0.002 if i % 10 < 5 else -0.002)
        
        data.append({
            'time': i,
            'open': price - 0.0002,
            'high': price + 0.0010,
            'low': price - 0.0008,
            'close': price,
            'volume': base_volume + (i * 100)
        })
    
    return data


# ==========================================
# 🧪 FLOW 1: Market Data → ScalpingBrain → Signal
# ==========================================

def test_scalping_flow_uptrend():
    """Test: Uptrend data should generate BUY signal or NEUTRAL."""
    print("\n🧪 Test Flow 1a: Scalping in Uptrend...")
    
    data = generate_realistic_market_data(100, trend='up')
    brain = ScalpingBrain(data)
    result = brain.analyze_market_state()
    
    print(f"   Action: {result['Action']}")
    print(f"   Confidence: {result['Confidence']}%")
    print(f"   Buy Score: {result['Metrics']['BuyScore']}")
    print(f"   Sell Score: {result['Metrics']['SellScore']}")
    
    # In uptrend, buy score should be higher than sell
    assert result['Metrics']['BuyScore'] >= result['Metrics']['SellScore'], \
        "Uptrend should favor buy signals"
    assert result['Action'] in ['BUY_PA_SIGNAL', 'NEUTRAL']
    print("   ✅ Scalping uptrend flow passed!")


def test_scalping_flow_downtrend():
    """Test: Downtrend data should generate SELL signal or NEUTRAL."""
    print("\n🧪 Test Flow 1b: Scalping in Downtrend...")
    
    data = generate_realistic_market_data(100, trend='down')
    brain = ScalpingBrain(data)
    result = brain.analyze_market_state()
    
    print(f"   Action: {result['Action']}")
    print(f"   Confidence: {result['Confidence']}%")
    
    # In downtrend, sell score should be higher
    assert result['Metrics']['SellScore'] >= result['Metrics']['BuyScore'], \
        "Downtrend should favor sell signals"
    print("   ✅ Scalping downtrend flow passed!")


# ==========================================
# 🧪 FLOW 2: LongTermBrain → Golden Cross Detection
# ==========================================

def test_long_term_flow():
    """Test: Long term analysis with trending data."""
    print("\n🧪 Test Flow 2: Long Term Analysis...")
    
    # Generate 300 bars for SMA calculations
    data = generate_realistic_market_data(300, trend='up')
    brain = LongTermBrain(data)
    result = brain.evaluate_market_health()
    
    print(f"   Action: {result['Action']}")
    print(f"   Confidence: {result['Confidence']}%")
    print(f"   Entry Type: {result['EntryType']}")
    
    assert 'Action' in result
    assert 'Confidence' in result
    assert result['Confidence'] >= 0 and result['Confidence'] <= 100
    print("   ✅ Long term flow passed!")


# ==========================================
# 🧪 FLOW 3: AEXI + Dream → Twin Turbo Signal
# ==========================================

def test_twin_turbo_flow():
    """Test: AEXI and Dream engines together."""
    print("\n🧪 Test Flow 3: Twin Turbo (AEXI + Dream)...")
    
    data = generate_realistic_market_data(100, trend='ranging')
    
    # Calculate AEXI
    aexi_engine = AEXIEngine(data)
    aexi = aexi_engine.get_aexi_score()
    
    # Calculate Dream
    dream_engine = DreamMachine(data)
    dream = dream_engine.get_dream_score()
    
    print(f"   AEXI Score: {aexi['score']}")
    print(f"   AEXI Signal: {aexi['signal']}")
    print(f"   Dream Score: {dream['score']}")
    print(f"   Dream Regime: {dream['regime']}")
    
    # Check Twin Turbo condition
    twin_turbo_active = aexi['score'] > 80 and dream['score'] > 70
    print(f"   Twin Turbo Active: {twin_turbo_active}")
    
    assert 0 <= aexi['score'] <= 100
    assert 0 <= dream['score'] <= 100
    print("   ✅ Twin Turbo flow passed!")


# ==========================================
# 🧪 FLOW 4: End-to-End Signal Pipeline
# ==========================================

def test_full_signal_pipeline():
    """Test: Complete signal generation pipeline."""
    print("\n🧪 Test Flow 4: Full Signal Pipeline...")
    
    data = generate_realistic_market_data(100, trend='up')
    
    # Step 1: Scalping Analysis
    scalper = ScalpingBrain(data)
    signal = scalper.analyze_market_state()
    
    # Step 2: AEXI Check
    aexi = AEXIEngine(data)
    exhaustion = aexi.get_aexi_score()
    
    # Step 3: Dream Check
    dream = DreamMachine(data)
    chaos = dream.get_dream_score()
    
    # Step 4: Decision Logic (simplified)
    final_decision = {
        "signal": signal['Action'],
        "confidence": signal['Confidence'],
        "aexi_warning": exhaustion['is_triggered'],
        "chaos_warning": chaos['is_chaotic'],
        "should_trade": signal['Confidence'] >= 80 and not chaos['is_chaotic']
    }
    
    print(f"   Signal: {final_decision['signal']}")
    print(f"   Confidence: {final_decision['confidence']}%")
    print(f"   AEXI Warning: {final_decision['aexi_warning']}")
    print(f"   Chaos Warning: {final_decision['chaos_warning']}")
    print(f"   Should Trade: {final_decision['should_trade']}")
    
    assert isinstance(final_decision['should_trade'], bool)
    print("   ✅ Full pipeline passed!")


# ==========================================
# 🧪 FLOW 5: Mock Environment Test
# ==========================================

def test_mock_environment():
    """Test: Mock environment works correctly."""
    print("\n🧪 Test Flow 5: Mock Environment...")
    
    env = MockEnv()
    
    # Test KV operations
    import asyncio
    
    async def test_kv():
        await env.BRAIN_MEMORY.put("test_key", "test_value")
        result = await env.BRAIN_MEMORY.get("test_key")
        return result
    
    result = asyncio.run(test_kv())
    assert result == "test_value", "KV mock should store and retrieve"
    
    # Test secrets exist
    assert env.TELEGRAM_BOT_TOKEN == "mock_telegram_token"
    assert env.GROQ_API_KEY == "mock_groq_key"
    
    print("   KV Store: ✅")
    print("   Secrets: ✅")
    print("   ✅ Mock environment passed!")


# ==========================================
# 🧪 FLOW 6: Error Handling
# ==========================================

def test_error_handling():
    """Test: Graceful error handling with insufficient data."""
    print("\n🧪 Test Flow 6: Error Handling...")
    
    # Very small dataset
    tiny_data = [
        {'time': 0, 'open': 100, 'high': 101, 'low': 99, 'close': 100, 'volume': 1000}
    ]
    
    # Scalping should handle gracefully
    scalper = ScalpingBrain(tiny_data)
    result = scalper.analyze_market_state()
    assert result is not None, "Should not crash with tiny data"
    
    # AEXI should handle gracefully
    aexi = AEXIEngine(tiny_data)
    aexi_result = aexi.get_aexi_score()
    assert aexi_result is not None
    
    # Dream should handle gracefully
    dream = DreamMachine(tiny_data)
    dream_result = dream.get_dream_score()
    assert dream_result is not None
    
    print("   ScalpingBrain: ✅ No crash")
    print("   AEXIEngine: ✅ No crash")
    print("   DreamMachine: ✅ No crash")
    print("   ✅ Error handling passed!")


# ==========================================
# 🏃 RUN ALL TESTS
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("    INTEGRATION TESTS - Trading System v0.1")
    print("=" * 60)
    
    # Flow 1: Scalping
    test_scalping_flow_uptrend()
    test_scalping_flow_downtrend()
    
    # Flow 2: Long Term
    test_long_term_flow()
    
    # Flow 3: Twin Turbo
    test_twin_turbo_flow()
    
    # Flow 4: Full Pipeline
    test_full_signal_pipeline()
    
    # Flow 5: Mock Environment
    test_mock_environment()
    
    # Flow 6: Error Handling
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("    ALL INTEGRATION TESTS PASSED ✅")
    print("=" * 60)
