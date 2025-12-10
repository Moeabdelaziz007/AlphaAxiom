"""
Cloudflare Worker Integration for AlphaAxiom v1.0 Self-Play Learning Loop
Provides endpoints and utilities for running the learning loop in Cloudflare Workers.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import the orchestrator
from learning_loop_v4.main import AlphaAxiomOrchestrator

# Global orchestrator instance (initialized once per worker instance)
orchestrator: AlphaAxiomOrchestrator = None


async def initialize_orchestrator(env: Any = None):
    """
    Initialize the AlphaAxiom orchestrator with Cloudflare bindings.
    
    Args:
        env: Cloudflare environment object with bindings
    """
    global orchestrator
    
    if orchestrator is None:
        # Initialize with Cloudflare bindings if available
        d1_db = getattr(env, 'D1_DB', None) if env else None
        r2_bucket = getattr(env, 'R2_BUCKET', None) if env else None
        
        orchestrator = AlphaAxiomOrchestrator(d1_db, r2_bucket)
        print("AlphaAxiom orchestrator initialized")


async def handle_dialectic_request(request: Any, env: Any) -> Dict[str, Any]:
    """
    Handle a dialectic processing request.
    
    Args:
        request: Incoming HTTP request with market data
        env: Cloudflare environment object
        
    Returns:
        Processing result as dictionary
    """
    try:
        # Initialize orchestrator if needed
        await initialize_orchestrator(env)
        
        # Parse request body
        content_type = request.headers.get('content-type', '')
        if 'application/json' in content_type:
            body = await request.json()
        else:
            body = {}
        
        # Process market data
        result = await orchestrator.process_market_data(body)
        return result
        
    except Exception as e:
        print(f"Error in dialectic request handling: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def handle_evolution_request(request: Any, env: Any) -> Dict[str, Any]:
    """
    Handle an evolution cycle request.
    
    Args:
        request: Incoming HTTP request
        env: Cloudflare environment object
        
    Returns:
        Evolution result as dictionary
    """
    try:
        # Initialize orchestrator if needed
        await initialize_orchestrator(env)
        
        # Parse request body for crime scenes (optional)
        crime_scenes = None
        content_type = request.headers.get('content-type', '')
        if 'application/json' in content_type:
            body = await request.json()
            crime_scenes = body.get('crime_scenes')
        
        # Run evolution cycle
        result = await orchestrator.run_evolution_cycle(crime_scenes)
        return result
        
    except Exception as e:
        print(f"Error in evolution request handling: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def handle_status_request(request: Any, env: Any) -> Dict[str, Any]:
    """
    Handle a system status request.
    
    Args:
        request: Incoming HTTP request
        env: Cloudflare environment object
        
    Returns:
        System status as dictionary
    """
    try:
        # Initialize orchestrator if needed
        await initialize_orchestrator(env)
        
        # Get system status
        status = await orchestrator.get_system_status()
        return status
        
    except Exception as e:
        print(f"Error in status request handling: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def handle_stream_request(request: Any, env: Any) -> Any:
    """
    Handle a real-time streaming request for dialectic sessions.
    
    Args:
        request: Incoming HTTP request
        env: Cloudflare environment object
        
    Returns:
        Streaming response
    """
    try:
        # Initialize orchestrator if needed
        await initialize_orchestrator(env)
        
        # In a real implementation, this would set up an SSE stream
        # For now, we'll return a placeholder
        return {
            "status": "streaming",
            "endpoint": "/api/dialectic/stream",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error in stream request handling: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Cloudflare Worker entry point
async def handle_request(request: Any, env: Any, ctx: Any) -> Any:
    """
    Main request handler for Cloudflare Worker.
    
    Args:
        request: Incoming HTTP request
        env: Cloudflare environment object
        ctx: Cloudflare context object
        
    Returns:
        HTTP response
    """
    try:
        # Route based on URL path
        url = request.url
        path = url.path if hasattr(url, 'path') else str(url).split('/')[-1]
        
        # Handle CORS preflight requests
        if request.method == 'OPTIONS':
            return create_cors_response()
        
        # Route to appropriate handler
        if path.startswith('/api/dialectic/process') or path == '/api/dialectic':
            result = await handle_dialectic_request(request, env)
            return create_json_response(result)
            
        elif path.startswith('/api/evolution/run') or path == '/api/evolution':
            result = await handle_evolution_request(request, env)
            return create_json_response(result)
            
        elif path.startswith('/api/system/status') or path == '/api/status':
            result = await handle_status_request(request, env)
            return create_json_response(result)
            
        elif path.startswith('/api/dialectic/stream'):
            result = await handle_stream_request(request, env)
            return create_json_response(result)
            
        else:
            # Default response
            return create_json_response({
                "message": "AlphaAxiom v1.0 Self-Play Learning Loop API",
                "endpoints": [
                    "POST /api/dialectic - Process market data through dialectic pipeline",
                    "POST /api/evolution - Run evolution cycle",
                    "GET /api/status - Get system status",
                    "GET /api/dialectic/stream - Real-time dialectic session stream"
                ],
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        print(f"Error in main request handler: {str(e)}")
        return create_json_response({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status=500)


def create_json_response(data: Dict[str, Any], status: int = 200) -> Any:
    """
    Create a JSON HTTP response.
    
    Args:
        data: Response data as dictionary
        status: HTTP status code
        
    Returns:
        HTTP response object
    """
    # This is a placeholder - actual implementation depends on Cloudflare Worker framework
    # In a real worker, you would return:
    # return Response(json.dumps(data), status=status, headers={
    #     'Content-Type': 'application/json',
    #     'Access-Control-Allow-Origin': '*',
    #     'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    #     'Access-Control-Allow-Headers': 'Content-Type, X-System-Key'
    # })
    
    return {
        "data": data,
        "status": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-System-Key"
        }
    }


def create_cors_response() -> Any:
    """
    Create a CORS preflight response.
    
    Returns:
        HTTP response object
    """
    # This is a placeholder - actual implementation depends on Cloudflare Worker framework
    return {
        "status": 204,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-System-Key",
            "Access-Control-Max-Age": "86400"
        }
    }


# Example usage for testing
if __name__ == "__main__":
    print("AlphaAxiom Cloudflare Integration Module")
    print("This module is designed to run in Cloudflare Workers environment")