import os
import sqlite3
from datetime import datetime
import json

# -------------------------
# Use persistent storage in /home
# -------------------------
HOME_DIR = os.environ.get("HOME", "/home")
DB_DIR = os.path.join(HOME_DIR, "app_data")

# Ensure the directory exists with proper permissions
try:
    os.makedirs(DB_DIR, exist_ok=True)
    # Set appropriate permissions (read/write for user, read for group/others)
    os.chmod(DB_DIR, 0o755)
except Exception as e:
    print(f"[WARNING] Could not create database directory: {e}")

DB_PATH = os.path.join(DB_DIR, "database.db")
print(f"[INFO] Using database path: {DB_PATH}")

# -------------------------
# Get connection with error handling
# -------------------------
def get_connection():
    try:
        # Add timeout to handle concurrent access
        conn = sqlite3.connect(
            DB_PATH, 
            check_same_thread=False,
            timeout=30.0
        )
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    except sqlite3.Error as e:
        print(f"[ERROR] Database connection failed: {e}")
        raise

# -------------------------
# Initialize DB with error handling
# -------------------------
def init_db():
    """Initialize database tables. Returns True if successful."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create user_predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_data TEXT NOT NULL,
                predicted_region TEXT,
                confidence REAL,
                status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create batch_predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                row_data TEXT NOT NULL,
                predicted_region TEXT,
                confidence REAL,
                status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_pred_created ON user_predictions(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_batch_pred_created ON batch_predictions(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_pred_region ON user_predictions(predicted_region)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_batch_pred_region ON batch_predictions(predicted_region)")
        
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"[INFO] Database initialized with tables: {[t['name'] for t in tables]}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database initialization failed: {e}")
        # Try to create database file with proper permissions
        try:
            if os.path.exists(DB_PATH):
                os.chmod(DB_PATH, 0o644)
        except:
            pass
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error during DB init: {e}")
        return False

# --------------------------
# Insert single prediction
# --------------------------
def insert_user_prediction(input_dict, predicted_region, confidence, status):
    try:
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
        return True
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to insert user prediction: {e}")
        return False

# --------------------------
# Insert batch predictions
# --------------------------
def insert_batch_prediction(filename, row_dict, predicted_region, confidence, status):
    try:
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
        return True
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to insert batch prediction: {e}")
        return False

# --------------------------
# Query all user predictions
# --------------------------
def get_all_user_predictions():
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, input_data, predicted_region, confidence, status, 
                   datetime(created_at) as created_at
            FROM user_predictions 
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to dictionaries
        return [
            {
                "id": row["id"],
                "input_data": json.loads(row["input_data"]),
                "predicted_region": row["predicted_region"],
                "confidence": row["confidence"],
                "status": row["status"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to fetch user predictions: {e}")
        return []

# --------------------------
# Query all batch predictions
# --------------------------
def get_all_batch_predictions():
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, filename, row_data, predicted_region, confidence, status,
                   datetime(created_at) as created_at
            FROM batch_predictions 
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row["id"],
                "filename": row["filename"],
                "row_data": json.loads(row["row_data"]),
                "predicted_region": row["predicted_region"],
                "confidence": row["confidence"],
                "status": row["status"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to fetch batch predictions: {e}")
        return []

# --------------------------
# Query region statistics
# --------------------------
def get_region_statistics():
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
                predicted_region,
                COUNT(*) as total,
                SUM(CASE WHEN status='ACCEPTED' THEN 1 ELSE 0 END) as accepted,
                AVG(confidence) as avg_confidence
            FROM (
                SELECT predicted_region, status, confidence FROM user_predictions
                WHERE predicted_region IS NOT NULL
                UNION ALL
                SELECT predicted_region, status, confidence FROM batch_predictions
                WHERE predicted_region IS NOT NULL
            )
            WHERE predicted_region IS NOT NULL
            GROUP BY predicted_region
            ORDER BY total DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "region": row["predicted_region"],
                "total": row["total"],
                "accepted": row["accepted"],
                "rejected": row["total"] - row["accepted"],
                "avg_confidence": round(row["avg_confidence"], 3) if row["avg_confidence"] else 0
            }
            for row in rows
        ]
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to fetch region statistics: {e}")
        return []

# --------------------------
# Health check function
# --------------------------
def check_database_health():
    """Check if database is accessible and tables exist."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user_predictions', 'batch_predictions')
        """)
        
        tables = cursor.fetchall()
        conn.close()
        
        return {
            "status": "healthy" if len(tables) == 2 else "tables_missing",
            "tables_found": [t[0] for t in tables]
        }
        
    except sqlite3.Error as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# --------------------------
# Initialize on import (optional - can be called manually)
# --------------------------
# Note: In Azure App Service, it's better to initialize DB lazily
# Remove this if you're calling init_db() from your main app
# init_db()