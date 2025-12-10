"""
Circuit Breaker System for AlphaAxiom v0.1 Beta
Implements multi-layer protection with Fail-Close philosophy.
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BreakerState(Enum):
    """Circuit Breaker States"""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Tripped - blocking all requests
    HALF_OPEN = "half_open" # Recovery probe mode


@dataclass
class BreakerConfig:
    """Configuration for a circuit breaker"""
    max_failures: int = 3
    cooldown_seconds: int = 300  # 5 minutes
    timeout_seconds: float = 15.0
    half_open_max_calls: int = 1


class CircuitBreaker:
    """
    Individual circuit breaker with state machine logic.
    Follows the Fail-Close philosophy.
    """
    
    def __init__(self, name: str, config: BreakerConfig = None):
        self.name = name
        self.config = config or BreakerConfig()
        self.state = BreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
    
    def check(self) -> bool:
        """Check if the breaker allows requests"""
        if self.state == BreakerState.CLOSED:
            return True
        
        if self.state == BreakerState.OPEN:
            # Check if cooldown has passed
            if self._cooldown_elapsed():
                self._transition_to_half_open()
                return True
            return False
        
        if self.state == BreakerState.HALF_OPEN:
            # Allow limited probe requests
            if self.half_open_calls < self.config.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
        
        return False
    
    def record_success(self) -> None:
        """Record a successful operation"""
        if self.state == BreakerState.HALF_OPEN:
            # Successful probe - reset to CLOSED
            self._transition_to_closed()
        elif self.state == BreakerState.CLOSED:
            # Reduce failure count on success
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self) -> None:
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == BreakerState.HALF_OPEN:
            # Probe failed - back to OPEN
            self._transition_to_open()
        elif self.failure_count >= self.config.max_failures:
            self._transition_to_open()
    
    def _transition_to_open(self) -> None:
        """Trip the circuit breaker"""
        logger.warning(f"Circuit Breaker [{self.name}] TRIPPED -> OPEN")
        self.state = BreakerState.OPEN
        self.last_failure_time = datetime.now()
    
    def _transition_to_half_open(self) -> None:
        """Enter recovery probe mode"""
        logger.info(f"Circuit Breaker [{self.name}] -> HALF_OPEN (probing)")
        self.state = BreakerState.HALF_OPEN
        self.half_open_calls = 0
    
    def _transition_to_closed(self) -> None:
        """Reset to normal operation"""
        logger.info(f"Circuit Breaker [{self.name}] -> CLOSED (recovered)")
        self.state = BreakerState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0
    
    def _cooldown_elapsed(self) -> bool:
        """Check if cooldown period has passed"""
        if not self.last_failure_time:
            return True
        elapsed = datetime.now() - self.last_failure_time
        return elapsed.total_seconds() >= self.config.cooldown_seconds


class LatencyBreaker(CircuitBreaker):
    """
    Specialized breaker for latency monitoring.
    Trips if Shadow response takes > 15 seconds.
    """
    
    def __init__(self, max_latency_seconds: float = 15.0):
        super().__init__("latency_breaker", BreakerConfig(timeout_seconds=max_latency_seconds))
        self.max_latency = max_latency_seconds
    
    def record_latency(self, latency_seconds: float) -> None:
        """Record response latency"""
        if latency_seconds > self.max_latency:
            logger.warning(f"Latency breach: {latency_seconds:.2f}s > {self.max_latency}s")
            self.record_failure()
        else:
            self.record_success()


class RiskBreaker(CircuitBreaker):
    """
    Dynamic risk breaker based on portfolio drawdown.
    Trips if max drawdown exceeds threshold.
    """
    
    def __init__(self, max_drawdown: float = 0.05):
        super().__init__("risk_breaker", BreakerConfig(max_failures=1))
        self.max_drawdown = max_drawdown
        self.initial_value: Optional[float] = None
        self.peak_value: Optional[float] = None
    
    def update_portfolio_value(self, current_value: float) -> None:
        """Update with current portfolio value and check drawdown"""
        if self.initial_value is None:
            self.initial_value = current_value
            self.peak_value = current_value
            return
        
        # Update peak
        if current_value > self.peak_value:
            self.peak_value = current_value
        
        # Calculate drawdown from peak
        drawdown = (self.peak_value - current_value) / self.peak_value
        
        if drawdown > self.max_drawdown:
            logger.critical(f"Risk Breaker: Drawdown {drawdown:.2%} > {self.max_drawdown:.2%}")
            self.record_failure()
        else:
            self.record_success()
    
    def check(self) -> bool:
        """Override to provide immediate risk check"""
        return self.state != BreakerState.OPEN


class SemanticDriftBreaker(CircuitBreaker):
    """
    Detects "Model Collapse" - when Core and Shadow become correlated.
    If they agree on everything, the dialectic is broken.
    """
    
    def __init__(self, correlation_threshold: float = 0.9, window_size: int = 50):
        super().__init__("semantic_drift_breaker")
        self.correlation_threshold = correlation_threshold
        self.window_size = window_size
        self.recent_agreements: list = []
    
    def record_dialectic(self, core_decision: str, shadow_agrees: bool) -> None:
        """Record whether Shadow agreed with Core"""
        self.recent_agreements.append(1 if shadow_agrees else 0)
        
        # Keep window size
        if len(self.recent_agreements) > self.window_size:
            self.recent_agreements.pop(0)
        
        # Check correlation
        if len(self.recent_agreements) >= self.window_size:
            agreement_rate = sum(self.recent_agreements) / len(self.recent_agreements)
            
            if agreement_rate > self.correlation_threshold:
                logger.critical(f"Semantic Drift: Agreement rate {agreement_rate:.2%} - Model Collapse!")
                self.record_failure()
            else:
                self.record_success()


class CircuitBreakerSystem:
    """
    Main orchestrator for all circuit breakers.
    Implements the "Fail-Close" philosophy.
    """
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {
            "api_breaker": CircuitBreaker("api_breaker", BreakerConfig(max_failures=3, cooldown_seconds=300)),
            "latency_breaker": LatencyBreaker(max_latency_seconds=15.0),
            "risk_breaker": RiskBreaker(max_drawdown=0.05),
            "semantic_drift_breaker": SemanticDriftBreaker()
        }
        
        self.system_halted = False
        self._alert_callbacks: list = []
    
    def add_alert_callback(self, callback: Callable[[str, str], None]) -> None:
        """Add callback for alert notifications"""
        self._alert_callbacks.append(callback)
    
    def _send_alert(self, breaker_name: str, message: str) -> None:
        """Send alert to all registered callbacks"""
        for callback in self._alert_callbacks:
            try:
                callback(breaker_name, message)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    async def execute_trade(
        self, 
        trade_signal: Dict[str, Any],
        portfolio_value: float,
        initial_value: float,
        execution_func: Callable
    ) -> Any:
        """
        Execute a trade with full circuit breaker protection.
        Returns "BLOCKED" if any breaker is tripped.
        """
        # Check all breakers first
        for name, breaker in self.breakers.items():
            if not breaker.check():
                logger.warning(f"Trade blocked by {name}")
                self._send_alert(name, f"Trade blocked: {trade_signal.get('symbol', 'unknown')}")
                return "BLOCKED"
        
        # Update risk breaker with current portfolio
        self.breakers["risk_breaker"].update_portfolio_value(portfolio_value)
        
        # Execute with latency monitoring
        start_time = datetime.now()
        
        try:
            result = await asyncio.wait_for(
                execution_func(trade_signal),
                timeout=self.breakers["latency_breaker"].max_latency
            )
            
            # Record latency
            latency = (datetime.now() - start_time).total_seconds()
            self.breakers["latency_breaker"].record_latency(latency)
            
            # Record API success
            self.breakers["api_breaker"].record_success()
            
            return result
            
        except asyncio.TimeoutError:
            logger.error("Trade execution timed out")
            self.breakers["latency_breaker"].record_failure()
            return "BLOCKED"
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            self.breakers["api_breaker"].record_failure()
            return "BLOCKED"
    
    def trigger_emergency_halt(self, reason: str) -> None:
        """
        Trigger emergency system halt.
        Used by Shadow Agent when detecting adversarial inputs.
        """
        logger.critical(f"EMERGENCY HALT: {reason}")
        self.system_halted = True
        
        # Trip all breakers
        for breaker in self.breakers.values():
            breaker._transition_to_open()
        
        self._send_alert("EMERGENCY", reason)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current status of all breakers"""
        return {
            "system_halted": self.system_halted,
            "breakers": {
                name: {
                    "state": breaker.state.value,
                    "failure_count": breaker.failure_count,
                    "check_allowed": breaker.check()
                }
                for name, breaker in self.breakers.items()
            }
        }