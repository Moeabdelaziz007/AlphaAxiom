"""
🌀 Dream Machine Engine - Chaos Theory Market Analysis
The "Entropy Scanner" for detecting market structure breakdown.

FORMULA:
DREAM = (0.3 × Entropy) + (0.25 × Fractal) + (0.25 × Hurst) + (0.2 × VolDisp)

Components:
- Entropy: Shannon Entropy (market randomness/disorder)
- Fractal: Fractal Dimension approximation (pattern complexity)
- Hurst: Hurst Exponent (persistence/mean-reversion indicator)
- VolDisp: Volume Dispersion (Coefficient of Variation)

Signal Trigger: Dream > 70 indicates chaos/breakdown
"""

import math

class DreamMachine:
    """
    Chaos Theory Analysis for Market Structure.
    Detects when market is transitioning between order and chaos.
    """
    
    # Configuration
    LOOKBACK = 30         # Bars for analysis
    NUM_BINS = 10         # Bins for entropy discretization
    SIGNAL_THRESHOLD = 70 # DREAM > 70 = High Chaos
    
    def __init__(self, data: list):
        """
        :param data: List of dicts [{'close':.., 'volume':..}, ...]
        """
        self.data = data
        self.closes = [d['close'] for d in data]
        self.volumes = [d['volume'] for d in data]
        
        # Calculate returns for most indicators
        self.returns = []
        for i in range(1, len(self.closes)):
            ret = (self.closes[i] - self.closes[i-1]) / self.closes[i-1]
            self.returns.append(ret)
    
    def calculate_entropy(self) -> dict:
        """
        Shannon Entropy of price returns.
        
        H = -Σ P(xi) × log₂(P(xi))
        
        Higher entropy = more randomness/unpredictability.
        Returns normalized score 0-100.
        """
        if len(self.returns) < self.LOOKBACK:
            return {"raw": 0, "normalized": 50, "interpretation": "INSUFFICIENT_DATA"}
        
        recent_returns = self.returns[-self.LOOKBACK:]
        
        # Discretize into bins
        min_ret = min(recent_returns)
        max_ret = max(recent_returns)
        range_ret = max_ret - min_ret if max_ret != min_ret else 0.0001
        
        # Count occurrences in each bin
        bin_counts = [0] * self.NUM_BINS
        for ret in recent_returns:
            bin_idx = min(int((ret - min_ret) / range_ret * self.NUM_BINS), self.NUM_BINS - 1)
            bin_counts[bin_idx] += 1
        
        # Calculate probabilities and entropy
        n = len(recent_returns)
        entropy = 0.0
        for count in bin_counts:
            if count > 0:
                p = count / n
                entropy -= p * math.log2(p)
        
        # Maximum entropy for NUM_BINS = log2(NUM_BINS)
        max_entropy = math.log2(self.NUM_BINS)
        normalized = (entropy / max_entropy) * 100 if max_entropy > 0 else 50
        
        # Interpretation
        interpretation = "NORMAL"
        if normalized > 80:
            interpretation = "HIGH_CHAOS"
        elif normalized < 30:
            interpretation = "LOW_CHAOS"  # Ordered/trending
        
        return {
            "raw": round(entropy, 4),
            "max_possible": round(max_entropy, 4),
            "normalized": round(normalized, 2),
            "interpretation": interpretation
        }
    
    def calculate_fractal_dimension(self) -> dict:
        """
        Fractal Dimension approximation via Higuchi method (simplified).
        
        FD measures the complexity of the price curve.
        FD = 1 (straight line) to 2 (fills the plane).
        Typical market: 1.3 - 1.7
        
        Returns normalized score 0-100.
        """
        if len(self.closes) < self.LOOKBACK:
            return {"fd": 1.5, "normalized": 50}
        
        series = self.closes[-self.LOOKBACK:]
        n = len(series)
        
        # Simplified box-counting approximation
        # Count sign changes in returns as proxy for complexity
        sign_changes = 0
        for i in range(1, len(series) - 1):
            curr_ret = series[i] - series[i-1]
            next_ret = series[i+1] - series[i]
            if curr_ret * next_ret < 0:  # Direction change
                sign_changes += 1
        
        # More sign changes = higher fractal dimension
        max_changes = n - 2
        fd_approx = 1.0 + (sign_changes / max_changes) if max_changes > 0 else 1.5
        
        # Normalize: FD 1.0 = 0%, FD 2.0 = 100%
        normalized = (fd_approx - 1.0) * 100
        normalized = min(100, max(0, normalized))
        
        return {
            "fd": round(fd_approx, 4),
            "sign_changes": sign_changes,
            "normalized": round(normalized, 2)
        }
    
    def calculate_hurst_exponent(self) -> dict:
        """
        Hurst Exponent via simplified R/S Analysis.
        
        H > 0.5: Persistent (trending)
        H = 0.5: Random walk
        H < 0.5: Mean-reverting
        
        Returns normalized score 0-100 (inverted: higher = more chaotic).
        """
        if len(self.returns) < self.LOOKBACK:
            return {"H": 0.5, "behavior": "RANDOM", "normalized": 50}
        
        series = self.returns[-self.LOOKBACK:]
        n = len(series)
        
        # Mean-centered cumulative deviations
        mean = sum(series) / n
        deviations = [x - mean for x in series]
        cumsum = []
        running = 0
        for d in deviations:
            running += d
            cumsum.append(running)
        
        # R = max - min of cumulative deviations
        R = max(cumsum) - min(cumsum)
        
        # S = standard deviation
        variance = sum((x - mean) ** 2 for x in series) / n
        S = math.sqrt(variance) if variance > 0 else 0.0001
        
        # R/S ratio
        RS = R / S if S > 0 else 0
        
        # Estimate H: For a proper calculation, we'd need multiple subdivisions.
        # This is a simplified single-scale estimate.
        # H ≈ log(R/S) / log(n)
        H = math.log(RS) / math.log(n) if RS > 0 and n > 1 else 0.5
        H = min(1.0, max(0.0, H))
        
        # Behavior classification
        if H > 0.6:
            behavior = "TRENDING"
        elif H < 0.4:
            behavior = "MEAN_REVERTING"
        else:
            behavior = "RANDOM"
        
        # Normalize: H = 0.5 (random) = 50, extremes = 0 or 100
        # We want chaos indicator: random walks are most chaotic for traders
        # H = 0.5 = 100% chaos, H = 0 or 1 = 0% chaos
        distance_from_random = abs(H - 0.5)
        normalized = (1 - distance_from_random * 2) * 100
        normalized = min(100, max(0, normalized))
        
        return {
            "H": round(H, 4),
            "RS": round(RS, 4),
            "behavior": behavior,
            "normalized": round(normalized, 2)
        }
    
    def calculate_vol_dispersion(self) -> dict:
        """
        Volume Dispersion (Coefficient of Variation).
        
        CV = StdDev(Volume) / Mean(Volume)
        
        High dispersion = erratic volume = uncertain market.
        Returns normalized score 0-100.
        """
        if len(self.volumes) < self.LOOKBACK:
            return {"cv": 0, "normalized": 50}
        
        recent = self.volumes[-self.LOOKBACK:]
        mean = sum(recent) / len(recent)
        
        if mean <= 0:
            return {"cv": 0, "normalized": 50}
        
        variance = sum((v - mean) ** 2 for v in recent) / len(recent)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean  # Coefficient of Variation
        
        # Normalize: CV of 1 = 100% (very dispersed)
        normalized = min(100, cv * 100)
        
        return {
            "cv": round(cv, 4),
            "std_dev": round(std_dev, 2),
            "mean_vol": round(mean, 2),
            "normalized": round(normalized, 2)
        }
    
    def get_dream_score(self) -> dict:
        """
        Composite DREAM Score.
        
        DREAM = (0.3 × Entropy) + (0.25 × Fractal) + (0.25 × Hurst) + (0.2 × VolDisp)
        
        Returns:
            dict: {score, signal, components}
        """
        entropy = self.calculate_entropy()
        fractal = self.calculate_fractal_dimension()
        hurst = self.calculate_hurst_exponent()
        vol_disp = self.calculate_vol_dispersion()
        
        # Weighted composite
        dream_score = (
            0.30 * entropy['normalized'] +
            0.25 * fractal['normalized'] +
            0.25 * hurst['normalized'] +
            0.20 * vol_disp['normalized']
        )
        
        # Determine market regime
        if dream_score >= 80:
            regime = "CHAOS"
            signal = "AVOID_TRADING"
        elif dream_score >= self.SIGNAL_THRESHOLD:
            regime = "UNSTABLE"
            signal = "CAUTION"
        elif dream_score <= 30:
            regime = "ORDERED"
            signal = "TREND_FOLLOW"
        else:
            regime = "NORMAL"
            signal = "NEUTRAL"
        
        return {
            "score": round(dream_score, 2),
            "regime": regime,
            "signal": signal,
            "is_chaotic": dream_score >= self.SIGNAL_THRESHOLD,
            "threshold": self.SIGNAL_THRESHOLD,
            "components": {
                "entropy": entropy,
                "fractal": fractal,
                "hurst": hurst,
                "vol_dispersion": vol_disp
            }
        }

