from flask import Blueprint, request, jsonify
import os

disease_routes = Blueprint('disease_routes', __name__)

# Usually you would import your ML model here
# from app.services.disease_service import predict_disease

@disease_routes.route('/predict-disease', methods=['POST'])
def predict_disease_api():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded. Please upload a leaf image."}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file."}), 400
            
        # 1. Save or read the image in memory
        # 2. Preprocess the image (resize, normalize)
        # 3. Pass through the model to get the prediction
        # Example:
        # result = predict_disease(file)
        
        # MOCK RESPONSE FOR NOW (Until model is integrated)
        mock_result = {
            "disease_name": "Apple Scab",
            "confidence": 98.5,
            "treatment": "Use fungicides and ensure proper spacing for air circulation."
        }
        
        return jsonify(mock_result), 200
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
