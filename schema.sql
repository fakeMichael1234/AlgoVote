-- Database schema for AlgoVote
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS polls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 0,
    created_at TEXT,
    closed_at TEXT
);

CREATE TABLE IF NOT EXISTS options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (poll_id) REFERENCES polls(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    option_id INTEGER NOT NULL,
    poll_id INTEGER,
    username TEXT,
    created_at TEXT,
    FOREIGN KEY (option_id) REFERENCES options(id) ON DELETE CASCADE
);
