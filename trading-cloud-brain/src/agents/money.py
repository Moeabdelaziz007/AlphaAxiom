# ========================================
# 💰 AXIOM MONEY AGENT - Risk Management
# ========================================
# Ported from Mini-Aladdin RiskAgent (JavaScript)
# Enhanced with D1 Learning Loop integration
# ========================================
# Capabilities:
#   - Trade Risk Assessment
#   - Position Sizing (ATR-based)
#   - Stop Loss Calculation
#   - Portfolio Diversification Analysis
#   - Historical Accuracy Integration (D1)
# ========================================

import math
from typing import List, Dict, Any, Optional


class MoneyAgent:
    """
    Risk Management Agent - "The Guardian of Capital".
    
    Ported from Mini-Aladdin's RiskAgent with:
    - Python optimizations
    - D1 database integration for historical learning
    - Enhanced position sizing
    """
    
    def __init__(self, max_risk_percent: float = 2.0):
        """
        Initialize MoneyAgent.
        
        Args:
            max_risk_percent: Maximum risk per trade (default 2%)
        """
        self.name = "MoneyAgent"
        self.specialty = "Risk Assessment & Position Sizing"
        self.max_risk_percent = max_risk_percent
    
    # ========================================
    # ⚖️ Trade Risk Assessment
    # ========================================
    
    def assess_risk(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any],
        historical_accuracy: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive trade risk assessment.
        
        Args:
            trade: Trade details (symbol, price, volatility, leverage, etc.)
            portfolio: Portfolio state (total_value, positions, etc.)
            historical_accuracy: Optional accuracy from Learning Loop (0-100)
        
        Returns:
            Risk assessment with approval status and recommendations
        """
        risk_score = self._calculate_risk_score(trade, portfolio)
        position_size = self._calculate_position_size(trade, portfolio)
        stop_loss = self._calculate_stop_loss(trade)
        
        # Learning Loop integration: reject low-accuracy signals
        learning_rejection = False
        if historical_accuracy is not None and historical_accuracy < 45:
            learning_rejection = True
            risk_score = min(100, risk_score + 30)  # Penalize heavily
        
        # Approval decision
        approved = risk_score < 70 and not learning_rejection
        
        return {
            "risk_score": risk_score,
            "risk_level": self._get_risk_level(risk_score),
            "approved": approved,
            "position_size": position_size,
            "stop_loss_percent": stop_loss,
            "max_loss": position_size * (stop_loss / 100),
            "recommendation": self._get_recommendation(risk_score, learning_rejection),
            "learning_blocked": learning_rejection,
            "historical_accuracy": historical_accuracy
        }
    
    def _calculate_risk_score(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any]
    ) -> float:
        """
        Calculate risk score (0-100).
        Higher = more risky.
        """
        score = 0.0
        
        # 1. Volatility Risk (0-25 points)
        volatility = trade.get("volatility", 0.02)
        if volatility > 0.05:
            score += 25
        elif volatility > 0.03:
            score += 15
        elif volatility > 0.02:
            score += 10
        else:
            score += 5
        
        # 2. Liquidity Risk (0-20 points)
        volume = trade.get("volume", 10000000)
        if volume < 1000000:
            score += 20
        elif volume < 5000000:
            score += 15
        elif volume < 10000000:
            score += 10
        else:
            score += 5
        
        # 3. Leverage Risk (0-25 points)
        leverage = trade.get("leverage", 1)
        if leverage > 10:
            score += 25
        elif leverage > 5:
            score += 20
        elif leverage > 3:
            score += 15
        elif leverage > 1:
            score += 10
        else:
            score += 0
        
        # 4. Position Concentration Risk (0-15 points)
        total_value = portfolio.get("total_value", 10000)
        trade_value = trade.get("amount", 1000)
        concentration = (trade_value / total_value) * 100 if total_value > 0 else 100
        
        if concentration > 20:
            score += 15
        elif concentration > 10:
            score += 10
        elif concentration > 5:
            score += 5
        
        # 5. Market Condition Risk (0-15 points)
        market_condition = trade.get("market_condition", "normal")
        if market_condition == "extreme_volatility":
            score += 15
        elif market_condition == "trending":
            score += 5
        elif market_condition == "ranging":
            score += 10
        
        return min(100, score)
    
    def _calculate_position_size(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any]
    ) -> float:
        """
        Calculate optimal position size based on risk tolerance.
        
        Uses ATR-based position sizing when available.
        """
        total_value = portfolio.get("total_value", 10000)
        risk_amount = total_value * (self.max_risk_percent / 100)
        
        # ATR-based sizing if available
        atr = trade.get("atr")
        price = trade.get("price", 100)
        
        if atr and atr > 0:
            # Position size = Risk Amount / ATR
            position_size = risk_amount / atr
        else:
            # Default: use stop loss percentage
            stop_loss_percent = trade.get("stop_loss_percent", 5)
            position_size = (risk_amount / stop_loss_percent) * 100
        
        # Ensure position doesn't exceed portfolio
        max_position = total_value * 0.25  # Max 25% in one position
        return min(position_size, max_position)
    
    def _calculate_stop_loss(self, trade: Dict[str, Any]) -> float:
        """
        Calculate stop loss percentage.
        
        Uses ATR when available, otherwise defaults based on asset type.
        """
        atr = trade.get("atr")
        price = trade.get("price", 100)
        
        if atr and price > 0:
            # 2x ATR stop loss
            return (atr * 2 / price) * 100
        
        # Default stop losses by asset type
        asset_type = trade.get("asset_type", "stock")
        defaults = {
            "crypto": 5.0,   # 5% for crypto
            "forex": 2.0,    # 2% for forex
            "stock": 3.0,    # 3% for stocks
            "index": 2.5     # 2.5% for indices
        }
        
        return defaults.get(asset_type, 3.0)
    
    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to level."""
        if score < 30:
            return "LOW"
        elif score < 50:
            return "MEDIUM"
        elif score < 70:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _get_recommendation(
        self,
        score: float,
        learning_blocked: bool
    ) -> str:
        """Generate human-readable recommendation."""
        if learning_blocked:
            return "❌ REJECT - Historical accuracy too low (Learning Loop)"
        
        if score < 30:
            return "✅ Execute with standard position size"
        elif score < 50:
            return "⚠️ Reduce position size by 25%"
        elif score < 70:
            return "⚠️ Reduce position size by 50%"
        else:
            return "❌ REJECT - Risk too high"
    
    # ========================================
    # 📊 Portfolio Diversification
    # ========================================
    
    def analyze_diversification(
        self,
        positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze portfolio diversification.
        
        Args:
            positions: List of positions with 'asset' and 'value' keys
        
        Returns:
            Diversification analysis
        """
        if not positions:
            return {
                "num_assets": 0,
                "diversification_score": 0,
                "is_well_diversified": False,
                "recommendation": "Portfolio is empty"
            }
        
        values = [p.get("value", 0) for p in positions]
        total = sum(values)
        
        if total == 0:
            return {
                "num_assets": len(positions),
                "diversification_score": 0,
                "is_well_diversified": False,
                "recommendation": "Portfolio has no value"
            }
        
        # Herfindahl-Hirschman Index (concentration)
        hhi = sum((v / total) ** 2 for v in values)
        
        # Diversification score (0 = concentrated, 100 = diversified)
        diversification_score = (1 - hhi) * 100
        
        # Find largest position
        max_concentration = max((v / total) * 100 for v in values)
        
        is_diversified = diversification_score > 60 and max_concentration < 30
        
        return {
            "num_assets": len(positions),
            "concentration_index": hhi,
            "diversification_score": diversification_score,
            "is_well_diversified": is_diversified,
            "largest_position_percent": max_concentration,
            "recommendation": self._diversification_recommendation(
                diversification_score, max_concentration
            )
        }
    
    def _diversification_recommendation(
        self,
        score: float,
        max_concentration: float
    ) -> str:
        """Generate diversification recommendation."""
        if score > 70 and max_concentration < 25:
            return "✅ Portfolio is well diversified"
        elif score > 50:
            return "⚠️ Consider adding more assets"
        else:
            return "❌ Too concentrated - reduce largest positions"
    
    # ========================================
    # 🎯 Quick Risk Check
    # ========================================
    
    def quick_check(
        self,
        signal_direction: str,
        confidence: float,
        volatility: float = 0.03,
        historical_accuracy: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Quick risk check for a signal.
        
        Args:
            signal_direction: BUY, SELL, STRONG_BUY, etc.
            confidence: Signal confidence (0-1)
            volatility: Current volatility
            historical_accuracy: From Learning Loop (0-100)
        
        Returns:
            Quick approval decision
        """
        # Base approval on confidence
        approved = confidence >= 0.6
        
        # Reduce confidence if volatile
        if volatility > 0.05:
            approved = confidence >= 0.75
        
        # Learning Loop override
        if historical_accuracy is not None and historical_accuracy < 45:
            approved = False
        
        # Position size multiplier
        if confidence >= 0.85:
            size_multiplier = 1.0
        elif confidence >= 0.7:
            size_multiplier = 0.75
        elif confidence >= 0.6:
            size_multiplier = 0.5
        else:
            size_multiplier = 0.25
        
        return {
            "approved": approved,
            "size_multiplier": size_multiplier,
            "reason": self._quick_reason(confidence, volatility, historical_accuracy, approved)
        }
    
    def _quick_reason(
        self,
        confidence: float,
        volatility: float,
        accuracy: Optional[float],
        approved: bool
    ) -> str:
        """Generate quick check reason."""
        if not approved:
            if accuracy is not None and accuracy < 45:
                return f"Historical accuracy too low ({accuracy:.1f}%)"
            if confidence < 0.6:
                return f"Confidence too low ({confidence*100:.0f}%)"
            return "High volatility + low confidence"
        
        if confidence >= 0.85:
            return "High confidence - full position"
        elif confidence >= 0.7:
            return "Good confidence - 75% position"
        else:
            return "Moderate confidence - 50% position"


# ========================================
# 🏭 Factory Function
# ========================================

def get_money_agent(max_risk: float = 2.0) -> MoneyAgent:
    """Get MoneyAgent instance with custom risk tolerance."""
    return MoneyAgent(max_risk_percent=max_risk)


# ========================================
# 🧪 Quick Test
# ========================================

def test_money_agent():
    """Test MoneyAgent functionality."""
    agent = MoneyAgent()
    
    # Test risk assessment
    trade = {
        "symbol": "BTCUSDT",
        "price": 45000,
        "volatility": 0.03,
        "leverage": 1,
        "volume": 50000000,
        "asset_type": "crypto"
    }
    
    portfolio = {
        "total_value": 10000,
        "positions": []
    }
    
    assessment = agent.assess_risk(trade, portfolio, historical_accuracy=55.0)
    
    # Test quick check
    quick = agent.quick_check("STRONG_BUY", 0.85, 0.03, 55.0)
    
    return {
        "assessment": {
            "risk_level": assessment["risk_level"],
            "approved": assessment["approved"],
            "position_size": round(assessment["position_size"], 2)
        },
        "quick_check": quick
    }
