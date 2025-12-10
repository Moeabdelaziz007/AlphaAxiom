"""
Counterfactual Vision Engine for AlphaAxiom Learning Loop v2.0

This module implements a counterfactual analysis engine that evaluates 
the potential regret cost of trading decisions by simulating alternative 
outcomes. It helps the system make safer decisions by quantifying what 
might have happened if different actions were taken.

The engine combines:
1. Historical price simulation for counterfactual outcomes
2. Volatility modeling for realistic scenario generation
3. Regret cost calculation for decision evaluation
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CounterfactualScenario:
    """Represents a counterfactual scenario and its outcomes"""
    scenario_id: str
    action_taken: str
    alternative_action: str
    factual_outcome: float
    counterfactual_outcome: float
    regret_cost: float
    confidence: float
    timestamp: datetime


@dataclass
class SimulationResult:
    """Result of a price simulation"""
    prices: List[float]
    returns: List[float]
    volatility: float
    final_return: float
    max_drawdown: float


class CounterfactualVisionEngine:
    """
    Enhanced counterfactual analysis engine for evaluating trading decisions.
    
    This engine enables AlphaAxiom to:
    1. Simulate alternative outcomes for trading decisions
    2. Calculate regret costs to inform decision making
    3. Improve risk-adjusted returns through counterfactual awareness
    """
    
    def __init__(self, d1_db=None, kv_store=None):
        """
        Initialize the Counterfactual Vision Engine.
        
        Args:
            d1_db: D1 database connection for persistent storage (optional)
            kv_store: KV store for fast access to simulation data (optional)
        """
        self.d1 = d1_db
        self.kv = kv_store
        self.simulation_cache = {}
        
        # Simulation parameters
        self.simulation_params = {
            'forecast_horizon_hours': 24,
            'simulation_steps': 240,  # 10-minute intervals for 24 hours
            'volatility_window': 30,  # Days of historical data for 
            # volatility calculation
            'confidence_threshold': 0.7,
            'max_regret_threshold': 0.05  # 5% maximum acceptable regret
        }
    
    async def evaluate_decision(
        self, 
        symbol: str,
        action: str,
        current_price: float,
        context: Dict[str, Any]
    ) -> CounterfactualScenario:
        """
        Evaluate a trading decision using counterfactual analysis.
        
        Args:
            symbol: Trading symbol
            action: Proposed action (BUY, SELL, HOLD)
            current_price: Current market price
            context: Full decision context including historical data
            
        Returns:
            CounterfactualScenario with analysis results
        """
        import uuid
        
        # Create scenario ID
        scenario_id = str(uuid.uuid4())[:12]
        
        # Get historical prices for simulation
        historical_prices = context.get('historical_prices', [])
        if not historical_prices:
            # Fallback to simple price array if not available
            historical_prices = [current_price] * 100
        
        # Simulate factual outcome (what happens if we take 
        # the proposed action)
        factual_result = await self._simulate_scenario(
            symbol, action, current_price, historical_prices
        )
        
        # Determine alternative action
        alternative_action = self._get_alternative_action(action)
        
        # Simulate counterfactual outcome (what happens if we take alternative)
        counterfactual_result = await self._simulate_scenario(
            symbol, alternative_action, current_price, historical_prices
        )
        
        # Calculate regret cost
        regret_cost = self._calculate_regret_cost(
            factual_result.final_return, 
            counterfactual_result.final_return
        )
        
        # Calculate confidence based on simulation reliability
        confidence = self._calculate_confidence(
            factual_result.volatility, 
            len(historical_prices)
        )
        
        # Create scenario object
        scenario = CounterfactualScenario(
            scenario_id=scenario_id,
            action_taken=action,
            alternative_action=alternative_action,
            factual_outcome=factual_result.final_return,
            counterfactual_outcome=counterfactual_result.final_return,
            regret_cost=regret_cost,
            confidence=confidence,
            timestamp=datetime.now()
        )
        
        # Store scenario for learning
        await self._store_scenario(scenario)
        
        return scenario
    
    async def _simulate_scenario(
        self, 
        symbol: str, 
        action: str, 
        current_price: float, 
        historical_prices: List[float]
    ) -> SimulationResult:
        """
        Simulate a trading scenario based on historical data and action.
        
        Args:
            symbol: Trading symbol
            action: Trading action (BUY, SELL, HOLD)
            current_price: Current market price
            historical_prices: Historical price data
            
        Returns:
            SimulationResult with projected outcomes
        """
        # Calculate volatility from historical prices
        volatility = self._calculate_volatility(historical_prices)
        
        # Determine simulation parameters based on action
        if action == "BUY":
            drift = 0.0001  # Slight positive drift for buy simulations
        elif action == "SELL":
            drift = -0.0001  # Slight negative drift for sell simulations
        else:  # HOLD
            drift = 0.0  # Neutral drift for hold simulations
        
        # Generate simulated price path
        prices = self._generate_price_path(
            current_price, 
            volatility, 
            drift, 
            self.simulation_params['simulation_steps']
        )
        
        # Calculate returns
        returns = self._calculate_returns(prices)
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown(prices)
        
        # Final return is the return over the entire simulation period
        final_return = (prices[-1] - prices[0]) / prices[0] \
            if prices[0] != 0 else 0.0
        
        return SimulationResult(
            prices=prices,
            returns=returns,
            volatility=volatility,
            final_return=final_return,
            max_drawdown=max_drawdown
        )
    
    def run_scenario(self, historical_close_prices: List[float], 
                     action: str = "HOLD") -> Dict[str, Any]:
        """
        Simplified simulator for 24-hour outcome prediction based on 
        historical close prices.
        
        Args:
            historical_close_prices: List of historical closing prices
            action: Trading action (BUY, SELL, HOLD)
            
        Returns:
            Dictionary with predicted outcome and risk metrics
        """
        if not historical_close_prices or len(historical_close_prices) < 2:
            return {
                "predicted_return": 0.0,
                "volatility": 0.01,
                "confidence": 0.5,
                "risk_level": "LOW"
            }
        
        # Calculate basic statistics
        # Get current price
        _ = historical_close_prices[-1]
        volatility = self._calculate_volatility(historical_close_prices)
        
        # Predict return based on action and volatility
        if action == "BUY":
            # Simplified positive expectation
            predicted_return = volatility * 0.1
        elif action == "SELL":
            # Simplified negative expectation
            predicted_return = -volatility * 0.1
        else:  # HOLD
            predicted_return = 0.0
        
        # Determine risk level
        if volatility > 0.05:
            risk_level = "HIGH"
        elif volatility > 0.02:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Calculate confidence based on data quality
        confidence = min(1.0, len(historical_close_prices) / 100.0)
        
        return {
            "predicted_return": predicted_return,
            "volatility": volatility,
            "confidence": confidence,
            "risk_level": risk_level
        }
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """
        Calculate volatility from historical prices.
        
        Args:
            prices: List of historical prices
            
        Returns:
            Float representing volatility (standard deviation of returns)
        """
        if len(prices) < 2:
            return 0.01  # Default low volatility
        
        # Calculate log returns
        log_returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                log_return = np.log(prices[i] / prices[i-1])
                log_returns.append(log_return)
        
        if not log_returns:
            return 0.01
        
        # Annualize volatility (assuming 252 trading days)
        volatility = np.std(log_returns) * np.sqrt(252)
        return volatility if volatility > 0 else 0.01
    
    def _generate_price_path(
        self, 
        initial_price: float, 
        volatility: float, 
        drift: float, 
        steps: int
    ) -> List[float]:
        """
        Generate a simulated price path using Geometric Brownian Motion.
        
        Args:
            initial_price: Starting price
            volatility: Volatility parameter
            drift: Drift parameter
            steps: Number of simulation steps
            
        Returns:
            List of simulated prices
        """
        # Time increment (hours)
        dt = self.simulation_params['forecast_horizon_hours'] / steps
        
        # Initialize price path
        prices = [initial_price]
        
        # Generate price path
        for _ in range(steps):
            # Random shock
            shock = np.random.normal(0, 1)
            
            # Calculate price change using GBM formula
            price_change = (drift - 0.5 * volatility**2) * dt + \
                volatility * np.sqrt(dt) * shock
            
            # Apply change to last price
            new_price = prices[-1] * np.exp(price_change)
            prices.append(new_price)
        
        return prices
    
    def _calculate_returns(self, prices: List[float]) -> List[float]:
        """
        Calculate returns from price series.
        
        Args:
            prices: List of prices
            
        Returns:
            List of returns
        """
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
            else:
                returns.append(0.0)
        return returns
    
    def _calculate_max_drawdown(self, prices: List[float]) -> float:
        """
        Calculate maximum drawdown from price series.
        
        Args:
            prices: List of prices
            
        Returns:
            Float representing maximum drawdown
        """
        if not prices:
            return 0.0
        
        peak = prices[0]
        max_dd = 0.0
        
        for price in prices:
            if price > peak:
                peak = price
            dd = (peak - price) / peak if peak != 0 else 0.0
            if dd > max_dd:
                max_dd = dd
                
        return max_dd
    
    def _get_alternative_action(self, action: str) -> str:
        """
        Get the alternative action for counterfactual analysis.
        
        Args:
            action: Original action
            
        Returns:
            Alternative action
        """
        if action == "BUY":
            return "SELL"
        elif action == "SELL":
            return "BUY"
        else:  # HOLD
            # For hold, we'll consider a buy as the alternative
            return "BUY"
    
    def _calculate_regret_cost(self, factual: float, 
                               counterfactual: float) -> float:
        """
        Calculate the regret cost of a decision.
        
        Regret cost represents the opportunity loss of taking action A
        instead of the optimal action B.
        
        Args:
            factual: Outcome of taken action
            counterfactual: Outcome of alternative action
            
        Returns:
            Float representing regret cost
        """
        # Regret is the difference between counterfactual and factual outcomes
        regret = counterfactual - factual
        
        # Ensure regret is non-negative (we only care about 
        # missed opportunities)
        return max(0.0, regret)
    
    def _calculate_confidence(self, volatility: float, 
                              history_length: int) -> float:
        """
        Calculate confidence in the simulation based on market conditions.
        
        Args:
            volatility: Market volatility
            history_length: Length of historical data
            
        Returns:
            Float representing confidence (0.0 - 1.0)
        """
        # Lower volatility increases confidence
        vol_confidence = max(0.0, 1.0 - volatility)
        
        # More history increases confidence
        history_confidence = min(1.0, history_length / 100.0)
        
        # Combine factors
        confidence = 0.7 * vol_confidence + 0.3 * history_confidence
        
        # Ensure bounds
        return max(0.0, min(1.0, confidence))
    
    async def _store_scenario(self, scenario: CounterfactualScenario) -> None:
        """
        Store a counterfactual scenario for learning.
        
        Args:
            scenario: CounterfactualScenario to store
        """
        # In a real implementation, this would store to D1 database
        # For now, we'll just cache it
        self.simulation_cache[scenario.scenario_id] = scenario
    
    def should_reject_decision(self, scenario: CounterfactualScenario) -> bool:
        """
        Determine if a decision should be rejected based on regret cost.
        
        Args:
            scenario: CounterfactualScenario to evaluate
            
        Returns:
            Boolean indicating whether decision should be rejected
        """
        # Reject if regret cost is too high and confidence is reasonable
        threshold_check = scenario.regret_cost > \
            self.simulation_params['max_regret_threshold']
        confidence_check = scenario.confidence > \
            self.simulation_params['confidence_threshold']
        return threshold_check and confidence_check
    
    async def get_engine_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the counterfactual engine.
        
        Returns:
            Dictionary with engine statistics
        """
        total_scenarios = len(self.simulation_cache)
        
        if total_scenarios > 0:
            avg_regret = np.mean([
                s.regret_cost for s in self.simulation_cache.values()
            ])
            avg_confidence = np.mean([
                s.confidence for s in self.simulation_cache.values()
            ])
            rejected_decisions = sum([
                1 for s in self.simulation_cache.values() 
                if self.should_reject_decision(s)
            ])
        else:
            avg_regret = 0.0
            avg_confidence = 0.0
            rejected_decisions = 0
        
        return {
            'total_scenarios_analyzed': total_scenarios,
            'average_regret_cost': avg_regret,
            'average_confidence': avg_confidence,
            'rejected_decisions': rejected_decisions,
            'max_regret_threshold': 
            self.simulation_params['max_regret_threshold']
        }
