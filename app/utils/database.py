import sqlite3
import os
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DB_PATH = os.path.join(BASE_DIR, 'database', 'farmer_ai.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crop_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            district TEXT,
            market TEXT,
            commodity TEXT,
            variety TEXT,
            arrival_date TEXT,
            min_price REAL,
            max_price REAL,
            modal_price REAL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            country TEXT,
            country_code TEXT,
            state TEXT,
            state_code TEXT,
            city TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Seed default admin if not exists
    cursor.execute("SELECT id FROM admins WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            ('admin', generate_password_hash('admin1234'))
        )
        print("[Database] Default admin account created (admin / admin1234)")
    
    # ── Phase 5 Tables ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmer_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lat REAL, lon REAL,
            crop_type TEXT, soil_type TEXT,
            planting_date TEXT,
            farm_size_ha REAL DEFAULT 1.0,
            phone TEXT, email TEXT,
            language TEXT DEFAULT 'en',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS irrigation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            action TEXT, amount_litres_per_ha INTEGER,
            water_saved_litres INTEGER DEFAULT 0,
            reason TEXT, weather_json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fertilizer_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            fertilizer_type TEXT,
            n_kg_ha REAL, p_kg_ha REAL, k_kg_ha REAL,
            timing TEXT, reason TEXT, soil_json TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ndvi_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            ndvi_score REAL, health_status TEXT,
            growth_stage TEXT, days_since_planting INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER NOT NULL,
            alert_type TEXT, severity TEXT,
            message TEXT, channel TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[Database] Initialized SQLite DB at {DB_PATH}")
