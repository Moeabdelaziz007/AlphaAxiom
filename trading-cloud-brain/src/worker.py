from js import Response, Headers, fetch
import json
import re

# ==========================================
# 🧠 ANTIGRAVITY TRADING BRAIN v5.0
# D1 Database + Smart Chat + Alpaca Execution
# The Master Controller
# ==========================================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
ALPACA_API_URL = "https://paper-api.alpaca.markets/v2"

# Circuit Breaker Limits
MAX_TRADES_PER_DAY = 10

SYSTEM_PROMPT = """You are the Architect of a Trading Bot. Translate user commands into strict JSON.

OUTPUT FORMAT:
{
  "type": "CREATE_RULE" | "EXECUTE_TRADE" | "CHAT" | "ANALYZE",
  "response_text": "Brief confirmation to user...",
  "trade_data": { "ticker": "AAPL", "side": "buy", "qty": 10 },
  "rule_data": { "ticker": "SPY", "logic_json": { "condition": "RSI_BELOW", "trigger": 30, "action": "BUY", "qty": 5 } }
}

Examples:
- "Buy 10 AAPL" → type="EXECUTE_TRADE", trade_data={ticker:"AAPL", side:"buy", qty:10}
- "If RSI drops below 30, buy SPY" → type="CREATE_RULE", rule_data={...}
- "Analyze TSLA" → type="ANALYZE", response_text="Market analysis..."
- "Hello" → type="CHAT", response_text="Hello! I'm your trading assistant..."

For trades, set trade_data. For rules, set rule_data. For chat/analyze, set response_text only."""


async def on_fetch(request, env):
    """Master Controller: Chat → AI → D1 → Alpaca"""
    
    url = str(request.url)
    method = str(request.method)
    
    # CORS Headers
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    headers = Headers.new(cors_headers.items())
    
    if method == "OPTIONS":
        return Response.new("", headers=headers)
    
    # ============ ROUTES ============
    
    if "api/chat" in url:
        return await handle_smart_chat(request, env, headers)
    
    if "api/trade" in url:
        return await handle_direct_trade(request, env, headers)
    
    if "api/rules" in url:
        return await get_rules(env, headers)
    
    if "api/logs" in url:
        return await get_logs(env, headers)
    
    if "api/account" in url:
        return await get_account(env, headers)
    
    if "api/positions" in url:
        return await get_positions(env, headers)
    
    if "api/status" in url:
        trades_today = await get_trades_count(env)
        result = {
            "status": "online",
            "version": "5.0",
            "ai": "Groq Llama 3.3",
            "database": "D1 Connected",
            "broker": "Alpaca Paper",
            "trades_today": trades_today,
            "max_trades": MAX_TRADES_PER_DAY
        }
        return Response.new(json.dumps(result), headers=headers)
    
    return Response.new(json.dumps({"message": "🦅 Antigravity D1 Brain Online v5.0"}), headers=headers)


async def handle_smart_chat(request, env, headers):
    """Smart AI Chat with D1 Storage"""
    try:
        method = str(request.method)
        user_msg = "Hello"
        
        if method == "POST":
            try:
                body = await request.json()
                user_msg = body.get("message", "Hello")
            except:
                pass
        else:
            url = str(request.url)
            if "message=" in url:
                user_msg = url.split("message=")[1].split("&")[0]
                user_msg = user_msg.replace("%20", " ").replace("+", " ")
        
        groq_key = str(getattr(env, 'GROQ_API_KEY', ''))
        if not groq_key:
            return Response.new(json.dumps({"reply": "⚠️ Groq API not configured"}), headers=headers)
        
        # Call Groq with JSON mode
        request_body = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 400
        })
        
        request_headers = Headers.new({
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(GROQ_API_URL, method="POST", headers=request_headers, body=request_body)
        response_text = await response.text()
        
        if not response.ok:
            return Response.new(json.dumps({"reply": f"API Error: {str(response_text)[:100]}"}), headers=headers)
        
        data = json.loads(str(response_text))
        ai_content = data["choices"][0]["message"]["content"]
        parsed_intent = json.loads(ai_content)
        
        # ============ SAVE TO D1 ============
        db = env.TRADING_DB
        
        # 1. Save user message to context
        await db.prepare(
            "INSERT INTO user_context (session_id, role, content) VALUES (?, ?, ?)"
        ).bind("web_session", "user", user_msg).run()
        
        trade_result = None
        rule_result = None
        
        # 2. Handle based on intent type
        intent_type = parsed_intent.get("type", "CHAT")
        
        if intent_type == "EXECUTE_TRADE":
            trade_data = parsed_intent.get("trade_data", {})
            if trade_data:
                # Check circuit breaker
                trades_today = await get_trades_count(env)
                if trades_today >= MAX_TRADES_PER_DAY:
                    trade_result = {"status": "blocked", "message": f"🛡️ Max trades reached ({MAX_TRADES_PER_DAY}/day)"}
                else:
                    trade_result = await execute_alpaca_trade(
                        env,
                        trade_data.get("ticker", "AAPL"),
                        trade_data.get("side", "buy"),
                        trade_data.get("qty", 1)
                    )
                    if trade_result.get("status") == "success":
                        # Log trade to D1
                        await db.prepare(
                            "INSERT INTO trade_logs (ticker, action, qty, order_id, trigger_reason) VALUES (?, ?, ?, ?, ?)"
                        ).bind(
                            trade_data.get("ticker"),
                            trade_data.get("side"),
                            trade_data.get("qty"),
                            trade_result.get("order_id", ""),
                            "chat_command"
                        ).run()
        
        elif intent_type == "CREATE_RULE":
            rule_data = parsed_intent.get("rule_data", {})
            if rule_data:
                import time
                rule_id = f"rule_{int(time.time())}"
                logic_str = json.dumps(rule_data.get("logic_json", {}))
                
                await db.prepare(
                    "INSERT INTO trading_rules (rule_id, ticker, logic_json, status) VALUES (?, ?, ?, ?)"
                ).bind(rule_id, rule_data.get("ticker", ""), logic_str, "active").run()
                
                rule_result = {"rule_id": rule_id, "status": "saved"}
                parsed_intent["response_text"] = f"{parsed_intent.get('response_text', '')} [Saved Rule ID: {rule_id}]"
        
        # 3. Save assistant response
        await db.prepare(
            "INSERT INTO user_context (session_id, role, content) VALUES (?, ?, ?)"
        ).bind("web_session", "assistant", parsed_intent.get("response_text", "")).run()
        
        result = {
            "reply": parsed_intent.get("response_text", ""),
            "type": intent_type,
            "trade_executed": trade_result,
            "rule_saved": rule_result,
            "model": "llama-3.3-70b-versatile"
        }
        
        return Response.new(json.dumps(result), headers=headers)
        
    except Exception as e:
        return Response.new(json.dumps({"reply": f"Error: {str(e)}", "status": "error"}), status=500, headers=headers)


async def execute_alpaca_trade(env, symbol, side, qty):
    """Execute trade on Alpaca"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        if not alpaca_key or not alpaca_secret:
            return {"status": "error", "message": "Alpaca keys not configured"}
        
        order_body = json.dumps({
            "symbol": symbol.upper(),
            "qty": str(qty),
            "side": side.lower(),
            "type": "market",
            "time_in_force": "day"
        })
        
        order_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret,
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/orders", method="POST", headers=order_headers, body=order_body)
        response_text = await response.text()
        
        if response.ok:
            order_data = json.loads(str(response_text))
            return {
                "status": "success",
                "order_id": order_data.get("id"),
                "symbol": symbol.upper(),
                "side": side,
                "qty": qty,
                "message": f"✅ {side.upper()} {qty} {symbol.upper()}"
            }
        else:
            return {"status": "error", "message": f"Alpaca: {str(response_text)[:100]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def handle_direct_trade(request, env, headers):
    """Direct trade endpoint"""
    url = str(request.url)
    symbol = "AAPL"
    side = "buy"
    qty = 1
    
    if "symbol=" in url:
        symbol = url.split("symbol=")[1].split("&")[0]
    if "side=" in url:
        side = url.split("side=")[1].split("&")[0]
    if "qty=" in url:
        qty = int(url.split("qty=")[1].split("&")[0])
    
    result = await execute_alpaca_trade(env, symbol, side, qty)
    return Response.new(json.dumps(result), headers=headers)


async def get_trades_count(env):
    """Get today's trade count from D1"""
    try:
        db = env.TRADING_DB
        result = await db.prepare(
            "SELECT COUNT(*) as count FROM trade_logs WHERE date(executed_at) = date('now')"
        ).all()
        return result.results[0]["count"] if result.results else 0
    except:
        return 0


async def get_rules(env, headers):
    """Get all trading rules from D1"""
    try:
        db = env.TRADING_DB
        result = await db.prepare("SELECT * FROM trading_rules WHERE status = 'active'").all()
        rules = [dict(r) for r in result.results] if result.results else []
        return Response.new(json.dumps({"rules": rules, "count": len(rules)}), headers=headers)
    except Exception as e:
        return Response.new(json.dumps({"rules": [], "error": str(e)}), headers=headers)


async def get_logs(env, headers):
    """Get trade logs from D1"""
    try:
        db = env.TRADING_DB
        result = await db.prepare("SELECT * FROM trade_logs ORDER BY executed_at DESC LIMIT 50").all()
        logs = [dict(r) for r in result.results] if result.results else []
        return Response.new(json.dumps({"logs": logs, "count": len(logs)}), headers=headers)
    except Exception as e:
        return Response.new(json.dumps({"logs": [], "error": str(e)}), headers=headers)


async def get_account(env, headers):
    """Get Alpaca account"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/account", method="GET", headers=req_headers)
        response_text = await response.text()
        
        if response.ok:
            account = json.loads(str(response_text))
            return Response.new(json.dumps({
                "buying_power": account.get("buying_power"),
                "portfolio_value": account.get("portfolio_value"),
                "cash": account.get("cash"),
                "status": "success"
            }), headers=headers)
        return Response.new(json.dumps({"error": "Failed"}), headers=headers)
    except Exception as e:
        return Response.new(json.dumps({"error": str(e)}), headers=headers)


async def get_positions(env, headers):
    """Get positions from Alpaca"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/positions", method="GET", headers=req_headers)
        response_text = await response.text()
        
        if response.ok:
            positions = json.loads(str(response_text))
            return Response.new(json.dumps({"positions": positions}), headers=headers)
        return Response.new(json.dumps({"positions": []}), headers=headers)
    except:
        return Response.new(json.dumps({"positions": []}), headers=headers)
