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

    # Table for single user predictions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_data TEXT NOT NULL,
            prediction TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for batch predictions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batch_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            row_data TEXT NOT NULL,
            prediction TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"[INFO] Database initialized at: {DB_PATH}")

# --------------------------
# Insert single prediction
# --------------------------
def insert_user_prediction(input_dict, prediction):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_predictions (input_data, prediction)
        VALUES (?, ?)
    """, (json.dumps(input_dict), str(prediction)))

    conn.commit()
    conn.close()

# --------------------------
# Insert batch predictions
# --------------------------
def insert_batch_prediction(filename, row_dict, prediction):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO batch_predictions (filename, row_data, prediction)
        VALUES (?, ?, ?)
    """, (filename, json.dumps(row_dict), str(prediction)))

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
