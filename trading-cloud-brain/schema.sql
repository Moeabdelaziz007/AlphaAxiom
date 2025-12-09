DROP TABLE IF EXISTS market_ohlcv;
CREATE TABLE market_ohlcv (
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    source TEXT,
    PRIMARY KEY (symbol, timestamp)
);
DROP TABLE IF EXISTS market_signals;
CREATE TABLE market_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    type TEXT,
    data TEXT,
    -- JSON string
    confidence REAL
);
-- Index for fast signal retrieval
CREATE INDEX idx_signals_symbol_ts ON market_signals(symbol, timestamp);
-- ==========================================
-- 🧠 KNOWLEDGE GRAPH (Deep Research)
-- ==========================================
DROP TABLE IF EXISTS knowledge_nodes;
CREATE TABLE knowledge_nodes (
    id TEXT PRIMARY KEY,
    type TEXT,
    -- 'COIN', 'EVENT', 'INDICATOR', 'PERSON'
    data TEXT,
    -- JSON attributes
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);
DROP TABLE IF EXISTS knowledge_edges;
CREATE TABLE knowledge_edges (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    relation TEXT,
    -- 'CAUSES', 'CORRELATES_WITH', 'AFFECTS'
    weight REAL DEFAULT 1.0,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    PRIMARY KEY (source, target, relation)
);
CREATE INDEX idx_edges_source ON knowledge_edges(source);
CREATE INDEX idx_edges_target ON knowledge_edges(target);