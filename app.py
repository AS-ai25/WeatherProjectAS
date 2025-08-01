import streamlit as st
import folium
from streamlit_folium import folium_static
import json
import pandas as pd
import requests
import datetime as dt
import os
import pytz
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns


# OpenWeatherMap API key (hardcoded)
KEY_W = 'abb622fc56c5a7f79bb4539ab03cc961'  # OpenWeatherMap
# Geoapify API key
KEY_ATR = "74fb904f381e44fca6a70c993515d53d"

# Main app title
st.title('Weather App')

# Filename for storing user settings locally
SETTINGS_FILE = "settings.json"

# Load user settings or return default if no settings file found
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default settings: Jerusalem, metric units, lat/lon of Jerusalem
        return {"city": "Jerusalem, IL", "units": "metric", "coord_lat":'35.216331' , "coord_lon":'31.769039'}

# Save user settings to file
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# Load saved or default settings
settings = load_settings()

# Intro text describing the app's features
st.write("Discover Your Destination Like Never Before\n")
st.write("Get real-time weather updates and hand-picked attractions tailored to the current conditions. Whether it’s sunny skies or rainy days, we’ll guide you to the best experiences in your chosen city – from nature walks and panoramic viewpoints to cozy museums and local gems.")

# Load city list from local JSON file (UTF-8 encoding)
with open("DATA_BASE/city.list.json", "r", encoding="utf-8") as f:
    city_data = json.load(f)

# Convert city list to DataFrame for searching/filtering
city_data_table = pd.DataFrame(city_data)

# Create a combined "city, country" column for easy search
city_data_table['city_finder'] = city_data_table['name'] + ", " + city_data_table['country']

# User input for city name to search
city_input = st.text_input("Type a city name to search:")

# Initialize city and coordinates from saved settings
city = settings["city"]
coord_lon = settings["coord_lon"]
coord_lat = settings["coord_lat"]

# If user typed a city name, find matches in city list
if city_input:
    matches = city_data_table[
        city_data_table['city_finder'].str.lower().str.contains(city_input.lower(), na=False)
    ]

    if not matches.empty:
        # User selects a city from matching results
        city_selected = st.selectbox("Please choos city from the list", matches['city_finder'].tolist())

        # Extract coordinates of selected city
        selected_row = matches[matches['city_finder'] == city_selected].iloc[0]
        city = selected_row['city_finder']
        coord_lat = selected_row['coord']['lat']
        coord_lon = selected_row['coord']['lon']

    else:
        # Show warning if no city matched
        st.warning("Unknow city, try again")

# User chooses units format: metric or imperial
units = st.radio("choos format", ("metric", "imperial"), horizontal=True)

# Set temperature symbol based on units
if units == "°F":
    temp_sym = "°F"
else:
    temp_sym = "°C"

# Update settings with current selections
if city:
    settings["city"] = city
if units in ["metric", "imperial"]:
    settings["units"] = units
if coord_lon:
    settings["coord_lon"] = coord_lon
if coord_lat:
    settings["coord_lat"] = coord_lat

# Save updated settings to file
save_settings(settings)


# Function to get current weather data from OpenWeatherMap API
def get_weather(lat, lon, KEY):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": KEY,
        "units": settings["units"]
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        return res.json()
    return None

# Display chosen city
st.write(city)

# Fetch selected city row (not used later directly)
selected_city = city_data_table[city_data_table.city_finder == settings["city"]]

# Get current weather for selected coordinates
weather = get_weather(coord_lat, coord_lon, KEY_W)

# Extract various weather details from API response
coord_lon = weather['coord']['lon']
coord_lat = weather['coord']['lat']
weather_main = weather['weather'][0]['main']
weather_description = weather['weather'][0]['description']
weather_code = icon = weather['weather'][0]['icon']
main_temp = weather['main']['temp']

# Set temperature unit symbol for display
if settings["units"] == 'metric':
    temp_sym = 'C'
if settings["units"] == 'imperial':
    temp_sym = 'F'

#main_temp_max = weather['main']['temp_max']
#main_temp_min = weather['main']['temp_min']
#wind_speed = weather['wind']['speed']
#clouds_all = weather['clouds']['all']
#city_time = weather['dt']
city_timezone = weather['timezone']

# Get weather icon URL and display
icon_code = weather['weather'][0]['icon']
url_icon = f"https://openweathermap.org/img/wn/{weather_code}@2x.png"
st.image(url_icon, caption="Weather Icon")

# Calculate current time at chosen city using UTC + timezone offset seconds
actual_cite_time = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=city_timezone)
actual_cite_time1 = actual_cite_time.strftime("%H:%M:%S %A %d-%m-%Y ")

###############################

# Function to get the user's timezone from IP using external API
def get_user_timezone():
    try:
        response = requests.get("https://ipapi.co/json/")
        data = response.json()
        return data.get("timezone")
    except Exception as e:
        return f"Error{e}"

# Get user timezone string and current user local time with timezone info
timezone = get_user_timezone()
tz = pytz.timezone(timezone)
time_now_user = dt.datetime.now(tz).strftime("%A, %Y-%m-%d %H:%M [UTC %Z]")

###############################

# Predefined recommendation texts per weather condition
weather_texts = {
    "Thunderstorm": "Stormy weather calls for indoor fun – visit a museum, relax in a spa, or enjoy a movie.",
    "Drizzle": "A light drizzle is perfect for cozy indoor activities – explore a planetarium or unwind at a spa.",
    "Rain": "Rainy day? Dive into an aquarium, enjoy a hot bath, or discover culture indoors.",
    "Snow": "Snowy weather is ideal for stunning mountain views or a warm bath experience. Or try a cozy café and watch the snow fall.",
    "Mist": "Misty conditions create a magical mood for museums, theatre, and historical sites. Ideal for photography lovers too.",
    "Smoke": "Poor air quality? Stay safe indoors with a museum visit, indoor botanical garden, or a relaxing movie.",
    "Haze": "Hazy views outside? Take in some art, visit a local gallery, or enjoy a quiet afternoon in a tea house.",
    "Dust": "Dusty skies? Head indoors – try an escape room, science center, or wellness center.",
    "Fog": "Fog rolling in? Discover the charm of local cafés, libraries, or ancient ruins wrapped in mystery.",
    "Sand": "Sandy air? Stay sheltered indoors and explore immersive museums or culinary workshops.",
    "Ash": "Volcanic ash in the air? Best to stay inside – it's a great time for pampering or cultural enrichment.",
    "Squall": "Unpredictable winds? Perfect excuse for a day at the spa, indoor climbing, or art museum.",
    "Tornado": "Stay safe – enrich your day with a museum or a good film. Consider a virtual tour from your hotel.",
    "Clear": "A perfect day for outdoor adventures – explore nature trails, scenic viewpoints, or take a walking tour of the city.",
    "Clouds": "Cloudy skies are great for a mix of culture, parks, and sightseeing. Try an urban garden or local market.",
}

# Display current city time and weather description with temperature
st.write(f"The time now in {city} is {actual_cite_time1} and the weather there is {weather_description}, {main_temp} {temp_sym}.\n")

###################################################################



# Define date range for historical weather: last 10 years (3650 days)
end_date = (actual_cite_time - dt.timedelta(days=1)).strftime("%Y-%m-%d")  # Subtract 1 day for server time fix
start_date = (actual_cite_time - dt.timedelta(days=3650)).strftime("%Y-%m-%d")

# Title for historical weather section
st.title(f"Historical Weather - {city} ")

# Construct Open-Meteo API URL for daily max/min temperature and precipitation
url = (
    f"https://archive-api.open-meteo.com/v1/archive?"
    f"latitude={coord_lat}&longitude={coord_lon}&start_date={start_date}&end_date={end_date}"
    f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
    f"&timezone=Asia%2FJerusalem"
)

# Request historical weather data from Open-Meteo
res = requests.get(url)
data = res.json()

# Create DataFrame from daily weather data
df = pd.DataFrame(data["daily"])
df["time"] = pd.to_datetime(df["time"])
if units == "imperial":
    df['temperature_2m_max'] = df['temperature_2m_max'] * 9 / 5 + 32
    df['temperature_2m_min'] = df['temperature_2m_min'] * 9 / 5 + 32

# Create copies for monthly and yearly analyses
df_m = df
df_y = df

# Sort and keep last 10 days for detailed recent data (without las one, to avoid data API error)
df = df.sort_values('time').tail(11).iloc[:-1]
# Sort and keep last 365 days for monthly statistics
df_m = df_m.sort_values('time').tail(365)

# Add year and month period columns for grouping by year/month
df_y['year'] = df_y['time'].dt.to_period('Y')
df_m['month'] = df_m['time'].dt.to_period('M')

# Create subplot with two y-axes for temperature and precipitation
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add max temperature line plot (left y-axis)
fig.add_trace(
    go.Scatter(x=df["time"], y=df["temperature_2m_max"], name=f"Max Temp (°{temp_sym})", mode="lines+markers"),
    secondary_y=False,
)

# Add min temperature line plot (left y-axis)
fig.add_trace(
    go.Scatter(x=df["time"], y=df["temperature_2m_min"], name="Min Temp (°{temp_sym})", mode="lines+markers"),
    secondary_y=False,
)

# Add precipitation bar plot (right y-axis)
fig.add_trace(
    go.Bar(x=df["time"], y=df["precipitation_sum"], name="Rain (mm)", opacity=0.6),
    secondary_y=True,
)

# Configure layout with titles and legend position
fig.update_layout(
    title_text="Daily Max/Min Temperature and Rainfall - Last 30 days",
    xaxis_title="Date",
    legend=dict(x=0, y=1.1, orientation="h"),
)

# Set y-axis titles for temperature and rainfall
fig.update_yaxes(title_text="Temperature (°{temp_sym})", secondary_y=False)
fig.update_yaxes(title_text="Rainfall (mm)", secondary_y=True)

# Display the Plotly figure in Streamlit with container width
st.plotly_chart(fig, use_container_width=True)

#######################################################################



# Create two equal columns for side-by-side plots
col1, col2 = st.columns(2)

# ===== Boxplot for monthly precipitation in left column =====
with col1:
    st.write("##### Precipitation last 12 months")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.boxplot(x='precipitation_sum', y='month', data=df_m, ax=ax1)
    ax1.set_title("Boxplot of Rainfall by Month")
    st.pyplot(fig1)

# ===== KDE plot of max temperature by year in right column =====
with col2:
    st.write("##### Max tem last 10 years")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.kdeplot(data=df_y, x="temperature_2m_max", hue="year", ax=ax2)
    ax2.set_title("KDE of Max Temperature by Year")
    st.pyplot(fig2)

######################################################################

# Show header and explanation for recommended places based on weather
st.write("\n\n## Interesting palaces to explorer")
st.write(f"\n\n{weather_texts[weather_main]} Here you can know some places to explorer in {city}")

# Mapping of weather types to Geoapify categories for place search
weather_to_categories = {
    "Thunderstorm": [
        "entertainment.museum",
        "entertainment.cinema",
        "entertainment.planetarium",
        "leisure.spa.sauna",
        "leisure.spa.public_bath",
        "heritage.unesco"
    ],
    "Drizzle": [
        "entertainment.museum",
        "entertainment.cinema",
        "leisure.spa.public_bath",
        "leisure.spa.sauna",
        "entertainment.planetarium",
        "heritage.unesco"
    ],
    "Rain": [
        "entertainment.museum",
        "entertainment.cinema",
        "entertainment.aquarium",
        "entertainment.planetarium",
        "leisure.spa.public_bath",
        "leisure.spa.sauna",
        "heritage.unesco"
    ],
    "Snow": [
        "natural.mountain.glacier",
        "natural.mountain.peak",
        "entertainment.theme_park",
        "leisure.spa.public_bath",
        "leisure.spa.sauna"
    ],
    "Mist": [
        "entertainment.museum",
        "entertainment.cinema",
        "heritage.unesco",
        "entertainment.culture.theatre"
    ],
    "Smoke": [
        "entertainment.museum",
        "entertainment.cinema",
        "heritage.unesco"
    ],
    "Haze": [
        "entertainment.museum",
        "entertainment.cinema",
        "heritage.unesco"
    ],
    "Dust": [
        "entertainment.museum",
        "entertainment.cinema",
        "heritage.unesco"
    ],
    "Fog": [
        "entertainment.museum",
        "entertainment.cinema",
        "heritage.unesco"
    ],
    "Sand": [
        "entertainment.museum",
        "entertainment.cinema",
        "heritage.unesco"
    ],
    "Ash": [
        "entertainment.museum",
        "entertainment.cinema",
        "heritage.unesco"
    ],
    "Squall": [
        "entertainment.museum",
        "entertainment.cinema",
        "leisure.spa.sauna",
        "heritage.unesco"
    ],
    "Tornado": [
        "entertainment.museum",
        "entertainment.cinema",
        "heritage.unesco"
    ],
    "Clear": [
        "tourism.attraction",
        "tourism.attraction.viewpoint",
        "tourism.attraction.fountain",
        "tourism.attraction.artwork",
        "tourism.sights.castle",
        "tourism.sights.bridge",
        "tourism.sights.memorial.monument",
        "tourism.sights.city_hall",
        "tourism.sights.tower",
        "tourism.sights.lighthouse",
        "tourism.sights.archaeological_site",
        "tourism.sights.windmill",
        "entertainment.zoo",
        "entertainment.activity_park",
        "entertainment.activity_park.trampoline",
        "entertainment.activity_park.climbing",
        "entertainment.water_park",
        "natural.forest",
        "natural.mountain.peak",
        "natural.water.spring",
        "natural.water.hot_spring",
        "natural.water.geyser",
        "natural.water.sea",
        "leisure.park",
        "leisure.park.garden",
        "leisure.playground",
        "leisure.picnic.picnic_site",
        "leisure.picnic.picnic_table",
        "leisure.picnic.bbq",
        "heritage.unesco"
    ],
    "Clouds": [
        "tourism.attraction",
        "tourism.sights.castle",
        "entertainment.museum",
        "entertainment.cinema",
        "entertainment.culture.gallery",
        "leisure.park",
        "heritage.unesco"
    ]
}

# Function to get recommended categories by weather type
def get_trip_recommendations(weather_type):
    return weather_to_categories.get(weather_type, [])

# Current weather type
weather_now = weather_main
# Get categories recommended for current weather
recommended_categories = get_trip_recommendations(weather_now)


# Fetch places from Geoapify API based on coordinates and categories
def fetch_attractions(lat, lon, key_atr, categories, radius=2000):
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": ",".join(categories),
        "filter": f"circle:{lon},{lat},{radius}",
        "limit": 20,
        "apiKey": key_atr
    }

    res = requests.get(url, params=params)

    if res.status_code == 200:
        data = res.json().get("features", [])
        attractions = []
        for feat in data:
            props = feat["properties"]
            attractions.append({
                "name": props.get("name"),
                "type": props.get("categories", [])[0] if props.get("categories") else "",
                "lat": props.get("lat"),
                "lon": props.get("lon")
            })
        return attractions
    else:
        print("API Error:", res.status_code, res.text)
        return []

# Create DataFrame from attractions list
atr_city = pd.DataFrame(fetch_attractions(coord_lat, coord_lon, KEY_ATR, recommended_categories, radius=2000))

# Create folium map centered at city coordinates with zoom 15
m = folium.Map(location=[coord_lat, coord_lon], zoom_start=14)

# Add marker for city center
folium.Marker([coord_lat, coord_lon], popup=city).add_to(m)

# Add markers for each recommended attraction
for idx, place in atr_city.iterrows():
    folium.Marker(
        location=[place['lat'], place['lon']],
        popup=folium.Popup(place['name'], max_width=200),
        tooltip=place['name'],
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)

# Save map to HTML file locally
m.save("places_map.html")

# Show map in Streamlit app
st.title("Local map")
folium_static(m)

# Display user timezone and local time in the app
st.write(f"User time Zone is {timezone}. {time_now_user}")

