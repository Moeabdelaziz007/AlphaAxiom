"""
🏥 HEALTH CONTROLLER - System Status
Handles /healthz and /api/status endpoints.
"""

from js import Response
import json
import datetime

from middleware.circuit_breaker import d1_circuit, oracle_circuit


async def handle_healthz(request, env, headers) -> Response:
    """
    GET /healthz
    Kubernetes-style health probe.
    Checks KV, D1, and Broker connectivity.
    """
    correlation_id = request.headers.get("X-Correlation-ID") or "unknown"

    components = {
        "kv": False,
        "db": False,
        "broker": False,
        "circuits": {
            "d1": d1_circuit.get_status(),
            "oracle": oracle_circuit.get_status()
        }
    }

    # KV Check
    try:
        kv = getattr(env, 'BRAIN_MEMORY', None)
        if kv:
            await kv.get("health_check_ping")
            components["kv"] = True
    except:
        pass

    # D1 Check
    try:
        db = getattr(env, 'TRADING_DB', None)
        if db:
            await db.prepare("SELECT 1").first()
            components["db"] = True
    except:
        pass

    # Broker Check (Simple key existence)
    components["broker"] = bool(getattr(env, 'ALPACA_KEY', '')) or bool(getattr(env, 'CAPITAL_API_KEY', ''))

    healthy = components["kv"] and components["db"]
    status_code = 200 if healthy else 503

    return Response.new(
        json.dumps({
            "status": "healthy" if healthy else "degraded",
            "components": components,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "correlation_id": correlation_id
        }),
        status=status_code,
        headers=headers
    )


async def handle_status(request, env, headers) -> Response:
    """
    GET /api/status
    Basic system status for dashboard.
    """
    return Response.new(
        json.dumps({
            "status": "online",
            "version": "2.1-modular",
            "name": "Antigravity MoE Brain",
            "architecture": "Router/Controller Pattern",
            "components": {
                "d1_circuit": d1_circuit.state.value,
                "oracle_circuit": oracle_circuit.state.value
            }
        }),
        headers=headers
    )
