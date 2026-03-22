from typing import Dict, Any, Tuple

# Comprehensive Regional averages for Indian Soils based on geographical soil types
# Data reflects general available N (kg/ha equivalent proxy), P, K, and pH.
# Values represent (N, P, K, pH)

SOIL_TYPE_DEFAULTS = {
    "alluvial": (40.0, 40.0, 40.0, 7.0),
    "black": (20.0, 30.0, 50.0, 7.8),
    "red": (20.0, 20.0, 20.0, 6.0),
    "laterite": (15.0, 15.0, 15.0, 5.5),
    "desert": (10.0, 15.0, 20.0, 8.0),
    "mountain": (30.0, 20.0, 30.0, 6.0)
}

REGIONAL_SOIL_DEFAULTS = {
    # Northern States (Alluvial & Mountainous)
    "Punjab": (40.0, 40.0, 40.0, 7.5),
    "Haryana": (40.0, 40.0, 40.0, 7.5),
    "Himachal Pradesh": (30.0, 20.0, 30.0, 6.5), # Mountain soil, slightly acidic
    "Uttarakhand": (30.0, 20.0, 30.0, 6.5),
    "Jammu and Kashmir": (30.0, 20.0, 30.0, 6.8),
    "Ladakh": (10.0, 10.0, 20.0, 7.8), # Cold desert
    "Delhi": (35.0, 35.0, 35.0, 7.5),
    "Uttar Pradesh": (40.0, 40.0, 40.0, 7.2), # Alluvial

    # Western & Central States (Black Soil, Desert)
    "Rajasthan": (15.0, 20.0, 30.0, 8.0), # Arid/Sandy, alkaline
    "Gujarat": (20.0, 30.0, 50.0, 7.6), # Black cotton and alluvial
    "Madhya Pradesh": (20.0, 30.0, 50.0, 7.5), # Black soil
    "Maharashtra": (20.0, 30.0, 50.0, 7.8), # Black soil
    "Chhattisgarh": (20.0, 20.0, 30.0, 6.8), # Red and Yellow soils
    "Goa": (20.0, 20.0, 20.0, 5.5), # Laterite soil, acidic

    # Southern States (Red, Laterite, Coastal)
    "Karnataka": (20.0, 20.0, 20.0, 6.0),
    "Kerala": (20.0, 20.0, 20.0, 5.8),
    "Tamil Nadu": (20.0, 20.0, 20.0, 6.2),
    "Andhra Pradesh": (20.0, 20.0, 25.0, 6.5),
    "Telangana": (20.0, 20.0, 25.0, 6.5),

    # Eastern States (Alluvial & Red/Yellow)
    "Bihar": (40.0, 40.0, 40.0, 7.0),
    "Jharkhand": (20.0, 20.0, 20.0, 6.5),
    "West Bengal": (40.0, 40.0, 40.0, 6.0), # Alluvial, slightly acidic
    "Odisha": (20.0, 20.0, 20.0, 6.5), # Red and Laterite

    # North-Eastern States (Acidic, Forest soils)
    "Assam": (40.0, 40.0, 40.0, 5.5),
    "Sikkim": (30.0, 20.0, 30.0, 5.5),
    "Arunachal Pradesh": (30.0, 20.0, 30.0, 5.5),
    "Nagaland": (30.0, 20.0, 30.0, 5.5),
    "Manipur": (30.0, 20.0, 30.0, 5.5),
    "Mizoram": (30.0, 20.0, 30.0, 5.5),
    "Tripura": (30.0, 20.0, 30.0, 5.5),
    "Meghalaya": (30.0, 20.0, 30.0, 5.5),

    # Union Territories
    "Andaman and Nicobar Islands": (20.0, 20.0, 30.0, 6.0),
    "Chandigarh": (40.0, 40.0, 40.0, 7.5),
    "Dadra and Nagar Haveli and Daman and Diu": (20.0, 30.0, 50.0, 7.5),
    "Lakshadweep": (15.0, 20.0, 30.0, 7.5),
    "Puducherry": (20.0, 20.0, 20.0, 6.2)
}

# National Average Fallback (Represents overall Indian soil health which is generally low in N and P)
NATIONAL_DEFAULT = (25.0, 25.0, 35.0, 6.8)

def infer_soil_data(state: str, district: str, n: float = None, p: float = None, k: float = None, ph: float = None, soil_type: str = None) -> Dict[str, float]:
    """
    Infers missing soil data (N, P, K, pH) using direct soil type if provided,
    otherwise falls back to regional averages.
    This replaces pure guesswork with firmer scientific defaults when the farmer specifies soil type.
    """
    
    # 1. If exact soil type is given, prioritize its scientific baseline over State geography
    if soil_type and soil_type.lower() in SOIL_TYPE_DEFAULTS:
        default_n, default_p, default_k, default_ph = SOIL_TYPE_DEFAULTS[soil_type.lower()]
    else:
        # 2. Fall back to state-based geographical averages
        state_normalized = state.title() if state else ""
        
        # Try finding an exact or partial match in states
        matched_state = None
        for s in REGIONAL_SOIL_DEFAULTS.keys():
            if s.lower() in state_normalized.lower():
                matched_state = s
                break
                
        # Get regional default or national default
        default_n, default_p, default_k, default_ph = REGIONAL_SOIL_DEFAULTS.get(matched_state, NATIONAL_DEFAULT)
    
    # Fill in missing values
    inferred_n = float(n) if n not in [None, "", 0, "0"] else default_n
    inferred_p = float(p) if p not in [None, "", 0, "0"] else default_p
    inferred_k = float(k) if k not in [None, "", 0, "0"] else default_k
    inferred_ph = float(ph) if ph not in [None, "", 0, "0"] else default_ph
    
    return {
        "N": inferred_n,
        "P": inferred_p,
        "K": inferred_k,
        "pH": inferred_ph,
        "inferred": not all([n, p, k, ph]) # Flag to indicate if we heavily inferred data
    }
