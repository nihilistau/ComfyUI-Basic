import sqlite3
from pathlib import Path
import json
import os
from typing import Optional, List

DRIVE_ROOT = Path(os.environ.get('DRIVE_ROOT', '/content/drive/MyDrive/ComfyUI'))
DB_PATH = DRIVE_ROOT / 'state' / 'queue.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_conn():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at REAL DEFAULT (strftime('%s','now'))
        )
    ''')
    conn.commit()
    return conn

def enqueue(item: dict):
    conn = init_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO queue (item_json, status) VALUES (?,?)', (json.dumps(item), 'pending'))
    conn.commit()
    return cur.lastrowid

def dequeue() -> Optional[dict]:
    conn = init_db()
    cur = conn.cursor()
    cur.execute("SELECT id, item_json FROM queue WHERE status='pending' ORDER BY id LIMIT 1")
    row = cur.fetchone()
    if not row:
        return None
    id_, j = row
    cur.execute("UPDATE queue SET status='processing' WHERE id=?", (id_,))
    conn.commit()
    return {'id': id_, 'item': json.loads(j)}

def mark_done(id_: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE queue SET status='done' WHERE id=?", (id_,))
    conn.commit()

def list_items(status: Optional[str]=None) -> List[dict]:
    conn = init_db()
    cur = conn.cursor()
    if status:
        cur.execute('SELECT id, item_json, status, created_at FROM queue WHERE status=? ORDER BY id', (status,))
    else:
        cur.execute('SELECT id, item_json, status, created_at FROM queue ORDER BY id')
    rows = cur.fetchall()
    out = []
    for r in rows:
        out.append({'id': r[0], 'item': json.loads(r[1]), 'status': r[2], 'created_at': r[3]})
    return out

def migrate_from_json(json_path: str):
    p = Path(json_path)
    if not p.exists():
        return 0
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    count = 0
    for item in data.get('queue', []):
        enqueue(item)
        count += 1
    return count
