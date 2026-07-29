"""
weather.py – OpenWeatherMap API client.

Fetches current weather conditions and a 5-day / 3-hour forecast for a
given city name and returns structured dictionaries that the chatbot
service can consume.
"""

import os
import requests

BASE_URL = "https://api.openweathermap.org/data/2.5"


def _api_key() -> str:
    key = os.getenv("OPENWEATHER_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "OPENWEATHER_API_KEY is not set. "
            "Add it to your .env file (see .env.example)."
        )
    return key


def get_current_weather(city: str) -> dict:
    """Return current weather data for *city*.

    Returns a dict with keys:
        city, country, description, temperature_c, feels_like_c,
        humidity_pct, wind_speed_mps, wind_direction_deg,
        visibility_m, clouds_pct, weather_id, icon
    Raises requests.HTTPError on API errors.
    """
    params = {
        "q": city,
        "appid": _api_key(),
        "units": "metric",
    }
    resp = requests.get(f"{BASE_URL}/weather", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    weather_item = data["weather"][0]
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "description": weather_item["description"].capitalize(),
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "temp_min_c": data["main"]["temp_min"],
        "temp_max_c": data["main"]["temp_max"],
        "humidity_pct": data["main"]["humidity"],
        "pressure_hpa": data["main"]["pressure"],
        "wind_speed_mps": data["wind"]["speed"],
        "wind_direction_deg": data["wind"].get("deg", 0),
        "visibility_m": data.get("visibility", None),
        "clouds_pct": data["clouds"]["all"],
        "weather_id": weather_item["id"],
        "icon": weather_item["icon"],
        "sunrise_ts": data["sys"]["sunrise"],
        "sunset_ts": data["sys"]["sunset"],
    }


def get_forecast(city: str, periods: int = 8) -> list[dict]:
    """Return up to *periods* forecast entries (each 3 hours apart) for *city*.

    Each entry contains:
        dt_txt, description, temperature_c, humidity_pct,
        wind_speed_mps, pop (probability of precipitation 0-1)
    """
    params = {
        "q": city,
        "appid": _api_key(),
        "units": "metric",
        "cnt": periods,
    }
    resp = requests.get(f"{BASE_URL}/forecast", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for entry in data["list"]:
        results.append(
            {
                "dt_txt": entry["dt_txt"],
                "description": entry["weather"][0]["description"].capitalize(),
                "temperature_c": entry["main"]["temp"],
                "humidity_pct": entry["main"]["humidity"],
                "wind_speed_mps": entry["wind"]["speed"],
                "pop": entry.get("pop", 0),
            }
        )
    return results


def summarise_for_chatbot(city: str) -> str:
    """Build a compact plain-text weather summary to feed the chatbot."""
    current = get_current_weather(city)
    forecast = get_forecast(city, periods=8)

    lines = [
        f"=== Current conditions in {current['city']}, {current['country']} ===",
        f"Weather: {current['description']}",
        f"Temperature: {current['temperature_c']:.1f} °C "
        f"(feels like {current['feels_like_c']:.1f} °C, "
        f"min {current['temp_min_c']:.1f} °C, max {current['temp_max_c']:.1f} °C)",
        f"Humidity: {current['humidity_pct']}%",
        f"Wind: {current['wind_speed_mps']} m/s at {current['wind_direction_deg']}°",
        f"Cloud cover: {current['clouds_pct']}%",
        f"Pressure: {current['pressure_hpa']} hPa",
    ]
    if current["visibility_m"] is not None:
        lines.append(f"Visibility: {current['visibility_m'] / 1000:.1f} km")

    lines.append("\n=== 24-hour forecast (3-hour intervals) ===")
    for f in forecast:
        pop_pct = int(f["pop"] * 100)
        lines.append(
            f"{f['dt_txt']}  {f['description']}, "
            f"{f['temperature_c']:.1f} °C, "
            f"humidity {f['humidity_pct']}%, "
            f"wind {f['wind_speed_mps']} m/s, "
            f"precipitation chance {pop_pct}%"
        )

    return "\n".join(lines)
