# ========================================
# 🧬 AXIOM DATA LEARNING LOOP - Outcome Tracker
# ========================================
# Phase 1: Hourly cron job to track signal outcomes
# Fetches current prices and calculates returns/correctness
# ========================================

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

# Rate limiting constants
BATCH_SIZE = 50  # Process 50 signals per run
RATE_LIMIT_DELAY = 0.1  # 100ms between API calls


class OutcomeTracker:
    """
    Hourly cron job that:
    1. Fetches pending signals from D1 (older than 1h without outcomes)
    2. Gets current prices via Finage (stock/forex) or Bybit (crypto)
    3. Calculates returns and correctness
    4. Updates signal_outcomes with 1h/4h/24h data
    """
    
    def __init__(self, env: Any):
        """
        Initialize with Cloudflare Worker environment bindings.
        
        Args:
            env: Worker environment with DB, BRAIN_MEMORY, secrets
        """
        self.db = env.DB  # D1 database binding
        self.kv = env.BRAIN_MEMORY  # KV store binding
        self.finage_key = getattr(env, 'FINAGE_API_KEY', None)
        self.telegram_token = getattr(env, 'TELEGRAM_BOT_TOKEN', None)
        self.telegram_chat = getattr(env, 'TELEGRAM_CHAT_ID', None)
        
    async def run(self) -> Dict:
        """Main execution function for hourly cron"""
        print("🔍 OutcomeTracker: Starting hourly run...")
        
        try:
            # Step 1: Fetch pending signals
            pending_signals = await self._fetch_pending_signals()
            
            if not pending_signals:
                print("✅ No pending signals to process")
                return {"status": "success", "processed": 0, "message": "No pending signals"}
            
            print(f"📊 Found {len(pending_signals)} signals to track")
            
            # Step 2: Process each signal
            successful = 0
            failed = 0
            
            for signal in pending_signals[:BATCH_SIZE]:
                try:
                    result = await self._process_signal(signal)
                    if result:
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    print(f"❌ Error processing signal {signal.get('id')}: {e}")
                    failed += 1
                
                # Rate limiting
                await asyncio.sleep(RATE_LIMIT_DELAY)
            
            print(f"✅ OutcomeTracker complete: {successful} successful, {failed} failed")
            
            # Log to system_monitoring (Manus enhancement)
            try:
                await self.db.prepare("""
                    INSERT INTO system_monitoring (metric_name, metric_value, metadata, created_at)
                    VALUES (?, ?, ?, ?)
                """).bind(
                    "outcome_tracker_run",
                    successful,
                    json.dumps({"processed": successful, "failed": failed, "total_pending": len(pending_signals)}),
                    int(datetime.now().timestamp() * 1000)
                ).run()
            except Exception:
                pass  # Don't fail the run if monitoring fails
            
            return {
                "status": "success",
                "processed": successful,
                "failed": failed,
                "total_pending": len(pending_signals)
            }
            
        except Exception as e:
            print(f"🚨 OutcomeTracker error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _fetch_pending_signals(self) -> List[Dict]:
        """
        Fetch signals that need outcome tracking.
        Returns signals older than 1 hour that don't have complete outcomes.
        """
        current_time = int(datetime.now().timestamp() * 1000)
        one_hour_ago = current_time - (60 * 60 * 1000)  # 1 hour in ms
        
        query = """
            SELECT 
                se.id,
                se.symbol,
                se.asset_type,
                se.signal_direction,
                se.price_at_signal,
                se.timestamp,
                so.id as outcome_id,
                so.was_correct_1h,
                so.was_correct_4h,
                so.was_correct_24h
            FROM signal_events se
            LEFT JOIN signal_outcomes so ON se.id = so.signal_event_id
            WHERE se.timestamp < ?
              AND (
                  so.id IS NULL
                  OR (so.was_correct_1h IS NULL AND se.timestamp < ?)
                  OR (so.was_correct_4h IS NULL AND se.timestamp < ?)
                  OR (so.was_correct_24h IS NULL AND se.timestamp < ?)
              )
            ORDER BY se.timestamp ASC
            LIMIT ?
        """
        
        four_hours_ago = current_time - (4 * 60 * 60 * 1000)
        twenty_four_hours_ago = current_time - (24 * 60 * 60 * 1000)
        
        try:
            result = await self.db.prepare(query).bind(
                one_hour_ago,
                one_hour_ago,
                four_hours_ago,
                twenty_four_hours_ago,
                BATCH_SIZE * 2  # Fetch more to filter
            ).all()
            
            return [dict(row) for row in result.results] if result.results else []
            
        except Exception as e:
            print(f"❌ Error fetching pending signals: {e}")
            return []
    
    async def _process_signal(self, signal: Dict) -> bool:
        """Process a single signal and update its outcome"""
        try:
            # Get current price
            current_price = await self._get_current_price(
                signal['symbol'], 
                signal['asset_type']
            )
            
            if current_price is None:
                print(f"⚠️ Could not fetch price for {signal['symbol']}")
                return False
            
            # Calculate signal age in hours
            current_time = int(datetime.now().timestamp() * 1000)
            signal_age_hours = (current_time - signal['timestamp']) / (60 * 60 * 1000)
            
            # Calculate return percentage
            return_pct = self._calculate_return(
                current_price,
                signal['price_at_signal'],
                signal['signal_direction']
            )
            
            # Determine if prediction was correct
            was_correct = self._determine_correctness(
                current_price,
                signal['price_at_signal'],
                signal['signal_direction']
            )
            
            # Determine which timeframe to update
            timeframe = self._determine_timeframe(signal_age_hours, signal)
            
            if timeframe is None:
                return False  # Already fully tracked
            
            # Update or insert outcome
            await self._upsert_outcome(
                signal_event_id=signal['id'],
                outcome_id=signal.get('outcome_id'),
                current_price=current_price,
                return_pct=return_pct,
                was_correct=was_correct,
                timeframe=timeframe
            )
            
            print(f"✅ {signal['symbol']} | {timeframe} | Return: {return_pct:.2f}% | Correct: {was_correct}")
            return True
            
        except Exception as e:
            print(f"❌ Error in _process_signal: {e}")
            return False
    
    async def _get_current_price(self, symbol: str, asset_type: str) -> Optional[float]:
        """Fetch current price based on asset type"""
        try:
            if asset_type == 'crypto':
                return await self._get_bybit_price(symbol)
            else:  # stock, forex
                return await self._get_finage_price(symbol, asset_type)
        except Exception as e:
            print(f"❌ Price fetch error for {symbol}: {e}")
            return None
    
    async def _get_bybit_price(self, symbol: str) -> Optional[float]:
        """Fetch crypto price from Bybit public API"""
        try:
            import js
            url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
            
            response = await js.fetch(url)
            data = await response.json()
            
            if data.get('retCode') == 0 and data.get('result', {}).get('list'):
                return float(data['result']['list'][0]['lastPrice'])
            return None
            
        except Exception as e:
            print(f"❌ Bybit API error: {e}")
            return None
    
    async def _get_finage_price(self, symbol: str, asset_type: str) -> Optional[float]:
        """Fetch stock/forex price from Finage API"""
        if not self.finage_key:
            print("⚠️ FINAGE_API_KEY not set")
            return None
            
        try:
            import js
            
            if asset_type == 'forex':
                url = f"https://api.finage.co.uk/last/forex/{symbol}?apikey={self.finage_key}"
            else:  # stock
                url = f"https://api.finage.co.uk/last/stock/{symbol}?apikey={self.finage_key}"
            
            response = await js.fetch(url)
            data = await response.json()
            
            # Finage returns price in different formats
            if 'price' in data:
                return float(data['price'])
            elif 'ask' in data and 'bid' in data:
                return (float(data['ask']) + float(data['bid'])) / 2
            return None
            
        except Exception as e:
            print(f"❌ Finage API error: {e}")
            return None
    
    def _calculate_return(self, current_price: float, signal_price: float, direction: str) -> float:
        """
        Calculate return percentage with direction adjustment.
        For SELL signals, profit is when price goes down.
        """
        if signal_price == 0:
            return 0.0
            
        return_pct = ((current_price - signal_price) / signal_price) * 100
        
        # Invert for short positions
        if direction in ["SELL", "STRONG_SELL"]:
            return_pct = -return_pct
            
        return round(return_pct, 4)
    
    def _determine_correctness(self, current_price: float, signal_price: float, direction: str) -> bool:
        """
        Determine if the signal prediction was correct.
        BUY = correct if price went up
        SELL = correct if price went down
        """
        if direction in ["BUY", "STRONG_BUY"]:
            return current_price > signal_price
        elif direction in ["SELL", "STRONG_SELL"]:
            return current_price < signal_price
        else:  # NEUTRAL
            return True  # Neutral is always "correct"
    
    def _determine_timeframe(self, signal_age_hours: float, signal: Dict) -> Optional[str]:
        """
        Determine which timeframe column to update based on signal age.
        Returns None if all timeframes already tracked.
        """
        # Check 1h (1-4 hours old, 1h not yet tracked)
        if signal_age_hours >= 1 and signal_age_hours < 4:
            if signal.get('was_correct_1h') is None:
                return '1h'
        
        # Check 4h (4-24 hours old, 4h not yet tracked)
        if signal_age_hours >= 4 and signal_age_hours < 24:
            if signal.get('was_correct_4h') is None:
                return '4h'
            elif signal.get('was_correct_1h') is None:
                return '1h'
        
        # Check 24h (24+ hours old, 24h not yet tracked)
        if signal_age_hours >= 24:
            if signal.get('was_correct_24h') is None:
                return '24h'
            elif signal.get('was_correct_4h') is None:
                return '4h'
            elif signal.get('was_correct_1h') is None:
                return '1h'
        
        return None  # All timeframes tracked
    
    async def _upsert_outcome(
        self,
        signal_event_id: int,
        outcome_id: Optional[int],
        current_price: float,
        return_pct: float,
        was_correct: bool,
        timeframe: str
    ) -> None:
        """Insert or update signal outcome in D1"""
        current_time = int(datetime.now().timestamp() * 1000)
        
        # Map timeframe to column names
        price_col = f"price_{timeframe}_later"
        return_col = f"return_{timeframe}"
        correct_col = f"was_correct_{timeframe}"
        
        if outcome_id is None:
            # INSERT new outcome
            query = f"""
                INSERT INTO signal_outcomes 
                (signal_event_id, {price_col}, {return_col}, {correct_col}, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """
            await self.db.prepare(query).bind(
                signal_event_id,
                current_price,
                return_pct,
                1 if was_correct else 0,
                current_time
            ).run()
        else:
            # UPDATE existing outcome
            query = f"""
                UPDATE signal_outcomes 
                SET {price_col} = ?,
                    {return_col} = ?,
                    {correct_col} = ?,
                    updated_at = ?
                WHERE signal_event_id = ?
            """
            await self.db.prepare(query).bind(
                current_price,
                return_pct,
                1 if was_correct else 0,
                current_time,
                signal_event_id
            ).run()
