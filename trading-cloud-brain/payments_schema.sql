-- ========================================
-- 💳 AXIOM PAYMENTS - D1 Schema
-- ========================================
-- Run this migration to add payment tables
-- ========================================
-- User OAuth connections (encrypted tokens)
CREATE TABLE IF NOT EXISTS user_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    -- 'coinbase', 'stripe'
    access_token TEXT NOT NULL,
    -- ENCRYPTED
    refresh_token TEXT,
    -- ENCRYPTED
    token_expires_at INTEGER,
    -- Unix timestamp (ms)
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    UNIQUE(user_id, provider)
);
-- Trade orders executed via platform
CREATE TABLE IF NOT EXISTS trade_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    -- 'coinbase'
    client_order_id TEXT NOT NULL,
    -- Our internal ID
    external_order_id TEXT,
    -- Coinbase order ID
    product_id TEXT NOT NULL,
    -- 'BTC-USD'
    side TEXT NOT NULL,
    -- 'BUY', 'SELL'
    order_type TEXT NOT NULL,
    -- 'MARKET', 'LIMIT'
    size TEXT,
    -- Base amount
    quote_size TEXT,
    -- Quote amount
    price TEXT,
    -- Limit price
    status TEXT DEFAULT 'PENDING',
    -- 'PENDING', 'FILLED', 'CANCELLED', 'FAILED'
    filled_size TEXT,
    filled_value TEXT,
    fee TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER
);
-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_connections_user ON user_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_orders_user ON trade_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_orders_client_id ON trade_orders(client_order_id);