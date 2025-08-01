# Weather Explorer App

A simple web application built with Streamlit to explore current and historical weather data and get weather-based attraction recommendations.

## Features

- Current weather (temperature, wind, cloud cover)
- City search
- Unit selection (Celsius/Fahrenheit)
- 10-year weather history
- Smart attraction suggestions based on weather
- Weather trend graphs
- Interactive map with nearby places
- Saves last used city and settings

## Tech Stack

| Feature            | Technology              |
|--------------------|--------------------------|
| Frontend           | Streamlit                |
| Real-time Weather  | OpenWeatherMap API       |
| Historical Weather | Open-Meteo API           |
| Places & Map       | Geoapify API + Folium    |
| Graphs             | Plotly, Seaborn          |
| Storage            | JSON (local file)        |

## Installation

```bash
poetry add $(cat requirements.txt)
Poetry run streamlit run app.py
