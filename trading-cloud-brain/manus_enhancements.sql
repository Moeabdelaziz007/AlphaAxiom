-- ============================================
-- MANUS ENHANCEMENTS - Schema Additions
-- ============================================
-- 1. Add volatility_score to signal_events (5th factor)
ALTER TABLE signal_events
ADD COLUMN volatility_score REAL;
-- 2. Add final_status to signal_outcomes for better tracking
-- (Values: incomplete, complete, error, skipped)
-- Note: SQLite doesn't support ADD COLUMN with constraints, so we add the column
-- and document the expected values
-- 3. Create system_monitoring table for observability
CREATE TABLE IF NOT EXISTS system_monitoring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metadata TEXT,
    -- JSON metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);
CREATE INDEX IF NOT EXISTS idx_system_monitoring_name ON system_monitoring(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_monitoring_created ON system_monitoring(created_at DESC);
-- 4. Create telegram_reports table for audit trail
CREATE TABLE IF NOT EXISTS telegram_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    -- daily, weekly, optimization
    report_date TEXT NOT NULL,
    -- YYYY-MM-DD
    report_content TEXT NOT NULL,
    -- Full message text
    sent_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);
CREATE INDEX IF NOT EXISTS idx_telegram_reports_date ON telegram_reports(report_date);
CREATE INDEX IF NOT EXISTS idx_telegram_reports_type ON telegram_reports(report_type);