import joblib
import pandas as pd
import os
from typing import List, Tuple, Dict, Any

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'yield_model.pkl')
try:
    yield_model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"[ml_yield_engine] Error loading yield_model.pkl: {e}")
    yield_model = None

def get_yield_ranking(feasible_crops: List[str], state: str, rainfall: float, season: str = "Whole Year") -> List[Tuple[str, float]]:

    if yield_model is None:
        raise ValueError("ML Yield Model is not loaded. Cannot rank crops.")
        
    crop_yields = []
    
    for crop in feasible_crops:
        best_yield_for_crop = 0.0
        
        input_df = pd.DataFrame([{
            "Crop": crop,
            "Season": season.strip(),
            "State": state,
            "Annual_Rainfall": float(rainfall)
        }])
        
        try:
            predicted_yield = yield_model.predict(input_df)[0]
            if predicted_yield > best_yield_for_crop:
                best_yield_for_crop = float(predicted_yield)
        except Exception as e:
            pass 
        
        crop_yields.append((crop, best_yield_for_crop))
        
        
    crop_yields.sort(key=lambda x: x[1], reverse=True)
    return crop_yields
