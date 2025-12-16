"""
Signal API Server - Standalone FastAPI for MT5 EA
Runs on port 8767 alongside the MCP server on 8766
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI(title="AlphaAxiom Signal API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Signal storage (file-based for persistence)
SIGNAL_FILE = "/tmp/latest_signal.json"

class Signal(BaseModel):
    action: str
    symbol: str
    price: float
    tp: float
    sl: float
    reason: str = "AlphaAxiom Signal"
    signal_id: str = None

def load_signal():
    try:
        with open(SIGNAL_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"status": "waiting"}

def save_signal(data):
    with open(SIGNAL_FILE, 'w') as f:
        json.dump(data, f)

@app.get("/")
async def root():
    return {"status": "online", "service": "AlphaAxiom Signal API"}

@app.get("/api/v1/signals/latest")
async def get_signal():
    """Called by MT5 AlphaReceiver EA to get latest signal"""
    return load_signal()

@app.post("/api/v1/signals/push")
async def push_signal(signal: Signal):
    """Called by Brain to push new signals"""
    data = signal.dict()
    if not data.get("signal_id"):
        data["signal_id"] = f"sig_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    data["time"] = datetime.now().isoformat()
    save_signal(data)
    return {"ok": True, "signal_id": data["signal_id"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8767)
