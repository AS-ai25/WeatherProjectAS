# https://bulk.openweathermap.org/sample/city.list.json.gz cities list data


import json
import pandas as pd
import pycountry
import requests
import datetime as dt
import os


SETTINGS_FILE = "settings.json"
#deafolt user parameters
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"city": "Jerusalem,Israel", "units": "metric"}

#save last choose parapeters
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

#show deafolt parameters
settings = load_settings()
print(f"\nDefault city: {settings['city']}")
print(f"Default units: {settings['units']}")

#choose new parameters
city = input("Enter city (leave empty for default): ").strip()
units = input("Enter units (metric/imperial, leave empty for default): ").strip()
if city:
    settings["city"] = city
if units in ["metric", "imperial"]:
    settings["units"] = units
save_settings(settings)


with open("DATA_BASE/city.list.json", "r", encoding="utf-8") as f:
    city_data = json.load(f)
city_data_table = pd.DataFrame(city_data)
#print(city_data_table.head())

#add complate country name base country code
def get_country_name(country_code):
    country = pycountry.countries.get(alpha_2=country_code.upper())
    return country.name if country else "Unknown"

#add columns country full name and coty_finder that included City name, Country full name
city_data_table['country_fn'] = city_data_table['country'].apply(get_country_name)
city_data_table['city_finder'] = city_data_table.apply(lambda row: row['name'] + ',' + row['country_fn'], axis=1)
# city_data_table['city_finder'] = city_data_table['name']+','+city_data_table['country_fn']
city_data_table['lat'] = city_data_table['coord'].apply(lambda x: x['lat'])
city_data_table['lon'] = city_data_table['coord'].apply(lambda x: x['lon'])
city_data_table = city_data_table.dropna()
city_data_table = city_data_table.drop_duplicates(subset='city_finder')

# print(city_data_table['lat']    ,city_data_table['lon'])
# print(city_data_table.dtypes)
print(city_data_table.columns)
#print(city_data_table.head())
print(city_data_table[city_data_table.name == 'Jerusalem'])
# print(city_data[200:202:])

#get weather to specific city
KEY_W = 'abb622fc56c5a7f79bb4539ab03cc961'  # OpenWeatherMap

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

print(city)
selected_city = city_data_table[city_data_table.city_finder == settings["city"]]
#selected_city = city_data_table[city_data_table.city_finder == 'Jerusalem,Israel']
weather = get_weather(selected_city['lat'], selected_city['lon'], KEY_W)

#weather information from API weather
coord_lon = weather['coord']['lon']
coord_lat = weather['coord']['lat']
weather_main = weather['weather'][0]['main']
weather_description = weather['weather'][0]['description']
weather_code = icon = weather['weather'][0]['icon']
main_temp = weather['main']['temp']
if settings["units"] == 'metric':temp_sym='C'
if settings["units"] == 'imperial':temp_sym='F'
main_temp_max = weather['main']['temp_max']
main_temp_min = weather['main']['temp_min']
wind_speed = weather['wind']['speed']
clouds_all = weather['clouds']['all']
city_time = weather['dt']
city_timezone = weather['timezone']

#get weather icon from the web
icon_code = weather['weather'][0]['icon']
url_icon = f"https://openweathermap.org/img/wn/{weather_code}@2x.png"
# st.image(url_icon, caption="Weather Icon"

#get actual chosen city time
actual_cite_time = dt.datetime.now(dt.timezone.utc)+dt.timedelta(seconds=city_timezone)
actual_cite_time = actual_cite_time.strftime("%H:%M:%S %A %d-%m-%Y ")
print(f"The time now in {selected_city.city_finder.iloc[0]} is {actual_cite_time} {main_temp} {temp_sym}")


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


def get_trip_recommendations(weather_type):
    return weather_to_categories.get(weather_type, [])

#def get_trip_descriptions(categories):
#    return [category_descriptions.get(cat, cat) for cat in categories]

weather_now = weather_main
recommended_categories = get_trip_recommendations(weather_now)
#print(recommended_categories)


KEY_ATR = "74fb904f381e44fca6a70c993515d53d"

def fetch_attractions(lat, lon, key_atr,categories, radius=2000):
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




#def filter_attractions_by_weather(attractions, weather_main):
#    allowed = weather_map.get(weather_main.lower(), [])
#    return [a for a in attractions if any(tag in a["type"] for tag in allowed)]


atr_city = pd.DataFrame(fetch_attractions(coord_lat, coord_lon, KEY_ATR, recommended_categories, radius=2000))
for idx, row in atr_city.iterrows():
    print(row['name'],row['lon'])
print(weather_main)

# good = filter_attractions_by_weather(atr, wm)
# st.markdown("### Attractions For This Weather:")
# for a in atr:#good:
#    st.write(f"- {a['name']} ({a['type']})")

'''
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="🌍 World Cities Weather Map", layout="wide")

# 🔑 הכנס כאן את ה־API KEY שלך
API_KEY = "PUT_YOUR_OPENWEATHERMAP_API_KEY_HERE"

# 1. טוען את רשימת הערים
@st.cache_data
def load_city_data():
    df = pd.read_csv("worldcities.csv")
    df = df.dropna(subset=["city", "country", "lat", "lng"])
    df["label"] = df["city"] + ", " + df["country"]
    return df

cities_df = load_city_data()

# 2. בחירת עיר
selected_city = st.selectbox("🌐 Choose a city", cities_df["label"].sort_values())
city_row = cities_df[cities_df["label"] == selected_city].iloc[0]

# 3. הצגת פרטי עיר
st.markdown(f"## 🏙 {city_row['city']}, {city_row['country']}")
st.write(f"📍 Coordinates: ({city_row['lat']}, {city_row['lng']})")
if not pd.isna(city_row.get("population")):
    st.write(f"👥 Population: {int(city_row['population']):,}")

# 4. הצגת מיקום על המפה
st.map(pd.DataFrame([{"lat": city_row["lat"], "lon": city_row["lng"]}]), zoom=8)

# 5. שליפת מזג אוויר מה־API
def get_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        return res.json()
    return None

weather = get_weather(city_row["lat"], city_row["lng"])

# 6. הצגת נתוני מזג אוויר
if weather:
    st.markdown("### 🌤 Current Weather:")
    st.write(f"🌡 Temperature: {weather['main']['temp']}°C")
    st.write(f"🥵 Feels like: {weather['main']['feels_like']}°C")
    st.write(f"💧 Humidity: {weather['main']['humidity']}%")
    st.write(f"🌬 Wind Speed: {weather['wind']['speed']} m/s")
    st.write(f"☁ Weather: {weather['weather'][0]['description'].title()}")
else:
    st.warning("Weather data not available.")






    --------------------------


    attractions = [
    {"name": "Museum of Art", "type": "museum"},
    {"name": "Central Park", "type": "park"},
    {"name": "Sunny Beach", "type": "beach"},
    {"name": "Cozy Cafe", "type": "cafe"},
    {"name": "Ski Resort", "type": "ski"},
    {"name": "City Mall", "type": "mall"},
]


weather_map = {
    "clear": ["park", "beach", "hiking"],
    "rain": ["museum", "cafe", "mall"],
    "clouds": ["park", "museum", "mall"],
    "snow": ["ski", "museum", "indoor"],
    "thunderstorm": ["indoor", "museum", "mall"],
}


def filter_attractions_by_weather(attractions, weather_main):
    weather_main = weather_main.lower()
    allowed_types = weather_map.get(weather_main, [])
    filtered = [a for a in attractions if a["type"] in allowed_types]
    return filtered

    import streamlit as st

# דוגמת אטרקציות
attractions = [
    {"name": "Museum of Art", "type": "museum"},
    {"name": "Central Park", "type": "park"},
    {"name": "Sunny Beach", "type": "beach"},
    {"name": "Cozy Cafe", "type": "cafe"},
    {"name": "Ski Resort", "type": "ski"},
    {"name": "City Mall", "type": "mall"},
]

# מיפוי מזג אוויר לסוגי אטרקציות
weather_map = {
    "clear": ["park", "beach", "hiking"],
    "rain": ["museum", "cafe", "mall"],
    "clouds": ["park", "museum", "mall"],
    "snow": ["ski", "museum", "indoor"],
    "thunderstorm": ["indoor", "museum", "mall"],
}

def filter_attractions_by_weather(attractions, weather_main):
    weather_main = weather_main.lower()
    allowed_types = weather_map.get(weather_main, [])
    filtered = [a for a in attractions if a["type"] in allowed_types]
    return filtered

# דוגמה של מזג אוויר נבחר (בפועל ישלב בקוד שלך את התוצאה מה-API)
weather_main = st.selectbox("Choose weather condition", ["Clear", "Rain", "Clouds", "Snow", "Thunderstorm"])

filtered_attractions = filter_attractions_by_weather(attractions, weather_main)

st.write(f"### Attractions suitable for {weather_main} weather:")
for a in filtered_attractions:
    st.write(f"- {a['name']} ({a['type']})")


0000000000000000000000000

with tur

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weather & Attractions", layout="wide")

API_KEY_WEATHER = "YOUR_OPENWEATHERMAP_KEY"
API_KEY_PLACES = "YOUR_GEOAPIFY_KEY"

def get_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    res = requests.get(url, params={"lat": lat, "lon": lon, "appid": API_KEY_WEATHER, "units": "metric"})
    if res.status_code == 200:
        return res.json()
    return None

def fetch_attractions(lat, lon, radius=2000):
    # ... use function above ...
    return fetch_attractions(lat, lon, radius, API_KEY_PLACES)

# --- UI ---
cities_df = pd.read_json("cities.json")  # או DataFrame של ערים
cities_df['label'] = cities_df['name'] + ", " + cities_df['country']
selected_label = st.selectbox("Select city", cities_df["label"].sort_values())
city = cities_df[cities_df["label"] == selected_label].iloc[0]

st.map(pd.DataFrame([{"lat": city["lat"], "lon": city["lon"]}]), zoom=10)

weather = get_weather(city["lat"], city["lon"])
if weather:
    wm = weather['weather'][0]['main']
    desc = weather['weather'][0]['description'].title()
    icon_url = f"https://openweathermap.org/img/wn/{weather['weather'][0]['icon']}@2x.png"

    st.columns([1, 3])[0].image(icon_url, width=80)
    st.columns([1, 3])[1].markdown(f"### {desc}\n🌡️ {weather['main']['temp']}°C  •  💧 {weather['main']['humidity']}%")

    tip = {
        "clear": "☀️ מושלם לטיול בטבע או פארק.",
        "rain": "🌧️ רצוי לפעילויות פנימיות כמו מוזיאון או קפה.",
        "clouds": "☁️ מתאים לטיול עירוני או קניון.",
        "snow": "❄️ זמן מצוין לסקי או אטרקציות חורף.",
        "thunderstorm": "⛈️ עדיף להישאר בפנים.",
    }.get(wm.lower(), "🌤️ מזג אוויר מגוון – מתאים למגוון פעילויות")
    st.info(tip)

    # fetch and filter attractions
    atr = fetch_attractions(city["lat"], city["lon"])
    good = filter_attractions_by_weather(atr, wm)
    st.markdown("### Attractions For This Weather:")
    for a in good:
        st.write(f"- {a['name']} ({a['type']})")
else:
    st.error("Weather data not available.")
    
    
    ---------------------
    
    
    weather_main_types = [
    "Thunderstorm",
    "Drizzle",
    "Rain",
    "Snow",
    "Mist",
    "Smoke",
    "Haze",
    "Dust",
    "Fog",
    "Sand",
    "Ash",
    "Squall",
    "Tornado",
    "Clear",
    "Clouds"
]

"""""
'''
