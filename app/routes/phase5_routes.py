"""
Phase 5 — Farm Management API Routes (Synchronous / On-Demand)
Fetches live data and decisions without background jobs.
"""
from flask import Blueprint, request, jsonify, session
from app.utils.database import get_db_connection
from app.services.smart_farm_service import (
    get_irrigation_decision,
    get_fertilizer_decision,
    get_farm_ndvi
)

phase5_bp = Blueprint('phase5', __name__)
phase5_pages_bp = Blueprint('phase5_pages', __name__)

@phase5_bp.route('/phase5/onboard', methods=['POST'])
def onboard_farm():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user_id = session.get("user", {}).get("id")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Upsert farmer_profile
        cursor.execute("SELECT id FROM farmer_profile WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE farmer_profile 
                SET lat=?, lon=?, crop_type=?, soil_type=?, planting_date=?, farm_size_ha=?, phone=?, language=?
                WHERE user_id=?
            ''', (data.get('lat'), data.get('lon'), data.get('crop_type'), data.get('soil_type'), 
                  data.get('planting_date'), data.get('farm_size_ha'), data.get('phone'), data.get('language'), user_id))
        else:
            cursor.execute('''
                INSERT INTO farmer_profile (user_id, lat, lon, crop_type, soil_type, planting_date, farm_size_ha, phone, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, data.get('lat'), data.get('lon'), data.get('crop_type'), data.get('soil_type'), 
                  data.get('planting_date'), data.get('farm_size_ha'), data.get('phone'), data.get('language')))
        
        conn.commit()
        return jsonify({"success": True, "message": "Farm onboarded successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@phase5_bp.route('/phase5/irrigation-data', methods=['GET'])
def get_irrigation_data():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user_id = session.get("user", {}).get("id")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmer_profile WHERE user_id = ?", (user_id,))
        farmer = cursor.fetchone()
        if not farmer: return jsonify({"error": "Farm not onboarded"}), 400
        
        decision = get_irrigation_decision(farmer["id"], farmer["lat"], farmer["lon"])
        return jsonify({"success": True, "decision": decision})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@phase5_bp.route('/phase5/fertilizer-data', methods=['GET'])
def get_fertilizer_data():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user_id = session.get("user", {}).get("id")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmer_profile WHERE user_id = ?", (user_id,))
        farmer = cursor.fetchone()
        if not farmer: return jsonify({"error": "Farm not onboarded"}), 400
        
        decision = get_fertilizer_decision(farmer["id"], farmer["lat"], farmer["lon"])
        return jsonify({"success": True, "decision": decision})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@phase5_bp.route('/phase5/farm-health-data', methods=['GET'])
def get_farm_health_data():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user_id = session.get("user", {}).get("id")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmer_profile WHERE user_id = ?", (user_id,))
        farmer = cursor.fetchone()
        if not farmer: return jsonify({"error": "Farm not onboarded"}), 400
        
        ndvi = get_farm_ndvi(farmer["lat"], farmer["lon"], farmer["crop_type"], farmer["planting_date"])
        return jsonify({"success": True, "ndvi": ndvi})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@phase5_bp.route('/phase5/admin/status', methods=['GET'])
def get_admin_status():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM farmer_profile")
        farmer_count = cursor.fetchone()[0]
        return jsonify({
            "success": True,
            "farmer_count": farmer_count,
            "system_health": "Good",
            "scheduler": {"running": False, "note": "Scheduler disabled. All endpoints are synchronous."}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()