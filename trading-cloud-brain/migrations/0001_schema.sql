-- Migration number: 0001 ⏱️ 2025-12-08T06:10:00Z
-- 1. Trades Table (The core ledger)
CREATE TABLE IF NOT EXISTS trades (
    id TEXT PRIMARY KEY,
    -- UUID
    symbol TEXT NOT NULL,
    -- e.g. EURUSD
    direction TEXT NOT NULL,
    -- BUY / SELL
    entry_price REAL NOT NULL,
    exit_price REAL,
    qty REAL NOT NULL,
    pnl REAL,
    status TEXT NOT NULL,
    -- OPEN, FILLED, CLOSED, CANCELED
    opened_at INTEGER NOT NULL,
    -- Unix Timestamp
    closed_at INTEGER,
    strategy TEXT,
    -- scalper / swing
    meta JSON -- Extra data (SL, TP, indicators)
);
-- Index for fast history lookup by symbol
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
-- Index for performance analysis over time
CREATE INDEX IF NOT EXISTS idx_trades_opened_at ON trades(opened_at);
-- 2. Signals Table (AI Decision Log)
CREATE TABLE IF NOT EXISTS signals (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    engine TEXT NOT NULL,
    -- AEXI, Dream, PatternScanner
    signal_type TEXT NOT NULL,
    -- BULLISH, BEARISH
    strength REAL,
    -- 0.0 - 1.0 (Confidence)
    timestamp INTEGER NOT NULL,
    raw_data JSON -- Full indicator values at that moment
);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);