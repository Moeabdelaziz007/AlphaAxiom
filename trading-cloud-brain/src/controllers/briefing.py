"""
🤖 BRIEFING CONTROLLER - AI Summaries
Handles all /api/briefing/* endpoints.
"""

from js import Response, JSON
import json

from middleware.circuit_breaker import d1_circuit


async def handle_briefing_save(request, env, headers):
    """
    POST /api/briefing/save
    Saves AI-generated briefing to D1.
    Requires: X-Internal-Secret (validated in router)
    """
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
            "INSERT INTO briefings (summary, sentiment) VALUES (?, ?)"
        ).bind(
            body.get("summary"),
            body.get("sentiment", "neutral")
        )

        await stmt.run()
        d1_circuit.record_success()

        return Response.new(
            json.dumps({"success": True, "message": "Briefing Saved ✅"}),
            headers=headers
        )

    except Exception as e:
        d1_circuit.record_failure()
        return Response.new(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers
        )


async def handle_briefing_latest(request, env, headers):
    """
    GET /api/briefing/latest
    Retrieves the most recent AI briefing for the dashboard.
    """
    if not d1_circuit.can_execute():
        return Response.new(
            json.dumps({"error": "Service Unavailable", "reason": "D1 Circuit Open"}),
            status=503,
            headers=headers
        )

    try:
        result = await env.TRADING_DB.prepare(
            "SELECT id, summary, sentiment, created_at FROM briefings ORDER BY created_at DESC LIMIT 1"
        ).first()

        if result:
            d1_circuit.record_success()
            return Response.new(
                json.dumps({
                    "id": result.id,
                    "summary": result.summary,
                    "sentiment": result.sentiment,
                    "created_at": str(result.created_at)
                }),
                headers=headers
            )
        else:
            return Response.new(
                json.dumps({"message": "No briefings available yet"}),
                headers=headers
            )

    except Exception as e:
        d1_circuit.record_failure()
        return Response.new(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers
        )
