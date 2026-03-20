from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.database import get_db_connection

def register_farmer(name, phone, password, country, country_code, state, state_code, city):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if phone already exists
    cursor.execute("SELECT id FROM farmers WHERE phone = ?", (phone,))
    if cursor.fetchone():
        conn.close()
        return None, "Phone number already registered."
    
    password_hash = generate_password_hash(password)
    cursor.execute('''
        INSERT INTO farmers (name, phone, password_hash, country, country_code, state, state_code, city)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, password_hash, country, country_code, state, state_code, city))
    
    farmer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "id": farmer_id,
        "name": name,
        "phone": phone,
        "country": country,
        "country_code": country_code,
        "state": state,
        "state_code": state_code,
        "city": city
    }, None

def login_farmer(phone, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmers WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None, "Phone number not found."
    
    if not check_password_hash(row["password_hash"], password):
        return None, "Incorrect password."
    
    return {
        "id": row["id"],
        "name": row["name"],
        "phone": row["phone"],
        "country": row["country"],
        "country_code": row["country_code"],
        "state": row["state"],
        "state_code": row["state_code"],
        "city": row["city"]
    }, None

def login_admin(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None, "Admin not found."
    
    if not check_password_hash(row["password_hash"], password):
        return None, "Incorrect password."
    
    return {"id": row["id"], "username": row["username"], "role": "admin"}, None
