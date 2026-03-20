from flask import Blueprint, request, jsonify
from app.services.disease_service import predict_disease

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
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500
