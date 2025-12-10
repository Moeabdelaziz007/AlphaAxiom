
import pytest
import sys
import os
import math

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from aexi_engine import AEXIEngine
from dream_engine import DreamMachine

# ==========================================
# ⚡ AEXI Engine Tests
# ==========================================

@pytest.fixture
def aexi_data():
    """Generate 30 bars of data for testing"""
    data = []
    base_price = 100.0
    for i in range(30):
        # Create a trend to test signals
        price = base_price + i * 2  # Strong uptrend

        # Add a massive spike at the end to force exhaustion
        if i >= 28:
            price += 50  # Sudden jump

        data.append({
            "close": price,
            "high": price + 1,
            "low": price - 1,
            "volume": 1000 + (i * 100) # Increasing volume
        })
    return data

def test_aexi_exh_calculation(aexi_data):
    engine = AEXIEngine(aexi_data)
    exh = engine.calculate_exh()

    assert "raw" in exh
    assert "normalized" in exh
    assert "signal" in exh

    # Since we have a strong uptrend, Z-score should be high
    assert exh["normalized"] > 50
    assert exh["signal"] == "OVERBOUGHT"

def test_aexi_vaf_calculation(aexi_data):
    engine = AEXIEngine(aexi_data)
    vaf = engine.calculate_vaf()

    assert "normalized" in vaf
    # Verify range 0-100
    assert 0 <= vaf["normalized"] <= 100

def test_aexi_svp_calculation(aexi_data):
    engine = AEXIEngine(aexi_data)
    svp = engine.calculate_svp()

    assert "normalized" in svp
    assert "is_spike" in svp
    # Increasing volume should yield high ratio
    assert svp["ratio"] >= 1.0

def test_aexi_score_composite(aexi_data):
    engine = AEXIEngine(aexi_data)
    result = engine.get_aexi_score()

    assert "score" in result
    assert "components" in result
    assert 0 <= result["score"] <= 100

    # Check weighted logic
    # score = 0.4*exh + 0.3*vaf + 0.3*svp
    comp = result["components"]
    expected = (0.4 * comp["exh"]["normalized"]) + \
               (0.3 * comp["vaf"]["normalized"]) + \
               (0.3 * comp["svp"]["normalized"])

    assert math.isclose(result["score"], expected, abs_tol=0.1)


# ==========================================
# 🌀 Dream Machine Tests
# ==========================================

@pytest.fixture
def dream_data():
    """Generate 40 bars of data"""
    data = []
    import random
    random.seed(42)
    base_price = 100.0
    for i in range(40):
        # Random walk for entropy testing
        base_price += random.uniform(-2, 2)
        data.append({
            "close": base_price,
            "volume": random.randint(500, 1500)
        })
    return data

def test_dream_entropy(dream_data):
    engine = DreamMachine(dream_data)
    entropy = engine.calculate_entropy()

    assert "normalized" in entropy
    assert 0 <= entropy["normalized"] <= 100
    assert entropy["interpretation"] in ["NORMAL", "HIGH_CHAOS", "LOW_CHAOS"]

def test_dream_fractal(dream_data):
    engine = DreamMachine(dream_data)
    fractal = engine.calculate_fractal_dimension()

    assert "fd" in fractal
    # FD should be between 1 and 2 approx
    assert 0.9 <= fractal["fd"] <= 2.1

def test_dream_hurst(dream_data):
    engine = DreamMachine(dream_data)
    hurst = engine.calculate_hurst_exponent()

    assert "H" in hurst
    assert 0 <= hurst["H"] <= 1.0
    assert hurst["behavior"] in ["TRENDING", "MEAN_REVERTING", "RANDOM"]

def test_dream_score_composite(dream_data):
    engine = DreamMachine(dream_data)
    result = engine.get_dream_score()

    assert "score" in result
    assert "regime" in result
    assert 0 <= result["score"] <= 100

    # Check weighted logic
    comp = result["components"]
    expected = (0.30 * comp["entropy"]["normalized"]) + \
               (0.25 * comp["fractal"]["normalized"]) + \
               (0.25 * comp["hurst"]["normalized"]) + \
               (0.20 * comp["vol_dispersion"]["normalized"])

    assert math.isclose(result["score"], expected, abs_tol=0.1)

# ==========================================
# 🛑 Panic Mode Trigger Tests
# ==========================================

from tests.mock_env import MockEnv
from routes import cron

@pytest.mark.asyncio
async def test_daily_loss_limit_trigger():
    env = MockEnv()

    # Mock CapitalConnector to return high loss
    # We need to monkeypatch the module where CapitalConnector is imported in cron.py
    # Since it's imported inside the function, we have to mock it via sys.modules or similar strategy.
    # However, mocking inside a function import is tricky.
    # A better way is to verify logic by mocking the entire CapitalConnector class before cron imports it.

    from unittest.mock import MagicMock

    # Mock class
    class MockCapital:
        def __init__(self, env): pass
        async def get_account_info(self):
            return {"equity": 90000} # 100k -> 90k = 10% loss

    # Inject into sys.modules so cron.py picks it up
    mock_module = MagicMock()
    mock_module.CapitalConnector = MockCapital
    sys.modules["capital_connector"] = mock_module

    # Ensure cron doesn't crash on other imports
    sys.modules["risk_manager"] = MagicMock()
    sys.modules["economic_calendar"] = MagicMock()

    # Setup initial state
    await env.BRAIN_MEMORY.put("panic_mode", "false")
    await env.BRAIN_MEMORY.put("daily_starting_equity", "100000")

    # Run cron
    await cron.on_scheduled(None, env)

    # Verify panic mode activated
    assert await env.BRAIN_MEMORY.get("panic_mode") == "true"
    assert "Daily loss" in await env.BRAIN_MEMORY.get("panic_reason")
