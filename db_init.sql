CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY,
    call_time TIMESTAMP,
    from_name TEXT,
    from_number TEXT,
    destination TEXT,
    to_number TEXT,
    duration TEXT,
    download_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_call_time ON calls(call_time);