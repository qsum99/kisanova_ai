"""
Phase 5 — Farm Management API Routes (Production)
Every API call fetches live data, stores decisions in DB, returns real history.
"""
import json
from flask import Blueprint, request, jsonify, session
from app.utils.database import get_db_connection
from app.services.smart_farm_service import (
    get_irrigation_decision, get_irrigation_history, get_total_water_saved,
    get_fertilizer_decision,
    get_farm_ndvi, get_ndvi_history,
    send_farm_alert, get_growth_info,
    get_farmer_activity_history
)

phase5_bp = Blueprint('phase5', __name__)
phase5_pages_bp = Blueprint('phase5_pages', __name__)


def _get_farmer_profile(user_id):
    """Helper to fetch farmer profile from DB as a plain dict."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM farmer_profile WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


@phase5_bp.route('/phase5/onboard', methods=['POST'])
def onboard_farm():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user_id = session.get("user", {}).get("id")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM farmer_profile WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()

        # Extract email from phone/contact field if it has @
        contact = data.get('phone', '')
        email = contact if '@' in str(contact) else ''
        phone = contact if '@' not in str(contact) else ''

        if existing:
            cursor.execute('''
                UPDATE farmer_profile
                SET lat=?, lon=?, crop_type=?, soil_type=?, planting_date=?,
                    farm_size_ha=?, phone=?, email=?, language=?
                WHERE user_id=?
            ''', (data.get('lat'), data.get('lon'), data.get('crop_type'),
                  data.get('soil_type'), data.get('planting_date'),
                  data.get('farm_size_ha', 1.0), phone, email,
                  data.get('language', 'en'), user_id))
        else:
            cursor.execute('''
                INSERT INTO farmer_profile
                (user_id, lat, lon, crop_type, soil_type, planting_date, farm_size_ha, phone, email, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, data.get('lat'), data.get('lon'), data.get('crop_type'),
                  data.get('soil_type'), data.get('planting_date'),
                  data.get('farm_size_ha', 1.0), phone, email,
                  data.get('language', 'en')))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Farm profile saved successfully! Your smart alerts are now active."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phase5_bp.route('/phase5/irrigation-data', methods=['GET'])
def get_irrigation_data():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get("user", {}).get("id")
    farmer = _get_farmer_profile(user_id)
    if not farmer:
        return jsonify({"success": False, "error": "Farm not set up. Go to Farm Setup first."}), 200

    decision = get_irrigation_decision(
        farmer["id"], farmer["lat"], farmer["lon"],
        farmer["crop_type"], farmer["soil_type"],
        farmer["planting_date"], farmer.get("farm_size_ha", 1.0)
    )
    history = get_irrigation_history(farmer["id"], limit=10)
    water_saved = get_total_water_saved(farmer["id"])
    activities = get_farmer_activity_history(farmer["id"], limit=10)

    return jsonify({
        "success": True,
        "decision": decision,
        "history": history,
        "water_saved_total": water_saved,
        "activities": activities,
        "crop_type": farmer["crop_type"],
        "farm_size_ha": farmer.get("farm_size_ha", 1.0)
    })


@phase5_bp.route('/phase5/fertilizer-data', methods=['GET'])
def get_fertilizer_data():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get("user", {}).get("id")
    farmer = _get_farmer_profile(user_id)
    if not farmer:
        return jsonify({"success": False, "error": "Farm not set up."}), 200

    decision = get_fertilizer_decision(
        farmer["id"], farmer["lat"], farmer["lon"],
        farmer["crop_type"], farmer["soil_type"],
        farmer["planting_date"]
    )
    activities = get_farmer_activity_history(farmer["id"], limit=10)

    return jsonify({
        "success": True,
        "decision": decision,
        "activities": activities,
        "crop_type": farmer["crop_type"],
        "soil_type": farmer["soil_type"]
    })


@phase5_bp.route('/phase5/farm-health-data', methods=['GET'])
def get_farm_health_data():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get("user", {}).get("id")
    farmer = _get_farmer_profile(user_id)
    if not farmer:
        return jsonify({"success": False, "error": "Farm not set up."}), 200

    ndvi = get_farm_ndvi(farmer["crop_type"], farmer["planting_date"])

    # Store in DB
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO ndvi_log (farmer_id, ndvi_score, health_status, growth_stage, days_since_planting) VALUES (?,?,?,?,?)",
            (farmer["id"], ndvi["ndvi_score"], ndvi["health"], ndvi["growth_stage"], ndvi["days_since_planting"])
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

    ndvi_history = get_ndvi_history(farmer["id"], limit=30)

    return jsonify({
        "success": True,
        "ndvi": ndvi,
        "ndvi_history": ndvi_history,
        "farmer_profile": {
            "crop_type": farmer["crop_type"],
            "soil_type": farmer["soil_type"],
            "planting_date": farmer["planting_date"],
            "farm_size_ha": farmer.get("farm_size_ha", 1.0)
        }
    })


@phase5_bp.route('/phase5/send-alert', methods=['POST'])
def send_alert():
    """Send daily farm alert email to the logged-in farmer."""
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get("user", {}).get("id")
    farmer = _get_farmer_profile(user_id)
    if not farmer:
        return jsonify({"error": "Farm not set up."}), 400

    # Generate all decisions
    irr = get_irrigation_decision(
        farmer["id"], farmer["lat"], farmer["lon"],
        farmer["crop_type"], farmer["soil_type"],
        farmer["planting_date"], farmer.get("farm_size_ha", 1.0)
    )
    fert = get_fertilizer_decision(
        farmer["id"], farmer["lat"], farmer["lon"],
        farmer["crop_type"], farmer["soil_type"],
        farmer["planting_date"]
    )
    ndvi = get_farm_ndvi(farmer["crop_type"], farmer["planting_date"])

    farmer_dict = dict(farmer)
    success = send_farm_alert(farmer_dict, irr, fert, ndvi)

    if success:
        return jsonify({"success": True, "message": f"Alert email sent to {farmer['email']}!"})
    else:
        return jsonify({"success": False, "message": "Email could not be sent. Check SMTP settings or provide a valid email in Farm Setup."})


@phase5_bp.route('/phase5/log-activity', methods=['POST'])
def log_activity():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session.get("user", {}).get("id")
    farmer = _get_farmer_profile(user_id)
    if not farmer:
        return jsonify({"error": "Farm not set up."}), 400

    data = request.json
    activity_type = data.get("activity_type")  # e.g., 'watered', 'skipped', 'fertilized'
    detail = data.get("detail", "")
    amount = data.get("amount", 0.0)

    if not activity_type:
        return jsonify({"error": "Missing activity_type"}), 400

    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO farmer_activity (farmer_id, activity_type, detail, amount) VALUES (?, ?, ?, ?)",
            (farmer["id"], activity_type, detail, amount)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Successfully logged {activity_type} activity."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phase5_bp.route('/phase5/admin/status', methods=['GET'])
def get_admin_status():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        farmer_count = conn.execute("SELECT COUNT(*) FROM farmer_profile").fetchone()[0]
        irrigation_count = conn.execute("SELECT COUNT(*) FROM irrigation_log").fetchone()[0]
        fertilizer_count = conn.execute("SELECT COUNT(*) FROM fertilizer_log").fetchone()[0]
        alerts_count = conn.execute("SELECT COUNT(*) FROM alerts_log").fetchone()[0]
        conn.close()

        return jsonify({
            "success": True,
            "farmer_count": farmer_count,
            "total_irrigation_decisions": irrigation_count,
            "total_fertilizer_decisions": fertilizer_count,
            "total_alerts_sent": alerts_count,
            "system_health": "Online",
            "mode": "On-Demand (Synchronous)"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phase5_bp.route('/phase5/admin/farmers', methods=['GET'])
def admin_get_farmers():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        rows = conn.execute('''
            SELECT fp.*, f.name, f.phone as auth_phone 
            FROM farmer_profile fp 
            JOIN farmers f ON fp.user_id = f.id
            ORDER BY fp.created_at DESC
        ''').fetchall()
        conn.close()
        return jsonify({"success": True, "farmers": [dict(r) for r in rows]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phase5_bp.route('/phase5/admin/activities', methods=['GET'])
def admin_get_activities():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        rows = conn.execute('''
            SELECT fa.*, fp.crop_type, f.name 
            FROM farmer_activity fa 
            JOIN farmer_profile fp ON fa.farmer_id = fp.id 
            JOIN farmers f ON fp.user_id = f.id 
            ORDER BY fa.logged_at DESC LIMIT 50
        ''').fetchall()
        conn.close()
        return jsonify({"success": True, "activities": [dict(r) for r in rows]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phase5_bp.route('/phase5/admin/recommendations', methods=['GET'])
def admin_get_recommendations():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        rows = conn.execute('''
            SELECT il.*, fp.crop_type, f.name 
            FROM irrigation_log il 
            JOIN farmer_profile fp ON il.farmer_id = fp.id 
            JOIN farmers f ON fp.user_id = f.id 
            ORDER BY il.created_at DESC LIMIT 50
        ''').fetchall()
        conn.close()
        
        recommendations = []
        for r in rows:
            w = {}
            try:
                w = json.loads(r["weather_json"]) if r["weather_json"] else {}
            except Exception:
                pass
            recommendations.append({
                "id": r["id"],
                "farmer_id": r["farmer_id"],
                "name": r["name"],
                "crop_type": r["crop_type"],
                "action": r["action"],
                "amount": r["amount_litres_per_ha"],
                "water_saved": r["water_saved_litres"],
                "reason": r["reason"],
                "weather": w,
                "created_at": r["created_at"]
            })
        return jsonify({"success": True, "recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phase5_bp.route('/phase5/admin/simulate-rain', methods=['POST'])
def admin_simulate_rain():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    data = request.json
    farmer_id = data.get("farmer_id")
    amount = data.get("amount", 25.0)  # default 25mm rain

    if not farmer_id:
        return jsonify({"error": "Missing farmer_id"}), 400

    try:
        conn = get_db_connection()
        
        # Check if farmer profile exists
        farmer = conn.execute("SELECT * FROM farmer_profile WHERE id = ?", (farmer_id,)).fetchone()
        if not farmer:
            conn.close()
            return jsonify({"error": "Farmer profile not found"}), 404

        conn.execute(
            "INSERT INTO farmer_activity (farmer_id, activity_type, detail, amount) VALUES (?, ?, ?, ?)",
            (farmer_id, "watered", f"Simulated Rain Event: {amount}mm of heavy rainfall", int(amount * 10000))
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Successfully simulated {amount}mm rain for farmer {farmer_id}."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phase5_bp.route('/phase5/admin/delete-farmer/<int:farmer_id>', methods=['POST'])
def admin_delete_farmer(farmer_id):
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM farmer_profile WHERE id = ?", (farmer_id,))
        conn.execute("DELETE FROM irrigation_log WHERE farmer_id = ?", (farmer_id,))
        conn.execute("DELETE FROM fertilizer_log WHERE farmer_id = ?", (farmer_id,))
        conn.execute("DELETE FROM ndvi_log WHERE farmer_id = ?", (farmer_id,))
        conn.execute("DELETE FROM farmer_activity WHERE farmer_id = ?", (farmer_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Deleted farmer profile {farmer_id}."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phase5_bp.route('/phase5/admin/trigger-alert/<int:farmer_id>', methods=['POST'])
def admin_trigger_alert(farmer_id):
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        farmer = conn.execute("SELECT * FROM farmer_profile WHERE id = ?", (farmer_id,)).fetchone()
        conn.close()
        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404

        farmer_dict = dict(farmer)
        
        # Calculate daily parameters to construct alert
        irr = get_irrigation_decision(
            farmer_dict["id"], farmer_dict["lat"], farmer_dict["lon"],
            farmer_dict["crop_type"], farmer_dict["soil_type"],
            farmer_dict["planting_date"], farmer_dict.get("farm_size_ha", 1.0)
        )
        fert = get_fertilizer_decision(
            farmer_dict["id"], farmer_dict["lat"], farmer_dict["lon"],
            farmer_dict["crop_type"], farmer_dict["soil_type"],
            farmer_dict["planting_date"]
        )
        ndvi = get_farm_ndvi(farmer_dict["crop_type"], farmer_dict["planting_date"])

        success = send_farm_alert(farmer_dict, irr, fert, ndvi)
        if success:
            return jsonify({"success": True, "message": f"Successfully sent alert email to {farmer_dict['email']}!"})
        else:
            return jsonify({"success": False, "message": "Failed to send alert. Check SMTP configuration or target email address."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500