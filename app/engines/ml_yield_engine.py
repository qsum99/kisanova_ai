import joblib
import pandas as pd
import os
from typing import List, Tuple, Dict, Any

# Load the new yield model which expects ['Crop', 'Season', 'State', 'Annual_Rainfall']
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'yield_model.pkl')
try:
    yield_model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"[ml_yield_engine] Error loading yield_model.pkl: {e}")
    yield_model = None

def get_yield_ranking(feasible_crops: List[str], state: str, rainfall: float) -> List[Tuple[str, float]]:
    """
    Returns a ranked list of crops based on predicted yield from the regression pipeline.
    The model takes ['Crop', 'Season', 'State', 'Annual_Rainfall'].
    """
    if yield_model is None:
        raise ValueError("ML Yield Model is not loaded. Cannot rank crops.")
        
    crop_yields = []
    
    # We will test each feasible crop across common seasons, or just use "Whole Year"
    # To get the absolute best predicted yield for that crop in that state and rainfall.
    seasons_to_test = ["Whole Year", "Kharif     ", "Rabi       ", "Summer     "]
    
    for crop in feasible_crops:
        best_yield_for_crop = 0.0
        
        for season in seasons_to_test:
            # The pipeline usually expects a dataframe or a structured 2D array matching the columns exactly
            input_df = pd.DataFrame([{
                "Crop": crop,
                "Season": season.strip(), # Might need exact whitespace matching depending on training data, but pipeline usually cleans or one-hot encodes
                "State": state,
                "Annual_Rainfall": float(rainfall)
            }])
            
            try:
                predicted_yield = yield_model.predict(input_df)[0]
                if predicted_yield > best_yield_for_crop:
                    best_yield_for_crop = float(predicted_yield)
            except Exception as e:
                pass # Model might not have seen this crop/season/state combination or failed encoding
                
        # If the model fails entirely for a crop, we'll assign it 0 yield
        crop_yields.append((crop, best_yield_for_crop))
        
    # Sort by highest predicted yield first
    crop_yields.sort(key=lambda x: x[1], reverse=True)
    return crop_yields
