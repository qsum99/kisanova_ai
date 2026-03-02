import joblib
import numpy as np
import os

def load_model():
    try:
        model_path="models/crop recommedation.pkl"
        if os.path.exists(model_path):
            return joblib.load(model_path)
    except Exception as e:
        print(f"Error loading model:{e}")
        return None
        
model=load_model()

def predict(feature_list):
    if model is None:
        return None
    features=np.array([feature_list])
    try:
        prediction=model.predict(features)
        return prediction[0]
    except Exception as e:
        print(f"Error during prdiction :{e}")
        return None
