from flask import Blueprint, request, jsonify
from app.services.weather_service import fetch_weather_features, WeatherServiceError
from app.services.model_service import model_service, ModelServiceError

crop_routes = Blueprint('crop_routes', __name__)

@crop_routes.route('/predict', methods=['POST'])
def predict_crop():
    """
    Predicts the best crop given soil nutrients and location.
    Expects JSON payload:
    {
        "N": float,
        "P": float,
        "K": float,
        "pH": float,
        "location": "City Name OR lat,lon"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request. Must send JSON payload."}), 400
            
        # 1. Input Validation
        required_fields = ["N", "P", "K", "pH", "location"]
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
            
        location = str(data["location"]).strip()
        if not location:
            return jsonify({"error": "Location cannot be empty."}), 400
            
        # 2. Fetch Weather Data
        weather_data = fetch_weather_features(location)
        
        temperature = weather_data["temperature"]
        humidity = weather_data["humidity"]
        rainfall_total = weather_data["rainfall_5day_total"]
        
        # 3. Construct feature list
        # Order must exactly match: [N, P, K, temperature, humidity, ph, total_rainfall]
        features = [n_val, p_val, k_val, temperature, humidity, ph_val, rainfall_total]
        
        # 4. Get Prediction
        recommended_crop = model_service.predict(features)
        
        # 5. Get Confidence
        confidence = model_service.predict_proba(features)
        
        # If the prediction is returned as a numpy type, convert to standard python type
        if hasattr(recommended_crop, "item"):
            recommended_crop = recommended_crop.item()
            
        # 6. Construct Response
        response = {
            "recommended_crop": recommended_crop,
            "confidence": round(confidence, 4) if confidence is not None else None,
            "weather_used": {
                "temperature": round(temperature, 2),
                "humidity": round(humidity, 2),
                "rainfall_5day_total": round(rainfall_total, 2)
            }
        }
        
        return jsonify(response), 200
        
    except WeatherServiceError as we:
        return jsonify({"error": f"Weather API Error: {str(we)}"}), 502
    except ModelServiceError as me:
        return jsonify({"error": f"Model Error: {str(me)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
