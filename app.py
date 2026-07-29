"""
app.py – Flask web application for the Live Weather Chatbot.

Routes
------
GET  /                  → Serve the main chat UI (index.html)
POST /api/weather       → Fetch & return current weather JSON for a city
POST /api/chat          → Send a user message, get chatbot reply
"""

import logging
import os
from flask import Flask, jsonify, render_template, request, session
from dotenv import load_dotenv
import requests as req_lib

import weather as weather_service
import chatbot as chatbot_service

logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

DEFAULT_CITY = os.getenv("DEFAULT_CITY", "London")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _err(msg: str, status: int = 400):
    return jsonify({"error": msg}), status


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", default_city=DEFAULT_CITY)


@app.route("/api/weather", methods=["POST"])
def api_weather():
    """Return current weather + reset the chat history for the new city."""
    body = request.get_json(silent=True) or {}
    city = (body.get("city") or "").strip()
    if not city:
        return _err("city is required")

    try:
        current = weather_service.get_current_weather(city)
        summary = weather_service.summarise_for_chatbot(city)
    except req_lib.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 502
        if status == 404:
            return _err(f"City '{city}' not found. Check the spelling and try again.", 404)
        logger.error("Weather API HTTP error for city %r: %s", city, exc)
        return _err("Weather service returned an error. Please try again.", 502)
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        return _err("Server configuration error. Contact the administrator.", 500)

    # Store the weather summary in the server-side session so subsequent
    # /api/chat calls can reuse it without fetching weather again.
    session["weather_summary"] = summary
    session["city"] = city
    session["history"] = []

    return jsonify(
        {
            "city": current["city"],
            "country": current["country"],
            "description": current["description"],
            "temperature_c": current["temperature_c"],
            "feels_like_c": current["feels_like_c"],
            "temp_min_c": current["temp_min_c"],
            "temp_max_c": current["temp_max_c"],
            "humidity_pct": current["humidity_pct"],
            "wind_speed_mps": current["wind_speed_mps"],
            "clouds_pct": current["clouds_pct"],
            "icon": current["icon"],
            "summary": summary,
        }
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Accept a user message and return the chatbot's reply."""
    body = request.get_json(silent=True) or {}
    user_message = (body.get("message") or "").strip()
    if not user_message:
        return _err("message is required")

    weather_summary = session.get("weather_summary")
    if not weather_summary:
        return _err(
            "No weather data loaded. Please search for a city first.", 400
        )

    history: list[dict] = session.get("history", [])
    history.append({"role": "user", "content": user_message})

    try:
        reply = chatbot_service.chat(weather_summary, history)
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        return _err("Server configuration error. Contact the administrator.", 500)
    except Exception as exc:  # noqa: BLE001
        logger.error("Chatbot error: %s", exc)
        return _err("The chatbot encountered an error. Please try again.", 502)

    history.append({"role": "assistant", "content": reply})
    # Keep history bounded to avoid bloating the session cookie
    session["history"] = history[-40:]

    return jsonify({"reply": reply})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Re-fetch weather for the current city and update the session summary."""
    city = session.get("city")
    if not city:
        return _err("No city loaded. Search for a city first.", 400)

    try:
        current = weather_service.get_current_weather(city)
        summary = weather_service.summarise_for_chatbot(city)
    except req_lib.HTTPError as exc:
        logger.error("Weather API HTTP error refreshing city %r: %s", city, exc)
        return _err("Weather service returned an error. Please try again.", 502)
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        return _err("Server configuration error. Contact the administrator.", 500)

    session["weather_summary"] = summary

    return jsonify(
        {
            "city": current["city"],
            "country": current["country"],
            "description": current["description"],
            "temperature_c": current["temperature_c"],
            "feels_like_c": current["feels_like_c"],
            "humidity_pct": current["humidity_pct"],
            "wind_speed_mps": current["wind_speed_mps"],
            "icon": current["icon"],
            "message": "Weather data refreshed.",
        }
    )


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=5000)
