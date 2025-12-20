PRAGMA foreign_keys = ON;

-- =========================
-- TOR RELAYS (Authoritative)
-- =========================
CREATE TABLE IF NOT EXISTS relays (
    relay_id TEXT PRIMARY KEY,        -- Base64 fingerprint
    nickname TEXT NOT NULL,
    ip TEXT NOT NULL,

    is_guard INTEGER NOT NULL,         -- 0 / 1
    is_exit INTEGER NOT NULL,          -- 0 / 1
    is_bad_exit INTEGER NOT NULL,      -- BadExit or MiddleOnly

    bandwidth INTEGER NOT NULL,        -- Consensus weight
    published DATETIME NOT NULL,       -- From r-line timestamp

    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_relays_ip ON relays(ip);
CREATE INDEX idx_relays_guard ON relays(is_guard);
CREATE INDEX idx_relays_exit ON relays(is_exit);

-- =========================
-- TOR SESSIONS (Observed)
-- =========================
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    exit_ip TEXT NOT NULL,

    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL
);

CREATE INDEX idx_sessions_exit_ip ON sessions(exit_ip);

-- =========================
-- CORRELATION RESULTS
-- =========================
CREATE TABLE IF NOT EXISTS correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    session_id TEXT NOT NULL,
    relay_id TEXT NOT NULL,

    score REAL NOT NULL,               -- Raw correlation score
    confidence REAL NOT NULL,          -- Normalized probability (0–1)

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(session_id) REFERENCES sessions(session_id),
    FOREIGN KEY(relay_id) REFERENCES relays(relay_id)
);

CREATE INDEX idx_corr_session ON correlations(session_id);
CREATE INDEX idx_corr_relay ON correlations(relay_id);

-- =========================
-- FORENSIC EVIDENCE
-- =========================
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    type TEXT NOT NULL,                -- pcap | log
    sha256 TEXT NOT NULL,

    ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flows (
    flow_id INTEGER PRIMARY KEY AUTOINCREMENT,

    evidence_id TEXT NOT NULL,

    client_ip TEXT NOT NULL,
    server_ip TEXT NOT NULL,
    client_port INTEGER NOT NULL,
    server_port INTEGER NOT NULL,

    protocol TEXT NOT NULL,

    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,

    packet_count INTEGER NOT NULL,
    byte_count INTEGER NOT NULL,

    FOREIGN KEY(evidence_id) REFERENCES evidence(evidence_id)
);

CREATE INDEX IF NOT EXISTS idx_flows_server_ip ON flows(server_ip);
CREATE INDEX IF NOT EXISTS idx_flows_time ON flows(start_time, end_time);
