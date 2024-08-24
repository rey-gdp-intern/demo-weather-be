from fastapi import FastAPI
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
import os
import pytz

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility function to get the current location using IP Geolocation API (IPv4 only)
def get_current_location():
    api_key = os.getenv("IPGEOLOCATION_API_KEY")
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ipVersion=4"  # Enforce IPv4
    try:
        response = requests.get(url)
        data = response.json()
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        city = data['city']
        return latitude, longitude, city
    except Exception as e:
        print(f"Error getting location: {e}")
        # Fallback to Jakarta's coordinates
        return -6.2088, 106.8456, "Jakarta"

@app.get("/")
async def root():
    return "ok"

@app.get("/api/weather")
async def get_weather():
    # Get the user's current location or fallback to Jakarta
    latitude, longitude, city = get_current_location()

    # Prepare the parameters for the Open-Meteo API to get current weather
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "precipitation", "rain"],
        "forecast_days": 1
    }
    url = "https://api.open-meteo.com/v1/forecast"
    
    # Make the API request
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Process the current weather data
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_precipitation = current.Variables(1).Value()
    current_rain = current.Variables(2).Value()
    current_time = pd.to_datetime(current.Time(), unit="s", utc=True)

    # Convert current time to Jakarta timezone
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    current_time = current_time.tz_convert(jakarta_tz)

    # Return the current weather data
    return {
        "city": city,
        "temperature_2m": current_temperature_2m,
        "precipitation": current_precipitation,
        "rain": current_rain,
        "time": current_time.isoformat()
    }