import requests 
city_name="New Delhi"
api="1e5ef983a10f2fd31654af73150a176a"
url=f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api}"

response=requests.get(url)

if response.status_code == 200:
    data=response.json()
    lon=data["coord"]["lon"]
    lat=data["coord"]["lat"]
url_for_rainfall=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api}"

response2=requests.get(url_for_rainfall)

if response2.status_code == 200:
    data2=response2.json()
    rain_data = data.get("rain", {})

    rain_last_hour = rain_data.get("1h", 0)
    
    print(f"Rain in the last hour: {rain_last_hour} mm")


