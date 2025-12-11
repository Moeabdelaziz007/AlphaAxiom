# backend/app/main.py
# ==============================================
# TRADING SYSTEM 0.1 - FastAPI Backend
# "النظام يزيل العاطفة. ينفذ كالجراح."
# ==============================================

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json
from datetime import datetime

from app.ai.sentinel_agent import SentinelAgent
from app.ai.dual_brain import DualBrain, run_strategy_updater
from app.config import DEMO_MODE
from app.adapters.tradingview import TradingViewWebhook, convert_tv_to_internal
from app.utils.secrets_manager import secrets

# ==============================================
# APP INITIALIZATION
# ==============================================

app = FastAPI(
    title="Trading System 0.1",
    description="Multi-Asset Trading Platform with Dual-Core AI Brain",
    version="0.1.0"
)

# CORS للاتصال مع الـ Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agents
sentinel = SentinelAgent()
brain = DualBrain()

# ... (Pydantic models remain the same) ...

class OrderRequest(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    amount: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    auto_risk: bool = True

class AnalysisRequest(BaseModel):
    symbol: str

class ChatRequest(BaseModel):
    message: str

# ... (Health endpoints remain the same) ...

@app.get("/")
async def root():
    return {
        "name": "Trading System 0.1",
        "status": "ONLINE",
        "mode": "DEMO" if DEMO_MODE else "LIVE",
        "brain": "Dual-Core (DeepSeek + Gemini) ACTIVE"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def get_system_status():
    """حالة النظام الكاملة"""
    status = sentinel.get_status()
    status["brain"] = brain.get_status()
    return status

@app.get("/api/brain/status")
async def get_brain_status():
    """حالة العقل المزدوج"""
    return brain.get_status()

# ... (Market Data and Trading endpoints remain using sentinel for now) ...

@app.get("/api/market/{symbol}")
async def get_market_price(symbol: str):
    asset_type = sentinel.detect_asset_type(symbol)
    if asset_type == "CRYPTO":
        data = sentinel.crypto.get_market_price(symbol)
    else:
        data = sentinel.tradfi.get_market_price(symbol)
    return {"asset_type": asset_type, **data}

@app.get("/api/market/{symbol}/history")
async def get_market_history(symbol: str, period: str = "1mo", interval: str = "1d"):
    data = sentinel.tradfi.get_historical_data(symbol, period, interval)
    return {"symbol": symbol, "data": data}

@app.post("/api/trade")
async def execute_trade(order: OrderRequest):
    result = sentinel.execute_trade(
        symbol=order.symbol,
        side=order.side,
        amount=order.amount,
        sl_price=order.stop_loss,
        tp_price=order.take_profit,
        auto_risk=order.auto_risk
    )
    return result

@app.post("/api/webhook/tradingview")
async def tradingview_webhook(webhook_data: TradingViewWebhook):
    """
    Handle webhooks from TradingView.
    """
    try:
        # Adapter Pattern: Convert TV format to Internal format
        internal_order_data = convert_tv_to_internal(webhook_data)

        # Execute Trade using the same logic as /api/trade
        result = sentinel.execute_trade(
            symbol=internal_order_data["symbol"],
            side=internal_order_data["side"],
            amount=internal_order_data["amount"],
            sl_price=internal_order_data["stop_loss"],
            tp_price=internal_order_data["take_profit"],
            auto_risk=internal_order_data["auto_risk"]
        )
        return {"status": "success", "source": "tradingview", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions")
async def get_positions():
    return sentinel.get_all_positions()

@app.post("/api/flatten")
async def flatten_all():
    return sentinel.flatten_all()

@app.post("/api/analyze")
async def analyze_asset(req: AnalysisRequest):
    momentum = sentinel.analyze_momentum(req.symbol)
    return momentum

@app.get("/api/ai/logs")
async def get_ai_logs(limit: int = 50):
    return {"logs": sentinel.get_logs(limit)}

# ==============================================
# AI CHAT ENDPOINT (Dual-Core Brain)
# ==============================================

@app.post("/api/ai/chat")
async def ai_chat(req: ChatRequest):
    """Chat with Gemini (connected to DeepSeek strategy)"""
    # Get live price for context
    price_data = sentinel.crypto.get_market_price("BTC/USD")
    current_price = price_data.get("price", 0)
    
    # Process with Dual Brain
    response = await brain.chat_and_execute(
        user_input=req.message,
        live_price=current_price
    )
    return response

# ... (WebSocket remains the same) ...
# ==============================================
# WEBSOCKET FOR REAL-TIME UPDATES
# ==============================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # إرسال تحديثات كل ثانية
            status = sentinel.get_status()
            brain_status = brain.get_status()
            logs = sentinel.get_logs(5)
            
            await websocket.send_json({
                "type": "update",
                "status": status,
                "brain": brain_status,
                "logs": logs,
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==============================================
# STARTUP EVENT
# ==============================================

@app.on_event("startup")
async def startup_event():
    print("=" * 50)
    print("🚀 TRADING SYSTEM 0.1 STARTED")
    print(f"📊 Mode: {'DEMO' if DEMO_MODE else 'LIVE'}")
    print("🧠 Brain: Dual-Core (DeepSeek + Gemini) ONLINE")
    print("=" * 50)
    
    # Start the DeepSeek Strategy Updater in background
    asyncio.create_task(run_strategy_updater(brain))

