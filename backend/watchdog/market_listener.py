import asyncio
import websockets
import json
import logging
import os
import requests
from datetime import datetime

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("market_watchdog.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Watchdog")

# Configuration
ALPACA_KEY = os.getenv("ALPACA_KEY", "PK******************") # Replace with env var or fallback
ALPACA_SECRET = os.getenv("ALPACA_SECRET", "********************")
ALPACA_STREAM_URL = "wss://stream.data.alpaca.markets/v2/iex" # Free tier IEX data
CLOUD_RUN_URL = os.getenv("CLOUD_RUN_URL", "http://localhost:8000")
ALERT_THRESHOLD_PERCENT = 2.0  # Alert on 2% moves

async def market_listener():
    """
    Lightweight WebSocket Listener for Market Data.
    Monitors for price spikes and triggers alerts.
    """
    logger.info("🐶 Watchdog Listener Starting...")

    auth_data = {
        "action": "auth",
        "key": ALPACA_KEY,
        "secret": ALPACA_SECRET
    }

    subscribe_data = {
        "action": "subscribe",
        "trades": ["SPY", "QQQ", "AAPL", "TSLA"]
    }

    while True:
        try:
            async with websockets.connect(ALPACA_STREAM_URL) as websocket:
                # 1. Authenticate
                await websocket.send(json.dumps(auth_data))
                auth_response = await websocket.recv()
                logger.info(f"Auth Response: {auth_response}")

                # 2. Subscribe
                await websocket.send(json.dumps(subscribe_data))
                sub_response = await websocket.recv()
                logger.info(f"Sub Response: {sub_response}")

                logger.info("✅ Connected to Market Stream")

                # 3. Listen Loop
                async for message in websocket:
                    data = json.loads(message)
                    for item in data:
                        if item.get("T") == "t": # Trade message
                            symbol = item.get("S")
                            price = float(item.get("p"))
                            # size = item.get("s")
                            # timestamp = item.get("t")

                            # Simple logic: Just log for now to be lightweight
                            # In real scenario: Compare with rolling average or previous close
                            # logger.debug(f"Tick: {symbol} @ {price}")

                            # Placeholder for anomaly detection
                            if price > 1000 and symbol == "AAPL": # Impossible condition just for logic structure
                                await trigger_alert(symbol, price, "PRICE_SPIKE")

        except Exception as e:
            logger.error(f"⚠️ Connection Error: {e}")
            logger.info("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

async def trigger_alert(symbol, price, alert_type):
    """Send alert to Cloud Run Backend"""
    try:
        payload = {
            "symbol": symbol,
            "price": price,
            "type": alert_type,
            "timestamp": datetime.now().isoformat()
        }
        # Assuming there is an endpoint for alerts or just log it
        logger.warning(f"🚨 ALERT: {symbol} {alert_type} @ {price}")

        # requests.post(f"{CLOUD_RUN_URL}/api/webhook/alert", json=payload)

    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(market_listener())
    except KeyboardInterrupt:
        logger.info("Watchdog stopped.")
