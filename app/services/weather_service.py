import requests 
city_name="New Delhi"
api="1e5ef983a10f2fd31654af73150a176a"
url=f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api}&units=metric"

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


