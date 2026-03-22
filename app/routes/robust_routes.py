from flask import Blueprint, request, jsonify

from app.engines.soil_engine import infer_soil_data
from app.engines.weather_engine import get_robust_weather
from app.engines.icar_rule_engine import apply_icar_filters
from app.engines.ml_yield_engine import get_yield_ranking
from app.engines.profit_engine import calculate_profitable_crops

robust_routes = Blueprint('robust_routes', __name__)

KNOWN_CROPS = [
    "rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans", "mungbean",
    "blackgram", "lentil", "pomegranate", "banana", "mango", "grapes", "watermelon",
    "muskmelon", "apple", "orange", "papaya", "coconut", "cotton", "jute", "coffee"
]

@robust_routes.route('/predict/robust', methods=['POST'])
def predict_robust_crop():
    """
    Robust prediction endpoint that handles missing soil/weather data gracefully
    and employs a multi-engine pipeline for accurate recommendations.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON payload provided"}), 400
            
        state = data.get("state", "")
        district = data.get("city_or_district", "")
        n = data.get("n")
        p = data.get("p")
        k = data.get("k")
        ph = data.get("ph")

        # 1. SOIL ENGINE
        soil_data = infer_soil_data(
            state=state,
            district=district,
            n=n, p=p, k=k, ph=ph
        )
        
        # 2. WEATHER ENGINE
        weather_data = get_robust_weather(
            city_name=district,
            state_name=state
        )
        
        # 3. ICAR RULE ENGINE
        feasible_crops = apply_icar_filters(
            crops=KNOWN_CROPS,
            temp=weather_data["temperature"],
            humidity=weather_data["humidity"],
            rainfall=weather_data["rainfall"],
            ph=soil_data["pH"]
        )
        
        if not feasible_crops:
            feasible_crops = KNOWN_CROPS
            
        # 4. ML YIELD ENGINE
        # The new yield model takes the state, rainfall, and crops to predict exact yield
        feasible_scores = get_yield_ranking(
            feasible_crops=feasible_crops,
            state=state,
            rainfall=weather_data["rainfall"]
        )

        # 5. PROFIT ENGINE
        final_recommendations = calculate_profitable_crops(feasible_scores)
        
        return jsonify({
            "success": True,
            "orchestration_metadata": {
                "inferred_soil": soil_data["inferred"],
                "inferred_weather": weather_data["inferred_weather"],
                "feasible_crops_count": len(feasible_crops)
            },
            "parameters_used": {
                "soil": soil_data,
                "weather": weather_data
            },
            "recommendations": final_recommendations[:5]
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
