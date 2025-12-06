from js import Response, Headers, fetch, Object
import json
import re

# ==========================================
# 🧠 SENTINEL TRADING BRAIN v3.0
# Smart Chat + Intent Parsing + Alpaca Execution
# ==========================================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
ALPACA_API_URL = "https://paper-api.alpaca.markets/v2"

SYSTEM_PROMPT = """You are Sentinel, an AI trading assistant for Alpaca Paper Trading.
You can analyze markets and execute trades. Keep responses under 100 words.

IMPORTANT: When user wants to trade, respond with a JSON block like this:
```json
{"action": "trade", "symbol": "AAPL", "side": "buy", "qty": 10}
```

For analysis, just provide your insights naturally.
For rules like "buy if drops 2%", respond with:
```json
{"action": "rule", "symbol": "SPY", "condition": "price_drop", "value": 2, "trade_side": "buy", "qty": 10}
```

Always confirm before executing trades."""


async def on_fetch(request, env):
    """Main async handler"""
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
    
    if "api/chat" in url:
        return await handle_smart_chat(request, env, headers)
    
    if "api/trade" in url:
        return await handle_trade(request, env, headers)
    
    if "api/positions" in url:
        return await get_positions(env, headers)
    
    if "api/account" in url:
        return await get_account(env, headers)
    
    if "api/status" in url:
        result = {"status": "online", "ai": "Groq Llama 3.3", "broker": "Alpaca", "version": "3.0"}
        return Response.new(json.dumps(result), headers=headers)
    
    if "api/market" in url:
        return await get_market_data(request, env, headers)

    result = {"status": "online", "message": "Sentinel AI v3.0 - Smart Trading"}
    return Response.new(json.dumps(result), headers=headers)


async def handle_smart_chat(request, env, headers):
    """Smart chat with intent parsing and trade execution"""
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
        
        # Call Groq for AI response
        request_body = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
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
        
        # Parse for trade intent
        trade_result = None
        json_match = re.search(r'```json\s*(\{[^`]+\})\s*```', ai_reply)
        
        if json_match:
            try:
                intent = json.loads(json_match.group(1))
                
                if intent.get("action") == "trade":
                    # Execute the trade
                    trade_result = await execute_alpaca_trade(
                        env, 
                        intent.get("symbol", "AAPL"),
                        intent.get("side", "buy"),
                        intent.get("qty", 1)
                    )
                    
                elif intent.get("action") == "rule":
                    # Save rule to KV (placeholder)
                    trade_result = {
                        "action": "rule_saved",
                        "rule": intent,
                        "message": f"✅ Rule created: {intent.get('trade_side')} {intent.get('qty')} {intent.get('symbol')} when {intent.get('condition')} {intent.get('value')}%"
                    }
            except:
                pass
        
        # Clean up the reply (remove JSON block for display)
        clean_reply = re.sub(r'```json\s*\{[^`]+\}\s*```', '', ai_reply).strip()
        
        result = {
            "reply": clean_reply if clean_reply else ai_reply,
            "status": "success",
            "model": "llama-3.3-70b-versatile",
            "source": "groq_live",
            "trade_executed": trade_result
        }
        
        return Response.new(json.dumps(result), headers=headers)
        
    except Exception as e:
        result = {"reply": f"Error: {str(e)}", "status": "error"}
        return Response.new(json.dumps(result), status=500, headers=headers)


async def execute_alpaca_trade(env, symbol, side, qty):
    """Execute trade on Alpaca Paper Trading"""
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
                "message": f"✅ Order executed: {side.upper()} {qty} {symbol.upper()}"
            }
        else:
            return {
                "status": "error",
                "message": f"Alpaca error: {str(response_text)[:100]}"
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}


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
    
    result = await execute_alpaca_trade(env, symbol, side, int(qty))
    return Response.new(json.dumps(result), headers=headers)


async def get_positions(env, headers):
    """Get current positions from Alpaca"""
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
            return Response.new(json.dumps({"positions": positions, "status": "success"}), headers=headers)
        else:
            return Response.new(json.dumps({"positions": [], "error": str(response_text)[:100]}), headers=headers)
            
    except Exception as e:
        return Response.new(json.dumps({"positions": [], "error": str(e)}), headers=headers)


async def get_account(env, headers):
    """Get Alpaca account info"""
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
        else:
            return Response.new(json.dumps({"error": str(response_text)[:100]}), headers=headers)
            
    except Exception as e:
        return Response.new(json.dumps({"error": str(e)}), headers=headers)


async def get_market_data(request, env, headers):
    """Get market data for a symbol"""
    url = str(request.url)
    symbol = "SPY"
    
    if "symbol=" in url:
        symbol = url.split("symbol=")[1].split("&")[0]
    
    # Return demo data for now (Alpaca market data needs subscription)
    result = {
        "symbol": symbol.upper(),
        "price": 595.50,
        "change": 2.30,
        "change_percent": 0.39,
        "status": "demo_data"
    }
    return Response.new(json.dumps(result), headers=headers)
