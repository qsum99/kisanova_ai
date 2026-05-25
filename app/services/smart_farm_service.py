"""
Phase 5 — Unified Smart Farm Service
Consolidates weather, soil, NDVI, irrigation, and fertilizer engines into a single module.
Called on-demand by the frontend routes.
"""

import os
import math
import requests
import time
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from app.utils.database import get_db_connection

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# ── 1. Weather Logic ──
def get_farm_weather(lat, lon):
    """Fetch current weather from OpenWeatherMap with offline fallback."""
    if not OPENWEATHER_API_KEY:
        return _get_offline_weather(lat, lon)
        
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            
            # Forecast for rain probability
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&cnt=8"
            f_resp = requests.get(forecast_url, timeout=5)
            rain_prob = 0
            if f_resp.status_code == 200:
                rain_probs = [slot.get("pop", 0) * 100 for slot in f_resp.json().get("list", [])]
                rain_prob = max(rain_probs) if rain_probs else 0
                
            return {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data.get("wind", {}).get("speed", 2.0),
                "rain_probability": round(rain_prob, 1),
                "description": data.get("weather", [{}])[0].get("description", "Clear"),
                "source": "openweathermap"
            }
    except Exception as e:
        print(f"[SmartFarm] Weather API error: {e}")
        
    return _get_offline_weather(lat, lon)

def _get_offline_weather(lat, lon):
    """Fallback weather data based on Karnataka averages."""
    month = datetime.now().month
    # Summer vs Winter rough approximation
    if month in [3, 4, 5]: return {"temperature": 32.5, "humidity": 45, "wind_speed": 3.0, "rain_probability": 10, "description": "Hot and Dry", "source": "offline"}
    if month in [6, 7, 8, 9]: return {"temperature": 26.5, "humidity": 82, "wind_speed": 4.5, "rain_probability": 85, "description": "Monsoon Rain", "source": "offline"}
    return {"temperature": 24.0, "humidity": 60, "wind_speed": 2.5, "rain_probability": 5, "description": "Cool and Clear", "source": "offline"}


# ── 2. Soil Data Logic ──
def get_soil_data(lat, lon):
    """Fetch soil data from ISRIC SoilGrids API (no key needed)."""
    try:
        url = "https://rest.soilgrids.org/soilgrids/v2.0/properties/query"
        params = {"lon": lon, "lat": lat, "property": ["phh2o", "nitrogen", "soc"], "depth": ["0-5cm"], "value": "mean"}
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            layers = resp.json().get("properties", {}).get("layers", [])
            data = {"ph": 6.5, "nitrogen": 40, "organic_carbon": 0.5, "source": "soilgrids"}
            for layer in layers:
                val = layer.get("depths", [{}])[0].get("values", {}).get("mean")
                if val:
                    if layer["name"] == "phh2o": data["ph"] = round(val / 10.0, 1)
                    if layer["name"] == "nitrogen": data["nitrogen"] = round(val * 0.15, 1)
            return data
    except Exception as e:
        print(f"[SmartFarm] Soil API error: {e}")
        
    return {"ph": 6.8, "nitrogen": 45, "organic_carbon": 0.6, "source": "offline"}


# ── 3. NDVI Logic ──
def get_farm_ndvi(lat, lon, crop_type, planting_date):
    """Calculate expected NDVI based on days since planting (offline growth curve)."""
    if isinstance(planting_date, str):
        try:
            planting_date = datetime.strptime(planting_date, "%Y-%m-%d").date()
        except ValueError:
            planting_date = date.today()
            
    days = (date.today() - planting_date).days
    if days < 0: days = 0
    
    # Generic curve: peaks at 70 days, ends around 120
    if days <= 20: ndvi = 0.15 + (days * 0.01)
    elif days <= 70: ndvi = 0.35 + ((days-20) * 0.009)
    elif days <= 100: ndvi = 0.80 - ((days-70) * 0.005)
    else: ndvi = max(0.2, 0.65 - ((days-100) * 0.015))
    
    health = "Good" if ndvi > 0.6 else "Moderate" if ndvi > 0.4 else "Poor/Stressed"
    return {"ndvi_score": round(ndvi, 3), "health": health, "days_since_planting": days, "source": "growth_curve"}


# ── 4. Irrigation Engine ──
def get_irrigation_decision(farmer_id, lat, lon):
    weather = get_farm_weather(lat, lon)
    
    # FAO-56 PM approximation
    eto = max(2.0, (weather["temperature"] * 0.15) + (weather["wind_speed"] * 0.2))
    kc = 0.8 # Average crop coefficient
    etc = eto * kc
    amount_litres = int(etc * 10000) # 1mm = 10k litres/ha
    
    if weather["rain_probability"] > 60:
        return {"action": "skip", "amount_litres_per_ha": 0, "water_saved_litres": amount_litres, "reason": f"High rain probability ({weather['rain_probability']}%). Skip irrigation.", "weather": weather}
    elif weather["temperature"] > 38:
        return {"action": "irrigate", "amount_litres_per_ha": int(amount_litres * 1.5), "water_saved_litres": 0, "reason": "Heat wave detected. Increase irrigation and apply in the evening.", "weather": weather}
    else:
        return {"action": "irrigate", "amount_litres_per_ha": amount_litres, "water_saved_litres": 0, "reason": "Standard daily irrigation based on current weather.", "weather": weather}


# ── 5. Fertilizer Engine ──
def get_fertilizer_decision(farmer_id, lat, lon):
    soil = get_soil_data(lat, lon)
    
    rec = {"fertilizer_type": "NPK Complex (20:20:0) + Urea", "amount_kg_per_ha": 80, "amendments": [], "reason": "Base recommendation for soil."}
    
    if soil["ph"] < 5.5:
        rec["amendments"].append("Apply 1000 kg/ha Agricultural Lime to fix acidity.")
    elif soil["ph"] > 8.0:
        rec["amendments"].append("Apply 500 kg/ha Gypsum to fix alkalinity.")
        
    if soil["nitrogen"] < 30:
        rec["fertilizer_type"] = "Urea Top-Dressing"
        rec["amount_kg_per_ha"] = 50
        rec["reason"] = "Soil nitrogen is low. Apply Urea immediately."
        
    rec["soil_data"] = soil
    return rec
