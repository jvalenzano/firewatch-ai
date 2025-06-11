"""
Historical Data Generator for POC-DA-3

Generates realistic 3-year historical weather datasets with seasonal variations,
diurnal patterns, and drought/wet cycles for fire risk analysis training.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass

@dataclass 
class SeasonalPatterns:
    """Seasonal weather pattern definitions"""
    # Temperature patterns (Fahrenheit)
    winter_temp_range: tuple = (25, 55)
    spring_temp_range: tuple = (45, 75) 
    summer_temp_range: tuple = (65, 95)
    fall_temp_range: tuple = (40, 70)
    
    # Humidity patterns (percentage)
    winter_humidity_range: tuple = (40, 80)
    spring_humidity_range: tuple = (35, 75)
    summer_humidity_range: tuple = (25, 60)
    fall_humidity_range: tuple = (30, 70)
    
    # Precipitation patterns (inches/day)
    winter_precip_prob: float = 0.15
    spring_precip_prob: float = 0.20
    summer_precip_prob: float = 0.10
    fall_precip_prob: float = 0.12

class HistoricalDataGenerator:
    """
    Generates realistic historical weather data with seasonal variations
    and regional patterns for fire risk analysis.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.seasonal_patterns = SeasonalPatterns()
        
    def generate_weather_history(self, station_metadata: pd.DataFrame) -> pd.DataFrame:
        """
        Generate 3-year historical weather dataset for all stations.
        
        Args:
            station_metadata: DataFrame with station information
            
        Returns:
            pd.DataFrame: Historical weather data with realistic patterns
        """
        try:
            self.logger.info(f"Generating historical data for {len(station_metadata)} stations...")
            
            # Generate date range for 3-year period
            start_date = datetime.strptime(self.config.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.config.end_date, "%Y-%m-%d")
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
            historical_records = []
            
            for _, station in station_metadata.iterrows():
                self.logger.debug(f"Generating data for station {station['station_id']}")
                
                station_history = self._generate_station_history(
                    station, date_range
                )
                historical_records.extend(station_history)
            
            historical_df = pd.DataFrame(historical_records)
            self.logger.info(f"Generated {len(historical_df)} historical weather records")
            
            return historical_df
            
        except Exception as e:
            self.logger.error(f"Error generating weather history: {e}")
            return pd.DataFrame()
    
    def _generate_station_history(self, station: pd.Series, date_range: pd.DatetimeIndex) -> List[Dict]:
        """Generate historical data for a single station"""
        
        station_records = []
        
        # Station-specific adjustments based on geography
        elevation_adj = self._get_elevation_adjustment(station.get('elevation', 0))
        latitude_adj = self._get_latitude_adjustment(station.get('latitude', 40))
        aspect_adj = self._get_aspect_adjustment(station.get('aspect', 'FL'))
        
        # Initialize climate state for long-term patterns
        drought_cycle = self._generate_drought_cycle(len(date_range))
        
        for i, date in enumerate(date_range):
            # Determine season
            month = date.month
            season = self._get_season(month)
            day_of_year = date.timetuple().tm_yday
            
            # Generate base weather conditions
            base_weather = self._generate_base_weather(season, elevation_adj, latitude_adj)
            
            # Apply diurnal variations (simulate daily high/low)
            diurnal_weather = self._apply_diurnal_patterns(base_weather, date)
            
            # Apply drought/wet cycle influences
            climate_weather = self._apply_climate_cycle(
                diurnal_weather, drought_cycle[i], season
            )
            
            # Apply aspect-based adjustments
            final_weather = self._apply_aspect_adjustments(climate_weather, aspect_adj)
            
            # Calculate fuel moisture based on weather conditions
            fuel_moisture = self._calculate_fuel_moisture(final_weather)
            
            # Create daily record
            record = {
                'station_id': station['station_id'],
                'date': date.strftime('%Y-%m-%d'),
                'timestamp': date.isoformat(),
                'season': season,
                'day_of_year': day_of_year,
                **final_weather,
                **fuel_moisture,
                'drought_index': drought_cycle[i],
                'elevation': station.get('elevation', 0),
                'latitude': station.get('latitude', 40),
                'longitude': station.get('longitude', -120),
                'aspect': station.get('aspect', 'FL')
            }
            
            station_records.append(record)
        
        return station_records
    
    def _get_season(self, month: int) -> str:
        """Determine season from month"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:  # 9, 10, 11
            return 'fall'
    
    def _get_elevation_adjustment(self, elevation: float) -> Dict[str, float]:
        """Calculate adjustments based on elevation"""
        # Temperature decreases ~3.5°F per 1000ft elevation
        temp_adj = -3.5 * (elevation / 1000.0)
        
        # Humidity generally increases with elevation
        humidity_adj = min(15, elevation / 500.0)
        
        # Wind speeds tend to be higher at elevation
        wind_adj = max(1.0, elevation / 2000.0)
        
        return {
            'temperature_adj': temp_adj,
            'humidity_adj': humidity_adj,
            'wind_adj': wind_adj
        }
    
    def _get_latitude_adjustment(self, latitude: float) -> Dict[str, float]:
        """Calculate adjustments based on latitude"""
        # Northern latitudes are generally cooler
        base_lat = 35.0  # Approximate center of fire-prone regions
        temp_adj = -1.5 * (latitude - base_lat)
        
        return {
            'latitude_temp_adj': temp_adj
        }
    
    def _get_aspect_adjustment(self, aspect: str) -> Dict[str, float]:
        """Calculate adjustments based on slope aspect"""
        aspect_adjustments = {
            'N': {'temp_adj': -2, 'humidity_adj': 5, 'wind_adj': 0.8},
            'S': {'temp_adj': 3, 'humidity_adj': -5, 'wind_adj': 1.2},
            'E': {'temp_adj': 1, 'humidity_adj': 0, 'wind_adj': 1.0},
            'W': {'temp_adj': 2, 'humidity_adj': -2, 'wind_adj': 1.1},
            'SW': {'temp_adj': 4, 'humidity_adj': -8, 'wind_adj': 1.3},
            'FL': {'temp_adj': 0, 'humidity_adj': 0, 'wind_adj': 1.0}  # Flat
        }
        
        return aspect_adjustments.get(aspect, aspect_adjustments['FL'])
    
    def _generate_drought_cycle(self, num_days: int) -> np.ndarray:
        """Generate realistic drought/wet cycles over 3-year period"""
        
        # Create base cycle with ~2-year drought/wet pattern
        base_cycle = np.sin(np.linspace(0, 3 * np.pi, num_days)) * 0.3
        
        # Add random weather variations
        weather_noise = np.random.normal(0, 0.2, num_days)
        
        # Add some extreme events (droughts/wet periods)
        extreme_events = np.zeros(num_days)
        for _ in range(6):  # 6 extreme events over 3 years
            event_start = np.random.randint(0, num_days - 90)
            event_duration = np.random.randint(30, 120)
            event_end = min(event_start + event_duration, num_days)
            event_intensity = np.random.choice([-0.7, 0.6])  # Drought or wet event
            extreme_events[event_start:event_end] = event_intensity
        
        # Combine all factors and normalize to [-1, 1] range
        drought_index = base_cycle + weather_noise + extreme_events
        drought_index = np.clip(drought_index, -1.0, 1.0)
        
        return drought_index
    
    def _generate_base_weather(self, season: str, elevation_adj: Dict, latitude_adj: Dict) -> Dict:
        """Generate base weather conditions for a season"""
        
        # Get seasonal ranges
        if season == 'winter':
            temp_range = self.seasonal_patterns.winter_temp_range
            humidity_range = self.seasonal_patterns.winter_humidity_range
            precip_prob = self.seasonal_patterns.winter_precip_prob
        elif season == 'spring':
            temp_range = self.seasonal_patterns.spring_temp_range
            humidity_range = self.seasonal_patterns.spring_humidity_range
            precip_prob = self.seasonal_patterns.spring_precip_prob
        elif season == 'summer':
            temp_range = self.seasonal_patterns.summer_temp_range
            humidity_range = self.seasonal_patterns.summer_humidity_range
            precip_prob = self.seasonal_patterns.summer_precip_prob
        else:  # fall
            temp_range = self.seasonal_patterns.fall_temp_range
            humidity_range = self.seasonal_patterns.fall_humidity_range
            precip_prob = self.seasonal_patterns.fall_precip_prob
        
        # Generate base values
        temperature = np.random.uniform(temp_range[0], temp_range[1])
        humidity = np.random.uniform(humidity_range[0], humidity_range[1])
        
        # Apply geographic adjustments
        temperature += elevation_adj['temperature_adj']
        temperature += latitude_adj['latitude_temp_adj']
        humidity += elevation_adj['humidity_adj']
        humidity = np.clip(humidity, 10, 95)  # Keep humidity in realistic range
        
        # Wind patterns
        wind_speed = np.random.exponential(8) * elevation_adj['wind_adj']
        wind_direction = np.random.randint(0, 360)
        
        # Precipitation
        precipitation = 0.0
        if np.random.random() < precip_prob:
            precipitation = np.random.exponential(0.3)  # Exponential distribution for precip
        
        return {
            'temperature_f': round(temperature, 1),
            'humidity_pct': round(humidity, 1),
            'wind_speed_mph': round(wind_speed, 1),
            'wind_direction': wind_direction,
            'precipitation_in': round(precipitation, 2)
        }
    
    def _apply_diurnal_patterns(self, base_weather: Dict, date: datetime) -> Dict:
        """Apply daily temperature and humidity variations"""
        
        # Create random but realistic daily variations
        temp_variation = np.random.normal(0, 3)  # ±3°F daily variation
        humidity_variation = np.random.normal(0, 5)  # ±5% humidity variation
        
        weather = base_weather.copy()
        weather['temperature_f'] += temp_variation
        weather['humidity_pct'] += humidity_variation
        weather['humidity_pct'] = np.clip(weather['humidity_pct'], 10, 95)
        
        return weather
    
    def _apply_climate_cycle(self, weather: Dict, drought_index: float, season: str) -> Dict:
        """Apply long-term drought/wet cycle effects"""
        
        adjusted_weather = weather.copy()
        
        # Drought conditions: hotter, drier, windier
        if drought_index < -0.3:  # Drought conditions
            adjusted_weather['temperature_f'] += abs(drought_index) * 8
            adjusted_weather['humidity_pct'] *= (1 + drought_index * 0.4)
            adjusted_weather['wind_speed_mph'] *= (1 + abs(drought_index) * 0.3)
            adjusted_weather['precipitation_in'] *= (1 + drought_index * 0.8)
            
        # Wet conditions: cooler, more humid, less wind
        elif drought_index > 0.3:  # Wet conditions
            adjusted_weather['temperature_f'] -= drought_index * 5
            adjusted_weather['humidity_pct'] *= (1 + drought_index * 0.3)
            adjusted_weather['wind_speed_mph'] *= (1 - drought_index * 0.2)
            adjusted_weather['precipitation_in'] *= (1 + drought_index * 1.5)
        
        # Keep values in realistic ranges
        adjusted_weather['humidity_pct'] = np.clip(adjusted_weather['humidity_pct'], 10, 95)
        adjusted_weather['wind_speed_mph'] = max(0, adjusted_weather['wind_speed_mph'])
        adjusted_weather['precipitation_in'] = max(0, adjusted_weather['precipitation_in'])
        
        return adjusted_weather
    
    def _apply_aspect_adjustments(self, weather: Dict, aspect_adj: Dict) -> Dict:
        """Apply slope aspect effects to weather"""
        
        adjusted_weather = weather.copy()
        adjusted_weather['temperature_f'] += aspect_adj['temp_adj']
        adjusted_weather['humidity_pct'] += aspect_adj['humidity_adj']
        adjusted_weather['wind_speed_mph'] *= aspect_adj['wind_adj']
        
        # Keep in realistic ranges
        adjusted_weather['humidity_pct'] = np.clip(adjusted_weather['humidity_pct'], 10, 95)
        adjusted_weather['wind_speed_mph'] = max(0, adjusted_weather['wind_speed_mph'])
        
        return adjusted_weather
    
    def _calculate_fuel_moisture(self, weather: Dict) -> Dict:
        """Calculate fuel moisture levels based on weather conditions"""
        
        temp = weather['temperature_f']
        humidity = weather['humidity_pct']
        wind = weather['wind_speed_mph']
        precip = weather['precipitation_in']
        
        # Simplified fuel moisture calculations
        # 1-hour fuels respond quickly to current conditions
        fuel_1hr = max(4, min(30, 
            20 - (temp - 60) * 0.1 + (humidity - 50) * 0.2 + precip * 10
        ))
        
        # 10-hour fuels respond more slowly
        fuel_10hr = max(6, min(35,
            fuel_1hr + np.random.normal(2, 1)
        ))
        
        # 100-hour fuels respond very slowly
        fuel_100hr = max(8, min(40,
            fuel_10hr + np.random.normal(3, 1.5)
        ))
        
        return {
            'fuel_moisture_1hr': round(fuel_1hr, 1),
            'fuel_moisture_10hr': round(fuel_10hr, 1),
            'fuel_moisture_100hr': round(fuel_100hr, 1)
        } 