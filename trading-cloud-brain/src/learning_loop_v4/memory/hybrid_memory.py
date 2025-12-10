"""
Hybrid Memory Architecture for AlphaAxiom v4.0
Combines D1 and R2 for Time-Travel Backtesting and Historical Analysis.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MarketSnapshot:
    """Represents a complete market state at a specific point in time"""
    snapshot_id: str
    timestamp: datetime
    price_data: Dict[str, Any]
    orderbook_data: Dict[str, Any]
    news_sentiment: Dict[str, Any]
    technical_indicators: Dict[str, float]
    macro_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialecticSession:
    """Represents a complete dialectic session with all context and 
    reasoning"""
    session_id: str
    snapshot_uuid: str
    timestamp: datetime
    market_condition: str  # Classification of market conditions
    debate_intensity: float  # Intensity of the dialectic debate
    outcome_confidence: float
    core_reasoning_chain: List[str]  # Core agent's reasoning steps
    shadow_counterpoints: List[str]  # Shadow agent's counterarguments
    synthesis_process: Dict[str, Any]  # Synthesis generation process
    embeddings: Dict[str, List[float]]  # Embeddings for semantic search
    metadata: Dict[str, Any] = field(default_factory=dict)


class HybridMemory:
    """
    Hybrid Memory Architecture combining D1 (structured) and R2 
    (unstructured) storage for Time-Travel Backtesting and Historical 
    Analysis.
    """
    
    def __init__(self, d1_db=None, r2_bucket=None):
        """
        Initialize the Hybrid Memory system.
        
        Args:
            d1_db: Cloudflare D1 database connection
            r2_bucket: Cloudflare R2 bucket connection
        """
        self.d1 = d1_db
        self.r2 = r2_bucket
        
    async def store_market_snapshot(self, snapshot: MarketSnapshot) -> str:
        """
        Store a complete market snapshot in hybrid storage.
        
        Args:
            snapshot: MarketSnapshot object to store
            
        Returns:
            Snapshot ID
        """
        # Store structured metadata in D1
        await self._store_snapshot_metadata(snapshot)
        
        # Store full context in R2 as JSON
        await self._store_snapshot_full_context(snapshot)
        
        return snapshot.snapshot_id
    
    async def _store_snapshot_metadata(self, snapshot: MarketSnapshot) -> None:
        """
        Store snapshot metadata in D1 database.
        
        Args:
            snapshot: MarketSnapshot object
        """
        if not self.d1:
            return
            
        query = """
        INSERT OR REPLACE INTO market_snapshots 
        (snapshot_id, timestamp, market_condition, data_summary, metadata)
        VALUES (?, ?, ?, ?, ?)
        """
        
        # Create a summary of the data for quick querying
        data_summary = {
            "symbols": list(snapshot.price_data.keys())[:10],  # First 10
            "indicators": list(snapshot.technical_indicators.keys()),
            "news_count": len(snapshot.news_sentiment.get("articles", [])),
            "orderbook_depth": len(snapshot.orderbook_data.get("levels", []))
        }
        
        await self.d1.execute(
            query,
            snapshot.snapshot_id,
            snapshot.timestamp.isoformat(),
            snapshot.metadata.get("market_condition", "normal"),
            json.dumps(data_summary),
            json.dumps(snapshot.metadata)
        )
    
    async def _store_snapshot_full_context(
            self, 
            snapshot: MarketSnapshot) -> None:
        """
        Store full snapshot context in R2 bucket.
        
        Args:
            snapshot: MarketSnapshot object
        """
        if not self.r2:
            return
            
        # Create the full context object
        full_context = {
            "snapshot_id": snapshot.snapshot_id,
            "timestamp": snapshot.timestamp.isoformat(),
            "price_data": snapshot.price_data,
            "orderbook_data": snapshot.orderbook_data,
            "news_sentiment": snapshot.news_sentiment,
            "technical_indicators": snapshot.technical_indicators,
            "macro_data": snapshot.macro_data,
            "metadata": snapshot.metadata
        }
        
        # Store in R2 as JSON
        timestamp_str = snapshot.timestamp.strftime('%Y/%m/%d')
        key = f"snapshots/{timestamp_str}/{snapshot.snapshot_id}.json"
        await self.r2.put(key, json.dumps(full_context))
    
    async def store_dialectic_session(self, session: DialecticSession) -> str:
        """
        Store a complete dialectic session in hybrid storage.
        
        Args:
            session: DialecticSession object to store
            
        Returns:
            Session ID
        """
        # Store structured metadata in D1
        await self._store_session_metadata(session)
        
        # Store full context in R2 as JSON
        await self._store_session_full_context(session)
        
        return session.session_id
    
    async def _store_session_metadata(self, session: DialecticSession) -> None:
        """
        Store session metadata in D1 database.
        
        Args:
            session: DialecticSession object
        """
        if not self.d1:
            return
            
        query = """
        INSERT OR REPLACE INTO dialectic_sessions 
        (session_id, snapshot_uuid, timestamp, market_condition, 
         debate_intensity, outcome_confidence, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        await self.d1.execute(
            query,
            session.session_id,
            session.snapshot_uuid,
            session.timestamp.isoformat(),
            session.market_condition,
            session.debate_intensity,
            session.outcome_confidence,
            json.dumps(session.metadata)
        )
    
    async def _store_session_full_context(
            self, 
            session: DialecticSession) -> None:
        """
        Store full session context in R2 bucket.
        
        Args:
            session: DialecticSession object
        """
        if not self.r2:
            return
            
        # Create the full context object
        full_context = {
            "session_id": session.session_id,
            "snapshot_uuid": session.snapshot_uuid,
            "timestamp": session.timestamp.isoformat(),
            "market_condition": session.market_condition,
            "debate_intensity": session.debate_intensity,
            "outcome_confidence": session.outcome_confidence,
            "core_reasoning_chain": session.core_reasoning_chain,
            "shadow_counterpoints": session.shadow_counterpoints,
            "synthesis_process": session.synthesis_process,
            "embeddings": session.embeddings,
            "metadata": session.metadata
        }
        
        # Store in R2 as JSON
        timestamp_str = session.timestamp.strftime('%Y/%m/%d')
        key = f"sessions/{timestamp_str}/{session.session_id}.json"
        await self.r2.put(key, json.dumps(full_context))
    
    async def retrieve_market_snapshot(
            self, 
            snapshot_id: str) -> Optional[MarketSnapshot]:
        """
        Retrieve a market snapshot from hybrid storage.
        
        Args:
            snapshot_id: ID of the snapshot to retrieve
            
        Returns:
            MarketSnapshot object or None if not found
        """
        # Try to get from R2 first (full context)
        try:
            # In practice, you'd need to search for the exact key
            # This is a simplified version
            key = f"snapshots/*/*/{snapshot_id}.json"
            obj = await self.r2.get(key)
            if obj:
                data = json.loads(await obj.text())
                return MarketSnapshot(
                    snapshot_id=data["snapshot_id"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    price_data=data["price_data"],
                    orderbook_data=data["orderbook_data"],
                    news_sentiment=data["news_sentiment"],
                    technical_indicators=data["technical_indicators"],
                    macro_data=data["macro_data"],
                    metadata=data["metadata"]
                )
        except Exception:
            pass
        
        # Fallback to D1 metadata only
        if self.d1:
            result = await self.d1.execute(
                "SELECT * FROM market_snapshots WHERE snapshot_id = ?",
                snapshot_id
            )
            if result:
                row = result[0]
                metadata_json = row["metadata"] if row["metadata"] else "{}"
                return MarketSnapshot(
                    snapshot_id=row["snapshot_id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    price_data={},  # Empty as we don't have full data
                    orderbook_data={},
                    news_sentiment={},
                    technical_indicators={},
                    macro_data={},
                    metadata=json.loads(metadata_json)
                )
        
        return None
    
    async def time_travel_query(
            self, 
            start_time: datetime, 
            end_time: datetime, 
            market_condition: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform a time-travel query to find snapshots within a time range.
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            market_condition: Optional market condition filter
            
        Returns:
            List of snapshot metadata
        """
        if not self.d1:
            return []
        
        query = """
        SELECT snapshot_id, timestamp, market_condition, data_summary, metadata
        FROM market_snapshots 
        WHERE timestamp BETWEEN ? AND ?
        """
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if market_condition:
            query += " AND market_condition = ?"
            params.append(market_condition)
        
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        result = await self.d1.execute(query, *params)
        return [dict(row) for row in result] if result else []
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the hybrid memory system.
        
        Returns:
            Dictionary with memory statistics
        """
        stats: Dict[str, Any] = {
            "total_snapshots": 0,
            "total_sessions": 0,
            "latest_snapshot": None,
            "storage_breakdown": {
                "d1_records": 0,
                "r2_objects": 0
            }
        }
        
        if self.d1:
            # Count snapshots
            snapshot_count = await self.d1.execute(
                "SELECT COUNT(*) as count FROM market_snapshots"
            )
            count_val = snapshot_count[0]["count"] if snapshot_count else 0
            stats["total_snapshots"] = int(count_val)
            
            # Count sessions
            session_count = await self.d1.execute(
                "SELECT COUNT(*) as count FROM dialectic_sessions"
            )
            sess_count_val = session_count[0]["count"] if session_count else 0
            stats["total_sessions"] = int(sess_count_val)
            
            # Latest snapshot
            latest = await self.d1.execute(
                "SELECT timestamp FROM market_snapshots " +
                "ORDER BY timestamp DESC LIMIT 1"
            )
            if latest:
                stats["latest_snapshot"] = latest[0]["timestamp"]
            
            # Calculate D1 records total
            total_snapshots = int(stats["total_snapshots"])
            total_sessions = int(stats["total_sessions"])
            d1_total = total_snapshots + total_sessions
            stats["storage_breakdown"]["d1_records"] = d1_total
        
        # R2 object count would require listing all objects, which is expensive
        # In practice, you might track this separately
        
        return stats