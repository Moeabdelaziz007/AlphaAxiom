"""
⚡ AEXI Engine - Adaptive Exhaustion Index Protocol
The "Early Warning System" for detecting market exhaustion and potential reversals.

FORMULA:
AEXI = (0.4 × EXH) + (0.3 × VAF) + (0.3 × SVP)

Components:
- EXH: Exhaustion Score via Z-Score (price deviation from mean)
- VAF: Velocity/ATR Factor (momentum relative to volatility)
- SVP: Surveillance Volume Proxy (volume spike detection)

Signal Trigger: AEXI > 80 indicates potential reversal
"""

import math

class AEXIEngine:
    """
    AEXI Protocol - Exhaustion Detection for Reversals.
    Identifies when price has moved too far, too fast.
    """
    
    # Configuration
    SMA_PERIOD = 20       # Period for mean calculation
    ATR_PERIOD = 14       # Period for ATR
    VOLUME_PERIOD = 20    # Period for volume analysis
    SIGNAL_THRESHOLD = 80 # AEXI > 80 = Potential Reversal
    
    def __init__(self, data: list):
        """
        :param data: List of dicts [{'close':.., 'high':.., 'low':.., 'volume':..}, ...]
        """
        self.data = data
        self.closes = [d['close'] for d in data]
        self.highs = [d['high'] for d in data]
        self.lows = [d['low'] for d in data]
        self.volumes = [d['volume'] for d in data]
    
    def calculate_exh(self) -> dict:
        """
        EXH - Exhaustion Score via Z-Score.
        
        Z = (Price - SMA) / StdDev
        Measures how far price has deviated from its mean in standard deviations.
        
        Returns normalized score 0-100.
        """
        if len(self.closes) < self.SMA_PERIOD:
            return {"raw": 0, "normalized": 0, "signal": "NEUTRAL"}
        
        recent = self.closes[-self.SMA_PERIOD:]
        sma = sum(recent) / len(recent)
        
        # Standard Deviation
        variance = sum((x - sma) ** 2 for x in recent) / len(recent)
        std_dev = math.sqrt(variance) if variance > 0 else 0.0001
        
        current_price = self.closes[-1]
        z_score = (current_price - sma) / std_dev
        
        # Normalize to 0-100 (capped at ±3 std dev)
        # Z-Score of 3 = 100%, Z-Score of -3 = 0%
        normalized = min(100, max(0, (z_score + 3) / 6 * 100))
        
        # Determine signal
        signal = "NEUTRAL"
        if z_score > 2.0:
            signal = "OVERBOUGHT"  # Possible top
        elif z_score < -2.0:
            signal = "OVERSOLD"   # Possible bottom
        
        return {
            "raw": round(z_score, 3),
            "normalized": round(normalized, 2),
            "signal": signal
        }
    
    def calculate_vaf(self) -> dict:
        """
        VAF - Velocity/ATR Factor.
        
        Measures momentum (ROC) relative to volatility (ATR).
        High VAF = Price moving fast relative to typical volatility.
        
        Returns normalized score 0-100.
        """
        if len(self.closes) < max(self.ATR_PERIOD + 1, 6):
            return {"roc": 0, "atr": 0, "normalized": 0}
        
        # Rate of Change (5 periods)
        roc = (self.closes[-1] - self.closes[-6]) / self.closes[-6] * 100
        
        # Average True Range
        tr_sum = 0
        for i in range(-self.ATR_PERIOD, 0):
            high = self.highs[i]
            low = self.lows[i]
            prev_close = self.closes[i-1]
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_sum += tr
        atr = tr_sum / self.ATR_PERIOD
        
        # Calculate VAF ratio
        atr_pct = (atr / self.closes[-1]) * 100 if self.closes[-1] > 0 else 0.0001
        vaf_ratio = abs(roc) / atr_pct if atr_pct > 0 else 0
        
        # Normalize to 0-100 (VAF > 3 is extreme)
        normalized = min(100, max(0, vaf_ratio / 3 * 100))
        
        return {
            "roc": round(roc, 3),
            "atr": round(atr, 4),
            "atr_pct": round(atr_pct, 3),
            "vaf_ratio": round(vaf_ratio, 3),
            "normalized": round(normalized, 2)
        }
    
    def calculate_svp(self) -> dict:
        """
        SVP - Surveillance Volume Proxy.
        
        Detects volume anomalies (spikes) that often precede reversals.
        SVP = Current Volume / SMA(Volume)
        
        Returns normalized score 0-100.
        """
        if len(self.volumes) < self.VOLUME_PERIOD:
            return {"ratio": 1, "normalized": 50}
        
        recent = self.volumes[-self.VOLUME_PERIOD:]
        vol_sma = sum(recent) / len(recent)
        
        current_vol = self.volumes[-1]
        vol_ratio = current_vol / vol_sma if vol_sma > 0 else 1
        
        # Normalize: Ratio of 2+ = 100%, Ratio of 0.5 = 25%
        normalized = min(100, max(0, vol_ratio / 2 * 100))
        
        return {
            "current_vol": current_vol,
            "avg_vol": round(vol_sma, 2),
            "ratio": round(vol_ratio, 3),
            "normalized": round(normalized, 2),
            "is_spike": vol_ratio > 1.5
        }
    
    def get_aexi_score(self) -> dict:
        """
        Composite AEXI Score.
        
        AEXI = (0.4 × EXH) + (0.3 × VAF) + (0.3 × SVP)
        
        Returns:
            dict: {score, signal, components}
        """
        exh = self.calculate_exh()
        vaf = self.calculate_vaf()
        svp = self.calculate_svp()
        
        # Weighted composite
        aexi_score = (
            0.4 * exh['normalized'] +
            0.3 * vaf['normalized'] +
            0.3 * svp['normalized']
        )
        
        # Determine signal
        signal = "NEUTRAL"
        direction = "NONE"
        
        if aexi_score >= self.SIGNAL_THRESHOLD:
            if exh['signal'] == "OVERBOUGHT":
                signal = "REVERSAL_DOWN"
                direction = "SHORT"
            elif exh['signal'] == "OVERSOLD":
                signal = "REVERSAL_UP"
                direction = "LONG"
            else:
                signal = "HIGH_EXHAUSTION"
        
        return {
            "score": round(aexi_score, 2),
            "signal": signal,
            "direction": direction,
            "is_triggered": aexi_score >= self.SIGNAL_THRESHOLD,
            "threshold": self.SIGNAL_THRESHOLD,
            "components": {
                "exh": exh,
                "vaf": vaf,
                "svp": svp
            }
        }

