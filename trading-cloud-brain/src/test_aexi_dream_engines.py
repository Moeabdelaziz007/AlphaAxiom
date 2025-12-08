"""
🧪 Unit Tests for AEXI Engine and Dream Machine
Tests the chaos theory and exhaustion detection engines.
"""

from aexi_engine import AEXIEngine
from dream_engine import DreamMachine

def generate_test_data(count=60, trend='up', volatility='normal'):
    """Generate realistic test OHLCV data."""
    data = []
    base_price = 100.0
    base_volume = 10000
    
    for i in range(count):
        # Price movement based on trend
        if trend == 'up':
            change = 0.5 + (0.1 if volatility == 'high' else 0)
        elif trend == 'down':
            change = -0.5 - (0.1 if volatility == 'high' else 0)
        else:  # choppy
            change = 0.3 * (1 if i % 2 == 0 else -1)
        
        price = base_price + (i * change)
        
        # Volume varies
        vol_mult = 1.5 if i > count - 5 else 1.0  # Spike at end
        volume = base_volume * vol_mult * (1 + 0.2 * (i % 3))
        
        data.append({
            'time': i,
            'open': price - 0.2,
            'high': price + 0.5,
            'low': price - 0.5,
            'close': price,
            'volume': volume
        })
    
    return data


# ==========================================
# 🧪 AEXI ENGINE TESTS
# ==========================================

def test_aexi_exh():
    print("\n🧪 Test AEXI: EXH (Exhaustion Z-Score)...")
    data = generate_test_data(60, trend='up')
    engine = AEXIEngine(data)
    
    exh = engine.calculate_exh()
    print(f"   Z-Score: {exh['raw']}")
    print(f"   Normalized: {exh['normalized']}")
    print(f"   Signal: {exh['signal']}")
    
    assert 0 <= exh['normalized'] <= 100, "Normalized should be 0-100"
    assert exh['signal'] in ["NEUTRAL", "OVERBOUGHT", "OVERSOLD"]
    print("   ✅ EXH calculation correct!")

def test_aexi_vaf():
    print("\n🧪 Test AEXI: VAF (Velocity/ATR Factor)...")
    data = generate_test_data(60, trend='up')
    engine = AEXIEngine(data)
    
    vaf = engine.calculate_vaf()
    print(f"   ROC: {vaf['roc']}%")
    print(f"   ATR: {vaf['atr']}")
    print(f"   VAF Ratio: {vaf['vaf_ratio']}")
    print(f"   Normalized: {vaf['normalized']}")
    
    assert 0 <= vaf['normalized'] <= 100, "Normalized should be 0-100"
    assert vaf['atr'] > 0, "ATR should be positive"
    print("   ✅ VAF calculation correct!")

def test_aexi_svp():
    print("\n🧪 Test AEXI: SVP (Volume Proxy)...")
    data = generate_test_data(60, trend='up')
    engine = AEXIEngine(data)
    
    svp = engine.calculate_svp()
    print(f"   Volume Ratio: {svp['ratio']}")
    print(f"   Normalized: {svp['normalized']}")
    print(f"   Is Spike: {svp['is_spike']}")
    
    assert 0 <= svp['normalized'] <= 100, "Normalized should be 0-100"
    assert svp['ratio'] > 0, "Ratio should be positive"
    print("   ✅ SVP calculation correct!")

def test_aexi_composite():
    print("\n🧪 Test AEXI: Composite Score...")
    data = generate_test_data(60, trend='up')
    engine = AEXIEngine(data)
    
    aexi = engine.get_aexi_score()
    print(f"   AEXI Score: {aexi['score']}")
    print(f"   Signal: {aexi['signal']}")
    print(f"   Direction: {aexi['direction']}")
    print(f"   Triggered: {aexi['is_triggered']}")
    
    assert 0 <= aexi['score'] <= 100, "Score should be 0-100"
    assert 'components' in aexi
    print("   ✅ AEXI composite working!")


# ==========================================
# 🧪 DREAM MACHINE TESTS
# ==========================================

def test_dream_entropy():
    print("\n🧪 Test Dream: Shannon Entropy...")
    data = generate_test_data(60, trend='choppy')
    engine = DreamMachine(data)
    
    entropy = engine.calculate_entropy()
    print(f"   Raw Entropy: {entropy['raw']}")
    print(f"   Normalized: {entropy['normalized']}")
    print(f"   Interpretation: {entropy['interpretation']}")
    
    assert 0 <= entropy['normalized'] <= 100, "Normalized should be 0-100"
    assert entropy['interpretation'] in ["HIGH_CHAOS", "LOW_CHAOS", "NORMAL", "INSUFFICIENT_DATA"]
    print("   ✅ Entropy calculation correct!")

def test_dream_fractal():
    print("\n🧪 Test Dream: Fractal Dimension...")
    data = generate_test_data(60, trend='choppy')
    engine = DreamMachine(data)
    
    fractal = engine.calculate_fractal_dimension()
    print(f"   Fractal Dimension: {fractal['fd']}")
    print(f"   Sign Changes: {fractal['sign_changes']}")
    print(f"   Normalized: {fractal['normalized']}")
    
    assert 1.0 <= fractal['fd'] <= 2.0, "FD should be 1-2"
    assert 0 <= fractal['normalized'] <= 100, "Normalized should be 0-100"
    print("   ✅ Fractal Dimension correct!")

def test_dream_hurst():
    print("\n🧪 Test Dream: Hurst Exponent...")
    data = generate_test_data(60, trend='up')
    engine = DreamMachine(data)
    
    hurst = engine.calculate_hurst_exponent()
    print(f"   Hurst H: {hurst['H']}")
    print(f"   R/S: {hurst['RS']}")
    print(f"   Behavior: {hurst['behavior']}")
    print(f"   Normalized: {hurst['normalized']}")
    
    assert 0 <= hurst['H'] <= 1, "H should be 0-1"
    assert hurst['behavior'] in ["TRENDING", "RANDOM", "MEAN_REVERTING"]
    print("   ✅ Hurst Exponent correct!")

def test_dream_vol_dispersion():
    print("\n🧪 Test Dream: Volume Dispersion...")
    data = generate_test_data(60)
    engine = DreamMachine(data)
    
    vol = engine.calculate_vol_dispersion()
    print(f"   CV: {vol['cv']}")
    print(f"   Normalized: {vol['normalized']}")
    
    assert vol['cv'] >= 0, "CV should be non-negative"
    assert 0 <= vol['normalized'] <= 100, "Normalized should be 0-100"
    print("   ✅ Volume Dispersion correct!")

def test_dream_composite():
    print("\n🧪 Test Dream: Composite Score...")
    data = generate_test_data(60, trend='choppy', volatility='high')
    engine = DreamMachine(data)
    
    dream = engine.get_dream_score()
    print(f"   DREAM Score: {dream['score']}")
    print(f"   Regime: {dream['regime']}")
    print(f"   Signal: {dream['signal']}")
    print(f"   Is Chaotic: {dream['is_chaotic']}")
    
    assert 0 <= dream['score'] <= 100, "Score should be 0-100"
    assert dream['regime'] in ["CHAOS", "UNSTABLE", "ORDERED", "NORMAL"]
    assert 'components' in dream
    print("   ✅ Dream composite working!")


# ==========================================
# 🧪 EDGE CASES
# ==========================================

def test_insufficient_data():
    print("\n🧪 Test: Insufficient Data Handling...")
    short_data = [{'close': 100, 'high': 101, 'low': 99, 'volume': 1000}]
    
    aexi = AEXIEngine(short_data)
    dream = DreamMachine(short_data)
    
    aexi_result = aexi.get_aexi_score()
    dream_result = dream.get_dream_score()
    
    print(f"   AEXI with 1 bar: {aexi_result['score']}")
    print(f"   Dream with 1 bar: {dream_result['score']}")
    
    # Should return safe defaults without crashing
    assert isinstance(aexi_result['score'], (int, float))
    assert isinstance(dream_result['score'], (int, float))
    print("   ✅ Edge cases handled gracefully!")


if __name__ == "__main__":
    print("=" * 60)
    print("    AEXI + DREAM ENGINE UNIT TESTS")
    print("=" * 60)
    
    # AEXI Tests
    test_aexi_exh()
    test_aexi_vaf()
    test_aexi_svp()
    test_aexi_composite()
    
    # Dream Tests
    test_dream_entropy()
    test_dream_fractal()
    test_dream_hurst()
    test_dream_vol_dispersion()
    test_dream_composite()
    
    # Edge Cases
    test_insufficient_data()
    
    print("\n" + "=" * 60)
    print("    ALL TESTS PASSED ✅")
    print("=" * 60)
