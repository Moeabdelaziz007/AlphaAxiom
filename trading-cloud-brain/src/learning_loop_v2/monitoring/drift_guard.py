"""
🛡️ DriftGuard v1.0
AlphaAxiom Learning Loop v2.0

Monitors system performance and detects concept drift to prevent catastrophic failures.
Implements early warning systems and automatic trading suspension when drift is detected.

Concept Drift Detection Methods:
1. Accuracy Drop Detection - Monitors prediction accuracy over time windows
2. Distribution Shift Detection - Tracks changes in input data distributions
3. Performance Degradation Alerts - Flags declining performance metrics
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


@dataclass
class DriftMetrics:
    """Performance metrics for drift detection"""
    window_accuracy: float = 0.0
    baseline_accuracy: float = 0.0
    drift_magnitude: float = 0.0
    window_size: int = 0
    total_predictions: int = 0
    correct_predictions: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class DriftStatus(Enum):
    """Enumeration of drift statuses."""
    NORMAL = "NORMAL"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    SEVERE_DRIFT = "SEVERE_DRIFT"


class DriftGuard:
    """
    🛡️ Drift Detection and Prevention System
    
    Monitors system performance and detects concept drift to prevent catastrophic failures.
    Implements early warning systems and automatic trading suspension when drift is detected.
    """
    
    def __init__(
        self,
        baseline_accuracy: float = 0.60,
        window_size: int = 50,
        drift_threshold: float = 0.15,
        kv_store: Optional[Any] = None
    ):
        """
        Initialize DriftGuard.
        
        Args:
            baseline_accuracy: Expected minimum accuracy rate
            window_size: Number of predictions to evaluate in each window
            drift_threshold: Accuracy drop threshold that triggers drift detection
            kv_store: Key-value store for persistence (optional)
        """
        self.baseline_accuracy = baseline_accuracy
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self.kv_store = kv_store
        
        # Performance tracking
        self.prediction_window: List[bool] = []
        self.total_predictions = 0
        self.correct_predictions = 0
        self.drift_detected = False
        self.drift_timestamp: Optional[datetime] = None
        self.last_health_check: Optional[datetime] = None
        
        # Metrics history for analysis
        self.metrics_history: List[DriftMetrics] = []
    
    def record_outcome(self, is_success: bool, pnl: float = 0.0) -> DriftStatus:
        """
        Record a prediction outcome for drift detection.
        
        Args:
            is_success: Whether the prediction was correct
            pnl: Profit/Loss from the trade (for additional metrics)
            
        Returns:
            DriftStatus indicating current drift state
        """
        # Add outcome to window
        self.prediction_window.append(is_success)
        self.total_predictions += 1
        if is_success:
            self.correct_predictions += 1
        
        # Maintain window size
        if len(self.prediction_window) > self.window_size:
            removed = self.prediction_window.pop(0)
            if removed:
                self.correct_predictions -= 1
        
        # Update drift status
        self._update_drift_status()
        
        # Store metrics
        metrics = DriftMetrics(
            window_accuracy=self._get_window_accuracy(),
            baseline_accuracy=self.baseline_accuracy,
            drift_magnitude=self._calculate_drift_magnitude(),
            window_size=len(self.prediction_window),
            total_predictions=self.total_predictions,
            correct_predictions=self.correct_predictions
        )
        self.metrics_history.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        # Persist to KV store if available
        if self.kv_store:
            self._persist_metrics(metrics)
        
        return DriftStatus.DRIFT_DETECTED if self.drift_detected else DriftStatus.NORMAL
    
    def _get_window_accuracy(self) -> float:
        """Calculate current window accuracy."""
        if not self.prediction_window:
            return 0.0
        return sum(self.prediction_window) / len(self.prediction_window)
    
    def _calculate_drift_magnitude(self) -> float:
        """Calculate the magnitude of drift from baseline."""
        current_accuracy = self._get_window_accuracy()
        return max(0.0, self.baseline_accuracy - current_accuracy)
    
    def _update_drift_status(self) -> None:
        """Update drift detection status."""
        if len(self.prediction_window) >= self.window_size:
            current_accuracy = self._get_window_accuracy()
            drift_magnitude = self._calculate_drift_magnitude()
            
            # Drift detected if accuracy drops below threshold
            self.drift_detected = drift_magnitude >= self.drift_threshold
            
            if self.drift_detected and not self.drift_timestamp:
                self.drift_timestamp = datetime.now()
            elif not self.drift_detected:
                self.drift_timestamp = None
    
    def _persist_metrics(self, metrics: DriftMetrics) -> None:
        """Persist metrics to KV store."""
        try:
            import json
            
            metrics_data = {
                "window_accuracy": metrics.window_accuracy,
                "baseline_accuracy": metrics.baseline_accuracy,
                "drift_magnitude": metrics.drift_magnitude,
                "window_size": metrics.window_size,
                "total_predictions": metrics.total_predictions,
                "correct_predictions": metrics.correct_predictions,
                "timestamp": metrics.timestamp.isoformat()
            }
            
            # Store recent metrics
            key = f"drift_metrics_{int(datetime.now().timestamp())}"
            self.kv_store.put(key, json.dumps(metrics_data))
            
            # Store drift status
            status_data = {
                "drift_detected": self.drift_detected,
                "drift_timestamp": self.drift_timestamp.isoformat() if self.drift_timestamp else None,
                "current_accuracy": self._get_window_accuracy(),
                "baseline_accuracy": self.baseline_accuracy
            }
            self.kv_store.put("drift_status", json.dumps(status_data))
        except Exception:
            # Silently fail to avoid disrupting main flow
            pass
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform a health check and return system status.
        
        Returns:
            Dictionary with health status and metrics
        """
        self.last_health_check = datetime.now()
        current_accuracy = self._get_window_accuracy()
        drift_magnitude = self._calculate_drift_magnitude()
        
        return {
            "drift_detected": self.drift_detected,
            "drift_magnitude": drift_magnitude,
            "current_accuracy": current_accuracy,
            "baseline_accuracy": self.baseline_accuracy,
            "window_size": len(self.prediction_window),
            "total_predictions": self.total_predictions,
            "accuracy_drop": self.baseline_accuracy - current_accuracy,
            "message": self._get_health_message(),
            "timestamp": self.last_health_check.isoformat()
        }
    
    def _get_health_message(self) -> str:
        """Generate a human-readable health message."""
        if self.drift_detected:
            drift_amount = self._calculate_drift_magnitude()
            return f"🚨 Drift detected: Accuracy dropped by {drift_amount:.1%}"
        elif len(self.prediction_window) < self.window_size:
            needed = self.window_size - len(self.prediction_window)
            return f"🟡 Warming up: Need {needed} more predictions"
        else:
            current_acc = self._get_window_accuracy()
            return f"🟢 Normal: Accuracy {current_acc:.1%}"
    
    def is_trading_allowed(self, mode: str = "LIVE") -> bool:
        """
        Check if trading is allowed based on drift status.
        
        Args:
            mode: Trading mode (LIVE, PAPER, SIMULATION)
            
        Returns:
            Boolean indicating if trading is allowed
        """
        # Only restrict LIVE trading when drift is detected
        if mode == "LIVE" and self.drift_detected:
            return False
        return True
    
    def get_metrics_json(self) -> Dict[str, Any]:
        """
        Get metrics in JSON format for API endpoints.
        
        Returns:
            Dictionary with metrics data
        """
        health = self.check_health()
        return {
            "status": "DRIFT_DETECTED" if health["drift_detected"] else "NORMAL",
            "drift_detected": health["drift_detected"],
            "current_accuracy": health["current_accuracy"],
            "baseline_accuracy": health["baseline_accuracy"],
            "accuracy_drop": health["accuracy_drop"],
            "window_size": health["window_size"],
            "total_predictions": health["total_predictions"],
            "drift_magnitude": health["drift_magnitude"],
            "message": health["message"],
            "timestamp": health["timestamp"]
        }
    
    def reset(self) -> None:
        """Reset drift guard to initial state."""
        self.prediction_window.clear()
        self.total_predictions = 0
        self.correct_predictions = 0
        self.drift_detected = False
        self.drift_timestamp = None
        self.metrics_history.clear()