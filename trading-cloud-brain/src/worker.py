from js import Response, Headers, fetch, Object
import json
import re
import time

# ==========================================
# 🧠 ANTIGRAVITY TRADING BRAIN v4.0
# Smart Chat + State Persistence + Circuit Breakers
# Based on Deep Research Architecture
# ==========================================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
ALPACA_API_URL = "https://paper-api.alpaca.markets/v2"

# Circuit Breaker Limits
MAX_TRADES_PER_DAY = 10
MAX_DRAWDOWN_PERCENT = 5

SYSTEM_PROMPT = """You are ANTIGRAVITY AI, an elite trading assistant.
Keep responses under 100 words. Be professional and precise.

CAPABILITIES:
1. Trade Execution: "Buy 10 AAPL" → Execute on Alpaca
2. Market Analysis: "Analyze SPY" → Provide insights
3. Create Rules: "If RSI drops below 30, buy" → Save automation rule

For trades, respond with:
```json
{"action": "trade", "symbol": "AAPL", "side": "buy", "qty": 10}
```

For rules, respond with:
```json
{"action": "rule", "symbol": "SPY", "condition": "RSI < 30", "trade": {"side": "buy", "qty": 5}}
```

Always confirm before executing. Remember: Paper Trading only."""


async def on_fetch(request, env):
    """Main async handler with state persistence"""
    url = str(request.url)
    method = str(request.method)
    
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
        return await handle_trade(request, env, headers)
    
    if "api/positions" in url:
        return await get_positions(env, headers)
    
    if "api/account" in url:
        return await get_account(env, headers)
    
    if "api/rules" in url:
        return await handle_rules(request, env, headers)
    
    if "api/logs" in url:
        return await get_trade_logs(env, headers)
    
    if "api/status" in url:
        trades_today = await get_kv(env, "trades_today") or "0"
        kill_switch = await get_kv(env, "kill_switch") or "false"
        result = {
            "status": "online",
            "ai": "Groq Llama 3.3",
            "broker": "Alpaca Paper",
            "version": "4.0",
            "trades_today": int(trades_today),
            "max_trades": MAX_TRADES_PER_DAY,
            "kill_switch": kill_switch == "true"
        }
        return Response.new(json.dumps(result), headers=headers)
    
    if "api/market" in url:
        return await get_market_data(request, env, headers)
    
    if "api/killswitch" in url:
        return await toggle_kill_switch(request, env, headers)

    result = {"status": "online", "message": "ANTIGRAVITY v4.0 - Zero Cost Trading Brain"}
    return Response.new(json.dumps(result), headers=headers)


# ============ KV HELPERS ============

async def get_kv(env, key):
    """Get value from KV store"""
    try:
        kv = env.BRAIN_MEMORY
        return await kv.get(key)
    except:
        return None

async def put_kv(env, key, value):
    """Put value to KV store"""
    try:
        kv = env.BRAIN_MEMORY
        await kv.put(key, str(value))
        return True
    except:
        return False


# ============ CIRCUIT BREAKERS ============

async def check_circuit_breakers(env):
    """Check if trading is allowed"""
    # Check kill switch
    kill_switch = await get_kv(env, "kill_switch")
    if kill_switch == "true":
        return False, "🛑 Kill Switch ACTIVE - Trading paused"
    
    # Check daily trade limit
    trades_today = await get_kv(env, "trades_today") or "0"
    if int(trades_today) >= MAX_TRADES_PER_DAY:
        return False, f"🛡️ Max trades reached ({MAX_TRADES_PER_DAY}/day)"
    
    return True, "OK"


async def increment_trade_count(env):
    """Increment daily trade counter"""
    trades_today = await get_kv(env, "trades_today") or "0"
    await put_kv(env, "trades_today", str(int(trades_today) + 1))


# ============ SMART CHAT ============

async def handle_smart_chat(request, env, headers):
    """Smart AI chat with intent parsing and execution"""
    try:
        method = str(request.method)
        user_message = "Hello"
        
        if method == "POST":
            try:
                body = await request.json()
                user_message = body.get("message", "Hello")
            except:
                pass
        else:
            url = str(request.url)
            if "message=" in url:
                user_message = url.split("message=")[1].split("&")[0]
                user_message = user_message.replace("%20", " ").replace("+", " ")
        
        groq_key = str(getattr(env, 'GROQ_API_KEY', ''))
        
        if not groq_key:
            result = {"reply": "⚠️ Groq API key not configured", "status": "error"}
            return Response.new(json.dumps(result), headers=headers)
        
        # Get chat history from KV (last 5 messages for context)
        chat_history = await get_kv(env, "chat_history")
        messages = []
        if chat_history:
            try:
                messages = json.loads(chat_history)[-5:]
            except:
                messages = []
        
        # Build request
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        full_messages.extend(messages)
        full_messages.append({"role": "user", "content": user_message})
        
        request_body = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": full_messages,
            "max_tokens": 300,
            "temperature": 0.7
        })
        
        request_headers = Headers.new({
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(GROQ_API_URL, method="POST", headers=request_headers, body=request_body)
        response_text = await response.text()
        
        if not response.ok:
            result = {"reply": f"API Error: {str(response_text)[:100]}", "status": "error"}
            return Response.new(json.dumps(result), headers=headers)
        
        data = json.loads(str(response_text))
        ai_reply = data["choices"][0]["message"]["content"]
        
        # Parse for actions
        trade_result = None
        rule_result = None
        json_match = re.search(r'```json\s*(\{[^`]+\})\s*```', ai_reply)
        
        if json_match:
            try:
                intent = json.loads(json_match.group(1))
                
                if intent.get("action") == "trade":
                    # Check circuit breakers first
                    can_trade, message = await check_circuit_breakers(env)
                    if not can_trade:
                        trade_result = {"status": "blocked", "message": message}
                    else:
                        trade_result = await execute_alpaca_trade(
                            env, 
                            intent.get("symbol", "AAPL"),
                            intent.get("side", "buy"),
                            intent.get("qty", 1)
                        )
                        if trade_result.get("status") == "success":
                            await increment_trade_count(env)
                            await log_trade(env, trade_result)
                    
                elif intent.get("action") == "rule":
                    rule_result = await save_rule(env, intent)
                    
            except Exception as e:
                pass
        
        # Save to chat history
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": ai_reply})
        await put_kv(env, "chat_history", json.dumps(messages[-10:]))
        
        # Clean reply
        clean_reply = re.sub(r'```json\s*\{[^`]+\}\s*```', '', ai_reply).strip()
        
        result = {
            "reply": clean_reply if clean_reply else ai_reply,
            "status": "success",
            "model": "llama-3.3-70b-versatile",
            "trade_executed": trade_result,
            "rule_saved": rule_result
        }
        
        return Response.new(json.dumps(result), headers=headers)
        
    except Exception as e:
        result = {"reply": f"Error: {str(e)}", "status": "error"}
        return Response.new(json.dumps(result), status=500, headers=headers)


# ============ TRADE EXECUTION ============

async def execute_alpaca_trade(env, symbol, side, qty):
    """Execute trade on Alpaca with circuit breaker check"""
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
        
        response = await fetch(
            f"{ALPACA_API_URL}/orders",
            method="POST",
            headers=order_headers,
            body=order_body
        )
        
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


async def log_trade(env, trade_data):
    """Log trade to KV"""
    try:
        logs = await get_kv(env, "trade_logs")
        log_list = json.loads(logs) if logs else []
        log_list.append({
            "timestamp": str(int(time.time())),
            **trade_data
        })
        await put_kv(env, "trade_logs", json.dumps(log_list[-50:]))
    except:
        pass


# ============ RULES ENGINE ============

async def save_rule(env, rule_data):
    """Save trading rule to KV"""
    try:
        rules = await get_kv(env, "trading_rules")
        rule_list = json.loads(rules) if rules else []
        rule_id = f"rule_{len(rule_list)+1}"
        rule_data["rule_id"] = rule_id
        rule_data["status"] = "active"
        rule_list.append(rule_data)
        await put_kv(env, "trading_rules", json.dumps(rule_list))
        return {"status": "success", "rule_id": rule_id, "message": f"✅ Rule saved: {rule_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def handle_rules(request, env, headers):
    """Get or manage trading rules"""
    rules = await get_kv(env, "trading_rules")
    rule_list = json.loads(rules) if rules else []
    return Response.new(json.dumps({"rules": rule_list, "count": len(rule_list)}), headers=headers)


async def get_trade_logs(env, headers):
    """Get trade logs"""
    logs = await get_kv(env, "trade_logs")
    log_list = json.loads(logs) if logs else []
    return Response.new(json.dumps({"logs": log_list, "count": len(log_list)}), headers=headers)


# ============ KILL SWITCH ============

async def toggle_kill_switch(request, env, headers):
    """Toggle kill switch"""
    current = await get_kv(env, "kill_switch") or "false"
    new_value = "false" if current == "true" else "true"
    await put_kv(env, "kill_switch", new_value)
    
    if new_value == "true":
        # Cancel all open orders
        try:
            alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
            alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
            order_headers = Headers.new({
                "APCA-API-KEY-ID": alpaca_key,
                "APCA-API-SECRET-KEY": alpaca_secret
            }.items())
            await fetch(f"{ALPACA_API_URL}/orders", method="DELETE", headers=order_headers)
        except:
            pass
    
    return Response.new(json.dumps({
        "kill_switch": new_value == "true",
        "message": "🛑 KILL SWITCH ACTIVATED" if new_value == "true" else "✅ Trading resumed"
    }), headers=headers)


# ============ OTHER ENDPOINTS ============

async def handle_trade(request, env, headers):
    """Direct trade endpoint"""
    url = str(request.url)
    
    symbol = "AAPL"
    side = "buy"
    qty = "1"
    
    if "symbol=" in url:
        symbol = url.split("symbol=")[1].split("&")[0]
    if "side=" in url:
        side = url.split("side=")[1].split("&")[0]
    if "qty=" in url:
        qty = url.split("qty=")[1].split("&")[0]
    
    can_trade, message = await check_circuit_breakers(env)
    if not can_trade:
        return Response.new(json.dumps({"status": "blocked", "message": message}), headers=headers)
    
    result = await execute_alpaca_trade(env, symbol, side, int(qty))
    if result.get("status") == "success":
        await increment_trade_count(env)
        await log_trade(env, result)
    return Response.new(json.dumps(result), headers=headers)


async def get_positions(env, headers):
    """Get current positions"""
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
        return Response.new(json.dumps({"error": "Failed to fetch"}), headers=headers)
    except Exception as e:
        return Response.new(json.dumps({"error": str(e)}), headers=headers)


async def get_market_data(request, env, headers):
    """Get market data"""
    url = str(request.url)
    symbol = "SPY"
    if "symbol=" in url:
        symbol = url.split("symbol=")[1].split("&")[0]
    
    result = {"symbol": symbol.upper(), "price": 595.50, "change": 2.30, "status": "demo"}
    return Response.new(json.dumps(result), headers=headers)
