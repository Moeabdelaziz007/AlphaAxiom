"""
🛡️ AUTH MIDDLEWARE - Security Layer
Zero Trust Validation for Internal and External Requests.

Usage:
    from middleware.auth import require_internal_secret, require_system_key

    @require_internal_secret
    async def handle_news_push(request, env, headers):
        # Only runs if X-Internal-Secret is valid
        ...
"""

from js import Response
import json


def _create_error_response(message: str, status: int = 401):
    """Factory for error responses."""
    return Response.new(
        json.dumps({"error": message, "status": status}),
        status=status,
        headers={"Content-Type": "application/json"}
    )


def validate_internal_secret(request, env) -> bool:
    """
    Validate the X-Internal-Secret header.
    Used for Oracle → Edge communication.

    Returns:
        True if valid, False otherwise.
    """
    auth_header = request.headers.get("X-Internal-Secret")
    internal_secret = str(getattr(env, 'INTERNAL_SECRET', ''))

    if not internal_secret:
        # Secret not configured = FAIL SECURE
        return False

    return auth_header == internal_secret


def validate_system_key(request, env) -> bool:
    """
    Validate the X-System-Key header.
    Used for Frontend → Edge communication.

    Returns:
        True if valid, False otherwise.
    """
    client_key = request.headers.get("X-System-Key")
    system_secret = str(getattr(env, 'SYSTEM_ACCESS_KEY', ''))

    if not system_secret:
        # No secret configured = Allow (Public Mode)
        return True

    return client_key == system_secret


async def with_internal_auth(handler, request, env, headers):
    """
    Higher-order function to wrap handlers with internal auth.

    Args:
        handler: The async function to call if auth passes.
        request: Cloudflare Request object.
        env: Worker environment.
        headers: CORS headers.

    Returns:
        Response from handler or 401 error.
    """
    if not validate_internal_secret(request, env):
        return _create_error_response("⛔ Unauthorized: Invalid X-Internal-Secret", 401)

    return await handler(request, env, headers)


async def with_system_auth(handler, request, env, headers):
    """
    Higher-order function to wrap handlers with system key auth.

    Args:
        handler: The async function to call if auth passes.
        request: Cloudflare Request object.
        env: Worker environment.
        headers: CORS headers.

    Returns:
        Response from handler or 401 error.
    """
    if not validate_system_key(request, env):
        return _create_error_response("⛔ Unauthorized: Invalid X-System-Key", 401)

    return await handler(request, env, headers)
