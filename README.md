# Live Weather Chatbot

A Flask web application that fetches **real-time weather data** from
OpenWeatherMap and feeds it into an **OpenAI-powered chatbot**.  The chatbot
explains current conditions in plain language, gives short-range predictions
from the forecast data, and answers follow-up questions — all based on live
conditions that you can refresh at any time.

---

## Features

| Feature | Detail |
|---|---|
| 🌍 Live weather data | Current conditions + 24-hour forecast via OpenWeatherMap |
| 🤖 AI chatbot | GPT-powered assistant that explains and predicts weather |
| 🔄 Auto-refresh | Re-fetch the latest data without leaving the page |
| 💬 Conversation memory | Multi-turn chat within a session |
| 📱 Responsive UI | Works on desktop and mobile |

---

## Project Structure

```
├── app.py            # Flask web server (routes)
├── weather.py        # OpenWeatherMap API client
├── chatbot.py        # OpenAI chatbot integration
├── templates/
│   └── index.html    # Chat UI (single-page)
├── static/
│   └── style.css     # App styling
├── requirements.txt  # Python dependencies
└── .env.example      # Template for environment variables
```

---

## Quick Start

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd Week-3-LIVE-weather-prorgram
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your API keys

```bash
cp .env.example .env
```

Open `.env` and fill in:

| Variable | Where to get it |
|---|---|
| `OPENWEATHER_API_KEY` | [openweathermap.org/api](https://openweathermap.org/api) — free tier is enough |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `DEFAULT_CITY` | Optional — city shown on load (default: `London`) |
| `FLASK_SECRET_KEY` | Any random string (used to sign sessions) |

### 3. Run the app

```bash
python app.py
```

Open your browser at **http://localhost:5000**.

---

## How It Works

1. **Weather fetch** — When you search for a city, the server calls
   `OpenWeatherMap /weather` (current) and `/forecast` (3-hour intervals for
   the next 24 hours) and builds a plain-text summary.

2. **Chatbot** — Your messages are sent to OpenAI together with the weather
   summary.  The model is instructed to base all answers on the real data,
   explain conditions clearly, and give practical advice.

3. **Refresh** — The "Refresh weather" button re-fetches live data and updates
   the session summary so subsequent chatbot answers use the latest readings.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serve the chat UI |
| `POST` | `/api/weather` | `{"city": "London"}` → current weather + reset session |
| `POST` | `/api/chat` | `{"message": "..."}` → chatbot reply |
| `POST` | `/api/refresh` | Re-fetch weather for the current session city |

