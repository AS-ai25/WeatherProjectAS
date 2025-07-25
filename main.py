# https://bulk.openweathermap.org/sample/city.list.json.gz cities list data

import json
import pandas as pd
import streamlit as st
import pycountry
import requests

with open("DATA_BASE/city.list.json", "r", encoding="utf-8") as f:
    city_data = json.load(f)

city_data_table = pd.DataFrame(city_data)


def get_country_name(city_code):
    country = pycountry.countries.get(alpha_2=city_code.upper())
    return country.name if country else "Unknown"


city_data_table['country_fn'] = city_data_table['country'].apply(get_country_name)
city_data_table['city_finder'] = city_data_table.apply(lambda row: row['name'] + ',' + row['country_fn'], axis=1)
# city_data_table['city_finder'] = city_data_table['name']+','+city_data_table['country_fn']
city_data_table['lat'] = city_data_table['coord'].apply(lambda x: x['lat'])
city_data_table['lon'] = city_data_table['coord'].apply(lambda x: x['lon'])
city_data_table.dropna()

# print(city_data_table['lat']    ,city_data_table['lon'])
# print(city_data_table.dtypes)
print(city_data_table.columns)
# print(city_data_table.coord)
print(city_data_table)
# print(city_data[200:202:])

KEY_W = 'abb622fc56c5a7f79bb4539ab03cc961'  # OpenWeatherMap


def get_weather(lat, lon, KEY):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": KEY,
        "units": "metric"
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        return res.json()
    return None


selected_city = city_data_table[city_data_table.city_finder == 'Tel Aviv,Israel']

weather = get_weather(selected_city['lat'], selected_city['lon'], KEY_W)

coord_lon = weather['coord']['lon']
coord_lat = weather['coord']['lat']
weather_main = weather['weather'][0]['main']
weather_description = weather['weather'][0]['description']
weather_code = icon = weather['weather'][0]['icon']
main_temp = weather['main']['temp']
main_temp_max = weather['main']['temp_max']
main_temp_min = weather['main']['temp_min']
wind_speed = weather['wind']['speed']
clouds_all = weather['clouds']['all']
city_time = weather['dt']
city_timezone = weather['timezone']

icon_code = weather['weather'][0]['icon']
url_icon = f"https://openweathermap.org/img/wn/{weather_code}@2x.png"
# st.image(url_icon, caption="Weather Icon"

KEY_ATR = "74fb904f381e44fca6a70c993515d53d"
import requests


def fetch_attractions(lat, lon, key_atr, radius=2000):
    url = "https://api.geoapify.com/v2/places"
    categories = [
        # Tourism
        "tourism.attraction",
        "tourism.attraction.artwork",
        "tourism.attraction.viewpoint",
        "tourism.attraction.fountain",
        "tourism.attraction.clock",
        "tourism.sights.castle",
        "tourism.sights.memorial",
        "tourism.sights.memorial.tomb",
        "tourism.sights.memorial.monument",
        "tourism.sights.city_hall",
        "tourism.sights.bridge",
        "tourism.sights.archaeological_site",
        "tourism.sights.windmill",
        "tourism.sights.tower",
        "tourism.sights.lighthouse",
        "tourism.information.office",
        "tourism.information.map",

        # Entertainment
        "entertainment.museum",
        "entertainment.zoo",
        "entertainment.cinema",
        "entertainment.aquarium",
        "entertainment.planetarium",
        "entertainment.bowling_alley",
        "entertainment.theme_park",
        "entertainment.water_park",
        "entertainment.escape_game",
        "entertainment.amusement_arcade",
        "entertainment.activity_park.trampoline",
        "entertainment.activity_park.climbing",
        "entertainment.activity_park",
        "entertainment.culture.theatre",
        "entertainment.culture.arts_centre",
        "entertainment.culture.gallery",

        # Leisure
        "leisure.park",
        "leisure.park.garden",
        "leisure.park.nature_reserve",
        "leisure.playground",
        "leisure.picnic.picnic_site",
        "leisure.picnic.picnic_table",
        "leisure.picnic.bbq",
        "leisure.spa.public_bath",
        "leisure.spa.sauna",

        # Natural
        "natural.forest",
        "natural.water.sea",
        "natural.water.spring",
        "natural.water.reef",
        "natural.water.hot_spring",
        "natural.water.geyser",
        "natural.mountain.peak",
        "natural.mountain.glacier",
        "natural.mountain.cliff",
        "natural.mountain.rock",
        "natural.mountain.cave_entrance",
        "natural.sand.dune",
        "natural.protected_area",

        # Heritage
        "heritage.unesco"
    ]


    params = {
        "categories": categories,
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


weather_map = {
    "clear": ["park", "beach", "tourism.sightseeing", "hiking"],
    "rain": ["museum", "cafe", "mall", "indoor"],
    "clouds": ["park", "museum", "mall"],
    "snow": ["ski", "indoor"],
    "thunderstorm": ["indoor", "museum", "mall"],
}


def filter_attractions_by_weather(attractions, weather_main):
    allowed = weather_map.get(weather_main.lower(), [])
    return [a for a in attractions if any(tag in a["type"] for tag in allowed)]


atr_city = pd.DataFrame(fetch_attractions(coord_lat, coord_lon, KEY_ATR,radius=2000))
print(atr_city.groupby('type')['type'].value_counts())#for a in atr :print(a['name'], a['type'])
#good = filter_attractions_by_weather(atr, wm)
#st.markdown("### Attractions For This Weather:")
#for a in atr:#good:
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

"""""
'''
