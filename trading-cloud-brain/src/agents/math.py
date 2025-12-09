# ========================================
# 🧮 AXIOM MATH AGENT - Quantitative Analysis
# ========================================
# Ported from Mini-Aladdin MathAgent (JavaScript)
# Enhanced for Cloudflare Workers Python
# ========================================
# Capabilities:
#   - Monte Carlo Simulation (Geometric Brownian Motion)
#   - Kelly Criterion (Optimal Position Sizing)
#   - Sharpe Ratio (Risk-Adjusted Returns)
#   - Triangular Arbitrage Detection
#   - Correlation Analysis
# ========================================

import math
import random
from typing import List, Dict, Any, Optional, Tuple


class MathAgent:
    """
    Advanced Mathematical Analysis Agent.
    The "Genius Mathematician" of the Axiom system.
    
    Ported from Mini-Aladdin's MathAgent with Python optimizations.
    """
    
    def __init__(self):
        self.name = "MathAgent"
        self.specialty = "Advanced Mathematics & Statistics"
    
    # ========================================
    # 📊 Monte Carlo Simulation
    # ========================================
    
    def monte_carlo_simulation(
        self,
        current_price: float,
        volatility: float,
        days: int = 30,
        simulations: int = 5000
    ) -> Dict[str, Any]:
        """
        Monte Carlo Simulation using Geometric Brownian Motion.
        Like BlackRock's Aladdin - generates thousands of future scenarios.
        
        Args:
            current_price: Current asset price
            volatility: Historical volatility (e.g., 0.03 = 3%)
            days: Days to simulate forward
            simulations: Number of simulation paths
        
        Returns:
            Statistical analysis of simulated outcomes
        """
        dt = 1 / 365  # Daily time step
        drift = 0.0001  # Small positive drift (market tendency)
        
        final_prices = []
        returns = []
        
        for _ in range(simulations):
            price = current_price
            
            for _ in range(days):
                # Geometric Brownian Motion (Black-Scholes model)
                shock = self._box_muller_random() * volatility * math.sqrt(dt)
                price = price * math.exp(drift * dt + shock)
            
            final_prices.append(price)
            ret = ((price - current_price) / current_price) * 100
            returns.append(ret)
        
        # Sort for percentile calculations
        returns.sort()
        final_prices.sort()
        
        n = len(returns)
        
        return {
            "expected_return": self._mean(returns),
            "volatility": self._std_dev(returns),
            "var_95": returns[int(n * 0.05)],  # 95% Value at Risk
            "var_99": returns[int(n * 0.01)],  # 99% Value at Risk
            "best_case": returns[-1],
            "worst_case": returns[0],
            "median_return": returns[n // 2],
            "probability_of_profit": (len([r for r in returns if r > 0]) / n) * 100,
            "expected_price": self._mean(final_prices),
            "price_range": {
                "low": final_prices[int(n * 0.05)],
                "high": final_prices[int(n * 0.95)],
            },
            "simulations": simulations,
            "days": days
        }
    
    def _box_muller_random(self) -> float:
        """Box-Muller transform for normally distributed random numbers."""
        u1 = random.random()
        u2 = random.random()
        return math.sqrt(-2 * math.log(u1 + 1e-10)) * math.cos(2 * math.pi * u2)
    
    # ========================================
    # 💰 Kelly Criterion - Optimal Bet Sizing
    # ========================================
    
    def kelly_calculator(
        self,
        win_probability: float,
        win_loss_ratio: float,
        bankroll: float,
        fractional: float = 0.25
    ) -> Dict[str, Any]:
        """
        Kelly Criterion - Optimal position sizing.
        
        Formula: f* = (bp - q) / b
        Where: b = odds (win/loss ratio), p = win prob, q = lose prob
        
        Args:
            win_probability: Probability of winning (0.0 - 1.0)
            win_loss_ratio: Average win / Average loss (e.g., 2.0 = 2:1)
            bankroll: Total available capital
            fractional: Kelly fraction to use (0.25 = Quarter Kelly for safety)
        
        Returns:
            Optimal position sizing recommendations
        """
        q = 1 - win_probability
        
        # Kelly formula
        kelly_percent = (win_loss_ratio * win_probability - q) / win_loss_ratio
        kelly_amount = max(0, kelly_percent * bankroll)
        
        # Fractional Kelly for safety
        fractional_amount = kelly_amount * fractional
        
        return {
            "full_kelly_percent": kelly_percent * 100,
            "full_kelly_amount": kelly_amount,
            "recommended_percent": (kelly_percent * fractional) * 100,
            "recommended_amount": fractional_amount,
            "max_risk": fractional_amount,
            "kelly_fraction_used": fractional,
            "edge": (win_probability * win_loss_ratio - q) * 100  # Expected edge %
        }
    
    # ========================================
    # 📈 Risk-Adjusted Returns
    # ========================================
    
    def sharpe_ratio(
        self,
        returns: List[float],
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Sharpe Ratio - Risk-adjusted return metric.
        
        Formula: (Average Return - Risk Free Rate) / Standard Deviation
        
        Args:
            returns: List of periodic returns
            risk_free_rate: Risk-free rate (default 2% annual)
        
        Returns:
            Sharpe ratio (higher is better, >1 is good, >2 is excellent)
        """
        if len(returns) < 2:
            return 0.0
        
        avg_return = self._mean(returns)
        std_dev = self._std_dev(returns)
        
        if std_dev == 0:
            return 0.0
        
        return (avg_return - risk_free_rate) / std_dev
    
    def sortino_ratio(
        self,
        returns: List[float],
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Sortino Ratio - Like Sharpe but only penalizes downside volatility.
        
        Args:
            returns: List of periodic returns
            risk_free_rate: Risk-free rate
        
        Returns:
            Sortino ratio
        """
        if len(returns) < 2:
            return 0.0
        
        avg_return = self._mean(returns)
        downside_returns = [r for r in returns if r < risk_free_rate]
        
        if len(downside_returns) < 2:
            return float('inf') if avg_return > risk_free_rate else 0.0
        
        downside_std = self._std_dev(downside_returns)
        
        if downside_std == 0:
            return 0.0
        
        return (avg_return - risk_free_rate) / downside_std
    
    # ========================================
    # 🔺 Triangular Arbitrage
    # ========================================
    
    def calculate_triangular_arbitrage(
        self,
        pair1_price: float,  # e.g., BTC/USDT
        pair2_price: float,  # e.g., ETH/BTC
        pair3_price: float,  # e.g., ETH/USDT
        start_amount: float = 1000,
        fee_percent: float = 0.1
    ) -> Dict[str, Any]:
        """
        Triangular Arbitrage Detection.
        
        Example: USDT -> BTC -> ETH -> USDT
        
        Args:
            pair1_price: Price of first pair (e.g., BTCUSDT = 45000)
            pair2_price: Price of second pair (e.g., ETHBTC = 0.055)
            pair3_price: Price of third pair (e.g., ETHUSDT = 2500)
            start_amount: Starting capital in quote currency
            fee_percent: Trading fee per leg (0.1 = 0.1%)
        
        Returns:
            Arbitrage opportunity analysis
        """
        fee_multiplier = 1 - (fee_percent / 100)
        
        # Forward path: USDT -> BTC -> ETH -> USDT
        step1 = (start_amount / pair1_price) * fee_multiplier  # USDT -> BTC
        step2 = (step1 / pair2_price) * fee_multiplier         # BTC -> ETH
        step3 = (step2 * pair3_price) * fee_multiplier         # ETH -> USDT
        forward_profit = step3 - start_amount
        forward_percent = (forward_profit / start_amount) * 100
        
        # Reverse path: USDT -> ETH -> BTC -> USDT
        rev_step1 = (start_amount / pair3_price) * fee_multiplier  # USDT -> ETH
        rev_step2 = (rev_step1 * pair2_price) * fee_multiplier     # ETH -> BTC
        rev_step3 = (rev_step2 * pair1_price) * fee_multiplier     # BTC -> USDT
        reverse_profit = rev_step3 - start_amount
        reverse_percent = (reverse_profit / start_amount) * 100
        
        best_path = "forward" if forward_percent > reverse_percent else "reverse"
        best_profit = max(forward_profit, reverse_profit)
        best_percent = max(forward_percent, reverse_percent)
        
        return {
            "forward": {"profit": forward_profit, "percent": forward_percent},
            "reverse": {"profit": reverse_profit, "percent": reverse_percent},
            "best_path": best_path,
            "best_profit": best_profit,
            "best_percent": best_percent,
            "worth_it": best_percent > 0.1,  # Minimum 0.1% after fees
            "start_amount": start_amount
        }
    
    # ========================================
    # 🔗 Correlation Analysis
    # ========================================
    
    def correlation(
        self,
        returns1: List[float],
        returns2: List[float]
    ) -> float:
        """
        Calculate Pearson correlation coefficient between two assets.
        
        Args:
            returns1: Returns of first asset
            returns2: Returns of second asset
        
        Returns:
            Correlation coefficient (-1 to 1)
        """
        n = min(len(returns1), len(returns2))
        if n < 3:
            return 0.0
        
        mean1 = self._mean(returns1[:n])
        mean2 = self._mean(returns2[:n])
        
        numerator = 0.0
        sum1_sq = 0.0
        sum2_sq = 0.0
        
        for i in range(n):
            diff1 = returns1[i] - mean1
            diff2 = returns2[i] - mean2
            numerator += diff1 * diff2
            sum1_sq += diff1 * diff1
            sum2_sq += diff2 * diff2
        
        denominator = math.sqrt(sum1_sq * sum2_sq)
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    # ========================================
    # 📊 Simple Arbitrage Calculation
    # ========================================
    
    def calculate_arbitrage(
        self,
        buy_price: float,
        sell_price: float,
        amount: float,
        fee_percent: float = 0.1
    ) -> Dict[str, Any]:
        """
        Calculate simple cross-exchange arbitrage profitability.
        
        Args:
            buy_price: Price to buy at
            sell_price: Price to sell at
            amount: Trade amount in quote currency
            fee_percent: Fee per trade (0.1 = 0.1%)
        
        Returns:
            Arbitrage profit analysis
        """
        fee_rate = fee_percent / 100
        buy_fee = buy_price * amount * fee_rate
        sell_fee = sell_price * amount * fee_rate
        buy_cost = (buy_price * amount) + buy_fee
        sell_revenue = (sell_price * amount) - sell_fee
        profit = sell_revenue - buy_cost
        profit_percent = (profit / buy_cost) * 100 if buy_cost > 0 else 0
        
        return {
            "profit": profit,
            "profit_percent": profit_percent,
            "buy_cost": buy_cost,
            "sell_revenue": sell_revenue,
            "fees": buy_fee + sell_fee,
            "worth_it": profit_percent > 0.3,  # Minimum 0.3% profit
            "roi": profit_percent
        }
    
    # ========================================
    # 🛠️ Statistical Helpers
    # ========================================
    
    def _mean(self, arr: List[float]) -> float:
        """Calculate arithmetic mean."""
        if not arr:
            return 0.0
        return sum(arr) / len(arr)
    
    def _std_dev(self, arr: List[float]) -> float:
        """Calculate standard deviation."""
        if len(arr) < 2:
            return 0.0
        avg = self._mean(arr)
        variance = sum((x - avg) ** 2 for x in arr) / len(arr)
        return math.sqrt(variance)
    
    def _percentile(self, arr: List[float], p: float) -> float:
        """Calculate percentile (p = 0.0 to 1.0)."""
        if not arr:
            return 0.0
        sorted_arr = sorted(arr)
        idx = int(len(sorted_arr) * p)
        return sorted_arr[min(idx, len(sorted_arr) - 1)]


# ========================================
# 🏭 Factory Function
# ========================================

def get_math_agent() -> MathAgent:
    """Get singleton MathAgent instance."""
    return MathAgent()


# ========================================
# 🧪 Quick Test
# ========================================

def test_math_agent():
    """Test MathAgent functionality."""
    agent = MathAgent()
    
    # Test Monte Carlo
    mc = agent.monte_carlo_simulation(45000, 0.03, 30, 1000)
    
    # Test Kelly
    kelly = agent.kelly_calculator(0.55, 2.0, 10000)
    
    # Test Arbitrage
    arb = agent.calculate_arbitrage(45000, 45200, 100)
    
    return {
        "monte_carlo": {
            "expected_return": round(mc["expected_return"], 2),
            "prob_profit": round(mc["probability_of_profit"], 1)
        },
        "kelly": {
            "recommended_percent": round(kelly["recommended_percent"], 2),
            "edge": round(kelly["edge"], 2)
        },
        "arbitrage": {
            "profit": round(arb["profit"], 2),
            "worth_it": arb["worth_it"]
        }
    }
