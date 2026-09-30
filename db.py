import os
import sqlite3


DB_FILE = os.environ.get("DB_FILE") or "reviews.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY,
        review TEXT NOT NULL,
        score INTEGER NOT NULL,
        label TEXT NOT NULL,
        theme TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()


def save_results(results):
    """Write all analyzed reviews into the database."""
    conn = sqlite3.connect(DB_FILE)
    for result in results:
        conn.execute(
            "INSERT INTO feedback (review, label, score, theme) VALUES (?, ?, ?, ?)",
            (result["review"], result["label"], result["score"], result["theme"]),
        )
    conn.commit()
    conn.close()


def load_history():
    """Read every review we have saved so far."""
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(
        "SELECT review, label, score, theme FROM feedback"
    ).fetchall()
    conn.close()
    return rows