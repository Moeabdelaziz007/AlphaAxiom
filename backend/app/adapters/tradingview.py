from pydantic import BaseModel, Field
from typing import Optional, Literal

class TradingViewWebhook(BaseModel):
    time: str
    exchange: str
    ticker: str
    close: float
    strategy: dict = Field(..., description="Strategy details containing order_action and order_contracts")

    class Config:
        json_schema_extra = {
            "example": {
                "time": "2023-10-27T10:00:00Z",
                "exchange": "BINANCE",
                "ticker": "BTCUSDT",
                "close": 34000.50,
                "strategy": {
                    "order_action": "buy",
                    "order_contracts": 1
                }
            }
        }

def convert_tv_to_internal(tv_data: TradingViewWebhook):
    """
    Converts TradingView webhook data to internal OrderRequest format.

    Mapping:
    - ticker -> symbol
    - strategy.order_action -> side
    - strategy.order_contracts -> amount
    """

    # Extract data
    symbol = tv_data.ticker
    side = tv_data.strategy.get("order_action", "").upper()
    amount = float(tv_data.strategy.get("order_contracts", 0))

    # Normalize side (TradingView might send 'buy'/'sell')
    if side not in ["BUY", "SELL"]:
        # Fallback or error handling if needed
        pass

    return {
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "auto_risk": True, # Default to auto risk management
        "stop_loss": None, # Could be calculated or passed in params if TV supports it
        "take_profit": None
    }
