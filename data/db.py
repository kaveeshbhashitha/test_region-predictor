import os
import sqlite3
from datetime import datetime
import json

# DB Path Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "Data", "database.db")

# Helper to get connection
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dict-like access
    return conn

# Initialize DB
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_data TEXT NOT NULL,
            predicted_region TEXT,
            confidence REAL,
            status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batch_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            row_data TEXT NOT NULL,
            predicted_region TEXT,
            confidence REAL,
            status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"[INFO] Database initialized at: {DB_PATH}")

# --------------------------
# Insert single prediction
# --------------------------
def insert_user_prediction(input_dict, predicted_region, confidence, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_predictions 
        (input_data, predicted_region, confidence, status)
        VALUES (?, ?, ?, ?)
    """, (
        json.dumps(input_dict),
        predicted_region,
        confidence,
        status
    ))

    conn.commit()
    conn.close()

# --------------------------
# Insert batch predictions
# --------------------------
def insert_batch_prediction(filename, row_dict, predicted_region, confidence, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO batch_predictions
        (filename, row_data, predicted_region, confidence, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        filename,
        json.dumps(row_dict),
        predicted_region,
        confidence,
        status
    ))

    conn.commit()
    conn.close()


# --------------------------
# Query all user predictions
# --------------------------
def get_all_user_predictions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_predictions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --------------------------
# Query all batch predictions
# --------------------------
def get_all_batch_predictions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM batch_predictions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Query to get statistics per region
def get_region_statistics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            predicted_region,
            COUNT(*) as total,
            SUM(CASE WHEN status='ACCEPTED' THEN 1 ELSE 0 END) as accepted,
            AVG(confidence) as avg_confidence
        FROM (
            SELECT predicted_region, status, confidence FROM user_predictions
            UNION ALL
            SELECT predicted_region, status, confidence FROM batch_predictions
        )
        GROUP BY predicted_region
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "region": r["predicted_region"],
            "total": r["total"],
            "accepted": r["accepted"],
            "rejected": r["total"] - r["accepted"],
            "avg_confidence": round(r["avg_confidence"], 3) if r["avg_confidence"] else None
        }
        for r in rows
    ]