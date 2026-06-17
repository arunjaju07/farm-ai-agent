from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import requests
import os
from datetime import datetime, timedelta
from app.database.db import SessionLocal
from app.models.location_model import Location

router = APIRouter()

# Weather API configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5"

# Request/Response models
class WeatherRequest(BaseModel):
    location_id: int
    
class WeatherResponse(BaseModel):
    location_name: str
    region: str
    temperature: float
    temperature_celsius: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_direction: int
    weather_main: str
    weather_description: str
    weather_icon: str
    sunrise: str
    sunset: str
    last_updated: str
    forecast: List[dict]

class ForecastResponse(BaseModel):
    date: str
    temperature_min: float
    temperature_max: float
    weather_main: str
    weather_description: str
    weather_icon: str
    humidity: int
    wind_speed: float
    rain_probability: float

@router.get("/weather/locations")
def get_weather_locations():
    """Get all locations for weather selection"""
    db = SessionLocal()
    try:
        locations = db.query(Location).all()
        return [
            {
                "id": loc.id,
                "name": loc.name,
                "region": loc.region,
                "area_acres": loc.area_acres
            }
            for loc in locations
        ]
    finally:
        db.close()

# Weather API configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")  # ← DO NOT hardcode the key here!
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5"

# ... (rest of your imports and code)

@router.post("/weather/current")
def get_current_weather(request: WeatherRequest):
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=503, detail="Weather service not configured")
    
    db = SessionLocal()
    try:
        # Get location details
        location = db.query(Location).filter(Location.id == request.location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # ========== UPDATED COORDINATES ==========
        # EXACT coordinates based on location name/region
        if "Morshi" in location.name or "Maharashtra" in location.region:
            lat = 21.3266   # Exact Morshi, Amravati coordinates
            lon = 77.99628
        elif "Ramanjapur" in location.name or "Ramanjapur" in location.region:
            lat = 18.33284  # Exact Rāmanjāpur, Telangana coordinates
            lon = 78.6187
        else:
            # Fallback coordinates (in case of unknown location)
            lat = 17.3850   # Default to Hyderabad
            lon = 78.4867
        # ========================================
            
        # Get current weather
        current_url = f"{WEATHER_API_URL}/weather"
        current_params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        current_response = requests.get(current_url, params=current_params)
        current_response.raise_for_status()
        current_data = current_response.json()
        
        
        # Get 5-day forecast
        forecast_url = f"{WEATHER_API_URL}/forecast"
        forecast_params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": 40  # 5 days * 8 readings per day
        }
        
        forecast_response = requests.get(forecast_url, params=forecast_params)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Process forecast data - group by day
        daily_forecasts = {}
        for item in forecast_data['list']:
            date_str = item['dt_txt'].split(' ')[0]
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    'temps': [],
                    'humidity': [],
                    'wind_speed': [],
                    'weather_main': item['weather'][0]['main'],
                    'weather_description': item['weather'][0]['description'],
                    'weather_icon': item['weather'][0]['icon'],
                    'rain_probability': item.get('pop', 0) * 100
                }
                daily_forecasts[date_str]['temps'].append(item['main']['temp'])
                daily_forecasts[date_str]['humidity'].append(item['main']['humidity'])
                daily_forecasts[date_str]['wind_speed'].append(item['wind']['speed'])
            else:
                daily_forecasts[date_str]['temps'].append(item['main']['temp'])
                daily_forecasts[date_str]['humidity'].append(item['main']['humidity'])
                daily_forecasts[date_str]['wind_speed'].append(item['wind']['speed'])
                # Update weather for the day
                if item['weather'][0]['main'] != daily_forecasts[date_str]['weather_main']:
                    daily_forecasts[date_str]['weather_main'] = item['weather'][0]['main']
                    daily_forecasts[date_str]['weather_description'] = item['weather'][0]['description']
                    daily_forecasts[date_str]['weather_icon'] = item['weather'][0]['icon']
        
        # Build forecast list
        forecast_list = []
        for date_str, data in list(daily_forecasts.items())[:5]:  # Max 5 days
            if data['temps']:
                forecast_list.append({
                    'date': date_str,
                    'temperature_min': min(data['temps']),
                    'temperature_max': max(data['temps']),
                    'weather_main': data['weather_main'],
                    'weather_description': data['weather_description'],
                    'weather_icon': data['weather_icon'],
                    'humidity': sum(data['humidity']) // len(data['humidity']),
                    'wind_speed': sum(data['wind_speed']) / len(data['wind_speed']),
                    'rain_probability': data['rain_probability']
                })
        
        # Format sunrise/sunset times
        sunrise_time = datetime.fromtimestamp(current_data['sys']['sunrise']).strftime('%I:%M %p')
        sunset_time = datetime.fromtimestamp(current_data['sys']['sunset']).strftime('%I:%M %p')
        
        return {
            "location_name": location.name,
            "region": location.region,
            "temperature": current_data['main']['temp'],
            "temperature_celsius": current_data['main']['temp'],
            "feels_like": current_data['main']['feels_like'],
            "humidity": current_data['main']['humidity'],
            "pressure": current_data['main']['pressure'],
            "wind_speed": current_data['wind']['speed'],
            "wind_direction": current_data['wind'].get('deg', 0),
            "weather_main": current_data['weather'][0]['main'],
            "weather_description": current_data['weather'][0]['description'],
            "weather_icon": current_data['weather'][0]['icon'],
            "sunrise": sunrise_time,
            "sunset": sunset_time,
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "forecast": forecast_list
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")
    finally:
        db.close()

@router.get("/weather/forecast/{location_id}")
def get_weather_forecast(location_id: int):
    """Get 5-day forecast for a location"""
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=503, detail="Weather service not configured")
    
    db = SessionLocal()
    try:
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Use same coordinates as above
        lat = 17.3850
        lon = 78.4867
        
        if "Maharashtra" in location.region:
            lat = 18.5204
            lon = 73.8567
        
        forecast_url = f"{WEATHER_API_URL}/forecast"
        forecast_params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(forecast_url, params=forecast_params)
        response.raise_for_status()
        data = response.json()
        
        # Group by day
        daily_forecasts = {}
        for item in data['list']:
            date_str = item['dt_txt'].split(' ')[0]
            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    'temps': [],
                    'weather_main': item['weather'][0]['main'],
                    'weather_description': item['weather'][0]['description'],
                    'weather_icon': item['weather'][0]['icon'],
                    'rain_probability': item.get('pop', 0) * 100
                }
            daily_forecasts[date_str]['temps'].append(item['main']['temp'])
            if item.get('pop', 0) * 100 > daily_forecasts[date_str]['rain_probability']:
                daily_forecasts[date_str]['rain_probability'] = item.get('pop', 0) * 100
        
        forecast_list = []
        for date_str, data in list(daily_forecasts.items())[:5]:
            if data['temps']:
                forecast_list.append({
                    'date': date_str,
                    'temperature_min': min(data['temps']),
                    'temperature_max': max(data['temps']),
                    'weather_main': data['weather_main'],
                    'weather_description': data['weather_description'],
                    'weather_icon': data['weather_icon'],
                    'rain_probability': data['rain_probability']
                })
        
        return {
            "location_name": location.name,
            "forecast": forecast_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecast: {str(e)}")
    finally:
        db.close()