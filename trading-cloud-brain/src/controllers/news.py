"""
📰 NEWS CONTROLLER - D1 Data Operations
Handles all /api/news/* endpoints.
"""

from js import Response, JSON
import json

from middleware.auth import with_internal_auth
from middleware.circuit_breaker import d1_circuit


async def handle_news_push(request, env, headers):
    """
    POST /api/news/push
    Ingests news from Oracle Spider into D1.
    Requires: X-Internal-Secret
    """
    # Circuit breaker check
    if not d1_circuit.can_execute():
        return Response.new(
            json.dumps({"error": "Service Unavailable", "reason": "D1 Circuit Open"}),
            status=503,
            headers=headers
        )

    try:
        body_js = await request.json()
        body = json.loads(JSON.stringify(body_js))

        stmt = env.TRADING_DB.prepare(
            "INSERT OR IGNORE INTO news (source, title, link, sentiment) VALUES (?, ?, ?, ?)"
        ).bind(
            body.get("source"),
            body.get("title"),
            body.get("link"),
            body.get("sentiment", "neutral")
        )

        await stmt.run()
        d1_circuit.record_success()

        return Response.new(json.dumps({"success": True}), headers=headers)

    except Exception as e:
        d1_circuit.record_failure()
        return Response.new(
            json.dumps({"error": f"Database Error: {str(e)}"}),
            status=500,
            headers=headers
        )


async def handle_news_latest(request, env, headers):
    """
    GET /api/news/latest
    Fetches recent news for AI analysis or dashboard.
    """
    if not d1_circuit.can_execute():
        return Response.new(
            json.dumps({"error": "Service Unavailable", "reason": "D1 Circuit Open"}),
            status=503,
            headers=headers
        )

    try:
        url = str(request.url)
        limit = 50

        if "?" in url:
            params = dict(p.split("=") for p in url.split("?")[1].split("&") if "=" in p)
            limit = int(params.get("limit", 50))

        result = await env.TRADING_DB.prepare(
            "SELECT id, source, title, published_at FROM news ORDER BY published_at DESC LIMIT ?"
        ).bind(limit).all()

        news_list = [
            {
                "id": row.id,
                "source": row.source,
                "title": row.title,
                "published_at": str(row.published_at)
            }
            for row in result.results
        ]

        d1_circuit.record_success()

        return Response.new(
            json.dumps({"news": news_list, "count": len(news_list)}),
            headers=headers
        )

    except Exception as e:
        d1_circuit.record_failure()
        return Response.new(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers
        )
