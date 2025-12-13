CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment TEXT DEFAULT 'neutral',
    raw_data TEXT
);
CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at DESC);
-- Daily AI Briefings
CREATE TABLE IF NOT EXISTS briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary TEXT,
    sentiment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_briefings_created ON briefings(created_at DESC);