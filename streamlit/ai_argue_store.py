# ai_argue_store.py
#
# SQLite persistence for AI Argue. Two databases share one schema:
#   data/debates.db   - curated; written only by scripts/run_batch.py, committed to git
#   data/web_runs.db  - visitor log; the page appends one row per debate run on the site (gitignored)

import json
import sqlite3
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
CURATED_DB = DATA_DIR / "debates.db"
WEB_DB = DATA_DIR / "web_runs.db"

COLUMNS = [
    "run_id", "batch_id", "condition", "rep", "timestamp_utc", "proposition",
    "model_a", "model_b", "model_j", "words_a", "words_b", "words_j_guidelines", "words_j_ruling",
    "rounds", "temperature", "winner", "ruling_text", "transcript_json", "judge_prompt_hash",
    "judge_disclosed_word_limits", "tokens_in", "tokens_out", "status", "source", "first_speaker",
]

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS debates (
    run_id TEXT PRIMARY KEY,
    batch_id TEXT,
    condition TEXT,
    rep INTEGER,
    timestamp_utc TEXT,
    proposition TEXT,
    model_a TEXT,
    model_b TEXT,
    model_j TEXT,
    words_a INTEGER,
    words_b INTEGER,
    words_j_guidelines INTEGER,
    words_j_ruling INTEGER,
    rounds INTEGER,
    temperature TEXT,
    winner TEXT,
    ruling_text TEXT,
    transcript_json TEXT,
    judge_prompt_hash TEXT,
    judge_disclosed_word_limits INTEGER,
    tokens_in INTEGER,
    tokens_out INTEGER,
    status TEXT,
    source TEXT,
    first_speaker TEXT
)
"""

# Batch 3 added first_speaker. Rows written before it (batches 1-2, older web runs) all had A first.
ADD_FIRST_SPEAKER = "ALTER TABLE debates ADD COLUMN first_speaker TEXT DEFAULT 'A'"


def connect(path, wal=False):
    """Open a database for writing, creating the directory and table if missing."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    if wal:
        conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(CREATE_TABLE)
    existing = {row[1] for row in conn.execute("PRAGMA table_info(debates)")}
    if "first_speaker" not in existing:
        conn.execute(ADD_FIRST_SPEAKER)
    conn.commit()
    return conn


def connect_readonly(path):
    """Open a database read-only. Raises sqlite3.OperationalError if it doesn't exist."""
    return sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)


def make_row(result, source, batch_id=None, condition=None, rep=None):
    """Turn a run_debate() result into a debates row."""
    transcript = {"statements": result["statements"], "usage": result["usage"]}
    if result.get("error"):
        transcript["error"] = result["error"]
    return {
        "run_id": str(uuid.uuid4()),
        "batch_id": batch_id,
        "condition": condition,
        "rep": rep,
        "timestamp_utc": result["timestamp_utc"],
        "proposition": result["proposition"],
        "model_a": result["model_a"],
        "model_b": result["model_b"],
        "model_j": result["model_j"],
        "words_a": result["words_a"],
        "words_b": result["words_b"],
        "words_j_guidelines": result["words_j1"],
        "words_j_ruling": result["words_j8"],
        "rounds": result["rounds"],
        "temperature": "default",
        "winner": result["winner"],
        "ruling_text": result["ruling_text"],
        "transcript_json": json.dumps(transcript, ensure_ascii=False),
        "judge_prompt_hash": result["judge_prompt_hash"],
        "judge_disclosed_word_limits": 1,   # the system prompt states both limits to all parties
        "tokens_in": result["tokens_in"],
        "tokens_out": result["tokens_out"],
        "status": result["status"],
        "source": source,
        "first_speaker": result.get("first_speaker", "A"),
    }


def insert_row(conn, row):
    placeholders = ", ".join("?" for _ in COLUMNS)
    conn.execute(
        f"INSERT INTO debates ({', '.join(COLUMNS)}) VALUES ({placeholders})",
        [row[c] for c in COLUMNS],
    )
    conn.commit()


def rows_for_batch(conn, batch_id):
    """{(condition, rep): [(status, winner), ...]} for one batch, oldest first."""
    found = {}
    cur = conn.execute(
        "SELECT condition, rep, status, winner FROM debates WHERE batch_id = ? ORDER BY timestamp_utc",
        (batch_id,),
    )
    for condition, rep, status, winner in cur:
        found.setdefault((condition, rep), []).append((status, winner))
    return found
