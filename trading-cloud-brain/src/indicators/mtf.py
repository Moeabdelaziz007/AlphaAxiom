# ========================================
# 🔄 AXIOM MTF - Multi-Timeframe Confluence Analysis
# ========================================
# Top-down approach: Daily → 4H → 1H
# Confluence = agreement across timeframes
# Inspired by Mini-Aladdin MarketAgent patterns
# ========================================

from typing import List, Dict, Any, Optional
from indicators.rsi import calculate_rsi, get_rsi_signal


class MTFAnalyzer:
    """
    Multi-Timeframe Confluence Analysis Engine.
    
    Uses 3-timeframe approach following best practices:
    - Daily: Overall trend direction (weight: 50%)
    - 4H: Setup confirmation (weight: 30%)
    - 1H: Entry timing (weight: 20%)
    
    Confluence scoring:
    - 3/3 timeframes agree = HIGH (1.0)
    - 2/3 timeframes agree = MEDIUM (0.7)
    - Split signals = LOW (0.3)
    """
    
    # Timeframe configurations
    TIMEFRAME_CONFIG = {
        'crypto': {
            'high': '1d',    # Daily for trend
            'medium': '4h',  # 4H for setup
            'low': '1h'      # 1H for entry
        },
        'forex': {
            'high': 'D',
            'medium': 'H4',
            'low': 'H1'
        },
        'stock': {
            'high': '1d',
            'medium': '4h',
            'low': '1h'
        }
    }
    
    # Weight distribution
    WEIGHTS = {
        'high': 0.50,    # Daily trend is most important
        'medium': 0.30,  # 4H setup
        'low': 0.20      # 1H entry
    }
    
    def __init__(self):
        self.last_analysis = None
    
    async def analyze_confluence(
        self,
        prices_by_timeframe: Dict[str, List[float]],
        asset_type: str = 'crypto'
    ) -> Dict[str, Any]:
        """
        Perform multi-timeframe confluence analysis.
        
        Args:
            prices_by_timeframe: Dict mapping timeframe key to price list
                Example: {'high': [...daily prices...], 'medium': [...4h prices...], 'low': [...1h prices...]}
            asset_type: 'crypto', 'forex', or 'stock'
        
        Returns:
            Confluence analysis with score, direction, and signals
        """
        signals_by_tf = {}
        rsi_by_tf = {}
        trends = []
        
        # Analyze each timeframe
        for tf_key in ['high', 'medium', 'low']:
            prices = prices_by_timeframe.get(tf_key, [])
            
            if len(prices) < 20:
                # Insufficient data
                signals_by_tf[tf_key] = {
                    'trend': 'NEUTRAL',
                    'rsi': 50.0,
                    'strength': 50,
                    'valid': False
                }
                trends.append('NEUTRAL')
                rsi_by_tf[tf_key] = 50.0
                continue
            
            # Calculate RSI
            rsi = calculate_rsi(prices, period=14)
            rsi_signal = get_rsi_signal(rsi)
            
            # Detect trend using SMA crossover + momentum
            trend_info = self._detect_trend(prices)
            
            # Combined signal for this timeframe
            tf_signal = self._combine_signals(rsi_signal, trend_info)
            
            signals_by_tf[tf_key] = {
                'trend': tf_signal['direction'],
                'rsi': rsi,
                'momentum': trend_info['momentum'],
                'sma_cross': trend_info['sma_cross'],
                'strength': tf_signal['strength'],
                'valid': True
            }
            
            trends.append(tf_signal['direction'])
            rsi_by_tf[tf_key] = rsi
        
        # Calculate confluence
        confluence_result = self._calculate_confluence(trends, signals_by_tf)
        
        # Store for reference
        self.last_analysis = {
            'timestamp': self._get_timestamp(),
            'signals': signals_by_tf,
            'confluence': confluence_result,
            'rsi': rsi_by_tf
        }
        
        return {
            'confluence_score': confluence_result['score'],
            'direction': confluence_result['direction'],
            'signal': confluence_result['signal'],
            'confidence': confluence_result['confidence'],
            'timeframes': signals_by_tf,
            'rsi': rsi_by_tf,
            'recommendation': confluence_result['recommendation']
        }
    
    def _detect_trend(self, prices: List[float]) -> Dict[str, Any]:
        """
        Detect trend using SMA crossover and momentum.
        
        Returns:
            Dict with trend direction, momentum, and SMA cross info
        """
        if len(prices) < 50:
            return {
                'direction': 'NEUTRAL',
                'momentum': 0,
                'sma_cross': 'none',
                'strength': 50
            }
        
        # Calculate SMAs
        sma_20 = sum(prices[-20:]) / 20
        sma_50 = sum(prices[-50:]) / 50
        
        # Current price vs SMAs
        current_price = prices[-1]
        above_sma20 = current_price > sma_20
        above_sma50 = current_price > sma_50
        
        # SMA crossover
        if sma_20 > sma_50:
            sma_cross = 'bullish'
        elif sma_20 < sma_50:
            sma_cross = 'bearish'
        else:
            sma_cross = 'neutral'
        
        # Momentum (price change percentage over 10 periods)
        if len(prices) >= 10:
            momentum = ((prices[-1] - prices[-10]) / prices[-10]) * 100
        else:
            momentum = 0
        
        # Determine trend direction
        bullish_signals = 0
        bearish_signals = 0
        
        if above_sma20: bullish_signals += 1
        else: bearish_signals += 1
        
        if above_sma50: bullish_signals += 1
        else: bearish_signals += 1
        
        if sma_cross == 'bullish': bullish_signals += 1
        elif sma_cross == 'bearish': bearish_signals += 1
        
        if momentum > 1: bullish_signals += 1
        elif momentum < -1: bearish_signals += 1
        
        # Calculate direction and strength
        if bullish_signals >= 3:
            direction = 'BULLISH'
            strength = min(90, 60 + bullish_signals * 10)
        elif bearish_signals >= 3:
            direction = 'BEARISH'
            strength = min(90, 60 + bearish_signals * 10)
        elif bullish_signals > bearish_signals:
            direction = 'NEUTRAL_BULLISH'
            strength = 55
        elif bearish_signals > bullish_signals:
            direction = 'NEUTRAL_BEARISH'
            strength = 45
        else:
            direction = 'NEUTRAL'
            strength = 50
        
        return {
            'direction': direction,
            'momentum': round(momentum, 2),
            'sma_cross': sma_cross,
            'sma_20': round(sma_20, 2),
            'sma_50': round(sma_50, 2),
            'above_sma20': above_sma20,
            'above_sma50': above_sma50,
            'strength': strength
        }
    
    def _combine_signals(self, rsi_signal: Dict, trend_info: Dict) -> Dict:
        """
        Combine RSI and trend signals into unified direction.
        """
        rsi_direction = rsi_signal['signal']
        trend_direction = trend_info['direction']
        
        # Map to simplified direction
        direction_map = {
            'STRONG_BUY': 'BULLISH',
            'BUY': 'BULLISH',
            'NEUTRAL_BULLISH': 'NEUTRAL_BULLISH',
            'NEUTRAL': 'NEUTRAL',
            'NEUTRAL_BEARISH': 'NEUTRAL_BEARISH',
            'SELL': 'BEARISH',
            'STRONG_SELL': 'BEARISH',
            'BULLISH': 'BULLISH',
            'BEARISH': 'BEARISH'
        }
        
        rsi_dir = direction_map.get(rsi_direction, 'NEUTRAL')
        trend_dir = direction_map.get(trend_direction, 'NEUTRAL')
        
        # If both agree
        if rsi_dir == trend_dir:
            return {'direction': rsi_dir, 'strength': 85}
        
        # If one is neutral
        if 'NEUTRAL' in rsi_dir:
            return {'direction': trend_dir, 'strength': 65}
        if 'NEUTRAL' in trend_dir:
            return {'direction': rsi_dir, 'strength': 65}
        
        # Conflicting signals - trend wins but reduced confidence
        return {'direction': trend_dir, 'strength': 50}
    
    def _calculate_confluence(self, trends: List[str], signals: Dict) -> Dict:
        """
        Calculate confluence score based on timeframe agreement.
        """
        # Simplify to bullish/bearish/neutral
        simplified = []
        for t in trends:
            if 'BULLISH' in t:
                simplified.append('BULLISH')
            elif 'BEARISH' in t:
                simplified.append('BEARISH')
            else:
                simplified.append('NEUTRAL')
        
        bullish_count = simplified.count('BULLISH')
        bearish_count = simplified.count('BEARISH')
        
        # 3/3 Agreement
        if bullish_count == 3:
            return {
                'score': 1.0,
                'direction': 'BULLISH',
                'signal': 'STRONG_BUY',
                'confidence': 90,
                'recommendation': '🟢 High confluence BUY - All timeframes aligned bullish'
            }
        if bearish_count == 3:
            return {
                'score': 1.0,
                'direction': 'BEARISH',
                'signal': 'STRONG_SELL',
                'confidence': 90,
                'recommendation': '🔴 High confluence SELL - All timeframes aligned bearish'
            }
        
        # 2/3 Agreement
        if bullish_count >= 2:
            return {
                'score': 0.7,
                'direction': 'BULLISH',
                'signal': 'BUY',
                'confidence': 70,
                'recommendation': '🟡 Medium confluence BUY - 2/3 timeframes bullish'
            }
        if bearish_count >= 2:
            return {
                'score': 0.7,
                'direction': 'BEARISH',
                'signal': 'SELL',
                'confidence': 70,
                'recommendation': '🟡 Medium confluence SELL - 2/3 timeframes bearish'
            }
        
        # Split or mostly neutral
        return {
            'score': 0.3,
            'direction': 'NEUTRAL',
            'signal': 'HOLD',
            'confidence': 40,
            'recommendation': '⚪ Low confluence - Wait for better alignment'
        }
    
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds"""
        from datetime import datetime
        return int(datetime.now().timestamp() * 1000)


# ========================================
# Simplified MTF Function for Quick Use
# ========================================

def quick_mtf_analysis(
    daily_prices: List[float],
    h4_prices: List[float],
    h1_prices: List[float]
) -> Dict[str, Any]:
    """
    Quick MTF analysis with 3 price lists.
    
    Args:
        daily_prices: Daily closing prices
        h4_prices: 4-hour closing prices
        h1_prices: 1-hour closing prices
    
    Returns:
        Confluence analysis result
    """
    import asyncio
    
    analyzer = MTFAnalyzer()
    prices = {
        'high': daily_prices,
        'medium': h4_prices,
        'low': h1_prices
    }
    
    # Run async in sync context
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(analyzer.analyze_confluence(prices))
    finally:
        loop.close()
    
    return result


def calculate_mtf_score_from_single_prices(
    prices: List[float],
    chunks: int = 3
) -> Dict[str, Any]:
    """
    Approximate MTF analysis from single price list.
    Divides into 3 segments simulating different timeframes.
    
    This is a fallback when we don't have actual multi-TF data.
    
    Args:
        prices: Single list of prices (at least 60 data points)
        chunks: Number of segments (default 3)
    
    Returns:
        Simplified MTF-like analysis
    """
    if len(prices) < 60:
        return {
            'confluence_score': 0.5,
            'direction': 'NEUTRAL',
            'signal': 'HOLD',
            'confidence': 40,
            'message': 'Insufficient data for MTF approximation'
        }
    
    # Simulate timeframes by resampling
    # "Daily" = last 60 prices (representing weekly trend)
    # "4H" = last 30 prices
    # "1H" = last 15 prices
    
    daily_sim = prices[-60::4]  # Every 4th price = ~15 points
    h4_sim = prices[-30::2]     # Every 2nd = ~15 points
    h1_sim = prices[-15:]       # Raw = 15 points
    
    # Calculate RSI for each
    rsi_daily = calculate_rsi(daily_sim) if len(daily_sim) >= 15 else 50
    rsi_4h = calculate_rsi(h4_sim) if len(h4_sim) >= 15 else 50
    rsi_1h = calculate_rsi(h1_sim) if len(h1_sim) >= 15 else 50
    
    # Simple confluence from RSI zones
    signals = []
    for rsi in [rsi_daily, rsi_4h, rsi_1h]:
        if rsi < 35:
            signals.append('BUY')
        elif rsi > 65:
            signals.append('SELL')
        else:
            signals.append('NEUTRAL')
    
    buy_count = signals.count('BUY')
    sell_count = signals.count('SELL')
    
    if buy_count == 3:
        return {
            'confluence_score': 1.0,
            'direction': 'BULLISH',
            'signal': 'STRONG_BUY',
            'confidence': 85,
            'rsi': {'daily': rsi_daily, '4h': rsi_4h, '1h': rsi_1h}
        }
    elif sell_count == 3:
        return {
            'confluence_score': 1.0,
            'direction': 'BEARISH',
            'signal': 'STRONG_SELL',
            'confidence': 85,
            'rsi': {'daily': rsi_daily, '4h': rsi_4h, '1h': rsi_1h}
        }
    elif buy_count >= 2:
        return {
            'confluence_score': 0.7,
            'direction': 'BULLISH',
            'signal': 'BUY',
            'confidence': 65,
            'rsi': {'daily': rsi_daily, '4h': rsi_4h, '1h': rsi_1h}
        }
    elif sell_count >= 2:
        return {
            'confluence_score': 0.7,
            'direction': 'BEARISH',
            'signal': 'SELL',
            'confidence': 65,
            'rsi': {'daily': rsi_daily, '4h': rsi_4h, '1h': rsi_1h}
        }
    else:
        return {
            'confluence_score': 0.4,
            'direction': 'NEUTRAL',
            'signal': 'HOLD',
            'confidence': 45,
            'rsi': {'daily': rsi_daily, '4h': rsi_4h, '1h': rsi_1h}
        }
