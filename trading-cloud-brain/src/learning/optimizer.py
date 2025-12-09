# ========================================
# 🧬 AXIOM DATA LEARNING LOOP - Weight Optimizer
# ========================================
# Phase 3: Weekly cron job to self-optimize signal weights
# Analyzes factor performance and adjusts weights with safeguards
# ========================================

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple


class WeightOptimizer:
    """
    Weekly cron job that:
    1. Analyzes last 30 days of signal performance
    2. Calculates accuracy for each factor (momentum, rsi, sentiment, volume)
    3. Adjusts weights based on performance with safety constraints
    4. Stores new weights in KV with versioning
    5. Sends optimization report via Telegram
    """
    
    # Safety constraints (from multi-AI synthesis)
    MAX_WEIGHT_CHANGE = 0.20   # Max 20% change per week
    MIN_WEIGHT = 0.05          # No factor below 5%
    MAX_WEIGHT = 0.50          # No factor above 50%
    
    # Accuracy thresholds
    ACCURACY_HIGH = 0.60       # Above 60% - increase weight
    ACCURACY_LOW = 0.40        # Below 40% - decrease weight
    
    # Adjustment multipliers
    INCREASE_MULTIPLIER = 1.10  # +10% for high performers
    DECREASE_MULTIPLIER = 0.90  # -10% for low performers
    
    # Minimum data requirements
    MIN_SIGNALS_FOR_OPTIMIZATION = 100
    
    # Default weights (now includes volatility from Manus enhancement)
    DEFAULT_WEIGHTS = {
        "momentum": 0.25,
        "rsi": 0.25,
        "sentiment": 0.20,
        "volume": 0.15,
        "volatility": 0.15  # New from Manus AI integration
    }
    
    # Kelly Criterion (Learning Loop 2.0)
    # Optimal position sizing fraction based on win rate
    DEFAULT_KELLY_FRACTION = 0.25  # Start with quarter Kelly (conservative)
    
    def __init__(self, env: Any):
        """Initialize with Cloudflare Worker environment bindings."""
        self.db = env.DB
        self.kv = env.BRAIN_MEMORY
        self.telegram_token = getattr(env, 'TELEGRAM_BOT_TOKEN', None)
        self.telegram_chat = getattr(env, 'TELEGRAM_CHAT_ID', None)
    
    async def run(self) -> Dict:
        """Main execution function for weekly cron (Sunday 00:00 UTC)"""
        print("🧠 WeightOptimizer: Starting weekly optimization...")
        
        try:
            # Step 1: Get current weights
            current_weights = await self._get_current_weights()
            current_version = current_weights.get('version', 0)
            weights = current_weights.get('weights', self.DEFAULT_WEIGHTS.copy())
            
            print(f"📊 Current version: {current_version}")
            print(f"📊 Current weights: {weights}")
            
            # Step 2: Analyze factor accuracies (last 30 days)
            factor_accuracies, total_signals = await self._analyze_factor_accuracies()
            
            if total_signals < self.MIN_SIGNALS_FOR_OPTIMIZATION:
                print(f"⚠️ Insufficient data: {total_signals} signals (need {self.MIN_SIGNALS_FOR_OPTIMIZATION})")
                return {
                    "status": "skipped",
                    "reason": "insufficient_data",
                    "total_signals": total_signals
                }
            
            print(f"📊 Factor accuracies: {factor_accuracies}")
            
            # Step 3: Calculate new weights
            new_weights = self._calculate_new_weights(weights, factor_accuracies)
            
            # Step 4: Apply safety constraints
            new_weights = self._apply_safety_constraints(weights, new_weights)
            
            # Step 5: Normalize to sum = 1.0
            new_weights = self._normalize_weights(new_weights)
            
            print(f"📊 New weights: {new_weights}")
            
            # Step 6: Get current accuracy for baseline
            current_accuracy = await self._get_current_accuracy()
            
            # Step 7: Calculate expected improvement
            expected_improvement = self._calculate_expected_improvement(
                weights, new_weights, factor_accuracies
            )
            
            # Step 8: Build optimization record
            optimization = {
                "version": current_version + 1,
                "weights": new_weights,
                "previous_weights": weights,
                "factor_accuracies": factor_accuracies,
                "based_on_signals": total_signals,
                "previous_accuracy": current_accuracy,
                "expected_improvement": expected_improvement,
                "created_at": int(datetime.now().timestamp() * 1000),
                "changes": self._calculate_changes(weights, new_weights)
            }
            
            # Step 9: Store new weights
            await self._store_weights(optimization)
            
            # Step 10: Send Telegram notification
            await self._send_telegram_report(optimization)
            
            print(f"✅ WeightOptimizer complete. Version: {optimization['version']}")
            
            return {
                "status": "success",
                "version": optimization['version'],
                "expected_improvement": expected_improvement,
                "total_signals": total_signals
            }
            
        except Exception as e:
            print(f"🚨 WeightOptimizer error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _get_current_weights(self) -> Dict:
        """Get current weights from KV store"""
        try:
            data = await self.kv.get("signal_weights:latest")
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"⚠️ Error getting current weights: {e}")
        
        # Return defaults if not found
        return {
            "version": 0,
            "weights": self.DEFAULT_WEIGHTS.copy()
        }
    
    async def _analyze_factor_accuracies(self) -> Tuple[Dict[str, float], int]:
        """
        Analyze accuracy for each factor over last 30 days.
        Returns factor accuracies (as decimals) and total signals analyzed.
        """
        thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        
        # Query to analyze which factor was dominant and if prediction was correct
        # Note: We check if the factor score was above threshold (>0.6) and count correctness
        query = """
            SELECT 
                COUNT(*) as total,
                -- Momentum analysis
                SUM(CASE WHEN momentum_score > 0.6 THEN 1 ELSE 0 END) as momentum_samples,
                SUM(CASE WHEN momentum_score > 0.6 AND was_correct_1h = 1 THEN 1 ELSE 0 END) as momentum_correct,
                -- RSI analysis
                SUM(CASE WHEN rsi_score IS NOT NULL THEN 1 ELSE 0 END) as rsi_samples,
                SUM(CASE WHEN rsi_score IS NOT NULL AND was_correct_1h = 1 THEN 1 ELSE 0 END) as rsi_correct,
                -- Sentiment analysis
                SUM(CASE WHEN sentiment_score > 0.6 THEN 1 ELSE 0 END) as sentiment_samples,
                SUM(CASE WHEN sentiment_score > 0.6 AND was_correct_1h = 1 THEN 1 ELSE 0 END) as sentiment_correct,
                -- Volume analysis
                SUM(CASE WHEN volume_score > 0.6 THEN 1 ELSE 0 END) as volume_samples,
                SUM(CASE WHEN volume_score > 0.6 AND was_correct_1h = 1 THEN 1 ELSE 0 END) as volume_correct
            FROM signal_events se
            JOIN signal_outcomes so ON se.id = so.signal_event_id
            WHERE se.timestamp > ?
              AND so.was_correct_1h IS NOT NULL
        """
        
        result = await self.db.prepare(query).bind(thirty_days_ago).all()
        
        if not result.results:
            return {}, 0
        
        row = result.results[0]
        total = row.get('total', 0) or 0
        
        # Calculate accuracies for each factor
        factor_accuracies = {}
        
        for factor in ['momentum', 'rsi', 'sentiment', 'volume']:
            samples = row.get(f'{factor}_samples', 0) or 0
            correct = row.get(f'{factor}_correct', 0) or 0
            
            if samples > 10:  # Need minimum samples for meaningful accuracy
                factor_accuracies[factor] = correct / samples
            else:
                factor_accuracies[factor] = 0.50  # Default neutral
        
        return factor_accuracies, total
    
    def _calculate_new_weights(
        self, 
        current_weights: Dict[str, float], 
        factor_accuracies: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate new weights based on factor performance"""
        new_weights = {}
        
        for factor, current_weight in current_weights.items():
            accuracy = factor_accuracies.get(factor, 0.50)
            
            if accuracy > self.ACCURACY_HIGH:
                # Performing well - increase weight
                new_weights[factor] = current_weight * self.INCREASE_MULTIPLIER
                print(f"📈 {factor}: Increasing weight (accuracy: {accuracy:.2%})")
            elif accuracy < self.ACCURACY_LOW:
                # Performing poorly - decrease weight
                new_weights[factor] = current_weight * self.DECREASE_MULTIPLIER
                print(f"📉 {factor}: Decreasing weight (accuracy: {accuracy:.2%})")
            else:
                # Neutral - maintain weight
                new_weights[factor] = current_weight
                print(f"➡️ {factor}: Maintaining weight (accuracy: {accuracy:.2%})")
        
        return new_weights
    
    def _apply_safety_constraints(
        self, 
        old_weights: Dict[str, float], 
        new_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """Apply safety constraints to prevent extreme changes"""
        safe_weights = {}
        
        for factor, new_weight in new_weights.items():
            old_weight = old_weights.get(factor, 0.25)
            
            # Constraint 1: Max change per week
            max_increase = old_weight * (1 + self.MAX_WEIGHT_CHANGE)
            max_decrease = old_weight * (1 - self.MAX_WEIGHT_CHANGE)
            
            if new_weight > max_increase:
                print(f"⚠️ Capping {factor} increase to {self.MAX_WEIGHT_CHANGE*100}%")
                new_weight = max_increase
            elif new_weight < max_decrease:
                print(f"⚠️ Capping {factor} decrease to {self.MAX_WEIGHT_CHANGE*100}%")
                new_weight = max_decrease
            
            # Constraint 2: Minimum weight
            if new_weight < self.MIN_WEIGHT:
                print(f"⚠️ Setting {factor} to minimum weight {self.MIN_WEIGHT}")
                new_weight = self.MIN_WEIGHT
            
            # Constraint 3: Maximum weight
            if new_weight > self.MAX_WEIGHT:
                print(f"⚠️ Capping {factor} to maximum weight {self.MAX_WEIGHT}")
                new_weight = self.MAX_WEIGHT
            
            safe_weights[factor] = new_weight
        
        return safe_weights
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights to sum to 1.0"""
        total = sum(weights.values())
        
        if total == 0:
            # Fallback to equal weights
            n = len(weights)
            return {k: 1.0 / n for k in weights.keys()}
        
        return {k: round(v / total, 4) for k, v in weights.items()}
    
    async def _get_current_accuracy(self) -> float:
        """Get current overall 1h accuracy"""
        query = """
            SELECT 
                SUM(CASE WHEN was_correct_1h = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as accuracy
            FROM signal_outcomes
            WHERE was_correct_1h IS NOT NULL
        """
        
        result = await self.db.prepare(query).all()
        
        if result.results:
            return round(result.results[0].get('accuracy', 0) or 0, 2)
        return 0.0
    
    def _calculate_expected_improvement(
        self,
        old_weights: Dict[str, float],
        new_weights: Dict[str, float],
        factor_accuracies: Dict[str, float]
    ) -> float:
        """Estimate expected accuracy improvement"""
        improvement = 0.0
        
        for factor in old_weights:
            old_w = old_weights.get(factor, 0)
            new_w = new_weights.get(factor, 0)
            accuracy = factor_accuracies.get(factor, 0.50)
            
            # If we increased weight on a high-accuracy factor, expect improvement
            weight_change = new_w - old_w
            factor_contribution = weight_change * (accuracy - 0.50) * 100
            improvement += factor_contribution
        
        return round(improvement, 2)
    
    def _calculate_changes(
        self, 
        old_weights: Dict[str, float], 
        new_weights: Dict[str, float]
    ) -> Dict[str, Dict]:
        """Calculate changes for reporting"""
        changes = {}
        
        for factor in old_weights:
            old_w = old_weights.get(factor, 0)
            new_w = new_weights.get(factor, 0)
            change = ((new_w - old_w) / old_w * 100) if old_w > 0 else 0
            
            changes[factor] = {
                "old": round(old_w, 4),
                "new": round(new_w, 4),
                "change_pct": round(change, 1)
            }
        
        return changes
    
    async def _store_weights(self, optimization: Dict) -> None:
        """Store optimized weights in KV and D1"""
        # Store in KV as latest
        await self.kv.put(
            "signal_weights:latest",
            json.dumps({
                "version": optimization['version'],
                "weights": optimization['weights'],
                "updated_at": optimization['created_at']
            })
        )
        
        # Store versioned copy in KV
        await self.kv.put(
            f"signal_weights:v{optimization['version']}",
            json.dumps(optimization)
        )
        
        # Store in D1 weight_history table
        query = """
            INSERT INTO weight_history 
            (version, weights, based_on_signals, previous_accuracy, 
             expected_improvement, factor_accuracies, created_at, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', 'Auto-optimized')
        """
        
        try:
            # Mark previous version as superseded
            await self.db.prepare(
                "UPDATE weight_history SET status = 'SUPERSEDED' WHERE status = 'ACTIVE'"
            ).run()
            
            # Insert new version
            await self.db.prepare(query).bind(
                optimization['version'],
                json.dumps(optimization['weights']),
                optimization['based_on_signals'],
                optimization['previous_accuracy'],
                optimization['expected_improvement'],
                json.dumps(optimization['factor_accuracies']),
                optimization['created_at']
            ).run()
            
            print("✅ Weights stored in KV and D1")
            
        except Exception as e:
            print(f"⚠️ Error storing weights in D1: {e}")
    
    async def _send_telegram_report(self, optimization: Dict) -> None:
        """Send optimization report to Telegram"""
        if not self.telegram_token or not self.telegram_chat:
            print("⚠️ Telegram credentials not set")
            return
        
        try:
            import js
            
            message = self._format_telegram_message(optimization)
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            response = await js.fetch(url, {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "chat_id": self.telegram_chat,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                })
            })
            
            result = await response.json()
            
            if result.get('ok'):
                print("✅ Telegram optimization report sent")
            else:
                print(f"⚠️ Telegram send failed: {result}")
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
    
    def _format_telegram_message(self, optimization: Dict) -> str:
        """Format optimization report for Telegram"""
        changes = optimization.get('changes', {})
        factor_acc = optimization.get('factor_accuracies', {})
        
        # Build weight changes list
        changes_text = ""
        for factor, data in changes.items():
            change = data['change_pct']
            emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            changes_text += f"• <b>{factor.upper()}:</b> {data['old']:.2%} → {data['new']:.2%} ({change:+.1f}%) {emoji}\n"
        
        # Build factor accuracies list
        acc_text = ""
        for factor, acc in factor_acc.items():
            emoji = "✅" if acc > 0.6 else "⚠️" if acc < 0.4 else "➡️"
            acc_text += f"• <b>{factor.upper()}:</b> {acc:.1%} {emoji}\n"
        
        message = f"""
🧠 <b>Weekly Weight Optimization Complete</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Version:</b> {optimization['version']}
📈 <b>Signals Analyzed:</b> {optimization['based_on_signals']}
📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}

📉 <b>Weight Adjustments:</b>
{changes_text}
🎯 <b>Factor Accuracy (30 days):</b>
{acc_text}
💡 <b>Expected Improvement:</b> {optimization['expected_improvement']:+.2f}%
📊 <b>Previous Accuracy:</b> {optimization['previous_accuracy']:.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━
🧬 <i>Axiom Learning System v{optimization['version']}</i>
<i>Next optimization: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}</i>
"""
        return message.strip()


class RollbackManager:
    """
    Safety mechanism to rollback weights if accuracy drops significantly.
    Called by health checks or manually.
    """
    
    CRITICAL_DROP_THRESHOLD = 0.10  # 10% drop triggers rollback
    
    def __init__(self, env: Any):
        self.db = env.DB
        self.kv = env.BRAIN_MEMORY
        self.telegram_token = getattr(env, 'TELEGRAM_BOT_TOKEN', None)
        self.telegram_chat = getattr(env, 'TELEGRAM_CHAT_ID', None)
    
    async def check_and_rollback_if_needed(self) -> Dict:
        """Check if accuracy has dropped and rollback if needed"""
        try:
            # Get current weights info
            current_data = await self.kv.get("signal_weights:latest")
            if not current_data:
                return {"status": "no_weights", "action": "none"}
            
            current = json.loads(current_data)
            version = current.get('version', 0)
            
            if version < 2:
                return {"status": "no_previous", "action": "none"}
            
            # Get previous version for comparison
            prev_data = await self.kv.get(f"signal_weights:v{version - 1}")
            if not prev_data:
                return {"status": "no_previous_data", "action": "none"}
            
            prev = json.loads(prev_data)
            prev_accuracy = prev.get('previous_accuracy', 0)
            
            # Get current accuracy
            query = """
                SELECT 
                    SUM(CASE WHEN was_correct_1h = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as accuracy
                FROM signal_outcomes
                WHERE was_correct_1h IS NOT NULL
                  AND updated_at > ?
            """
            
            # Only check signals from last 7 days
            seven_days_ago = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
            result = await self.db.prepare(query).bind(seven_days_ago).all()
            
            current_accuracy = result.results[0].get('accuracy', 0) if result.results else 0
            
            # Check for significant drop
            drop = prev_accuracy - current_accuracy
            
            if drop > self.CRITICAL_DROP_THRESHOLD * 100:
                # Trigger rollback
                await self._execute_rollback(version, prev, drop)
                return {
                    "status": "rolled_back",
                    "from_version": version,
                    "to_version": version - 1,
                    "accuracy_drop": drop
                }
            
            return {"status": "healthy", "action": "none", "current_accuracy": current_accuracy}
            
        except Exception as e:
            print(f"🚨 Rollback check error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _execute_rollback(self, current_version: int, previous: Dict, drop: float) -> None:
        """Execute rollback to previous weights"""
        print(f"🔄 Executing rollback from v{current_version} to v{current_version - 1}")
        
        # Restore previous weights as latest
        await self.kv.put(
            "signal_weights:latest",
            json.dumps({
                "version": current_version,  # Keep version but use old weights
                "weights": previous['weights'],
                "updated_at": int(datetime.now().timestamp() * 1000),
                "notes": f"Rolled back due to {drop:.1f}% accuracy drop"
            })
        )
        
        # Mark current version as rolled back in D1
        await self.db.prepare(
            "UPDATE weight_history SET status = 'ROLLED_BACK', notes = ? WHERE version = ?"
        ).bind(f"Accuracy dropped {drop:.1f}%", current_version).run()
        
        # Send critical alert
        await self._send_rollback_alert(current_version, drop)
    
    async def _send_rollback_alert(self, version: int, drop: float) -> None:
        """Send critical rollback alert to Telegram"""
        if not self.telegram_token or not self.telegram_chat:
            return
        
        try:
            import js
            
            message = f"""
🚨 <b>CRITICAL: AUTO-ROLLBACK EXECUTED</b>
━━━━━━━━━━━━━━━━━━━━━━━━

<b>Reason:</b> Accuracy dropped by {drop:.1f}%

<b>Action:</b> Rolled back from v{version} to v{version - 1}

⚠️ <b>Immediate attention required.</b>
Please investigate the cause of performance degradation.

━━━━━━━━━━━━━━━━━━━━━━━━
🧬 <i>Axiom Safety System</i>
"""
            
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            await js.fetch(url, {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "chat_id": self.telegram_chat,
                    "text": message.strip(),
                    "parse_mode": "HTML"
                })
            })
            
        except Exception as e:
            print(f"❌ Alert error: {e}")
