import requests

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

def get_weather():
    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params).json()
    daily = response["daily"]
    current = response["current"]
    current_quote = f"La météo est actuellement {translate_weather_code(current["weather_code"])} avec une température de {current["temperature_2m"]}"
    today_quote = f"Aujourd'hui la température sera entre {daily["apparent_temperature_min"][0]} et {daily["apparent_temperature_max"][0]} avec une météo {translate_weather_code(daily["weather_code"][0])}"
    tomorrow_quote = f"Demain la température sera entre {daily["apparent_temperature_min"][1]} et {daily["apparent_temperature_max"][1]} avec une météo {translate_weather_code(daily["weather_code"][1])}"
    hourly = response["hourly"]
    hourly_forcast = f"Dans les 10 prochaines heures les température seront entre {max(hourly["temperature_2m"])}°C et {min(hourly["temperature_2m"])}°C, et les quantités de précipitations seront au total de {sum(hourly["rain"])} mm"
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
        
