"""
Middleware __init__.py
Exposes all middleware functions.
"""

from middleware.auth import (
    validate_internal_secret,
    validate_system_key,
    with_internal_auth,
    with_system_auth
)

from middleware.cors import (
    create_cors_headers,
    create_headers_object
)

from middleware.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    d1_circuit,
    oracle_circuit
)

__all__ = [
    # Auth
    "validate_internal_secret",
    "validate_system_key",
    "with_internal_auth",
    "with_system_auth",
    # CORS
    "create_cors_headers",
    "create_headers_object",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    "d1_circuit",
    "oracle_circuit",
]
