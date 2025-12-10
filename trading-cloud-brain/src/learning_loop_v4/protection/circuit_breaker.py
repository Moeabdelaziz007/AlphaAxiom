"""
Multi-Layer Circuit Breaker System for AlphaAxiom v1.0
Provides robust failure management for the Self-Play Learning Loop.
"""

import time
import json
from typing import Dict, Any, Optional, Callable
from enum import Enum


class CircuitState(Enum):
    """Enumeration of circuit breaker states"""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerBase:
    """Base class for circuit breakers"""
    
    def __init__(self, name: str, failure_threshold: int = 3, timeout: int = 300):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED
    
    def can_execute(self) -> bool:
        """Check if execution is allowed based on circuit state"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True
    
    def on_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def on_failure(self, error: str = ""):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


class ApiCircuitBreaker(CircuitBreakerBase):
    """Circuit breaker for API calls"""
    
    def __init__(self, max_fails: int = 3, cooldown: int = 300):
        super().__init__("API_BREAKER", max_fails, cooldown)


class RiskCircuitBreaker(CircuitBreakerBase):
    """Circuit breaker for risk management"""
    
    def __init__(self, max_drawdown: float = 0.05):
        super().__init__("RISK_BREAKER", 1, 0)  # Trigger immediately
        self.max_drawdown = max_drawdown
        self.portfolio_history = []
    
    def check(self, current_portfolio_value: float, initial_value: float) -> bool:
        """Check if risk limits are exceeded"""
        if initial_value <= 0:
            return False
            
        drawdown = (initial_value - current_portfolio_value) / initial_value
        return drawdown < self.max_drawdown


class LatencyCircuitBreaker(CircuitBreakerBase):
    """Circuit breaker for latency monitoring"""
    
    def __init__(self, max_latency: float = 15.0):
        super().__init__("LATENCY_BREAKER", 3, 300)
        self.max_latency = max_latency
    
    def check(self, current_latency: float) -> bool:
        """Check if latency exceeds threshold"""
        return current_latency < self.max_latency


class CircuitBreakerSystem:
    """
    Multi-layer Circuit Breaker System for protecting the AlphaAxiom system.
    Provides multiple levels of protection against various failure modes.
    """
    
    def __init__(self):
        self.breakers = {
            "api_breaker": ApiCircuitBreaker(max_fails=3, cooldown=300),
            "risk_breaker": RiskCircuitBreaker(max_drawdown=0.05),
            "latency_breaker": LatencyCircuitBreaker(max_latency=15.0)
        }
    
    async def execute_trade(self, trade_signal: Dict[str, Any], 
                          portfolio_value: float, 
                          initial_value: float,
                          execution_func: Callable) -> str:
        """
        Execute trade with multi-layer protection.
        
        Args:
            trade_signal: Trade signal to execute
            portfolio_value: Current portfolio value
            initial_value: Initial portfolio value
            execution_func: Function to execute the trade
            
        Returns:
            Execution status ("EXECUTED", "BLOCKED", or "FAILED")
        """
        # Check all circuit breakers
        for name, breaker in self.breakers.items():
            if hasattr(breaker, 'check'):
                # Specialized check for certain breakers
                if name == "risk_breaker":
                    if not breaker.check(portfolio_value, initial_value):
                        await self._safe_block_trade(
                            f"Risk breaker tripped: {name}", 
                            trade_signal
                        )
                        return "BLOCKED"
                elif name == "latency_breaker":
                    # In a real implementation, we would measure actual latency
                    # For now, we'll assume it passes
                    pass
            else:
                # Standard circuit breaker check
                if not breaker.can_execute():
                    await self._safe_block_trade(
                        f"Circuit breaker tripped: {name}", 
                        trade_signal
                    )
                    return "BLOCKED"
        
        # If all breakers pass, execute the trade
        try:
            result = await execution_func(trade_signal)
            # Record success for all breakers
            for breaker in self.breakers.values():
                if hasattr(breaker, 'on_success'):
                    breaker.on_success()
            return "EXECUTED"
        except Exception as e:
            # Record failure for all breakers
            for breaker in self.breakers.values():
                if hasattr(breaker, 'on_failure'):
                    breaker.on_failure(str(e))
            return "FAILED"
    
    async def _safe_block_trade(self, reason: str, trade_signal: Dict[str, Any]):
        """
        Safely block a trade and log the reason.
        
        Args:
            reason: Reason for blocking the trade
            trade_signal: Trade signal that was blocked
        """
        print(f"[CIRCUIT_BREAKER] Trade blocked: {reason}")
        print(f"[CIRCUIT_BREAKER] Blocked signal: {json.dumps(trade_signal, indent=2)}")
        
        # In a real implementation, you might want to:
        # 1. Log to a monitoring system
        # 2. Send alerts
        # 3. Store blocked trades for later analysis


# Example usage
if __name__ == "__main__":
    # This would be used in the main system
    circuit_breaker_system = CircuitBreakerSystem()
    print("Circuit Breaker System initialized")