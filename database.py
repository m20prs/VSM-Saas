import sqlite3
from datetime import datetime

DB_NAME = "monitor_results.db"

def init_db():
    """Initializes the database and creates the results table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            timestamp DATETIME,
            status TEXT,
            mismatch_pixels INTEGER,
            baseline_path TEXT,
            current_path TEXT,
            diff_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_result(url, status, mismatch, base, curr, diff):
    """Logs the outcome of a visual check into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scan_history (url, timestamp, status, mismatch_pixels, baseline_path, current_path, diff_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, mismatch, base, curr, diff))
    conn.commit()
    conn.close()