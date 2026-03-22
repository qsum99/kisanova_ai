import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import requests
import datetime
from typing import List, Dict, Any
from app.config import GOV_API_KEY
from app.utils.database import get_db_connection

GOV_API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

def fetch_and_store_prices() -> int:
    if not GOV_API_KEY:
        raise ValueError("GOV_API_KEY is not configured in .env.")
        
    params = {
        "api-key": GOV_API_KEY,
        "format": "json",
        "limit": 10
    }
    
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
        query += " AND commodity LIKE ?"
        params.append(f"%{commodity}%")
    query += " ORDER BY modal_price DESC LIMIT 100"
    
    cursor.execute(query, params)
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
