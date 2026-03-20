from flask import Blueprint, request, jsonify, session

from app.services.auth_service import register_farmer, login_farmer, login_admin

auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/auth/register', methods=['POST'])
def register_api():
    data = request.get_json()
    required = ['name', 'phone', 'password', 'country', 'country_code', 'state', 'state_code', 'city']
    for field in required:
        if not data.get(field):
            return jsonify({"success": False, "error": f"'{field}' is required."}), 400
    
    farmer, error = register_farmer(
        name=data['name'],
        phone=data['phone'],
        password=data['password'],
        country=data['country'],
        country_code=data['country_code'],
        state=data['state'],
        state_code=data['state_code'],
        city=data['city']
    )
    
    if error:
        return jsonify({"success": False, "error": error}), 400
    
    # Auto-login after registration
    session['user'] = farmer
    session['role'] = 'farmer'
    return jsonify({"success": True, "user": farmer}), 201

@auth_routes.route('/auth/login', methods=['POST'])
def login_api():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    
    if not phone or not password:
        return jsonify({"success": False, "error": "Phone and password are required."}), 400
    
    farmer, error = login_farmer(phone, password)
    if error:
        return jsonify({"success": False, "error": error}), 401
    
    session['user'] = farmer
    session['role'] = 'farmer'
    return jsonify({"success": True, "user": farmer}), 200

@auth_routes.route('/auth/admin-login', methods=['POST'])
def admin_login_api():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required."}), 400
    
    admin, error = login_admin(username, password)
    if error:
        return jsonify({"success": False, "error": error}), 401
    
    session['user'] = admin
    session['role'] = 'admin'
    return jsonify({"success": True, "user": admin}), 200

@auth_routes.route('/auth/logout', methods=['POST'])
def logout_api():
    session.clear()
    return jsonify({"success": True, "message": "Logged out."}), 200

@auth_routes.route('/auth/me', methods=['GET'])
def me_api():
    user = session.get('user')
    role = session.get('role')
    if not user:
        return jsonify({"success": False, "logged_in": False}), 200
    return jsonify({"success": True, "logged_in": True, "role": role, "user": user}), 200
