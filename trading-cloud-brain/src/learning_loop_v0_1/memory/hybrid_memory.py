"""
Hybrid Memory Architecture for AlphaAxiom v0.1 Beta
Implements D1 (Index) + R2 (Crime Scene Snapshots) pattern for Time-Travel Debugging.
"""

import json
import gzip
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
import uuid
import hashlib


@dataclass
class MarketSnapshot:
    """
    Immutable "Crime Scene" snapshot stored in R2.
    Contains the EXACT state of the world at decision time.
    """
    snapshot_id: str
    timestamp: datetime
    
    # Market Data (200k tokens worth)
    price_data: Dict[str, Any]  # OHLCV for multiple timeframes
    orderbook_data: Dict[str, Any]  # L2 depth (top 20 levels)
    
    # Contextual Data
    news_sentiment: Dict[str, Any]  # News articles + sentiment scores
    technical_indicators: Dict[str, float]  # RSI, MACD, ATR, etc.
    macro_data: Dict[str, Any]  # Fed rates, CPI, etc.
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_compressed_json(self) -> bytes:
        """Compress snapshot for R2 storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        json_str = json.dumps(data, ensure_ascii=False)
        return gzip.compress(json_str.encode('utf-8'))
    
    @classmethod
    def from_compressed_json(cls, data: bytes) -> 'MarketSnapshot':
        """Decompress snapshot from R2"""
        json_str = gzip.decompress(data).decode('utf-8')
        d = json.loads(json_str)
        d['timestamp'] = datetime.fromisoformat(d['timestamp'])
        return cls(**d)


@dataclass
class DialecticSession:
    """
    D1 Index record for quick querying.
    Links to full snapshot in R2.
    """
    session_id: str
    snapshot_uuid: str  # Reference to R2 object
    timestamp: datetime
    
    # Decision Metrics
    market_condition: str  # "bullish", "bearish", "ranging", "volatile"
    debate_intensity: float  # Length/intensity of Core-Shadow debate
    outcome_confidence: float
    
    # Reasoning Chains (for explainability)
    core_reasoning_chain: List[str]
    shadow_counterpoints: List[str]
    synthesis_process: Dict[str, Any]
    
    # Embeddings for semantic search
    embeddings: Dict[str, List[float]] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class HybridMemory:
    """
    Manages the D1 + R2 hybrid storage architecture.
    Enables "Time-Travel" backtesting with perfect fidelity.
    """
    
    def __init__(self, d1_db=None, r2_bucket=None):
        """
        Args:
            d1_db: Cloudflare D1 database connection
            r2_bucket: Cloudflare R2 bucket connection
        """
        self.d1 = d1_db
        self.r2 = r2_bucket
        
        # Local cache for development/testing
        self._local_snapshots: Dict[str, MarketSnapshot] = {}
        self._local_sessions: Dict[str, DialecticSession] = {}
    
    def generate_snapshot_id(self, market_data: Dict) -> str:
        """Generate deterministic ID based on content hash"""
        content = json.dumps(market_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def store_market_snapshot(self, snapshot: MarketSnapshot) -> str:
        """
        Store a complete market state in R2.
        Returns the snapshot_uuid for D1 reference.
        """
        snapshot_uuid = str(uuid.uuid4())
        
        if self.r2:
            # Production: Store in Cloudflare R2
            key = f"snapshots/{snapshot.timestamp.strftime('%Y/%m/%d')}/{snapshot_uuid}.json.gz"
            await self.r2.put(key, snapshot.to_compressed_json())
        else:
            # Development: Local storage
            self._local_snapshots[snapshot_uuid] = snapshot
        
        return snapshot_uuid
    
    async def retrieve_snapshot(self, snapshot_uuid: str) -> Optional[MarketSnapshot]:
        """
        Retrieve a complete market state from R2 for Time-Travel.
        """
        if self.r2:
            # Production: Fetch from Cloudflare R2
            # Note: Would need date info or index lookup in production
            pass
        else:
            # Development: Local retrieval
            return self._local_snapshots.get(snapshot_uuid)
        
        return None
    
    async def store_dialectic_session(self, session: DialecticSession) -> None:
        """
        Index a dialectic session in D1 for quick querying.
        """
        if self.d1:
            # Production: Insert into D1
            sql = """
                INSERT INTO dialectic_sessions (
                    session_id, snapshot_uuid, timestamp,
                    market_condition, debate_intensity, outcome_confidence,
                    core_reasoning, shadow_reasoning, synthesis,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            await self.d1.execute(sql, [
                session.session_id,
                session.snapshot_uuid,
                session.timestamp.isoformat(),
                session.market_condition,
                session.debate_intensity,
                session.outcome_confidence,
                json.dumps(session.core_reasoning_chain),
                json.dumps(session.shadow_counterpoints),
                json.dumps(session.synthesis_process),
                json.dumps(session.metadata)
            ])
        else:
            # Development: Local storage
            self._local_sessions[session.session_id] = session
    
    async def query_sessions_by_condition(
        self, 
        condition: str, 
        limit: int = 100
    ) -> List[DialecticSession]:
        """
        Query sessions by market condition for pattern analysis.
        """
        if self.d1:
            sql = """
                SELECT * FROM dialectic_sessions 
                WHERE market_condition = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            results = await self.d1.execute(sql, [condition, limit])
            return [self._row_to_session(r) for r in results]
        else:
            # Development: Filter local sessions
            return [
                s for s in self._local_sessions.values() 
                if s.market_condition == condition
            ][:limit]
    
    async def get_time_travel_context(
        self, 
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Reconstruct the EXACT context that existed at decision time.
        This is the "Crime Scene" reconstruction for backtesting.
        """
        session = self._local_sessions.get(session_id)
        if not session:
            return None
        
        snapshot = await self.retrieve_snapshot(session.snapshot_uuid)
        if not snapshot:
            return None
        
        return {
            "session": asdict(session),
            "market_state": asdict(snapshot),
            "reconstructed_at": datetime.now().isoformat()
        }
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Return memory usage statistics"""
        return {
            "local_snapshots": len(self._local_snapshots),
            "local_sessions": len(self._local_sessions),
            "storage_type": "production" if self.r2 else "local"
        }
    
    def _row_to_session(self, row) -> DialecticSession:
        """Convert D1 row to DialecticSession object"""
        # Implementation depends on D1 row format
        pass


# D1 Schema for reference (to be created via Wrangler)
D1_SCHEMA = """
-- AlphaAxiom v0.1 Beta: Dialectic Sessions Index

CREATE TABLE IF NOT EXISTS dialectic_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    snapshot_uuid TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    
    -- Decision Context
    market_condition TEXT,
    debate_intensity REAL,
    outcome_confidence REAL,
    
    -- Reasoning (JSON)
    core_reasoning TEXT,
    shadow_reasoning TEXT,
    synthesis TEXT,
    
    -- Metadata
    metadata TEXT,
    
    -- Indexes
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON dialectic_sessions(timestamp);
CREATE INDEX IF NOT EXISTS idx_condition ON dialectic_sessions(market_condition);
CREATE INDEX IF NOT EXISTS idx_confidence ON dialectic_sessions(outcome_confidence);
"""