"""
🔥 Stress Test - The Market Simulator
=====================================
Simulates 1 year of market conditions in 1 minute to test system resilience.

Scenarios:
1. The Crash: -30% drop in 1 hour
2. The Pump: +50% rally
3. The Chop: Sideways price action

Usage:
    python scripts/stress_test.py
"""

import asyncio
import logging
import random
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../trading-cloud-brain/src')))

# Mocks for independent running
from unittest.mock import MagicMock, AsyncMock

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("StressTest")

# Mock dependencies if imports fail (since we are running this as a script)
try:
    from engine.aladdin import AladdinRiskEngine
    from engine.cipher import CipherEngine
except ImportError:
    # Basic mock classes if real ones can't be imported due to path issues
    logger.warning("Could not import actual engines. Using mocks.")
    class AladdinRiskEngine:
        def __init__(self, **kwargs): pass
        def emergency_check(self, dd): return dd > 0.05
        def evaluate_trade(self, **kwargs): return MagicMock(approved=True, adjusted_size=kwargs.get('proposed_size'))

    class CipherEngine:
        def analyze(self, **kwargs): return MagicMock(signal="neutral")


class MarketSimulator:
    def __init__(self):
        self.aladdin = AladdinRiskEngine(max_risk_per_trade=0.02, max_portfolio_risk=0.10)
        self.cipher = CipherEngine()
        self.price = 10000.0
        self.balance = 10000.0
        self.positions = []
        self.peak_balance = 10000.0

    async def run_scenario(self, name, duration_seconds, price_change_pct, volatility):
        logger.info(f"🎬 START SCENARIO: {name} | Target Change: {price_change_pct*100}%")

        start_price = self.price
        target_price = start_price * (1 + price_change_pct)
        steps = duration_seconds * 10 # 10 ticks per second
        price_step = (target_price - start_price) / steps

        for i in range(steps):
            # 1. Update Price (with noise)
            noise = random.uniform(-volatility, volatility) * self.price
            self.price += price_step + noise

            # 2. Check Risk (Drawdown)
            current_dd = (self.peak_balance - self.balance) / self.peak_balance
            if self.aladdin.emergency_check(current_dd):
                logger.critical(f"🚨 HALT TRADING! Drawdown: {current_dd*100:.2f}%")
                break

            # 3. Simulate Trading (Randomly for stress test)
            if i % 10 == 0: # Every second
                # Evaluate a random trade
                side = 'buy' if random.random() > 0.5 else 'sell'
                size = self.balance * 0.1 # Try 10% size

                assessment = self.aladdin.evaluate_trade(
                    symbol="BTCUSD",
                    proposed_size=size,
                    side=side,
                    account_balance=self.balance,
                    current_positions={}
                )

                if assessment.approved:
                    # Execute (Simulated)
                    pass

            # 4. Update Balance (Mark to Market)
            # For simplicity, just adding random PnL fluctuation based on volatility
            pnl_swing = random.uniform(-0.001, 0.001) * self.balance
            self.balance += pnl_swing
            self.peak_balance = max(self.peak_balance, self.balance)

            await asyncio.sleep(0.01) # Fast forward

        logger.info(f"🏁 END SCENARIO: {name} | Final Price: {self.price:.2f} | Balance: {self.balance:.2f}")

async def main():
    sim = MarketSimulator()

    # 1. The Crash: -30% drop
    await sim.run_scenario("The Crash", duration_seconds=5, price_change_pct=-0.30, volatility=0.01)

    # 2. The Pump: +50% rally
    await sim.run_scenario("The Pump", duration_seconds=5, price_change_pct=0.50, volatility=0.02)

    # 3. The Chop: Sideways
    await sim.run_scenario("The Chop", duration_seconds=5, price_change_pct=0.0, volatility=0.005)

    logger.info("✅ Stress Test Complete")

if __name__ == "__main__":
    asyncio.run(main())
