
import multiprocessing
import time
import requests
import uvicorn
import json
import sys
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

# --- REPLICATING MAIN.PY (The Brain) ---
app = FastAPI()
SIGNAL_FILE = "test_signal.json"

class Signal(BaseModel):
    action: str
    symbol: str
    price: float
    tp: float
    sl: float
    reason: str = "Test Signal"

@app.get("/api/v1/signals/latest")
async def get_signal(x_api_key: str = Header(None)):
    # Simulating the loose auth check
    if x_api_key and len(x_api_key) < 3:
        raise HTTPException(status_code=403, detail="Invalid Key")
    
    try:
        with open(SIGNAL_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"status": "waiting"}

@app.post("/api/v1/signals/push")
async def push(signal: Signal):
    data = signal.dict()
    with open(SIGNAL_FILE, 'w') as f:
        json.dump(data, f)
    return {"ok": True}

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=9999, log_level="critical")

# --- OFFENSIVE SIMULATION (The EA) ---
def simulate_ea_client():
    base_url = "http://127.0.0.1:9999"
    
    print("⏳ [1/4] Waiting for Brain to wake up...")
    time.sleep(5)
    
    # 1. Pushing a Test Signal
    print("🚀 [2/4] Brain generating signal (Push)...")
    signal_data = {
        "action": "BUY",
        "symbol": "EURUSD",
        "price": 1.1050,
        "tp": 1.1100,
        "sl": 1.1000,
        "reason": "Simulation Test"
    }
    try:
        res = requests.post(f"{base_url}/api/v1/signals/push", json=signal_data)
        assert res.status_code == 200
        print("   ✅ Signal Pushed Successfully")
    except Exception as e:
        print(f"   ❌ Push Failed: {e}")
        return

    # 2. Simulating EA Polling (Zero-Config inputs)
    print("📡 [3/4] EA Polling (simulating AlphaReceiver.mq5)...")
    headers = {"X-API-Key": "aw-windows-local-key"} # Default Key from MQ5
    
    try:
        res = requests.get(f"{base_url}/api/v1/signals/latest", headers=headers)
        if res.status_code == 200:
            data = res.json()
            print(f"   📥 Received: {data}")
            
            # 3. Verification
            print("🔍 [4/4] Verifying Protocol...")
            assert data["action"] == "BUY"
            assert data["symbol"] == "EURUSD"
            print("   ✅ Protocol Match: EA would execute this trade.")
        else:
            print(f"   ❌ EA Poll Failed: Status {res.status_code}")
    except Exception as e:
        print(f"   ❌ Connection Failed: {e}")

if __name__ == "__main__":
    # Start Server in background
    p = multiprocessing.Process(target=run_server)
    p.start()
    
    try:
        simulate_ea_client()
    finally:
        p.terminate()
        p.join()
