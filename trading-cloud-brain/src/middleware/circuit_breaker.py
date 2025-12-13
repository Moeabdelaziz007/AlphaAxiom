"""
⚡ CIRCUIT BREAKER - Fail-Safe Pattern
Protects downstream services (D1, Oracle) from cascading failures.

States:
    CLOSED:    Normal operation, all requests pass through.
    OPEN:      Failure threshold exceeded, requests are blocked (return cached/503).
    HALF_OPEN: Testing if service recovered (allow 1 request through).

Configuration:
    FAILURE_THRESHOLD: 3 failures within WINDOW_SECONDS opens the circuit.
    RECOVERY_TIMEOUT: 30 seconds before attempting recovery (HALF_OPEN).
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitBreaker:
    """
    In-memory circuit breaker for Worker instance.

    Note: Cloudflare Workers are stateless per-request.
    For true persistence, use KV or Durable Objects.
    This implementation provides per-instance protection.
    """
    name: str
    failure_threshold: int = 3
    recovery_timeout: int = 30  # seconds
    window_seconds: int = 60

    # State tracking
    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0

    def record_success(self):
        """Record a successful call."""
        self.failure_count = 0
        self.last_success_time = time.time()
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def can_execute(self) -> bool:
        """
        Check if a request should be allowed through.

        Returns:
            True if request should proceed, False if blocked.
        """
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        # HALF_OPEN: Allow one request through to test
        return True

    def get_status(self) -> Dict:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time,
            "last_success": self.last_success_time,
        }


# Global circuit breakers for critical services
oracle_circuit = CircuitBreaker(name="oracle_uplink", failure_threshold=3, recovery_timeout=30)
d1_circuit = CircuitBreaker(name="d1_database", failure_threshold=5, recovery_timeout=15)
