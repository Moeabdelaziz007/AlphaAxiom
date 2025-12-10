from js import Response, fetch, Headers, JSON
import json

# Constants
TELEGRAM_API_URL = "https://api.telegram.org/bot"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

async def handle_telegram_webhook(request, env, headers):
    """Receive Telegram messages and reply with LLM"""
    try:
        # Parse JS object to Python dict
        body_js = await request.json()
        body = json.loads(JSON.stringify(body_js))
        
        message = body.get("message", {})
        if not message:
            return Response.new(json.dumps({"ok": True}), headers=headers)
            
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user_name = message.get("from", {}).get("first_name", "Trader")
        
        if not chat_id or not text:
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # ============ COMMAND HANDLING ============
        
        # /start command
        if text.startswith("/start") and not text.startswith("/starttrade"):
            reply = f"""🦅 <b>ANTIGRAVITY TERMINAL</b> Online!

مرحباً {user_name}! أنا Sentinel AI - مساعدك الذكي للتداول.

<b>📋 الأوامر المتاحة:</b>
• /balance - عرض رصيد المحفظة
• /positions - المراكز المفتوحة
• /stoptrade - 🛑 إيقاف التداول التلقائي
• /starttrade - ▶️ تشغيل التداول التلقائي
• /status - حالة النظام
• Analyze EURUSD - تحليل زوج
• أي سؤال - سأجيبك!

<b>🔗 Dashboard:</b> trading-brain-v1.amrikyy.workers.dev"""
            await send_telegram_reply(env, chat_id, reply)
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # /stoptrade - Activate panic mode
        if text.startswith("/stoptrade") or text.startswith("/stop"):
            try:
                kv = env.BRAIN_MEMORY
                await kv.put("panic_mode", "true")
                await kv.put("panic_timestamp", str(int(__import__('time').time())))
                reply = """🛑 <b>KILL SWITCH ACTIVATED</b>

التداول التلقائي <b>متوقف الآن</b>.

جميع عمليات التداول الآلية معلقة.
لإعادة التشغيل، أرسل: /starttrade"""
                await send_telegram_reply(env, chat_id, reply)
            except Exception as e:
                await send_telegram_reply(env, chat_id, f"⚠️ خطأ: {str(e)}")
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # /starttrade - Deactivate panic mode
        if text.startswith("/starttrade"):
            try:
                kv = env.BRAIN_MEMORY
                await kv.put("panic_mode", "false")
                reply = """▶️ <b>TRADING RESUMED</b>

التداول التلقائي <b>نشط الآن</b>.

سيتم تنفيذ جميع إشارات Twin-Turbo المعتمدة."""
                await send_telegram_reply(env, chat_id, reply)
            except Exception as e:
                await send_telegram_reply(env, chat_id, f"⚠️ خطأ: {str(e)}")
            return Response.new(json.dumps({"ok": True}), headers=headers)

        # /status - System status
        if text.startswith("/status"):
            try:
                kv = env.BRAIN_MEMORY
                panic_mode = await kv.get("panic_mode") or "false"
                # Import CapitalConnector here to avoid circular imports if extracted
                from capital_connector import CapitalConnector 
                capital = CapitalConnector(env)
                account = await capital.get_account_info()
                
                status_emoji = "🛑" if panic_mode == "true" else "🟢"
                status_text = "متوقف" if panic_mode == "true" else "نشط"
                
                reply = f"""📊 <b>SYSTEM STATUS</b>

{status_emoji} التداول التلقائي: <b>{status_text}</b>
💰 الرصيد: ${float(account.get('balance', 0)):,.2f}
📈 الوسيط: {account.get('source', 'Capital.com Demo')}

⏰ آخر فحص: الآن"""
                await send_telegram_reply(env, chat_id, reply)
            except Exception as e:
                await send_telegram_reply(env, chat_id, f"⚠️ خطأ: {str(e)}")
            return Response.new(json.dumps({"ok": True}), headers=headers)
            
        # General Chat (Groq Fallback for now to simplify)
        # For deeper integration, we'd import the specific agents (DeepSeek, Workers AI)
        # But to keep this file clean, we handle basic responses or route back.
        
        # If it's a specific command handled elsewhere in worker.py (like /analyze, /ai), 
        # we might need to duplicate logic or import helpers. 
        # For this refactor step, we'll keep the core structure and focus on 
        # moving the 'handle_telegram_webhook' function itself.
        
        # IMPORTANT: To make this work fully as a standalone module, 
        # we need to ensure all dependencies (like DeepSeekAnalyst, WorkersAI) 
        # are importable.
        
        return Response.new(json.dumps({"ok": True}), headers=headers)

    except Exception as e:
        return Response.new(json.dumps({"ok": True, "error": str(e)}), headers=headers)

async def send_telegram_reply(env, chat_id, text):
    """Helper to send message"""
    try:
        telegram_token = str(getattr(env, 'TELEGRAM_BOT_TOKEN', ''))
        if not telegram_token: return
        
        url = f"{TELEGRAM_API_URL}{telegram_token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        })
        
        headers = Headers.new({"Content-Type": "application/json"}.items())
        await fetch(url, method="POST", headers=headers, body=payload)
    except:
        pass

async def send_telegram_alert(env, message):
    """External alert sender"""
    try:
        telegram_token = str(getattr(env, 'TELEGRAM_BOT_TOKEN', ''))
        telegram_chat_id = str(getattr(env, 'TELEGRAM_CHAT_ID', ''))
        
        if not telegram_token or not telegram_chat_id:
            return
        
        url = f"{TELEGRAM_API_URL}{telegram_token}/sendMessage"
        
        payload = json.dumps({
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        })
        
        req_headers = Headers.new({"Content-Type": "application/json"}.items())
        await fetch(url, method="POST", headers=req_headers, body=payload)
    except:
        pass
