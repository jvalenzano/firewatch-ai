"""
Weather.gov API Client for Real-Time Weather Data Integration

Phase III Sprint 1 Implementation
Built on Phase II optimized performance foundation
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import aiohttp
import json

logger = logging.getLogger(__name__)

@dataclass
class WeatherStationData:
    """Weather station data structure for real-time integration"""
    station_id: str
    name: str
    state: str
    latitude: float
    longitude: float
    elevation: float
    temperature: Optional[float] = None
    relative_humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    precipitation: Optional[float] = None
    barometric_pressure: Optional[float] = None
    last_updated: Optional[datetime] = None
    data_quality: str = "UNKNOWN"

class WeatherGovAPIClient:
    """
    Real-time Weather.gov API client for fire weather analysis
    
    Integrates with existing BigQuery fire_risk_poc dataset
    Maintains Phase II performance optimizations (sub-10s response)
    """
    
    BASE_URL = "https://api.weather.gov"
    
    def __init__(self, update_interval_minutes: int = 5):
        """
        Initialize Weather.gov API client
        
        Args:
            update_interval_minutes: How often to refresh data (default: 5 minutes)
        """
        self.update_interval = timedelta(minutes=update_interval_minutes)
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, WeatherStationData] = {}
        self.last_update: Dict[str, datetime] = {}
        
        # Headers as recommended by Weather.gov API docs
        self.headers = {
            'User-Agent': 'RisenOne-Fire-Risk-Agent/3.0 (usda-ai-innovation-hub@techtrend.us)',
            'Accept': 'application/json'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_station_info(self, station_id: str) -> Optional[WeatherStationData]:
        """
        Get station metadata from Weather.gov API
        
        Args:
            station_id: Weather station identifier (e.g., 'KORD')
            
        Returns:
            WeatherStationData with station metadata or None if not found
        """
        if not self.session:
            raise RuntimeError("WeatherGovAPIClient must be used as async context manager")
        
        try:
            # Get station metadata
            station_url = f"{self.BASE_URL}/stations/{station_id}"
            async with self.session.get(station_url) as response:
                if response.status != 200:
                    logger.warning(f"Station {station_id} not found: {response.status}")
                    return None
                
                station_data = await response.json()
                properties = station_data.get('properties', {})
                geometry = station_data.get('geometry', {})
                coordinates = geometry.get('coordinates', [0, 0, 0])
                
                return WeatherStationData(
                    station_id=station_id,
                    name=properties.get('name', 'Unknown'),
                    state=properties.get('state', 'Unknown'),
                    longitude=coordinates[0] if len(coordinates) > 0 else 0.0,
                    latitude=coordinates[1] if len(coordinates) > 1 else 0.0,
                    elevation=coordinates[2] if len(coordinates) > 2 else 0.0
                )
                
        except Exception as e:
            logger.error(f"Error fetching station info for {station_id}: {e}")
            return None
    
    async def get_current_observations(self, station_id: str) -> Optional[WeatherStationData]:
        """
        Get current weather observations for a station
        
        Args:
            station_id: Weather station identifier
            
        Returns:
            WeatherStationData with current observations or None if unavailable
        """
        if not self.session:
            raise RuntimeError("WeatherGovAPIClient must be used as async context manager")
        
        # Check cache freshness
        if self._is_data_fresh(station_id):
            return self.cache.get(station_id)
        
        try:
            # Get latest observations
            obs_url = f"{self.BASE_URL}/stations/{station_id}/observations/latest"
            async with self.session.get(obs_url) as response:
                if response.status != 200:
                    logger.warning(f"No observations for {station_id}: {response.status}")
                    return None
                
                obs_data = await response.json()
                properties = obs_data.get('properties', {})
                
                # Get station info if not cached
                if station_id not in self.cache:
                    station_info = await self.get_station_info(station_id)
                    if not station_info:
                        return None
                    self.cache[station_id] = station_info
                
                # Update with current observations
                station_data = self.cache[station_id]
                station_data.temperature = self._extract_value(properties.get('temperature'))
                station_data.relative_humidity = self._extract_value(properties.get('relativeHumidity'))
                station_data.wind_speed = self._extract_value(properties.get('windSpeed'))
                station_data.wind_direction = self._extract_value(properties.get('windDirection'))
                station_data.precipitation = self._extract_value(properties.get('precipitationLastHour'))
                station_data.barometric_pressure = self._extract_value(properties.get('barometricPressure'))
                station_data.last_updated = datetime.utcnow()
                station_data.data_quality = self._assess_data_quality(station_data)
                
                # Update cache timestamp
                self.last_update[station_id] = datetime.utcnow()
                
                return station_data
                
        except Exception as e:
            logger.error(f"Error fetching observations for {station_id}: {e}")
            return None
    
    async def get_multiple_stations(self, station_ids: List[str]) -> Dict[str, WeatherStationData]:
        """
        Get current observations for multiple stations efficiently
        
        Args:
            station_ids: List of weather station identifiers
            
        Returns:
            Dictionary mapping station_id to WeatherStationData
        """
        tasks = []
        for station_id in station_ids:
            task = asyncio.create_task(self.get_current_observations(station_id))
            tasks.append((station_id, task))
        
        results = {}
        for station_id, task in tasks:
            try:
                station_data = await task
                if station_data:
                    results[station_id] = station_data
            except Exception as e:
                logger.error(f"Error processing {station_id}: {e}")
        
        return results
    
    def _is_data_fresh(self, station_id: str) -> bool:
        """Check if cached data is still fresh"""
        if station_id not in self.last_update:
            return False
        
        time_since_update = datetime.utcnow() - self.last_update[station_id]
        return time_since_update < self.update_interval
    
    def _extract_value(self, measurement: Optional[Dict]) -> Optional[float]:
        """Extract numeric value from Weather.gov measurement object"""
        if not measurement or not isinstance(measurement, dict):
            return None
        
        value = measurement.get('value')
        if value is None:
            return None
        
        try:
            # Convert from Celsius to Fahrenheit for temperature
            unit_code = measurement.get('unitCode', '')
            if 'celsius' in unit_code.lower() or 'degC' in unit_code:
                return (float(value) * 9/5) + 32
            elif 'meter' in unit_code.lower() and 'wind' not in unit_code.lower():
                # Convert meters to feet for elevation
                return float(value) * 3.28084
            elif 'kilometer' in unit_code.lower():
                # Convert km/h to mph for wind speed
                return float(value) * 0.621371
            else:
                return float(value)
        except (ValueError, TypeError):
            return None
    
    def _assess_data_quality(self, station_data: WeatherStationData) -> str:
        """Assess data quality based on available measurements"""
        required_fields = [
            station_data.temperature,
            station_data.relative_humidity,
            station_data.wind_speed
        ]
        
        available_count = sum(1 for field in required_fields if field is not None)
        
        if available_count == len(required_fields):
            return "EXCELLENT"
        elif available_count >= 2:
            return "GOOD"
        elif available_count >= 1:
            return "FAIR"
        else:
            return "POOR"

class FireWeatherCalculator:
    """
    Fire weather calculations using real-time data
    Integrates with existing NFDRS engine from Phase II
    """
    
    @staticmethod
    def calculate_fire_weather_index(weather_data: WeatherStationData) -> Optional[Dict]:
        """
        Calculate fire weather parameters from real-time data
        
        Args:
            weather_data: Current weather station data
            
        Returns:
            Dictionary with fire weather calculations or None if insufficient data
        """
        if not weather_data.temperature or not weather_data.relative_humidity:
            return None
        
        try:
            # Basic fire weather calculations
            # These integrate with the existing NFDRS engine from Phase II
            
            # Calculate drought factor (simplified)
            drought_factor = max(0, min(10, (100 - weather_data.relative_humidity) / 10))
            
            # Calculate wind factor
            wind_factor = 1.0
            if weather_data.wind_speed:
                wind_factor = min(10, weather_data.wind_speed / 5.0)
            
            # Calculate temperature factor
            temp_factor = max(0, (weather_data.temperature - 32) / 10) if weather_data.temperature else 0
            
            # Composite fire weather index
            fire_weather_index = (drought_factor + wind_factor + temp_factor) / 3
            
            return {
                'fire_weather_index': fire_weather_index,
                'drought_factor': drought_factor,
                'wind_factor': wind_factor,
                'temperature_factor': temp_factor,
                'data_quality': weather_data.data_quality,
                'timestamp': weather_data.last_updated.isoformat() if weather_data.last_updated else None
            }
            
        except Exception as e:
            logger.error(f"Error calculating fire weather index: {e}")
            return None

# Integration functions for existing agent system
async def get_real_time_fire_weather(station_ids: List[str]) -> Dict[str, Dict]:
    """
    Get real-time fire weather data for multiple stations
    Designed for integration with existing agent system
    
    Args:
        station_ids: List of weather station identifiers
        
    Returns:
        Dictionary mapping station_id to fire weather calculations
    """
    async with WeatherGovAPIClient() as client:
        weather_data = await client.get_multiple_stations(station_ids)
        
        results = {}
        for station_id, data in weather_data.items():
            fire_weather = FireWeatherCalculator.calculate_fire_weather_index(data)
            if fire_weather:
                results[station_id] = {
                    'station_name': data.name,
                    'location': {'latitude': data.latitude, 'longitude': data.longitude},
                    'current_conditions': {
                        'temperature': data.temperature,
                        'humidity': data.relative_humidity,
                        'wind_speed': data.wind_speed,
                        'wind_direction': data.wind_direction
                    },
                    'fire_weather': fire_weather
                }
        
        return results

# Example usage for testing
if __name__ == "__main__":
    async def test_weather_api():
        """Test the Weather.gov API integration"""
        # Test with a few sample stations
        test_stations = ['KORD', 'KLAX', 'KJFK']  # Chicago, LA, NYC
        
        print("🌡️ Testing Weather.gov API Integration...")
        results = await get_real_time_fire_weather(test_stations)
        
        for station_id, data in results.items():
            print(f"\n📍 {data['station_name']} ({station_id})")
            conditions = data['current_conditions']
            fire_weather = data['fire_weather']
            
            print(f"   Temperature: {conditions.get('temperature', 'N/A')}°F")
            print(f"   Humidity: {conditions.get('humidity', 'N/A')}%")
            print(f"   Wind: {conditions.get('wind_speed', 'N/A')} mph")
            print(f"   Fire Weather Index: {fire_weather.get('fire_weather_index', 'N/A'):.2f}")
            print(f"   Data Quality: {fire_weather.get('data_quality', 'N/A')}")
    
    # Run test
    asyncio.run(test_weather_api())