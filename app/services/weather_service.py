import requests 
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
env_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path=env_path)

def get_weater_data(city_name,state_code,country_code):
    api = os.environ.get('OPENWEATHER_API_KEY')
    if not api:
        print("Error: OPENWEATHER_API_KEY could not be found in the .env file.")
        return None
        
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city_name},{state_code},{country_code}&appid={api}&units=metric"

    response=requests.get(url)

    if response.status_code == 200:
        data=response.json()
        temp=data["main"]["temp"]
        humidity=data["main"]["humidity"]
        rain_data = data.get("rain", {})
        rain_last_hour = rain_data.get("1h", 0)
        
        print(f"Temperature: {temp}")
        print(f"Humidity: {humidity}")
        print(f"Rain in the last hour: {rain_last_hour} mm")
        
        return {
            "temperature": temp,
            "humidity": humidity,
            "rainfall_5day_total": rain_last_hour
        }
    else:
        print(f"Error fetching weather: {response.status_code}")
        print(f"Message: {response.text}")
        return None
        
