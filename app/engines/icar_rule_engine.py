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
        
    # 2.5 Specialty Crop Filters (Strict Geography bounds)
    if temp > 30.0 or rainfall < 1200.0:
        # Coffee and Apples require cool temps and, for coffee, very high rainfall/elevation
        unsuited = {"coffee", "apple"}
        feasible_crops -= unsuited
        
    if rainfall > 1500.0 or humidity > 85.0:
        # Grapes rot in extremely high humidity and monsoon conditions
        unsuited = {"grapes"}
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
        
    feasible_list = [c for c in crops if str(c).lower().strip() in feasible_crops]
    return feasible_list


def filter_by_geography(feasible_crops: List[str], state: str, district: str) -> List[str]:
    """
    Prevents unrealistic, meme-worthy predictions (like Apples in Chennai or Coffee in Hubli) 
    that destroy user trust, by hard-locking sensitive crops to their known Indian geographical domains.
    """
    safe_state = str(state).lower()
    safe_dist = str(district).lower()
    
    final_crops = set(feasible_crops)
    
    # 1. COFFEE GEOGRAPHY
    # Coffee only grows in high-altitude zones in Southern India (Chikmagalur, Kodagu, Hassan, Wayanad, Nilgiris, Yercaud, Araku)
    coffee_districts = ["chikmagalur", "kodagu", "hassan", "coorg", "wayanad", "nilgiri", "yercaud", "araku"]
    if "coffee" in final_crops:
        is_coffee_zone = any(d in safe_dist for d in coffee_districts)
        if not is_coffee_zone:
            final_crops.discard("coffee")

    # 2. APPLE GEOGRAPHY
    # Apples only grow in Northern Himalayan/Hilly states
    apple_states = ["jammu", "kashmir", "himachal", "uttarakhand", "arunachal"]
    if "apple" in final_crops:
        if not any(s in safe_state for s in apple_states):
            final_crops.discard("apple")
            
    # 3. JUTE GEOGRAPHY
    # Jute is strictly an Eastern mega-river delta crop
    jute_states = ["bengal", "assam", "bihar", "odisha", "meghalaya"]
    if "jute" in final_crops:
        if not any(s in safe_state for s in jute_states):
            final_crops.discard("jute")
            
    # 4. GRAPES GEOGRAPHY
    # Mostly Maharashtra (Nashik, Sangli) and Northern Karnataka (Bijapur, Bangalore Rural)
    grape_friendly = ["maharashtra", "karnataka", "tamil nadu", "punjab", "haryana"]
    if "grapes" in final_crops:
        if not any(s in safe_state for s in grape_friendly):
            final_crops.discard("grapes")
            
    # 5. COTTON GEOGRAPHY
    # Black soil, extremely dry-friendly, mostly West/South/Central India
    cotton_hostile = ["kerala", "himachal", "uttarakhand", "jammu", "kashmir", "sikkim", "assam"]
    if "cotton" in final_crops:
        if any(s in safe_state for s in cotton_hostile):
            final_crops.discard("cotton")
            
    return [c for c in feasible_crops if c in final_crops]
