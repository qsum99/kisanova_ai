import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
import datetime
from typing import List, Dict, Any
from app.config import GOV_API_KEY
from app.utils.database import get_db_connection

GOV_API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

CROP_ALIASES = {
    "rice": ["rice", "paddy", "dhan"],
    "cotton": ["cotton", "kapas"],
    "maize": ["maize", "makka", "corn"],
    "mungbean": ["green gram", "moong", "mung"],
    "blackgram": ["black gram", "urad"],
    "lentil": ["lentil", "masur", "masoor"],
    "chickpea": ["chana", "gram", "chickpea", "bengal gram"],
    "kidneybeans": ["rajma", "kidney bean"],
    "pigeonpeas": ["tur", "arhar", "red gram", "pigeon"],
    "mothbeans": ["moth", "dew gram"],
    "pomegranate": ["pomegranate", "anar"],
    "banana": ["banana", "kele"],
    "mango": ["mango", "aam"],
    "grapes": ["grapes", "angoor"],
    "watermelon": ["watermelon", "tarbuj"],
    "muskmelon": ["muskmelon", "kharbuja"],
    "apple": ["apple", "seb"],
    "orange": ["orange", "santra"],
    "papaya": ["papaya", "papita"],
    "coconut": ["coconut", "nariyal"],
    "jute": ["jute"],
    "coffee": ["coffee"]
}

def fetch_and_store_prices(state_filter: str = None) -> int:
    if not GOV_API_KEY:
        raise ValueError("GOV_API_KEY is not configured in .env.")
        
    params = {
        "api-key": GOV_API_KEY,
        "format": "json",
    }
    
    if state_filter:
        params["filters[state]"] = state_filter
        params["limit"] = 2000 # Max for specific states
    else:
        params["limit"] = 10000
    
    try:
        print(f"[market_price_service] Fetching data from {GOV_API_URL}")
        response = requests.get(GOV_API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        records = data.get("records", [])
        if not records:
            print("[market_price_service] No records fetched.")
            return 0
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Only wipe the database if we are pulling a global snapshot
        if not state_filter:
            cursor.execute("DELETE FROM crop_prices")
        
        insert_query = '''
            INSERT INTO crop_prices 
            (state, district, market, commodity, variety, arrival_date, min_price, max_price, modal_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        inserted_count = 0
        for r in records:
            state = r.get("state", "Unknown")
            district = r.get("district", "Unknown")
            market = r.get("market", "Unknown")
            commodity = r.get("commodity", "Unknown")
            variety = r.get("variety", "Unknown")
            arrival_date = r.get("arrival_date", "")
    
            def parse_price(val):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0.0
            
            min_price = parse_price(r.get("min_price", 0))
            max_price = parse_price(r.get("max_price", 0))
            modal_price = parse_price(r.get("modal_price", 0))
            
            cursor.execute(insert_query, (
                state, district, market, commodity, variety, arrival_date, min_price, max_price, modal_price
            ))
            inserted_count += 1
            
        conn.commit()
        conn.close()
        
        print(f"[market_price_service] Successfully stored {inserted_count} price records.")
        return inserted_count
        
    except requests.exceptions.RequestException as e:
        print(f"[market_price_service] API Error: {e}")
        raise
    except Exception as e:
        print(f"[market_price_service] Database/Processing Error: {e}")
        raise


def check_and_refresh_cache():
    """Checks if the database is empty or older than 12 hours, and updates if necessary."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_updated FROM crop_prices LIMIT 1")
    row = cursor.fetchone()
    
    needs_refresh = False
    if not row:
        needs_refresh = True
    else:
        last_updated_str = row["last_updated"]
        try:
            last_updated = datetime.datetime.strptime(last_updated_str, "%Y-%m-%d %H:%M:%S")
            if (datetime.datetime.utcnow() - last_updated).total_seconds() > 12 * 3600:
                needs_refresh = True
        except ValueError:
            # Fallback if parsing fails
            needs_refresh = True
            
    conn.close()
    
    if needs_refresh:
        print("[market_price_service] Cache empty or expired (>12 hours). Auto-refreshing data...")
        try:
            fetch_and_store_prices()
        except Exception as e:
            print(f"[market_price_service] Failed to auto-refresh cache: {e}")

def get_latest_prices(state: str=None, commodity: str=None) -> List[Dict[str, Any]]:
    check_and_refresh_cache()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM crop_prices WHERE 1=1"
    params = []
    
    if state:
        query += " AND state LIKE ?"
        params.append(f"%{state}%")
    if commodity:
        c_clean = str(commodity).lower().strip()
        aliases = CROP_ALIASES.get(c_clean, [c_clean])
        
        like_clauses = ["commodity LIKE ?"] * len(aliases)
        query += f" AND ({' OR '.join(like_clauses)})"
        for alias in aliases:
            params.append(f"%{alias}%")
            
    query += " ORDER BY modal_price DESC LIMIT 100"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # [Dynamic State Caching] If we pulled less than 20 rows dynamically for a specific state,
    # let's trigger an on-the-fly fetch strictly for that State!
    if state and len(rows) < 20:
        try:
            print(f"[market_price_service] Auto-expanding cache for state: {state}")
            fetch_and_store_prices(state_filter=state)
            cursor.execute(query, params) # Re-run query after populating
            rows = cursor.fetchall()
        except Exception as e:
            print(f"[market_price_service] Dynamic cache expansion failed: {e}")
            
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "state": row["state"],
            "district": row["district"],
            "market": row["market"],
            "commodity": row["commodity"],
            "variety": row["variety"],
            "arrival_date": row["arrival_date"],
            "min_price": row["min_price"],
            "max_price": row["max_price"],
            "modal_price": row["modal_price"],
            "last_updated": row["last_updated"]
        })
        
    conn.close()
    print(result)
    return result

def get_top_crops(limit: int = 30) -> List[Dict[str, Any]]:
    check_and_refresh_cache()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM crop_prices ORDER BY modal_price DESC LIMIT ?"
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "state": row["state"],
            "district": row["district"],
            "market": row["market"],
            "commodity": row["commodity"],
            "variety": row["variety"],
            "arrival_date": row["arrival_date"],
            "min_price": row["min_price"],
            "max_price": row["max_price"],
            "modal_price": row["modal_price"],
            "last_updated": row["last_updated"]
        })
        
    conn.close()
    return result

if __name__ == "__main__":
    get_latest_prices()
