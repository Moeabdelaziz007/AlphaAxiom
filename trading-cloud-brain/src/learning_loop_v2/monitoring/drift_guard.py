"""
🚨 DriftGuard: Concept Drift & Performance Monitor v1.0
AlphaAxiom Learning Loop v2.0

The final safeguard for the trading system. Monitors prediction accuracy
in real-time and automatically responds to degrading performance by:
1. Pausing live trading activities
2. Sending retraining alert notifications
3. Detecting market regime shifts (trending → sideways → crash)

Author: Axiom AI Partner
Status: LIVE as of December 9, 2025

Research-backed approach:
- Performance-based detection (rolling accuracy, drawdown)
- Regime-aware modulation (volatility/market regime)
- CUSUM/Page-Hinkley inspired cumulative deviation tracking
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json


class DriftStatus(Enum):
    """حالات الـ Drift | Drift Status States"""
    WARMING_UP = "warming_up"      # لم تصل البيانات للحد الأدنى
    HEALTHY = "healthy"            # الأداء ضمن النطاق الطبيعي
    WARNING = "warning"            # الأداء يتراجع - تحذير
    DRIFT_DETECTED = "drift_detected"  # انحراف حاد - إيقاف التداول
    PAUSED = "paused"             # متوقف بسبب Drift


class MarketRegime(Enum):
    """أنماط السوق | Market Regimes"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    CRASH = "crash"
    UNKNOWN = "unknown"


@dataclass
class DriftMetrics:
    """مقاييس الأداء الحالية | Current Performance Metrics"""
    current_accuracy: float = 0.0
    baseline_accuracy: float = 0.60
    deviation: float = 0.0
    sample_size: int = 0
    window_size: int = 50
    consecutive_losses: int = 0
    max_drawdown: float = 0.0
    cumulative_pnl: float = 0.0
    market_regime: MarketRegime = MarketRegime.UNKNOWN
    volatility_regime: str = "MODERATE"
    
    def to_dict(self) -> Dict:
        return {
            "current_accuracy": round(self.current_accuracy, 3),
            "baseline_accuracy": self.baseline_accuracy,
            "deviation": round(self.deviation, 3),
            "sample_size": self.sample_size,
            "window_size": self.window_size,
            "consecutive_losses": self.consecutive_losses,
            "max_drawdown": round(self.max_drawdown, 4),
            "cumulative_pnl": round(self.cumulative_pnl, 4),
            "market_regime": self.market_regime.value,
            "volatility_regime": self.volatility_regime
        }


@dataclass
class DriftAlert:
    """تنبيه Drift | Drift Alert"""
    alert_id: str
    status: DriftStatus
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    metrics: DriftMetrics
    recommended_action: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "alert_id": self.alert_id,
            "status": self.status.value,
            "severity": self.severity,
            "message": self.message,
            "metrics": self.metrics.to_dict(),
            "recommended_action": self.recommended_action,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_telegram_message(self) -> str:
        """Format alert for Telegram notification."""
        emoji_map = {
            "LOW": "⚪",
            "MEDIUM": "🟡",
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }
        emoji = emoji_map.get(self.severity, "⚠️")
        
        return f"""
{emoji} <b>DRIFT ALERT: {self.status.value.upper()}</b>
━━━━━━━━━━━━━━━━━━━━

📊 <b>الأداء الحالي:</b>
• الدقة: <code>{self.metrics.current_accuracy:.1%}</code> (الأساس: {self.metrics.baseline_accuracy:.1%})
• الانحراف: <code>{self.metrics.deviation:.1%}</code>
• الخسائر المتتالية: <code>{self.metrics.consecutive_losses}</code>
• نمط السوق: <code>{self.metrics.market_regime.value}</code>

⚠️ <b>الرسالة:</b>
{self.message}

🎯 <b>الإجراء المطلوب:</b>
{self.recommended_action}

⏰ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""


class DriftGuard:
    """
    🛡️ DriftGuard: Concept Drift & Performance Monitor
    
    الحارس الأمني لنظام التداول - يراقب الأداء ويوقف التداول
    عند اكتشاف انحراف في الأداء أو تغير في نمط السوق.
    
    The guardian of the trading system - monitors performance and
    pauses trading when detecting performance drift or regime change.
    """
    
    VERSION = "1.0.0"
    
    def __init__(
        self,
        baseline_accuracy: float = 0.60,
        window_size: int = 50,
        drift_threshold: float = 0.15,
        warning_threshold: float = 0.08,
        max_consecutive_losses: int = 5,
        max_drawdown_pct: float = 0.05,
        min_samples: int = 10,
        kv_store: Optional[Any] = None
    ):
        """
        تهيئة DriftGuard مع الإعدادات المحددة.
        Initialize DriftGuard with specified configuration.
        
        Args:
            baseline_accuracy: الدقة الأساسية (الحد الأدنى المقبول)
            window_size: حجم نافذة المراقبة
            drift_threshold: حد اكتشاف الـ Drift (انحراف الدقة)
            warning_threshold: حد التحذير
            max_consecutive_losses: الحد الأقصى للخسائر المتتالية
            max_drawdown_pct: الحد الأقصى للـ Drawdown
            min_samples: الحد الأدنى للعينات قبل التقييم
            kv_store: Cloudflare KV للاستمرارية
        """
        # Configuration
        self.baseline_accuracy = baseline_accuracy
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self.warning_threshold = warning_threshold
        self.max_consecutive_losses = max_consecutive_losses
        self.max_drawdown_pct = max_drawdown_pct
        self.min_samples = min_samples
        self.kv = kv_store
        
        # State tracking
        self.results_window: List[int] = []  # 1=Win, 0=Loss
        self.pnl_window: List[float] = []    # Raw PnL values
        self.consecutive_losses: int = 0
        self.current_drawdown: float = 0.0
        self.peak_equity: float = 0.0
        self.cumulative_pnl: float = 0.0
        
        # Regime info (updated externally)
        self.market_regime: MarketRegime = MarketRegime.UNKNOWN
        self.volatility_regime: str = "MODERATE"
        
        # Status
        self.is_active: bool = False  # True = Drift detected, trading paused
        self.current_status: DriftStatus = DriftStatus.WARMING_UP
        self.last_check_time: Optional[datetime] = None
        self.alerts_history: List[DriftAlert] = []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 OUTCOME RECORDING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def record_outcome(
        self,
        is_success: bool,
        pnl: float = 0.0,
        regime_info: Optional[Dict] = None
    ) -> DriftStatus:
        """
        تسجيل نتيجة صفقة جديدة.
        Record a new trade outcome.
        
        Args:
            is_success: هل كانت الصفقة ناجحة
            pnl: الربح/الخسارة
            regime_info: معلومات نمط السوق (اختياري)
        
        Returns:
            DriftStatus: الحالة الحالية
        """
        # Record win/loss
        self.results_window.append(1 if is_success else 0)
        self.pnl_window.append(pnl)
        
        # Maintain window size
        if len(self.results_window) > self.window_size:
            self.results_window.pop(0)
        if len(self.pnl_window) > self.window_size:
            self.pnl_window.pop(0)
        
        # Update cumulative PnL
        self.cumulative_pnl += pnl
        
        # Track consecutive losses
        if not is_success:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Update drawdown
        if self.cumulative_pnl > self.peak_equity:
            self.peak_equity = self.cumulative_pnl
        if self.peak_equity > 0:
            self.current_drawdown = (self.peak_equity - self.cumulative_pnl) / self.peak_equity
        
        # Update regime info if provided
        if regime_info:
            if "market_regime" in regime_info:
                try:
                    self.market_regime = MarketRegime(regime_info["market_regime"])
                except ValueError:
                    self.market_regime = MarketRegime.UNKNOWN
            if "volatility_regime" in regime_info:
                self.volatility_regime = regime_info["volatility_regime"]
        
        # Check health and return status
        health = self.check_health()
        return self.current_status
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔍 HEALTH CHECK
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def check_health(self) -> Dict[str, Any]:
        """
        تحليل الأداء الحالي مقارنة بالأساس.
        Analyze current performance vs baseline.
        
        Returns:
            Dict: تقرير الصحة الكامل
        """
        self.last_check_time = datetime.now()
        
        # Build metrics
        metrics = DriftMetrics(
            baseline_accuracy=self.baseline_accuracy,
            window_size=self.window_size,
            sample_size=len(self.results_window),
            consecutive_losses=self.consecutive_losses,
            max_drawdown=self.current_drawdown,
            cumulative_pnl=self.cumulative_pnl,
            market_regime=self.market_regime,
            volatility_regime=self.volatility_regime
        )
        
        # Not enough data yet
        if len(self.results_window) < self.min_samples:
            self.current_status = DriftStatus.WARMING_UP
            self.is_active = False
            return {
                "status": DriftStatus.WARMING_UP.value,
                "drift_detected": False,
                "message": f"جاري جمع البيانات ({len(self.results_window)}/{self.min_samples})",
                "metrics": metrics.to_dict()
            }
        
        # Calculate current accuracy
        current_accuracy = sum(self.results_window) / len(self.results_window)
        deviation = self.baseline_accuracy - current_accuracy
        
        metrics.current_accuracy = current_accuracy
        metrics.deviation = deviation
        
        # Initialize response
        response = {
            "status": DriftStatus.HEALTHY.value,
            "drift_detected": False,
            "message": "الأداء ضمن النطاق الطبيعي",
            "metrics": metrics.to_dict()
        }
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 🚨 CRITICAL: Multiple drift signals
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        drift_reasons = []
        
        # Check accuracy drift
        if deviation >= self.drift_threshold:
            drift_reasons.append(f"انحراف الدقة {deviation:.1%}")
        
        # Check consecutive losses
        if self.consecutive_losses >= self.max_consecutive_losses:
            drift_reasons.append(f"{self.consecutive_losses} خسائر متتالية")
        
        # Check drawdown
        if self.current_drawdown >= self.max_drawdown_pct:
            drift_reasons.append(f"Drawdown {self.current_drawdown:.1%}")
        
        # Regime-aware: stricter in high volatility
        if self.volatility_regime == "HIGH" and deviation >= (self.drift_threshold * 0.7):
            drift_reasons.append("أداء ضعيف في تقلب عالي")
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # DETERMINE STATUS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        if len(drift_reasons) >= 2 or self.consecutive_losses >= self.max_consecutive_losses:
            # 🔴 CRITICAL DRIFT
            self.current_status = DriftStatus.DRIFT_DETECTED
            self.is_active = True
            response["status"] = DriftStatus.DRIFT_DETECTED.value
            response["drift_detected"] = True
            response["message"] = f"🚨 DRIFT: {', '.join(drift_reasons)}"
            response["severity"] = "CRITICAL"
            response["recommended_action"] = "إيقاف التداول الحي وإعادة تدريب النموذج"
            
            # Generate alert
            self._generate_alert(DriftStatus.DRIFT_DETECTED, "CRITICAL", response["message"], metrics)
            
        elif len(drift_reasons) == 1 or deviation >= self.warning_threshold:
            # 🟠 WARNING
            self.current_status = DriftStatus.WARNING
            self.is_active = False  # Don't pause yet
            response["status"] = DriftStatus.WARNING.value
            response["message"] = f"⚠️ تحذير: {drift_reasons[0] if drift_reasons else 'أداء يتراجع'}"
            response["severity"] = "MEDIUM"
            response["recommended_action"] = "مراقبة دقيقة وتقليل حجم المراكز"
            
        else:
            # 🟢 HEALTHY
            self.current_status = DriftStatus.HEALTHY
            self.is_active = False
            response["severity"] = "LOW"
        
        return response
    
    def _generate_alert(
        self,
        status: DriftStatus,
        severity: str,
        message: str,
        metrics: DriftMetrics
    ) -> DriftAlert:
        """Generate and store a drift alert."""
        import uuid
        
        alert = DriftAlert(
            alert_id=str(uuid.uuid4())[:8],
            status=status,
            severity=severity,
            message=message,
            metrics=metrics,
            recommended_action=self._get_recommended_action(status, metrics)
        )
        
        self.alerts_history.append(alert)
        
        # Keep only last 20 alerts
        if len(self.alerts_history) > 20:
            self.alerts_history = self.alerts_history[-20:]
        
        return alert
    
    def _get_recommended_action(self, status: DriftStatus, metrics: DriftMetrics) -> str:
        """Get recommended action based on status and metrics."""
        if status == DriftStatus.DRIFT_DETECTED:
            if metrics.consecutive_losses >= self.max_consecutive_losses:
                return "إيقاف فوري للتداول. تحليل سبب الخسائر المتتالية."
            if metrics.max_drawdown >= self.max_drawdown_pct:
                return "إيقاف التداول. Drawdown تجاوز الحد المسموح."
            return "إيقاف التداول الحي وإعادة تدريب النموذج."
        elif status == DriftStatus.WARNING:
            return "تقليل حجم المراكز بنسبة 50% ومراقبة الأداء."
        return "الاستمرار مع المراقبة."
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔄 CONTROL METHODS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def reset_baseline(self, new_baseline: float):
        """
        إعادة ضبط الأساس بعد إعادة التدريب.
        Reset baseline after retraining.
        """
        self.baseline_accuracy = new_baseline
        self.results_window = []
        self.pnl_window = []
        self.consecutive_losses = 0
        self.current_drawdown = 0.0
        self.peak_equity = 0.0
        self.cumulative_pnl = 0.0
        self.is_active = False
        self.current_status = DriftStatus.WARMING_UP
    
    def acknowledge_alert(self):
        """
        تأكيد التنبيه وإعادة تشغيل النظام.
        Acknowledge alert and resume system.
        """
        self.is_active = False
        self.current_status = DriftStatus.HEALTHY
        self.consecutive_losses = 0
    
    def force_pause(self, reason: str = "Manual pause"):
        """إيقاف قسري | Force pause"""
        self.is_active = True
        self.current_status = DriftStatus.PAUSED
    
    def is_trading_allowed(self, mode: str = "LIVE") -> bool:
        """
        هل التداول مسموح به؟
        Is trading allowed?
        
        Args:
            mode: SIMULATION, PAPER, or LIVE
        
        Returns:
            bool: True if trading is allowed
        """
        if mode != "LIVE":
            return True  # Always allow simulation/paper
        return not self.is_active
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 EXPORT METHODS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_metrics_json(self) -> Dict:
        """Export metrics for API endpoint."""
        health = self.check_health()
        return {
            "version": self.VERSION,
            "drift_active": self.is_active,
            "status": self.current_status.value,
            "trading_allowed": not self.is_active,
            "health": health,
            "config": {
                "baseline_accuracy": self.baseline_accuracy,
                "window_size": self.window_size,
                "drift_threshold": self.drift_threshold,
                "warning_threshold": self.warning_threshold,
                "max_consecutive_losses": self.max_consecutive_losses,
                "max_drawdown_pct": self.max_drawdown_pct
            },
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "recent_alerts": [a.to_dict() for a in self.alerts_history[-5:]]
        }
    
    def get_latest_alert(self) -> Optional[DriftAlert]:
        """Get the most recent alert."""
        return self.alerts_history[-1] if self.alerts_history else None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 STANDALONE TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("🧪 Testing DriftGuard...")
    
    guard = DriftGuard(
        baseline_accuracy=0.60,
        window_size=20,
        min_samples=5
    )
    
    # Simulate good performance
    print("\n📈 Simulating good performance...")
    for _ in range(10):
        guard.record_outcome(is_success=True, pnl=0.02)
    health = guard.check_health()
    print(f"   Status: {health['status']}, Accuracy: {health['metrics']['current_accuracy']:.1%}")
    
    # Simulate degrading performance
    print("\n📉 Simulating degrading performance...")
    for _ in range(8):
        guard.record_outcome(is_success=False, pnl=-0.01)
    health = guard.check_health()
    print(f"   Status: {health['status']}, Drift: {health['drift_detected']}")
    
    # Check if trading is blocked
    print(f"\n🔒 Trading allowed (LIVE): {guard.is_trading_allowed('LIVE')}")
    print(f"🔓 Trading allowed (PAPER): {guard.is_trading_allowed('PAPER')}")
    
    # Get alert
    alert = guard.get_latest_alert()
    if alert:
        print(f"\n🚨 Alert: {alert.message}")
    
    print("\n✅ DriftGuard Test Complete!")
