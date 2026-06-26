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
    send_farm_alert, get_growth_info
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

    return jsonify({
        "success": True,
        "decision": decision,
        "history": history,
        "water_saved_total": water_saved,
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

    return jsonify({
        "success": True,
        "decision": decision,
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