import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'algovote.db')
SCHEMA = os.path.join(BASE_DIR, 'schema.sql')

def ensure_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        with open(SCHEMA, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()

def seed_sample_poll():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Skip if an active poll exists
    cur.execute('SELECT id FROM polls WHERE active = 1')
    if cur.fetchone():
        print('Active poll exists; skipping seed.')
        conn.close()
        return

    question = 'Who should be the Class Representative?'
    options = ['Candidate A', 'Candidate B', 'Candidate C', 'Candidate D']

    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO polls (question, active, created_at) VALUES (?, ?, ?)', (question, 1, now))
    poll_id = cur.lastrowid
    for opt in options:
        cur.execute('INSERT INTO options (poll_id, text) VALUES (?, ?)', (poll_id, opt))

    conn.commit()
    conn.close()
    print('Seeded sample poll and activated it. Poll id:', poll_id)

if __name__ == '__main__':
    ensure_db()
    seed_sample_poll()
