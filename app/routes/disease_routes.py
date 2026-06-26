from flask import Blueprint, request, jsonify, session
from app.services.disease_service import predict_disease
from app.utils.database import get_db_connection

disease_routes = Blueprint('disease_routes', __name__)

@disease_routes.route('/predict-disease', methods=['POST'])
def predict_disease_api():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded. Please upload a leaf image."}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file."}), 400
        
        result = predict_disease(file)
        if result is None:
            return jsonify({"error": "Could not generate prediction. Ensure the file is a valid image and the model is loaded."}), 500
        
        # Store in database if user is logged in
        user_id = session.get("user", {}).get("id") if 'user' in session else None
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO disease_scans_log (farmer_id, image_filename, detected_disease, confidence) VALUES (?, ?, ?, ?)",
                (user_id, file.filename, result.get("disease", "Unknown"), float(result.get("confidence", 0.0)))
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Database] Log disease scan error: {e}")
            
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
