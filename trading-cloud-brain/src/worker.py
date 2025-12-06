from js import Response, Headers, fetch
import json
import re

# ==========================================
# 🚀 ANTIGRAVITY TRADING LLM v6.0
# The Super-Worker: Chart + News + Research + Trade
# ==========================================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
ALPACA_API_URL = "https://paper-api.alpaca.markets/v2"
ALPACA_DATA_URL = "https://data.alpaca.markets/v2"
TELEGRAM_API_URL = "https://api.telegram.org/bot"

MAX_TRADES_PER_DAY = 10

SYSTEM_PROMPT = """You are SENTINEL - an expert AI trading assistant inside AntigravityTradingLLM.

YOUR PERSONALITY:
- You're a seasoned Wall Street quant with 20 years experience
- You speak confidently but concisely
- You use emojis sparingly for clarity (📈 📉 💰 ⚠️)
- You provide actionable insights, not generic advice

YOUR CAPABILITIES:
1. CHART ANALYSIS - When user asks for price/chart/technicals:
   → Respond: {"type": "SHOW_CHART", "symbol": "SPY", "reply": "📈 Loading SPY. Current trend shows bullish momentum with RSI at 62..."}

2. RESEARCH & NEWS - When user asks about news/why/analysis:
   → Respond: {"type": "RESEARCH", "symbol": "AAPL", "reply": "🔬 Analyzing AAPL: Strong earnings beat last quarter. Institutional buying pressure..."}

3. TRADE EXECUTION - When user wants to buy/sell:
   → Respond: {"type": "TRADE", "symbol": "TSLA", "side": "buy", "qty": 10, "reply": "💰 Executing: BUY 10 TSLA at market..."}

4. CONVERSATION - For general questions, provide REAL insights:
   → Respond: {"type": "CHAT", "reply": "Your smart, detailed response with actual value..."}

RULES:
- ALWAYS output valid JSON with "type" and "reply" fields
- For CHAT type, give REAL trading wisdom, not generic filler
- Be helpful, knowledgeable, and confident
- If asked about a stock, provide real analysis

EXAMPLES OF GOOD REPLIES:
- "SPY is showing a bullish flag pattern on the 4H chart. Volume confirms the breakout. Consider entries above 595."
- "Gold typically rallies during rate uncertainty. With Fed signals mixed, GLD could see upside. Watch 182 resistance."
- "TSLA's RSI is oversold at 28. Historically, this leads to a 5-7% bounce within 3 days."

Remember: You're a REAL trading expert, not a generic chatbot."""


async def on_fetch(request, env):
    """The Super-Worker: Handles all requests"""
    
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
    
    # Telegram Webhook - Bot receives messages and replies with LLM
    if "/telegram/webhook" in url or "/api/telegram" in url:
        return await handle_telegram_webhook(request, env, headers)
    
    if "api/chat" in url:
        return await handle_smart_chat(request, env, headers)
    
    if "api/candles" in url or "api/chart" in url:
        return await get_candles(request, env, headers)
    
    if "api/news" in url:
        return await get_news(request, env, headers)
    
    if "api/trade" in url:
        return await handle_trade(request, env, headers)
    
    if "api/account" in url:
        return await get_account(env, headers)
    
    if "api/positions" in url:
        return await get_positions(env, headers)
    
    if "api/rules" in url:
        return await get_rules(env, headers)
    
    if "api/status" in url:
        trades_today = await get_trades_count(env)
        result = {
            "status": "online",
            "version": "6.0",
            "name": "AntigravityTradingLLM",
            "ai": "Groq Llama 3.3 + Gemini",
            "database": "D1 Connected",
            "broker": "Alpaca Paper",
            "trades_today": trades_today,
            "max_trades": MAX_TRADES_PER_DAY,
            "features": ["chart", "news", "research", "trade", "automation"]
        }
        return Response.new(json.dumps(result), headers=headers)
    
    return Response.new(json.dumps({"message": "🚀 AntigravityTradingLLM v6.0 Online"}), headers=headers)


async def handle_smart_chat(request, env, headers):
    """Smart AI Chat with Intent Classification"""
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
            return Response.new(json.dumps({"reply": "⚠️ API not configured"}), headers=headers)
        
        # Call Groq for intent classification
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
            return Response.new(json.dumps({"reply": f"API Error"}), headers=headers)
        
        data = json.loads(str(response_text))
        intent = json.loads(data["choices"][0]["message"]["content"])
        
        intent_type = intent.get("type", "CHAT")
        
        # ============ EXECUTE BASED ON INTENT ============
        
        # 1. SHOW CHART
        if intent_type == "SHOW_CHART":
            symbol = intent.get("symbol", "SPY").upper()
            candles = await fetch_alpaca_bars(symbol, env)
            
            return Response.new(json.dumps({
                "type": "SHOW_CHART",
                "symbol": symbol,
                "candles": candles,
                "reply": intent.get("reply", f"📈 Loading {symbol} chart...")
            }), headers=headers)
        
        # 2. RESEARCH / NEWS
        elif intent_type == "RESEARCH":
            symbol = intent.get("symbol", "SPY").upper()
            
            # Fetch news
            raw_news = await fetch_yahoo_news(symbol)
            
            # Analyze with Gemini if key available
            gemini_key = str(getattr(env, 'GEMINI_API_KEY', ''))
            if gemini_key and raw_news != "No news available.":
                summary = await analyze_with_gemini(raw_news, symbol, env)
            else:
                summary = f"📰 Latest headlines for {symbol} fetched. Analysis module ready."
            
            return Response.new(json.dumps({
                "type": "RESEARCH",
                "symbol": symbol,
                "reply": summary
            }), headers=headers)
        
        # 3. TRADE
        elif intent_type == "TRADE":
            symbol = intent.get("symbol", "AAPL").upper()
            side = intent.get("side", "buy")
            qty = intent.get("qty", 1)
            
            # Check circuit breaker
            trades_today = await get_trades_count(env)
            if trades_today >= MAX_TRADES_PER_DAY:
                return Response.new(json.dumps({
                    "type": "TRADE",
                    "status": "blocked",
                    "reply": f"🛡️ Circuit breaker: Max {MAX_TRADES_PER_DAY} trades/day reached."
                }), headers=headers)
            
            trade_result = await execute_alpaca_trade(env, symbol, side, qty)
            
            if trade_result.get("status") == "success":
                # Log to D1
                try:
                    db = env.TRADING_DB
                    await db.prepare(
                        "INSERT INTO trade_logs (ticker, action, qty, order_id, trigger_reason) VALUES (?, ?, ?, ?, ?)"
                    ).bind(symbol, side, qty, trade_result.get("order_id", ""), "chat_command").run()
                except:
                    pass
                
                # Send Telegram notification
                emoji = "🟢" if side == "buy" else "🔴"
                tg_msg = f"{emoji} <b>ANTIGRAVITY TRADE</b>\n\n📊 <b>{symbol}</b>\n💰 {side.upper()} {qty} shares\n🆔 {trade_result.get('order_id', 'N/A')[:8]}..."
                await send_telegram_alert(env, tg_msg)
            
            return Response.new(json.dumps({
                "type": "TRADE",
                "trade_executed": trade_result,
                "reply": trade_result.get("message", "Trade processing...")
            }), headers=headers)
        
        # 4. CHAT
        else:
            return Response.new(json.dumps({
                "type": "CHAT",
                "reply": intent.get("reply", "How can I help you trade today?")
            }), headers=headers)
        
    except Exception as e:
        return Response.new(json.dumps({"reply": f"Error: {str(e)}"}), status=500, headers=headers)


# ============ HELPER FUNCTIONS ============

async def send_telegram_alert(env, message):
    """Send instant notification to Telegram"""
    try:
        telegram_token = str(getattr(env, 'TELEGRAM_BOT_TOKEN', ''))
        telegram_chat_id = str(getattr(env, 'TELEGRAM_CHAT_ID', ''))
        
        if not telegram_token or not telegram_chat_id:
            return  # Telegram not configured
        
        url = f"{TELEGRAM_API_URL}{telegram_token}/sendMessage"
        
        payload = json.dumps({
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        })
        
        req_headers = Headers.new({"Content-Type": "application/json"}.items())
        await fetch(url, method="POST", headers=req_headers, body=payload)
    except:
        pass  # Don't fail if Telegram fails


async def handle_telegram_webhook(request, env, headers):
    """Receive Telegram messages and reply with smart LLM"""
    try:
        body = await request.json()
        message = body.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user_name = message.get("from", {}).get("first_name", "Trader")
        
        if not chat_id or not text:
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # Skip commands for now
        if text.startswith("/start"):
            reply = f"🧠 <b>SENTINEL AI</b> Online!\n\nHello {user_name}! I'm your expert trading assistant.\n\n<b>Try:</b>\n• What's happening with Tesla?\n• Analyze SPY\n• Buy 5 AAPL\n• News on gold"
            await send_telegram_reply(env, chat_id, reply)
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # Call Gemini for smart response
        ai_response = await call_gemini_chat(text, user_name, env)
        
        # Send reply
        await send_telegram_reply(env, chat_id, ai_response)
        
        return Response.new(json.dumps({"ok": True}), headers=headers)
    except Exception as e:
        return Response.new(json.dumps({"ok": True, "error": str(e)}), headers=headers)


async def send_telegram_reply(env, chat_id, text):
    """Send reply to specific chat"""
    try:
        telegram_token = str(getattr(env, 'TELEGRAM_BOT_TOKEN', ''))
        url = f"{TELEGRAM_API_URL}{telegram_token}/sendMessage"
        
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        })
        
        req_headers = Headers.new({"Content-Type": "application/json"}.items())
        await fetch(url, method="POST", headers=req_headers, body=payload)
    except:
        pass


async def call_gemini_chat(user_message, user_name, env):
    """Call Gemini 1.5 Flash for intelligent trading chat"""
    try:
        gemini_key = str(getattr(env, 'GEMINI_API_KEY', ''))
        
        if not gemini_key:
            # Fallback to Groq
            return await call_groq_chat(user_message, env)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        
        prompt = f"""You are SENTINEL - an expert AI trading assistant for {user_name}.

PERSONALITY:
- Seasoned Wall Street quant with 20 years experience
- Confident, concise, uses emojis sparingly (📈📉💰⚠️)
- Provides actionable insights, not generic advice

CAPABILITIES:
- Market analysis and sentiment
- Technical analysis (RSI, MACD, patterns)
- News interpretation
- Trade recommendations
- Risk assessment

User: {user_message}

Respond naturally as a trading expert. Be helpful, insightful, and specific. Keep response under 500 characters for Telegram."""

        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 300
            }
        })
        
        req_headers = Headers.new({"Content-Type": "application/json"}.items())
        response = await fetch(url, method="POST", headers=req_headers, body=payload)
        
        if response.ok:
            data = json.loads(await response.text())
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if text:
                return text
        
        # Fallback to Groq
        return await call_groq_chat(user_message, env)
    except:
        return await call_groq_chat(user_message, env)


async def call_groq_chat(user_message, env):
    """Fallback to Groq for chat"""
    try:
        groq_key = str(getattr(env, 'GROQ_API_KEY', ''))
        
        if not groq_key:
            return "⚠️ AI not configured"
        
        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are SENTINEL, an expert trading AI. Be concise and insightful."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        })
        
        req_headers = Headers.new({
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(GROQ_API_URL, method="POST", headers=req_headers, body=payload)
        
        if response.ok:
            data = json.loads(await response.text())
            return data.get("choices", [{}])[0].get("message", {}).get("content", "🤔 Let me think...")
        
        return "⚠️ AI temporarily unavailable"
    except:
        return "⚠️ Connection error"

async def fetch_alpaca_bars(symbol, env):
    """Fetch candles from Alpaca for charting"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        # Use Alpaca Data API
        url = f"{ALPACA_DATA_URL}/stocks/{symbol}/bars?timeframe=1Hour&limit=100"
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(url, method="GET", headers=req_headers)
        response_text = await response.text()
        
        if response.ok:
            data = json.loads(str(response_text))
            bars = data.get("bars", [])
            
            # Format for lightweight-charts
            formatted = []
            for bar in bars:
                formatted.append({
                    "time": bar["t"][:10],  # YYYY-MM-DD
                    "open": bar["o"],
                    "high": bar["h"],
                    "low": bar["l"],
                    "close": bar["c"],
                    "volume": bar["v"]
                })
            return formatted
        else:
            # Return demo data if API fails
            return generate_demo_candles()
    except:
        return generate_demo_candles()


def generate_demo_candles():
    """Generate demo candle data"""
    import time
    candles = []
    base_price = 595
    current_time = int(time.time())
    
    for i in range(100):
        t = current_time - (100 - i) * 3600
        o = base_price + (hash(str(t)) % 10 - 5)
        c = o + (hash(str(t+1)) % 8 - 4)
        h = max(o, c) + (hash(str(t+2)) % 3)
        l = min(o, c) - (hash(str(t+3)) % 3)
        v = 1000000 + hash(str(t+4)) % 500000
        
        # Convert timestamp to date string
        from datetime import datetime
        dt = datetime.utcfromtimestamp(t)
        date_str = dt.strftime('%Y-%m-%d')
        
        candles.append({"time": date_str, "open": o, "high": h, "low": l, "close": c, "volume": v})
        base_price = c
    
    return candles


async def fetch_yahoo_news(symbol):
    """Fetch news from Yahoo Finance RSS (Free)"""
    try:
        rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}"
        response = await fetch(rss_url)
        text = await response.text()
        return str(text)[:5000]  # First 5000 chars
    except:
        return "No news available."


async def analyze_with_gemini(news_text, symbol, env):
    """Use Gemini to analyze news sentiment"""
    try:
        gemini_key = str(getattr(env, 'GEMINI_API_KEY', ''))
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        
        prompt = f"""Analyze this RSS news feed for {symbol}. Give a brief bullet-point summary:
- Overall Sentiment (Bullish/Bearish/Neutral)
- Key headlines (2-3 max)
- Trading implication

RSS DATA:
{news_text[:3000]}"""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        req_headers = Headers.new({"Content-Type": "application/json"}.items())
        
        response = await fetch(url, method="POST", headers=req_headers, body=json.dumps(payload))
        response_text = await response.text()
        
        if response.ok:
            data = json.loads(str(response_text))
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"📰 News fetched for {symbol}. Sentiment analysis pending."
    except:
        return f"📰 News fetched for {symbol}."


async def execute_alpaca_trade(env, symbol, side, qty):
    """Execute trade on Alpaca"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
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
            return {"status": "error", "message": f"Order failed: {str(response_text)[:100]}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def handle_trade(request, env, headers):
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


async def get_candles(request, env, headers):
    """Direct candles endpoint"""
    url = str(request.url)
    symbol = "SPY"
    if "symbol=" in url:
        symbol = url.split("symbol=")[1].split("&")[0]
    
    candles = await fetch_alpaca_bars(symbol.upper(), env)
    return Response.new(json.dumps({"symbol": symbol.upper(), "candles": candles}), headers=headers)


async def get_news(request, env, headers):
    """Direct news endpoint"""
    url = str(request.url)
    symbol = "SPY"
    if "symbol=" in url:
        symbol = url.split("symbol=")[1].split("&")[0]
    
    news = await fetch_yahoo_news(symbol.upper())
    return Response.new(json.dumps({"symbol": symbol.upper(), "news": news[:1000]}), headers=headers)


async def get_trades_count(env):
    """Get today's trade count"""
    try:
        db = env.TRADING_DB
        result = await db.prepare(
            "SELECT COUNT(*) as count FROM trade_logs WHERE date(executed_at) = date('now')"
        ).all()
        return result.results[0]["count"] if result.results else 0
    except:
        return 0


async def get_rules(env, headers):
    """Get trading rules"""
    try:
        db = env.TRADING_DB
        result = await db.prepare("SELECT * FROM trading_rules WHERE status = 'active'").all()
        rules = [dict(r) for r in result.results] if result.results else []
        return Response.new(json.dumps({"rules": rules}), headers=headers)
    except:
        return Response.new(json.dumps({"rules": []}), headers=headers)


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
    except:
        return Response.new(json.dumps({"error": "Connection failed"}), headers=headers)


async def get_positions(env, headers):
    """Get positions"""
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


# ============ CRON JOB AUTOMATION ============

async def on_scheduled(event, env, ctx):
    """
    🕐 Cron Job Handler - Runs every minute
    Checks active trading rules and executes them if conditions are met
    """
    try:
        db = env.TRADING_DB
        
        # 1. Fetch all active rules
        result = await db.prepare(
            "SELECT * FROM trading_rules WHERE status = 'active'"
        ).all()
        
        rules = result.results if result.results else []
        
        if not rules:
            return  # No active rules
        
        # 2. Fetch account info to check if we can trade
        trades_today = await get_trades_count_internal(env)
        if trades_today >= MAX_TRADES_PER_DAY:
            # Log that we hit the limit
            await db.prepare(
                "INSERT INTO trade_logs (ticker, action, qty, trigger_reason) VALUES (?, ?, ?, ?)"
            ).bind("SYSTEM", "blocked", 0, "Daily trade limit reached").run()
            return
        
        # 3. Process each rule
        for rule in rules:
            try:
                rule_id = rule["rule_id"]
                ticker = rule["ticker"]
                logic_json = json.loads(rule["logic_json"]) if isinstance(rule["logic_json"], str) else rule["logic_json"]
                
                # Get current price (simplified - using demo for now)
                current_price = await get_current_price(ticker, env)
                
                # Evaluate condition
                should_execute = evaluate_rule(logic_json, current_price)
                
                if should_execute:
                    # Execute the trade
                    action = logic_json.get("action", "BUY").lower()
                    qty = logic_json.get("qty", 1)
                    
                    trade_result = await execute_trade_internal(env, ticker, action, qty)
                    
                    if trade_result.get("status") == "success":
                        # Log successful trade
                        await db.prepare(
                            "INSERT INTO trade_logs (ticker, action, qty, order_id, trigger_reason) VALUES (?, ?, ?, ?, ?)"
                        ).bind(ticker, action, qty, trade_result.get("order_id", ""), f"cron_rule_{rule_id}").run()
                        
                        # Optionally deactivate one-time rules
                        # await db.prepare("UPDATE trading_rules SET status = 'executed' WHERE rule_id = ?").bind(rule_id).run()
                        
            except Exception as rule_error:
                # Log rule error and continue
                pass
                
    except Exception as e:
        # Log cron error
        pass


def evaluate_rule(logic, current_price):
    """Evaluate if a rule condition is met"""
    try:
        condition = logic.get("condition", "").upper()
        trigger = float(logic.get("trigger", 0))
        
        if condition == "PRICE_BELOW" and current_price < trigger:
            return True
        elif condition == "PRICE_ABOVE" and current_price > trigger:
            return True
        elif condition == "RSI_BELOW":
            # RSI logic would need indicator calculation
            return False
        elif condition == "RSI_ABOVE":
            return False
        
        return False
    except:
        return False


async def get_current_price(symbol, env):
    """Get current price for a symbol"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        url = f"{ALPACA_DATA_URL}/stocks/{symbol}/trades/latest"
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(url, method="GET", headers=req_headers)
        
        if response.ok:
            response_text = await response.text()
            data = json.loads(str(response_text))
            return float(data.get("trade", {}).get("p", 0))
        
        # Return demo price
        demo_prices = {"SPY": 595, "AAPL": 245, "TSLA": 380, "GOOGL": 175}
        return demo_prices.get(symbol.upper(), 100)
    except:
        return 100


async def get_trades_count_internal(env):
    """Internal function to get trade count"""
    try:
        db = env.TRADING_DB
        result = await db.prepare(
            "SELECT COUNT(*) as count FROM trade_logs WHERE date(executed_at) = date('now')"
        ).all()
        return result.results[0]["count"] if result.results else 0
    except:
        return 0


async def execute_trade_internal(env, symbol, side, qty):
    """Internal trade execution for cron"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
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
            return {"status": "success", "order_id": order_data.get("id")}
        return {"status": "error"}
    except:
        return {"status": "error"}

