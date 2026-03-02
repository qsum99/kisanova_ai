import joblib
import numpy as np
import os
from app.config import Config

class ModelServiceError(Exception):
    pass

class ModelService:
    def __init__(self):
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Loads the model once into memory."""
        try:
            model_path = Config.MODEL_PATH
            if not os.path.exists(model_path):
                # Try a fallback to check if it's relative to the CWD
                fallback_path = os.path.join(os.getcwd(), 'backend', 'models', 'crop recommedation.pkl')
                if os.path.exists(fallback_path):
                    model_path = fallback_path
                else:
                    raise ModelServiceError(f"Model file not found at {model_path} or {fallback_path}")
                
            self.model = joblib.load(model_path)
            print(f"Model loaded successfully from {model_path}.")
        except Exception as e:
            raise ModelServiceError(f"Error loading model: {str(e)}")
            
    def predict(self, feature_list):
        """
        Takes a list of features: [N, P, K, temperature, humidity, ph, total_rainfall]
        Returns the recommended crop.
        """
        if not self.model:
            raise ModelServiceError("Model is not loaded.")
            
        # Format the data as a 2D numpy array
        features = np.array([feature_list])
        
        try:
            prediction = self.model.predict(features)
            return prediction[0]
        except Exception as e:
            raise ModelServiceError(f"Error during prediction: {str(e)}")
            
    def predict_proba(self, feature_list):
        """
        Takes a list of features: [N, P, K, temperature, humidity, ph, total_rainfall]
        Returns the confidence score (probability) of the top predicted crop.
        """
        if not self.model:
            raise ModelServiceError("Model is not loaded.")
            
        features = np.array([feature_list])
        
        try:
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba(features)
                # Max probability corresponds to the predicted class
                return float(np.max(probabilities[0]))
            else:
                # If the model does not support probabilities, return 1.0 (100%) or None
                return None
        except Exception as e:
            raise ModelServiceError(f"Error during probability prediction: {str(e)}")

# Create a singleton instance to be imported and used
model_service = ModelService()
