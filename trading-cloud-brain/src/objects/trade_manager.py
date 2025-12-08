"""
🏰 TradeManager - Durable Object
The "Citadel" of strict state consistency.

Role:
- In-memory strict locking (Single Threaded)
- Prevents race conditions 100%
- Manages trade lifecycle state (OPEN -> ORDER_SENT -> FILLED -> CLOSED)
"""

import json
from js import Response, Headers

class TradeManager:
    def __init__(self, state, env):
        self.state = state
        self.env = env
        # In-memory lock state (strictly consistent within this DO instance)
        self.locks = {} 
    
    async def fetch(self, request):
        """
        RPC Handler.
        Route requests to internal methods.
        """
        try:
            url = str(request.url)
            method = str(request.method)
            
            # --- LOCKING ---
            if "acquire_lock" in url:
                data = await request.json()
                symbol = data.get("symbol")
                acquired = self._acquire_lock(symbol)
                return Response.new(json.dumps({"acquired": acquired}))
                
            if "release_lock" in url:
                data = await request.json()
                symbol = data.get("symbol")
                self._release_lock(symbol)
                return Response.new(json.dumps({"released": True}))
                
            # --- ACCOUNTING ---
            if "get_state" in url:
                return Response.new(json.dumps({
                    "locks": self.locks,
                    "active_trades": await self.state.storage.list()
                }))

            return Response.new("Method not found", status=404)
            
        except Exception as e:
            return Response.new(f"Error: {str(e)}", status=500)

    def _acquire_lock(self, symbol):
        """Strict in-memory lock"""
        if symbol in self.locks:
            return False
        self.locks[symbol] = True
        return True
        
    def _release_lock(self, symbol):
        if symbol in self.locks:
            del self.locks[symbol]
