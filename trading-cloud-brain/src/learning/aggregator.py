# ========================================
# 🧬 AXIOM DATA LEARNING LOOP - Metrics Aggregator
# ========================================
# Phase 2: Daily cron job to calculate performance metrics
# Aggregates accuracy by symbol, direction, timeframe
# Sends daily Telegram report
# ========================================

import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class MetricsAggregator:
    """
    Daily cron job that:
    1. Calculates accuracy metrics across all dimensions
    2. Identifies top and bottom performers
    3. Generates performance report
    4. Stores metrics in D1 and KV
    5. Sends Telegram notification with summary
    """
    
    # Accuracy thresholds for recommendations
    THRESHOLD_EXCELLENT = 65.0
    THRESHOLD_GOOD = 55.0
    THRESHOLD_WARNING = 45.0
    
    def __init__(self, env: Any):
        """
        Initialize with Cloudflare Worker environment bindings.
        """
        self.db = env.DB
        self.kv = env.BRAIN_MEMORY
        self.telegram_token = getattr(env, 'TELEGRAM_BOT_TOKEN', None)
        self.telegram_chat = getattr(env, 'TELEGRAM_CHAT_ID', None)
    
    async def run(self) -> Dict:
        """Main execution function for daily cron"""
        print("📊 MetricsAggregator: Starting daily run...")
        
        try:
            # Step 1: Calculate all metrics
            metrics = await self._calculate_all_metrics()
            
            if not metrics['overall']['total_signals']:
                print("⚠️ No signals to analyze")
                return {"status": "success", "message": "No signals to analyze"}
            
            # Step 2: Identify top/bottom performers
            performers = await self._get_performers()
            
            # Step 3: Generate recommendation
            recommendation = self._generate_recommendation(metrics['overall'])
            
            # Step 4: Build report
            report = {
                "report_date": datetime.now().strftime("%Y-%m-%d"),
                "overall": metrics['overall'],
                "by_symbol": metrics['by_symbol'][:10],  # Top 10
                "by_direction": metrics['by_direction'],
                "top_performers": performers['top'],
                "worst_performers": performers['worst'],
                "recommendation": recommendation,
                "generated_at": int(datetime.now().timestamp() * 1000)
            }
            
            # Step 5: Store metrics
            await self._store_metrics(report)
            
            # Step 6: Send Telegram notification
            await self._send_telegram_report(report)
            
            # Step 7: Log to system_monitoring (Manus enhancement)
            try:
                await self.db.prepare("""
                    INSERT INTO system_monitoring (metric_name, metric_value, metadata, created_at)
                    VALUES (?, ?, ?, ?)
                """).bind(
                    "metrics_aggregator_run",
                    metrics['overall']['accuracy_1h'],
                    json.dumps({"total_signals": metrics['overall']['total_signals'], "tracked_1h": metrics['overall']['tracked_1h']}),
                    int(datetime.now().timestamp() * 1000)
                ).run()
            except Exception:
                pass
            
            # Step 8: Store Telegram report in D1 (Manus enhancement)
            try:
                message = self._format_telegram_message(report)
                await self.db.prepare("""
                    INSERT INTO telegram_reports (report_type, report_date, report_content, sent_at, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """).bind(
                    "daily",
                    report['report_date'],
                    message,
                    int(datetime.now().timestamp() * 1000),
                    int(datetime.now().timestamp() * 1000)
                ).run()
            except Exception:
                pass
            
            print(f"✅ MetricsAggregator complete. Total signals: {metrics['overall']['total_signals']}")
            
            return {
                "status": "success",
                "total_signals": metrics['overall']['total_signals'],
                "accuracy_1h": metrics['overall']['accuracy_1h']
            }
            
        except Exception as e:
            print(f"🚨 MetricsAggregator error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _calculate_all_metrics(self) -> Dict:
        """Calculate accuracy metrics for all dimensions"""
        
        # Overall metrics
        overall_query = """
            SELECT 
                COUNT(*) as total_signals,
                SUM(CASE WHEN was_correct_1h = 1 THEN 1 ELSE 0 END) as correct_1h,
                SUM(CASE WHEN was_correct_4h = 1 THEN 1 ELSE 0 END) as correct_4h,
                SUM(CASE WHEN was_correct_24h = 1 THEN 1 ELSE 0 END) as correct_24h,
                SUM(CASE WHEN was_correct_1h IS NOT NULL THEN 1 ELSE 0 END) as tracked_1h,
                SUM(CASE WHEN was_correct_4h IS NOT NULL THEN 1 ELSE 0 END) as tracked_4h,
                SUM(CASE WHEN was_correct_24h IS NOT NULL THEN 1 ELSE 0 END) as tracked_24h,
                ROUND(AVG(return_1h), 4) as avg_return_1h,
                ROUND(AVG(return_4h), 4) as avg_return_4h,
                ROUND(AVG(return_24h), 4) as avg_return_24h,
                MAX(return_1h) as max_return_1h,
                MIN(return_1h) as min_return_1h
            FROM signal_outcomes
        """
        
        overall_result = await self.db.prepare(overall_query).all()
        overall_row = overall_result.results[0] if overall_result.results else {}
        
        # Calculate accuracy percentages
        tracked_1h = overall_row.get('tracked_1h', 0) or 0
        tracked_4h = overall_row.get('tracked_4h', 0) or 0
        tracked_24h = overall_row.get('tracked_24h', 0) or 0
        
        overall = {
            "total_signals": overall_row.get('total_signals', 0) or 0,
            "accuracy_1h": round((overall_row.get('correct_1h', 0) or 0) / tracked_1h * 100, 2) if tracked_1h > 0 else 0,
            "accuracy_4h": round((overall_row.get('correct_4h', 0) or 0) / tracked_4h * 100, 2) if tracked_4h > 0 else 0,
            "accuracy_24h": round((overall_row.get('correct_24h', 0) or 0) / tracked_24h * 100, 2) if tracked_24h > 0 else 0,
            "tracked_1h": tracked_1h,
            "tracked_4h": tracked_4h,
            "tracked_24h": tracked_24h,
            "avg_return_1h": overall_row.get('avg_return_1h', 0) or 0,
            "avg_return_4h": overall_row.get('avg_return_4h', 0) or 0,
            "avg_return_24h": overall_row.get('avg_return_24h', 0) or 0,
            "max_return_1h": overall_row.get('max_return_1h', 0) or 0,
            "min_return_1h": overall_row.get('min_return_1h', 0) or 0
        }
        
        # By symbol metrics
        by_symbol_query = """
            SELECT 
                se.symbol,
                se.asset_type,
                COUNT(*) as total,
                SUM(CASE WHEN so.was_correct_1h = 1 THEN 1 ELSE 0 END) as correct,
                ROUND(AVG(so.return_1h), 4) as avg_return
            FROM signal_events se
            JOIN signal_outcomes so ON se.id = so.signal_event_id
            WHERE so.was_correct_1h IS NOT NULL
            GROUP BY se.symbol, se.asset_type
            ORDER BY total DESC
            LIMIT 20
        """
        
        by_symbol_result = await self.db.prepare(by_symbol_query).all()
        by_symbol = []
        
        for row in (by_symbol_result.results or []):
            total = row.get('total', 0) or 0
            correct = row.get('correct', 0) or 0
            accuracy = round(correct / total * 100, 2) if total > 0 else 0
            
            by_symbol.append({
                "symbol": row.get('symbol'),
                "asset_type": row.get('asset_type'),
                "total": total,
                "accuracy": accuracy,
                "avg_return": row.get('avg_return', 0) or 0
            })
        
        # By direction metrics
        by_direction_query = """
            SELECT 
                se.signal_direction,
                COUNT(*) as total,
                SUM(CASE WHEN so.was_correct_1h = 1 THEN 1 ELSE 0 END) as correct,
                ROUND(AVG(so.return_1h), 4) as avg_return
            FROM signal_events se
            JOIN signal_outcomes so ON se.id = so.signal_event_id
            WHERE so.was_correct_1h IS NOT NULL
            GROUP BY se.signal_direction
            ORDER BY total DESC
        """
        
        by_direction_result = await self.db.prepare(by_direction_query).all()
        by_direction = []
        
        for row in (by_direction_result.results or []):
            total = row.get('total', 0) or 0
            correct = row.get('correct', 0) or 0
            accuracy = round(correct / total * 100, 2) if total > 0 else 0
            
            by_direction.append({
                "direction": row.get('signal_direction'),
                "total": total,
                "accuracy": accuracy,
                "avg_return": row.get('avg_return', 0) or 0
            })
        
        return {
            "overall": overall,
            "by_symbol": by_symbol,
            "by_direction": by_direction
        }
    
    async def _get_performers(self) -> Dict:
        """Get top and worst performing symbols"""
        
        query = """
            SELECT 
                se.symbol,
                se.signal_direction,
                COUNT(*) as total,
                SUM(CASE WHEN so.was_correct_1h = 1 THEN 1 ELSE 0 END) as correct,
                ROUND(AVG(so.return_1h), 4) as avg_return
            FROM signal_events se
            JOIN signal_outcomes so ON se.id = so.signal_event_id
            WHERE so.was_correct_1h IS NOT NULL
            GROUP BY se.symbol, se.signal_direction
            HAVING total >= 5
            ORDER BY (correct * 1.0 / total) DESC
        """
        
        result = await self.db.prepare(query).all()
        rows = result.results or []
        
        performers = []
        for row in rows:
            total = row.get('total', 0) or 0
            correct = row.get('correct', 0) or 0
            accuracy = round(correct / total * 100, 2) if total > 0 else 0
            
            performers.append({
                "symbol": row.get('symbol'),
                "direction": row.get('signal_direction'),
                "total": total,
                "accuracy": accuracy,
                "avg_return": row.get('avg_return', 0) or 0
            })
        
        return {
            "top": performers[:5],
            "worst": performers[-5:][::-1] if len(performers) > 5 else []
        }
    
    def _generate_recommendation(self, overall: Dict) -> str:
        """Generate actionable recommendation based on metrics"""
        acc_1h = overall.get('accuracy_1h', 0)
        acc_4h = overall.get('accuracy_4h', 0)
        
        if acc_1h >= self.THRESHOLD_EXCELLENT and acc_4h >= 60:
            return "✅ Excellent! System performing well. Consider increasing signal frequency."
        elif acc_1h >= self.THRESHOLD_GOOD:
            return "📈 Good performance. Focus on top performers, reduce underperformers."
        elif acc_1h >= self.THRESHOLD_WARNING:
            return "⚠️ Mixed results. Review signal generation factors carefully."
        else:
            return "🚨 Critical: Low accuracy. Pause and analyze signal methodology."
    
    async def _store_metrics(self, report: Dict) -> None:
        """Store metrics in D1 and KV"""
        current_time = int(datetime.now().timestamp() * 1000)
        report_date = report['report_date']
        
        # Store in KV for quick access
        await self.kv.put(
            "learning_report:latest",
            json.dumps(report)
        )
        
        # Store historical in KV
        await self.kv.put(
            f"learning_report:{report_date}",
            json.dumps(report)
        )
        
        # Store aggregated metrics in D1
        for entry in report.get('by_symbol', []):
            query = """
                INSERT INTO learning_metrics 
                (symbol, signal_direction, timeframe, date_range, 
                 total_signals, correct_signals, accuracy_pct, avg_return, last_updated)
                VALUES (?, 'ALL', '1h', ?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol, signal_direction, timeframe, date_range) 
                DO UPDATE SET
                    total_signals = excluded.total_signals,
                    correct_signals = excluded.correct_signals,
                    accuracy_pct = excluded.accuracy_pct,
                    avg_return = excluded.avg_return,
                    last_updated = excluded.last_updated
            """
            
            try:
                await self.db.prepare(query).bind(
                    entry['symbol'],
                    report_date,
                    entry['total'],
                    int(entry['total'] * entry['accuracy'] / 100),
                    entry['accuracy'],
                    entry['avg_return'],
                    current_time
                ).run()
            except Exception as e:
                print(f"⚠️ Error storing metrics for {entry['symbol']}: {e}")
    
    async def _send_telegram_report(self, report: Dict) -> None:
        """Send formatted daily report to Telegram"""
        if not self.telegram_token or not self.telegram_chat:
            print("⚠️ Telegram credentials not set")
            return
        
        try:
            import js
            
            # Format message
            message = self._format_telegram_message(report)
            
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
                print("✅ Telegram report sent")
            else:
                print(f"⚠️ Telegram send failed: {result}")
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
    
    def _format_telegram_message(self, report: Dict) -> str:
        """Format report for Telegram with emoji and structure"""
        overall = report['overall']
        
        # Build top performers list
        top_list = ""
        for p in report.get('top_performers', [])[:3]:
            top_list += f"• {p['symbol']} {p['direction']}: {p['accuracy']}%\n"
        
        # Build worst performers list
        worst_list = ""
        for p in report.get('worst_performers', [])[:3]:
            worst_list += f"• {p['symbol']} {p['direction']}: {p['accuracy']}%\n"
        
        message = f"""
📊 <b>Daily Learning Report</b>
━━━━━━━━━━━━━━━━━━━━━━━━

📅 <b>Date:</b> {report['report_date']}
📈 <b>Signals Analyzed:</b> {overall['total_signals']}

🎯 <b>Overall Accuracy:</b>
• <b>1h:</b> {overall['accuracy_1h']}% ({overall['tracked_1h']} tracked)
• <b>4h:</b> {overall['accuracy_4h']}%
• <b>24h:</b> {overall['accuracy_24h']}%

📊 <b>Average Returns:</b>
• 1h: {overall['avg_return_1h']:.2f}%
• 4h: {overall['avg_return_4h']:.2f}%
• 24h: {overall['avg_return_24h']:.2f}%

🏆 <b>Top Performers:</b>
{top_list if top_list else "• Not enough data yet"}

⚠️ <b>Underperformers:</b>
{worst_list if worst_list else "• Not enough data yet"}

💡 <b>Recommendation:</b>
{report['recommendation']}

━━━━━━━━━━━━━━━━━━━━━━━━
🧬 <i>Axiom Learning System</i>
"""
        return message.strip()
