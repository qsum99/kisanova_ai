from app.services.weather_service import get_weather_data
from typing import Dict, Any

# National averages for fallback (Annual representations)
FALLBACK_TEMP = 28.0
FALLBACK_HUMIDITY = 60.0
FALLBACK_RAINFALL = 1200.0

def get_robust_weather(city_name: str, state_name: str) -> Dict[str, float]:
    """
    Attempts to fetch real weather data.
    If the farm location is missing or the external API fails,
    provides a robust fallback to prevent the model from failing.
    """
    
    if not city_name or not state_name:
        return {
            "temperature": FALLBACK_TEMP,
            "humidity": FALLBACK_HUMIDITY,
            "rainfall": FALLBACK_RAINFALL,
            "inferred_weather": True
        }
        
    try:
        # We pass "IN" assuming India context based on prior discussions
        # State code usually needs abbreviations, but we'll try what's given.
        # This wrapper handles the potential UnboundLocalError in existing weather_service
        weather = get_weather_data(city_name, state_name, "IN")
        
        temp = weather.get("temperature", FALLBACK_TEMP)
        humidity = weather.get("humidity", FALLBACK_HUMIDITY)
        daily_rainfall = weather.get("rainfall_5day_total", FALLBACK_RAINFALL / 365.0)
        
        # Simulate annual rainfall based on the daily data as requested
        annual_rainfall = daily_rainfall * 365.0
        
        # Ensure values aren't mathematically impossible or zero where it hurts
        if temp < -20 or temp > 60: temp = FALLBACK_TEMP
        if humidity <= 0 or humidity > 100: humidity = FALLBACK_HUMIDITY
        if annual_rainfall <= 0: annual_rainfall = FALLBACK_RAINFALL
            
        return {
            "temperature": temp,
            "humidity": humidity,
            "rainfall": annual_rainfall, # Passed downstream as Annual Rainfall
            "inferred_weather": False
        }
    except Exception as e:
        print(f"[weather_engine] Error fetching real weather: {e}. Using robust fallbacks.")
        return {
            "temperature": FALLBACK_TEMP,
            "humidity": FALLBACK_HUMIDITY,
            "rainfall": FALLBACK_RAINFALL,
            "inferred_weather": True
        }
