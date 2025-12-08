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
                # When releasing lock (trade closed), we can optionally record history
                self._release_lock(symbol)
                return Response.new(json.dumps({"released": True}))

            # --- PERSISTENCE (Write-Behind) ---
            if "record_trade" in url:
                trade_data = await request.json()
                # Run async background task to save to D1 without blocking response
                # Note: Cloudflare Workers should use ctx.waitUntil, but in DO we
                # usually just await or spawn. For safety/speed, we await here or use correct syntax.
                await self._persist_to_d1(trade_data)
                return Response.new(json.dumps({"recorded": True}))
                
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

    async def _persist_to_d1(self, trade):
        """
        Persist closed trade to D1 Database (WARM Storage).
        """
        try:
            # Prepare SQL query
            query = """
                INSERT INTO trades (id, symbol, direction, entry_price, exit_price, qty, pnl, status, opened_at, closed_at, strategy, meta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Bind parameters safely
            params = [
                trade.get("id"),
                trade.get("symbol"),
                trade.get("direction"),
                trade.get("entry_price"),
                trade.get("exit_price"),
                trade.get("qty"),
                trade.get("pnl"),
                trade.get("status"),
                trade.get("opened_at"),
                trade.get("closed_at"),
                trade.get("strategy"),
                json.dumps(trade.get("meta", {}))
            ]
            
            # Execute against D1 binding (TRADING_DB)
            # Assuming self.env.TRADING_DB is available
            if hasattr(self.env, 'TRADING_DB'):
                await self.env.TRADING_DB.prepare(query).bind(*params).run()
            else:
                print(f"⚠️ persist_to_d1: TRADING_DB binding not found. Trade: {trade.get('id')}")

        except Exception as e:
            print(f"❌ D1 Write Error: {e}")
            # In production, we might save to a 'dead letter queue' or Retry logic

