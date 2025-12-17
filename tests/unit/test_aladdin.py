import pytest
from engine.aladdin import AladdinRiskEngine, RiskAssessment

@pytest.fixture
def aladdin():
    return AladdinRiskEngine(max_risk_per_trade=0.02, max_portfolio_risk=0.10)

def test_drawdown_limit(aladdin):
    # Scenario A: Drawdown > 5% → Block new trades?
    # The method is emergency_check(current_drawdown)

    assert aladdin.emergency_check(0.04) is False
    assert aladdin.emergency_check(0.05) is True
    assert aladdin.emergency_check(0.06) is True
    assert aladdin.emergency_check(-0.06) is True # Should handle absolute value usually, but code uses abs()

def test_correlated_assets_reduction(aladdin):
    # Scenario B: Correlated assets (BTC & ETH) → Reduce size?

    # 1. Simulate BTC price history (Upward)
    for i in range(10):
        aladdin.update_price('BTCUSDT', 100 + i)

    # 2. Simulate ETH price history (Perfectly correlated)
    for i in range(10):
        aladdin.update_price('ETHUSDT', 10 + i)

    # 3. Simulate existing BTC position
    current_positions = {
        'BTCUSDT': {'side': 'buy', 'size': 1.0}
    }

    # 4. Try to buy ETH
    assessment = aladdin.evaluate_trade(
        symbol='ETHUSDT',
        proposed_size=1.0,
        side='buy',
        account_balance=10000.0,
        current_positions=current_positions
    )

    # Logic: If correlation > 0.8, reduce size by 50%
    # Our mocked prices are perfectly correlated (corr=1.0)

    assert assessment.approved is True
    assert assessment.adjusted_size == 0.5 # Halved
    assert "Correlated with BTCUSDT" in assessment.reason

def test_portfolio_risk_limit(aladdin):
    # Max portfolio risk is 10%
    # Account balance 100,000. Max exposure 10,000.

    current_positions = {
        'A': {'size': 9000} # 9% exposure
    }

    # Try to add 2000 (2%) -> Total 11% > 10%
    assessment = aladdin.evaluate_trade(
        symbol='B',
        proposed_size=2000,
        side='buy',
        account_balance=100000,
        current_positions=current_positions
    )

    # Should be reduced to fit remaining 1000
    assert assessment.adjusted_size == 1000
    assert "Size reduced" in assessment.reason
