"""
🌐 CORS MIDDLEWARE - Unified Headers Factory
Ensures consistent CORS headers across all responses.
"""

from js import Headers


def create_cors_headers(correlation_id: str = None) -> dict:
    """
    Create standard CORS headers for API responses.

    Args:
        correlation_id: Optional request trace ID.

    Returns:
        Dictionary of CORS headers.
    """
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
        "Access-Control-Allow-Headers": "Content-Type, X-System-Key, X-Internal-Secret, X-Correlation-ID, X-API-Key",
    }

    if correlation_id:
        headers["X-Correlation-ID"] = correlation_id

    return headers


def create_headers_object(correlation_id: str = None) -> Headers:
    """
    Create a Cloudflare Headers object with CORS settings.

    Args:
        correlation_id: Optional request trace ID.

    Returns:
        Cloudflare Headers object.
    """
    return Headers.new(create_cors_headers(correlation_id).items())
