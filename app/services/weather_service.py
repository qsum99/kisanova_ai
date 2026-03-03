import requests
from app.config import OPENWEATHER_API_KEY

def get_weather_data(city_name, state_code, country_code):
    """
    Fetches current weather (temperature, humidity) and uses the 5-day forecast
    to estimate monthly rainfall — matching the scale the ML model was trained on.
    """
    api = OPENWEATHER_API_KEY
    if not api:
        print("Error: OPENWEATHER_API_KEY could not be found in the .env file.")
        return None

    # ── 1. Current weather for temperature & humidity ──
    current_url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city_name},{state_code},{country_code}&appid={api}&units=metric"
    )
    current_resp = requests.get(current_url)

    if current_resp.status_code != 200:
        print(f"Error fetching current weather: {current_resp.status_code}")
        print(f"Message: {current_resp.text}")
        return None

    current_data = current_resp.json()
    temp = current_data["main"]["temp"]
    humidity = current_data["main"]["humidity"]

    # ── 2. 5-day / 3-hour forecast for realistic rainfall estimate ──
    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city_name},{state_code},{country_code}&appid={api}&units=metric"
    )
    forecast_resp = requests.get(forecast_url)

    rainfall_monthly = 0.0  # fallback

    if forecast_resp.status_code == 200:
        forecast_data = forecast_resp.json()
        # Sum all rain across the 5-day forecast (40 x 3-hour slots)
        total_rain_5day = 0.0
        for slot in forecast_data.get("list", []):
            rain = slot.get("rain", {}).get("3h", 0)
            total_rain_5day += rain

        # Scale 5-day total to a 30-day (monthly) estimate
        # The ML model was trained on monthly-scale rainfall (range ~20-300 mm)
        rainfall_monthly = round(total_rain_5day * (30 / 5), 2)

        # Clamp to a minimum realistic value if forecast shows zero rain
        # (the training data never has 0; minimum is ~20 mm)
        if rainfall_monthly < 20:
            rainfall_monthly = 20.0
    else:
        print(f"Warning: Could not fetch forecast data ({forecast_resp.status_code}). Using fallback rainfall.")
        rainfall_monthly = 100.0  # safe mid-range fallback

    print(f"Temperature: {temp}")
    print(f"Humidity: {humidity}")
    print(f"Estimated monthly rainfall: {rainfall_monthly} mm")

    return {
        "temperature": temp,
        "humidity": humidity,
        "rainfall_5day_total": rainfall_monthly
    }

