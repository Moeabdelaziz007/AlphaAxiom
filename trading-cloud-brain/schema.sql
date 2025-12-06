-- ANTIGRAVITY Trading Brain - D1 Schema
-- State persistence for trading rules, logs, and context
-- Trading Rules (Bot Memory)
CREATE TABLE IF NOT EXISTS trading_rules (
    rule_id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL,
    logic_json TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
-- Trade Logs (Audit Trail)
CREATE TABLE IF NOT EXISTS trade_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    action TEXT NOT NULL,
    qty INTEGER NOT NULL,
    price REAL,
    order_id TEXT,
    trigger_reason TEXT,
    executed_at TEXT DEFAULT CURRENT_TIMESTAMP
);
-- User Context (Chat Memory)
CREATE TABLE IF NOT EXISTS user_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
-- Circuit Breaker State
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
-- Initialize circuit breaker values
INSERT
    OR IGNORE INTO system_state (key, value)
VALUES ('trades_today', '0');
INSERT
    OR IGNORE INTO system_state (key, value)
VALUES ('max_trades_per_day', '10');
INSERT
    OR IGNORE INTO system_state (key, value)
VALUES ('kill_switch', 'false');
INSERT
    OR IGNORE INTO system_state (key, value)
VALUES ('starting_equity', '100000');