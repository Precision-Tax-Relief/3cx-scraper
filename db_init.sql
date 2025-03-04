CREATE TABLE IF NOT EXISTS calls (
    id TEXT PRIMARY KEY,
    call_end TIMESTAMP,
    from_name TEXT,
    from_number TEXT,
    dialed TEXT,
    to_number TEXT,
    duration TEXT,
    download_url TEXT,
    filename TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_call_end ON calls(call_end, id);
CREATE INDEX IF NOT EXISTS idx_filename ON calls(filename, call_end, download_url, id);
