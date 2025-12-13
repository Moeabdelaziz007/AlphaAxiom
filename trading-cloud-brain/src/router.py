"""
🛣️ CENTRAL ROUTER - Request Dispatcher
Decouples URL matching from business logic.
This is the ONLY file that knows about all endpoints.

Usage:
    In worker.py, call:
        from router import dispatch_request
        response = await dispatch_request(request, env)
"""

from js import Response
import json

# Middleware
from middleware.cors import create_headers_object
from middleware.auth import validate_internal_secret, validate_system_key
from core import log

# Controllers
from controllers.news import handle_news_push, handle_news_latest
from controllers.briefing import handle_briefing_save, handle_briefing_latest
from controllers.health import handle_healthz, handle_status


# ==========================================
# 📋 ROUTE TABLE
# ==========================================
# Format: (path_contains, method, handler, requires_auth)

PUBLIC_ROUTES = [
    # Health
    ("/healthz", "GET", handle_healthz, None),
    ("/api/health", "GET", handle_healthz, None),
    ("/api/status", "GET", handle_status, None),
    # News (Read)
    ("/api/news/latest", "GET", handle_news_latest, None),
    # Briefing (Read)
    ("/api/briefing/latest", "GET", handle_briefing_latest, None),
]

INTERNAL_ROUTES = [
    # News (Write - requires INTERNAL_SECRET)
    ("/api/news/push", "POST", handle_news_push, "internal"),
    # Briefing (Write - requires INTERNAL_SECRET)
    ("/api/briefing/save", "POST", handle_briefing_save, "internal"),
]

# Combine for lookup
ALL_ROUTES = PUBLIC_ROUTES + INTERNAL_ROUTES


# ==========================================
# 🎯 DISPATCH LOGIC
# ==========================================

async def dispatch_request(request, env) -> Response:
    """
    Main request dispatcher.
    Routes to appropriate controller based on URL path.

    Args:
        request: Cloudflare Request object.
        env: Worker environment (secrets, KV, D1).

    Returns:
        Response object.
    """
    url = str(request.url)
    method = str(request.method)

    # Generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID") or log.new_correlation_id()
    log.set_correlation_id(correlation_id)
    log.request(method, url.split("?")[0])

    # Create headers
    headers = create_headers_object(correlation_id)

    # Handle CORS Preflight
    if method == "OPTIONS":
        return Response.new("", headers=headers)

    # Root path
    if url.endswith("/") or url.endswith("/api"):
        return Response.new(
            json.dumps({
                "name": "Antigravity MoE Brain",
                "version": "2.1-modular",
                "status": "🔒 Secured",
                "message": "Router Pattern Active"
            }),
            headers=headers
        )

    # Match route
    for path, route_method, handler, auth_type in ALL_ROUTES:
        if path in url and (route_method == method or route_method == "*"):
            # Auth check
            if auth_type == "internal":
                if not validate_internal_secret(request, env):
                    return Response.new(
                        json.dumps({"error": "⛔ Unauthorized: Invalid X-Internal-Secret"}),
                        status=401,
                        headers=headers
                    )
            elif auth_type == "system":
                if not validate_system_key(request, env):
                    return Response.new(
                        json.dumps({"error": "⛔ Unauthorized: Invalid X-System-Key"}),
                        status=401,
                        headers=headers
                    )

            # Execute handler
            try:
                return await handler(request, env, headers)
            except Exception as e:
                log.error(f"Handler error: {str(e)}")
                return Response.new(
                    json.dumps({"error": str(e)}),
                    status=500,
                    headers=headers
                )

    # Fallback: Return 404 or delegate to legacy worker
    return None  # Signal to worker.py to use legacy routing
