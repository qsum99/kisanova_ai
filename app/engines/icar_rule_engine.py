from typing import List

def apply_icar_filters(crops: List[str], temp: float, humidity: float, rainfall: float, ph: float) -> List[str]:

    feasible_crops = set([str(c).lower().strip() for c in crops])
    
    # 1. Temperature Filters
    if temp < 10.0:
        # Too cold for tropical crops
        unsuited = {"mango", "banana", "papaya", "coconut", "cotton", "jute"}
        feasible_crops -= unsuited
        
    if temp > 40.0:
        # Too hot for temperate crops
        unsuited = {"apple", "grapes"}
        feasible_crops -= unsuited
        
    # 2. Rainfall/Water Filters (Now expecting simulated Annual Rainfall in mm, typical ranges 300-3000mm)
    if rainfall < 400.0:
        # Too dry for highly water-intensive crops (assuming no extreme irrigation indicated)
        unsuited = {"rice", "jute", "papaya"}
        feasible_crops -= unsuited
        
    if rainfall > 2500.0:
        # Too wet for dryland crops
        unsuited = {"mothbeans", "mungbean", "lentil", "chickpea"}
        feasible_crops -= unsuited
        
    # 3. pH Filters
    if ph < 4.5:
        # Very acidic soils
        # Most crops fail except maybe tea/coffee
        unsuited = {"cotton", "chickpea", "maize", "pomegranate"}
        feasible_crops -= unsuited
        
    if ph > 8.5:
        # Alkaline soils
        unsuited = {"apple", "coffee", "grapes"}
        feasible_crops -= unsuited
        
        
    return [c for c in crops if str(c).lower().strip() in feasible_crops]
