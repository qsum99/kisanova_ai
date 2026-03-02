import requests
import json
from .cache_service import weather_cache
from app.config import Config

class WeatherServiceError(Exception):
    pass

def fetch_weather_features(location):
    """
    Fetches weather given a location which can be a city name or 'lat,lon'.
    Uses the OpenWeatherMap 5-day / 3-hour forecast API.
    
    Returns:
       A dict containing: temperature, humidity, rainfall_5day_total
    """
    # 1. Check Cache first
    cache_key = str(location).strip().lower()
    cached_data = weather_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # 2. Extract API Key
    api_key = Config.OPENWEATHER_API_KEY
    if not api_key:
        raise WeatherServiceError("OpenWeatherMap API Key is missing. Check .env configuration.")
        
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "appid": api_key,
        "units": "metric" # to get current temperature in metric
    }
    
    # Check if location is lat/lon or city
    if ',' in location and all(part.strip().replace('.','',1).replace('-','',1).isdigit() for part in location.split(',')):
        parts = location.split(',')
        params["lat"] = parts[0].strip()
        params["lon"] = parts[1].strip()
    else:
        params["q"] = location.strip()
        
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.status_code != 200:
            error_msg = data.get("message", "Failed to fetch weather data")
            raise WeatherServiceError(f"OpenWeatherMap Error: {error_msg}")
            
        if "list" not in data or len(data["list"]) == 0:
            raise WeatherServiceError("No forecast data available in the API response.")
            
        forecast_list = data["list"]
        
        # 3. Extract required features
        # The first item in the forecast list is typically the nearest to current time
        current_data = forecast_list[0]
        
        temperature = current_data.get("main", {}).get("temp", 0.0)
        humidity = current_data.get("main", {}).get("humidity", 0.0)
        
        # Calculate total rainfall over the next 5 days (sum of all rain["3h"])
        total_rainfall = 0.0
        for item in forecast_list:
            # Default to 0 if rain key or 3h key is missing
            rain_data = item.get("rain", {})
            rain_3h = rain_data.get("3h", 0.0)
            total_rainfall += float(rain_3h)
            
        result = {
            "temperature": float(temperature),
            "humidity": float(humidity),
            "rainfall_5day_total": float(total_rainfall)
        }
        
        # 4. Cache the valid result
        weather_cache.set(cache_key, result)
        
        return result
        
    except requests.exceptions.RequestException as e:
        raise WeatherServiceError(f"Network error while fetching weather: {str(e)}")
