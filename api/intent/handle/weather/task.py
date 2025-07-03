import httpx
from cachetools import cached, TTLCache

params = {
	"latitude": 50.6369495,
	"longitude": 3.1246207,
	"current": ["temperature_2m", "apparent_temperature", "precipitation", "weather_code"],
	"hourly": ["temperature_2m", "rain", "weather_code"],
	"daily": ["weather_code", "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum", "rain_sum", "precipitation_hours"],
 	"timezone": "Europe/Berlin",
  	"forecast_hours": 10,
    "forecast_days": 2
}

weather = TTLCache(maxsize=1, ttl=3600)

@cached(weather)
def get_weather():
    response = httpx.get("https://api.open-meteo.com/v1/forecast", params=params).json()
    daily = response["daily"]
    current = response["current"]

    current_weather = translate_weather_code(current["weather_code"])
    current_temperature = current["temperature_2m"] 
    current_quote = f"La météo est actuellement {current_weather} avec une température de {current_temperature} degrés celsuis"

    today_min_temp = daily["apparent_temperature_min"][0]
    today_max_temp = daily["apparent_temperature_max"][0]
    today_weather = translate_weather_code(daily["weather_code"][0])
    today_quote = f"Aujourd'hui la température sera entre {today_min_temp} et {today_max_temp} degrés celsuis avec une météo {today_weather}"

    tomorrow_min_temp = daily["apparent_temperature_min"][1]
    tomorrow_max_temp = daily["apparent_temperature_max"][1]
    tomorrow_weather = translate_weather_code(daily["weather_code"][1])
    tomorrow_quote = f"Demain la température sera entre {tomorrow_min_temp} et {tomorrow_max_temp} degrés celsuis avec une météo {tomorrow_weather}"

    hourly = response["hourly"]
    hourly_min_temp = min(hourly["temperature_2m"])
    hourly_max_temp = max(hourly["temperature_2m"])
    hourly_rain = sum(hourly["rain"])
    hourly_forcast = f"Dans les 10 prochaines heures les température seront entre {hourly_min_temp} et {hourly_max_temp} degrés celsuis, et les quantités de précipitations seront au total de {hourly_rain} mm"



    return f"{current_quote}\n{today_quote}\n{tomorrow_quote}\n{hourly_forcast}"


def translate_weather_code(weather_code: int):
    if weather_code == 0:
        return "au ciel bleu"
    elif weather_code == 1:
        return "avec peu de nuages"
    elif weather_code == 2:
        return "nuageuse"
    elif weather_code == 3:
        return "Couvert"
    elif weather_code >= 45 and weather_code <= 48 :
        return "de brouillaurd"
    elif weather_code >= 51 and weather_code <= 55 :
        return "brumeuse"
    elif weather_code >= 56 and weather_code <= 57 :
        return "avec Brume verglaçante"
    elif weather_code == 61:
        return "de légère pluies"
    elif weather_code == 63:
        return "pluvieuse"
    elif weather_code == 65 :
        return "très pluvieuse"
    elif weather_code >= 66 and weather_code <= 67:
        return "de pluies glaçantes"
    elif weather_code == 71: 
        return "un peu neigeux"
    elif weather_code == 73: 
        return "neigeuse"
    elif weather_code == 75: 
        return "avec beaucoup de neige"
    elif weather_code >= 80 and weather_code >= 82: 
        return "parsemée d'averses"
    elif weather_code >= 85 and weather_code >= 86: 
        return "parsemée d'averses de neige"
    elif weather_code == 95 : 
        return "orageuse"
    elif weather_code >= 96 : 
        return "orageuse avec de la grêle"
    else:
        return "inconnue"
        
