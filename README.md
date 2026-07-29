# Week-3 LIVE Weather Program

SkyTalk is a polished single-page weather chatbot built with HTML, CSS, and JavaScript.
It pulls live weather data from Open-Meteo, explains current conditions, and gives simple short-term predictions based on hourly forecast signals.

## Features

- Live weather data (no API key required) using Open-Meteo
- City search with geocoding
- Optional browser geolocation support
- Chatbot responses based on real weather and forecast data
- Simple predictions for rain, temperature trend, and wind
- Safety-oriented weather tips for storms, heat, and heavy rain
- Dynamic themed backgrounds that adapt to conditions
- Optional ambient sound mode (generated with Web Audio)
- Mobile-friendly, single-page responsive layout

## Tech Stack

- HTML5
- CSS3
- Vanilla JavaScript (ES6+)
- Open-Meteo APIs:
	- Geocoding API
	- Forecast API

## Project Structure

- `index.html` - Application layout
- `style.css` - Visual design, theming, and responsiveness
- `script.js` - API calls, chatbot logic, and app behavior

## Run Locally

Because this is a static front-end app, you can run it with any static file server.

### Option 1: Use VS Code Live Server

Open `index.html` with Live Server.

### Option 2: Use Python simple server

```bash
python3 -m http.server 8080
```

Then open:

```text
http://localhost:8080
```

## How to Use

1. Enter a city and click **Find City**, or click **Use My Location**.
2. View current weather conditions in the left panel.
3. Ask weather questions in the chat panel, for example:
	 - Will it rain later?
	 - Is it safe to run outside?
	 - Give me a weather summary.
4. Click **Refresh Weather** to pull the latest data.
5. Toggle **Ambient Sound** on or off as desired.

## Notes

- Forecast-style predictions are lightweight and intended for general guidance.
- For severe weather and emergency planning, always follow your official local weather service.
