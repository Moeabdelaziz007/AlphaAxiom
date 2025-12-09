# ========================================
# 🎯 AXIOM RSI INDICATOR - Wilder's Smoothed RSI
# ========================================
# Based on J. Welles Wilder Jr.'s original formula
# With enhancements from Mini-Aladdin MathAgent
# ========================================

from typing import List, Dict, Optional, Tuple
from datetime import datetime


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate RSI using Wilder's smoothed method.
    
    This is the CORRECT implementation (not simple SMA).
    Uses exponential smoothing: AvgU = (Previous_AvgU × (N-1) + Current_U) / N
    
    Args:
        prices: List of closing prices (oldest first)
        period: RSI period, default 14 (Wilder's recommended)
    
    Returns:
        RSI value between 0-100
        Returns 50.0 (neutral) if insufficient data
    """
    if len(prices) < period + 1:
        return 50.0  # Neutral if insufficient data
    
    # Step 1: Calculate price changes
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Step 2: Separate gains and losses
    gains = [max(0, c) for c in changes]
    losses = [abs(min(0, c)) for c in changes]
    
    # Step 3: First average (simple average for initial period)
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Step 4: Wilder's smoothing for remaining periods
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    # Step 5: Calculate RSI
    if avg_loss == 0:
        return 100.0  # No losses = max RSI
    
    if avg_gain == 0:
        return 0.0  # No gains = min RSI
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def get_rsi_signal(rsi_value: float) -> Dict[str, any]:
    """
    Convert RSI value to trading signal.
    
    Thresholds:
        < 20: Extremely Oversold (Strong Buy)
        < 30: Oversold (Buy)
        30-40: Neutral-Bullish
        40-60: Neutral
        60-70: Neutral-Bearish
        > 70: Overbought (Sell)
        > 80: Extremely Overbought (Strong Sell)
    
    Args:
        rsi_value: RSI between 0-100
    
    Returns:
        Dict with signal, strength, and description
    """
    if rsi_value < 20:
        return {
            "signal": "STRONG_BUY",
            "strength": 90,
            "zone": "extreme_oversold",
            "description": f"RSI {rsi_value:.1f} - Extreme oversold, high reversal probability"
        }
    elif rsi_value < 30:
        return {
            "signal": "BUY",
            "strength": 75,
            "zone": "oversold",
            "description": f"RSI {rsi_value:.1f} - Oversold territory"
        }
    elif rsi_value < 40:
        return {
            "signal": "NEUTRAL_BULLISH",
            "strength": 55,
            "zone": "neutral_low",
            "description": f"RSI {rsi_value:.1f} - Neutral with bullish bias"
        }
    elif rsi_value <= 60:
        return {
            "signal": "NEUTRAL",
            "strength": 50,
            "zone": "neutral",
            "description": f"RSI {rsi_value:.1f} - Neutral zone"
        }
    elif rsi_value <= 70:
        return {
            "signal": "NEUTRAL_BEARISH",
            "strength": 45,
            "zone": "neutral_high",
            "description": f"RSI {rsi_value:.1f} - Neutral with bearish bias"
        }
    elif rsi_value <= 80:
        return {
            "signal": "SELL",
            "strength": 75,
            "zone": "overbought",
            "description": f"RSI {rsi_value:.1f} - Overbought territory"
        }
    else:
        return {
            "signal": "STRONG_SELL",
            "strength": 90,
            "zone": "extreme_overbought",
            "description": f"RSI {rsi_value:.1f} - Extreme overbought, high reversal probability"
        }


def calculate_rsi_divergence(prices: List[float], rsi_values: List[float]) -> Optional[Dict]:
    """
    Detect RSI divergence (advanced signal).
    
    Bullish Divergence: Price making lower lows, RSI making higher lows
    Bearish Divergence: Price making higher highs, RSI making lower highs
    
    Args:
        prices: List of prices
        rsi_values: Corresponding RSI values
    
    Returns:
        Divergence info or None if no divergence
    """
    if len(prices) < 10 or len(rsi_values) < 10:
        return None
    
    # Look back 10 periods
    recent_prices = prices[-10:]
    recent_rsi = rsi_values[-10:]
    
    # Find local minima/maxima
    price_trend = recent_prices[-1] - recent_prices[0]
    rsi_trend = recent_rsi[-1] - recent_rsi[0]
    
    # Bullish divergence: price down, RSI up
    if price_trend < 0 and rsi_trend > 5:
        return {
            "type": "bullish_divergence",
            "signal": "BUY",
            "strength": 80,
            "description": "Bullish divergence: momentum shifting up despite price drop"
        }
    
    # Bearish divergence: price up, RSI down
    if price_trend > 0 and rsi_trend < -5:
        return {
            "type": "bearish_divergence",
            "signal": "SELL",
            "strength": 80,
            "description": "Bearish divergence: momentum weakening despite price rise"
        }
    
    return None


def calculate_stochastic_rsi(prices: List[float], rsi_period: int = 14, stoch_period: int = 14) -> Tuple[float, float]:
    """
    Calculate Stochastic RSI (more sensitive than regular RSI).
    
    Formula:
        StochRSI = (RSI - Lowest RSI) / (Highest RSI - Lowest RSI) × 100
    
    Args:
        prices: List of prices
        rsi_period: Period for RSI calculation
        stoch_period: Period for stochastic calculation
    
    Returns:
        Tuple of (StochRSI %K, StochRSI %D)
    """
    if len(prices) < rsi_period + stoch_period:
        return (50.0, 50.0)
    
    # Calculate RSI for each period
    rsi_values = []
    for i in range(stoch_period, len(prices)):
        rsi = calculate_rsi(prices[:i+1], rsi_period)
        rsi_values.append(rsi)
    
    if len(rsi_values) < stoch_period:
        return (50.0, 50.0)
    
    # Calculate Stochastic RSI
    recent_rsi = rsi_values[-stoch_period:]
    lowest_rsi = min(recent_rsi)
    highest_rsi = max(recent_rsi)
    
    if highest_rsi == lowest_rsi:
        stoch_rsi = 50.0
    else:
        stoch_rsi = ((rsi_values[-1] - lowest_rsi) / (highest_rsi - lowest_rsi)) * 100
    
    # %D is 3-period SMA of %K
    k_values = []
    for i in range(-3, 0):
        if len(rsi_values) + i >= stoch_period:
            r = rsi_values[i]
            k = ((r - lowest_rsi) / (highest_rsi - lowest_rsi)) * 100 if highest_rsi != lowest_rsi else 50
            k_values.append(k)
    
    percent_d = sum(k_values) / len(k_values) if k_values else stoch_rsi
    
    return (round(stoch_rsi, 2), round(percent_d, 2))


# ========================================
# Quick Test Function
# ========================================
def test_rsi():
    """Test RSI calculation with sample data"""
    # Simulated uptrend prices
    uptrend = [100, 102, 104, 103, 105, 107, 108, 110, 109, 111, 
               113, 115, 114, 116, 118, 120, 119, 121]
    
    # Simulated downtrend prices
    downtrend = [120, 118, 119, 117, 115, 116, 114, 112, 113, 111,
                 109, 110, 108, 106, 107, 105, 103, 102]
    
    # Flat prices
    flat = [100] * 20
    
    rsi_up = calculate_rsi(uptrend)
    rsi_down = calculate_rsi(downtrend)
    rsi_flat = calculate_rsi(flat)
    
    return {
        "uptrend_rsi": rsi_up,  # Should be > 60
        "downtrend_rsi": rsi_down,  # Should be < 40
        "flat_rsi": rsi_flat,  # Should be ~50
        "uptrend_signal": get_rsi_signal(rsi_up),
        "downtrend_signal": get_rsi_signal(rsi_down)
    }
