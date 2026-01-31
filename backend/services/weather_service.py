import os
import random
from typing import Dict, Optional
import httpx
from datetime import datetime

class WeatherService:
    """
    Service to fetch real-time weather data or provide simulated weather
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.default_city = os.getenv("DEFAULT_CITY", "London")
        self.use_simulation = os.getenv("USE_WEATHER_SIMULATION", "true").lower() == "true"
        self._cached_weather = None
        self._last_update = None
        
    async def get_current_weather(self, city: Optional[str] = None) -> Dict:
        """
        Get current weather for a city
        """
        target_city = city or self.default_city
        
        # Check cache (15 minutes)
        now = datetime.now()
        if (self._cached_weather and self._last_update and 
            (now - self._last_update).total_seconds() < 900):
            return self._cached_weather
            
        if self.use_simulation or not self.api_key:
            weather = self._simulate_weather(target_city)
        else:
            weather = await self._fetch_from_api(target_city)
            
        self._cached_weather = weather
        self._last_update = now
        return weather
        
    def _simulate_weather(self, city: str) -> Dict:
        """Simulate realistic weather data"""
        conditions = [
            {"condition": "clear", "visibility": 10000, "precipitation": 0, "temp": 22},
            {"condition": "cloudy", "visibility": 8000, "precipitation": 0, "temp": 18},
            {"condition": "rain", "visibility": 4000, "precipitation": 5, "temp": 15},
            {"condition": "heavy_rain", "visibility": 1500, "precipitation": 15, "temp": 12},
            {"condition": "fog", "visibility": 500, "precipitation": 0, "temp": 10},
        ]
        
        # Select random condition based on time (more likely to be clear/cloudy)
        weights = [0.5, 0.3, 0.1, 0.05, 0.05]
        selected = random.choices(conditions, weights=weights)[0]
        
        return {
            "city": city,
            "condition": selected["condition"],
            "temperature": selected["temp"] + random.uniform(-2, 2),
            "humidity": random.randint(40, 90),
            "visibility": selected["visibility"],
            "precipitation": selected["precipitation"],
            "wind_speed": random.uniform(2, 25),
            "is_simulated": True,
            "timestamp": datetime.now().isoformat()
        }
        
    async def _fetch_from_api(self, city: str) -> Dict:
        """Fetch weather from OpenWeatherMap API"""
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Map API conditions to our internal condition types
                main_condition = data["weather"][0]["main"].lower()
                condition_map = {
                    "clear": "clear",
                    "clouds": "cloudy",
                    "rain": "rain",
                    "drizzle": "rain",
                    "thunderstorm": "heavy_rain",
                    "fog": "fog",
                    "mist": "fog",
                    "snow": "snow"
                }
                
                return {
                    "city": data["name"],
                    "condition": condition_map.get(main_condition, "clear"),
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "visibility": data.get("visibility", 10000),
                    "precipitation": data.get("rain", {}).get("1h", 0),
                    "wind_speed": data["wind"]["speed"],
                    "is_simulated": False,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return self._simulate_weather(city)

# Singleton
_weather_service = WeatherService()

def get_weather_service() -> WeatherService:
    return _weather_service
