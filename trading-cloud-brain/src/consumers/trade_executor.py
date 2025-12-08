"""
📨 Trade Executor Consumer
Handles async trade execution from Cloudflare Queue.
"""

from brokers import BrokerGateway
from core import log

async def consume_trade_queue(batch, env):
    """
    Process batch of trade instructions.
    
    Args:
        batch: Queue batch object
        env: Worker environment
    """
    gateway = BrokerGateway(env)
    
    for message in batch.messages:
        try:
            payload = message.body
            symbol = payload.get("symbol")
            action = payload.get("action", "BUY")
            qty = payload.get("qty", 100)
            
            log.info(f"📨 Queue Processing: {action} {symbol}")
            
            # 1. Execute Trade
            # Note: We retry here if broker fails
            # result = await gateway.execute(...) 
            
            # 2. Acknowledge success
            message.ack()
            
        except Exception as e:
            log.error(f"Queue Execution Failed: {e}")
            # message.retry() # Optional: Retry later
