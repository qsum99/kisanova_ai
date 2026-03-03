from flask import Blueprint, request, jsonify
from app.services import weather_service
from app.services import model_service

crop_routes = Blueprint('crop_routes', __name__)

@crop_routes.route('/predict', methods=['POST'])
def predict_crop():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request. Must send JSON payload."}), 400
        
        required_fields = ["N", "P", "K", "pH", "city_name", "state_code", "country_code"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
        try:
            n_val = float(data["N"])
            p_val = float(data["P"])
            k_val = float(data["K"])
            ph_val = float(data["pH"])
        except ValueError:
            return jsonify({"error": "Fields N, P, K, pH must be numbers."}), 400
            
        city_name = str(data["city_name"]).strip()
        state_code = str(data["state_code"]).strip()
        country_code = str(data["country_code"]).strip()
        if not city_name or not state_code or not country_code:
            return jsonify({"error": "Location details cannot be empty."}), 400
            
        weather_data = weather_service.get_weather_data(city_name, state_code, country_code)
        
        if not weather_data:
            return jsonify({"error": "Could not fetch weather data from API."}), 502
        
        temperature = weather_data["temperature"]
        humidity = weather_data["humidity"]
        rainfall_total = weather_data["rainfall_5day_total"]
        features = [n_val, p_val, k_val, temperature, humidity, ph_val, rainfall_total]

        recommended_crop = model_service.predict(features)

        # Convert numpy type to plain Python string for JSON serialization
        recommended_crop = str(recommended_crop)
    
        response = {
            "recommended_crop": recommended_crop,
            "weather_used": {
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "rainfall_5day_total": round(rainfall_total, 2)
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
