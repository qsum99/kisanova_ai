import requests
from app.config import OPENWEATHER_API_KEY

def get_weather_data(city_name, state_code, country_code):
    api = OPENWEATHER_API_KEY
    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city_name},{state_code},{country_code}&appid={api}&units=metric"
    )
    forecast_resp = requests.get(forecast_url)
    if forecast_resp.status_code == 200:
        forecast_data = forecast_resp.json()
        for slot in forecast_data.get("list", []):
            rain = slot.get("rain", {}).get("3h", 0)
            temp = slot["main"]["temp"]
            humidity =slot["main"]["humidity"]
        if rain <0.1:
            rain=0.1
        rain_of_day=rain*100*3
    else:
        print(f"Warning: Could not fetch forecast data ({forecast_resp.status_code}). Using fallback rainfall.")

    return {
        "temperature": temp,
        "humidity": humidity,
        "rainfall_5day_total":rain_of_day
    }
