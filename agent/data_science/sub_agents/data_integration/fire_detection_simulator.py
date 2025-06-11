"""
Fire Detection Simulator for POC-DA-3

Generates realistic fire detection events based on geographic clustering,
weather patterns, and historical fire behavior for training AI agents.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

@dataclass
class FireRiskProfile:
    """Fire risk characteristics for different regions"""
    base_ignition_prob: float = 0.001  # Daily base probability
    weather_multiplier: Dict[str, float] = None
    seasonal_multiplier: Dict[str, float] = None
    elevation_factor: float = 1.0
    aspect_factor: float = 1.0
    
    def __post_init__(self):
        if self.weather_multiplier is None:
            self.weather_multiplier = {
                'high_temp': 2.5,      # Hot days increase risk
                'low_humidity': 3.0,    # Dry conditions increase risk
                'high_wind': 2.0,       # Windy conditions increase risk
                'no_precip': 1.5        # No recent rain increases risk
            }
        
        if self.seasonal_multiplier is None:
            self.seasonal_multiplier = {
                'winter': 0.3,
                'spring': 1.2,
                'summer': 2.5,
                'fall': 1.8
            }

class FireDetectionSimulator:
    """
    Simulates realistic fire detection events based on weather conditions,
    geographic factors, and historical fire patterns.
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.fire_risk_profile = FireRiskProfile()
        
    def generate_fire_events(self, station_metadata: pd.DataFrame, 
                           historical_weather: pd.DataFrame) -> pd.DataFrame:
        """
        Generate realistic fire detection events based on station locations and weather history.
        
        Args:
            station_metadata: DataFrame with station geographic information
            historical_weather: DataFrame with historical weather data
            
        Returns:
            pd.DataFrame: Fire detection events with location, timing, and characteristics
        """
        try:
            self.logger.info("Generating fire detection simulation data...")
            
            fire_events = []
            
            # Group weather data by station for efficient processing
            weather_by_station = historical_weather.groupby('station_id')
            
            for station_id, station_weather in weather_by_station:
                station_info = station_metadata[station_metadata['station_id'] == station_id]
                if station_info.empty:
                    continue
                
                station_info = station_info.iloc[0]
                station_fires = self._generate_station_fire_events(station_info, station_weather)
                fire_events.extend(station_fires)
            
            fire_df = pd.DataFrame(fire_events)
            self.logger.info(f"Generated {len(fire_df)} fire detection events")
            
            return fire_df
            
        except Exception as e:
            self.logger.error(f"Error generating fire events: {e}")
            return pd.DataFrame()
    
    def _generate_station_fire_events(self, station_info: pd.Series, 
                                     station_weather: pd.DataFrame) -> List[Dict]:
        """Generate fire events for a single station based on weather history"""
        
        fire_events = []
        
        # Calculate base fire risk for this station
        base_risk = self._calculate_station_fire_risk(station_info)
        
        # Track recent precipitation for drought effects
        precip_history = []
        
        for _, weather_day in station_weather.iterrows():
            
            # Update precipitation history (last 30 days)
            precip_history.append(weather_day.get('precipitation_in', 0))
            if len(precip_history) > 30:
                precip_history.pop(0)
            
            # Calculate daily fire probability
            daily_fire_prob = self._calculate_daily_fire_probability(
                weather_day, base_risk, precip_history
            )
            
            # Determine if fire occurs
            if np.random.random() < daily_fire_prob:
                fire_event = self._create_fire_event(
                    station_info, weather_day, daily_fire_prob
                )
                fire_events.append(fire_event)
        
        return fire_events
    
    def _calculate_station_fire_risk(self, station_info: pd.Series) -> float:
        """Calculate base fire risk for a station based on geographic factors"""
        
        base_risk = self.fire_risk_profile.base_ignition_prob
        
        # Elevation factor - higher elevations often have different fire patterns
        elevation = station_info.get('elevation', 0)
        if elevation > 5000:
            base_risk *= 0.8  # High elevation - often more moist
        elif elevation > 2000:
            base_risk *= 1.2  # Mid elevation - often fire-prone
        else:
            base_risk *= 1.0  # Low elevation - baseline
        
        # Aspect factor - south-facing slopes are typically drier
        aspect = station_info.get('aspect', 'FL')
        aspect_multipliers = {
            'S': 1.4,   # South-facing: hottest, driest
            'SW': 1.3,  # Southwest: hot afternoon sun
            'W': 1.2,   # West: hot afternoon sun
            'SE': 1.1,  # Southeast: warm morning sun
            'E': 1.0,   # East: morning sun
            'N': 0.7,   # North: coolest, most moist
            'NW': 0.8,  # Northwest: some afternoon sun
            'NE': 0.8,  # Northeast: limited sun
            'FL': 1.0   # Flat: baseline
        }
        base_risk *= aspect_multipliers.get(aspect, 1.0)
        
        # Regional adjustments based on latitude (fire season length)
        latitude = station_info.get('latitude', 40)
        if latitude > 45:
            base_risk *= 0.8  # Northern regions - shorter fire season
        elif latitude < 35:
            base_risk *= 1.3  # Southern regions - longer fire season
        
        return base_risk
    
    def _calculate_daily_fire_probability(self, weather_day: pd.Series, 
                                        base_risk: float, 
                                        precip_history: List[float]) -> float:
        """Calculate fire probability for a specific day based on weather conditions"""
        
        daily_prob = base_risk
        
        # Weather factor adjustments
        temp = weather_day.get('temperature_f', 70)
        humidity = weather_day.get('humidity_pct', 50)
        wind = weather_day.get('wind_speed_mph', 5)
        precip = weather_day.get('precipitation_in', 0)
        season = weather_day.get('season', 'summer')
        
        # Temperature effects
        if temp > 85:
            daily_prob *= self.fire_risk_profile.weather_multiplier['high_temp']
        elif temp > 75:
            daily_prob *= 1.5
        
        # Humidity effects
        if humidity < 20:
            daily_prob *= self.fire_risk_profile.weather_multiplier['low_humidity']
        elif humidity < 30:
            daily_prob *= 2.0
        elif humidity < 40:
            daily_prob *= 1.3
        
        # Wind effects
        if wind > 20:
            daily_prob *= self.fire_risk_profile.weather_multiplier['high_wind']
        elif wind > 10:
            daily_prob *= 1.4
        
        # Precipitation effects (current day)
        if precip > 0.1:
            daily_prob *= 0.1  # Significant precipitation greatly reduces risk
        elif precip > 0.01:
            daily_prob *= 0.5  # Light precipitation reduces risk
        
        # Drought effects (recent precipitation history)
        recent_precip = sum(precip_history)
        if recent_precip < 0.5:  # Very dry period
            daily_prob *= 2.5
        elif recent_precip < 1.0:  # Dry period
            daily_prob *= 1.8
        elif recent_precip > 5.0:  # Wet period
            daily_prob *= 0.3
        
        # Seasonal effects
        seasonal_multiplier = self.fire_risk_profile.seasonal_multiplier.get(season, 1.0)
        daily_prob *= seasonal_multiplier
        
        # Fuel moisture effects
        fuel_1hr = weather_day.get('fuel_moisture_1hr', 15)
        if fuel_1hr < 8:
            daily_prob *= 3.0  # Very dry fuels
        elif fuel_1hr < 12:
            daily_prob *= 1.8  # Dry fuels
        elif fuel_1hr > 20:
            daily_prob *= 0.4  # Moist fuels
        
        # Cap maximum probability at reasonable level
        daily_prob = min(daily_prob, 0.05)  # Max 5% chance per day
        
        return daily_prob
    
    def _create_fire_event(self, station_info: pd.Series, weather_day: pd.Series, 
                          fire_probability: float) -> Dict:
        """Create a realistic fire event record"""
        
        # Generate fire characteristics based on conditions
        temp = weather_day.get('temperature_f', 70)
        humidity = weather_day.get('humidity_pct', 50)
        wind = weather_day.get('wind_speed_mph', 5)
        
        # Fire intensity based on weather conditions
        fire_intensity = self._calculate_fire_intensity(temp, humidity, wind)
        
        # Fire size based on intensity and response time
        fire_size_acres = self._estimate_fire_size(fire_intensity, wind)
        
        # Detection time (random within day)
        base_date = datetime.strptime(weather_day['date'], '%Y-%m-%d')
        detection_hour = np.random.randint(6, 22)  # Fires typically detected 6 AM - 10 PM
        detection_time = base_date + timedelta(hours=detection_hour)
        
        # Generate nearby location (within ~10 miles of station)
        lat_offset = np.random.normal(0, 0.1)  # ~±6 miles
        lon_offset = np.random.normal(0, 0.1)  # ~±6 miles
        
        fire_event = {
            'fire_id': f"FIRE_{station_info['station_id']}_{weather_day['date'].replace('-', '')}_{detection_hour:02d}",
            'detection_date': weather_day['date'],
            'detection_time': detection_time.isoformat(),
            'station_id': station_info['station_id'],
            'latitude': round(station_info['latitude'] + lat_offset, 6),
            'longitude': round(station_info['longitude'] + lon_offset, 6),
            'elevation': station_info.get('elevation', 0) + np.random.randint(-200, 200),
            'fire_size_acres': round(fire_size_acres, 1),
            'fire_intensity': fire_intensity,
            'weather_temp_f': weather_day.get('temperature_f', 70),
            'weather_humidity_pct': weather_day.get('humidity_pct', 50),
            'weather_wind_mph': weather_day.get('wind_speed_mph', 5),
            'weather_wind_direction': weather_day.get('wind_direction', 180),
            'fuel_moisture_1hr': weather_day.get('fuel_moisture_1hr', 15),
            'fuel_moisture_10hr': weather_day.get('fuel_moisture_10hr', 18),
            'fuel_moisture_100hr': weather_day.get('fuel_moisture_100hr', 22),
            'season': weather_day.get('season', 'summer'),
            'ignition_probability': round(fire_probability, 6),
            'cause': self._generate_fire_cause(),
            'suppression_difficulty': self._estimate_suppression_difficulty(fire_intensity, wind, station_info.get('elevation', 0)),
            'region': self._determine_region(station_info['latitude'], station_info['longitude'])
        }
        
        return fire_event
    
    def _calculate_fire_intensity(self, temperature: float, humidity: float, wind: float) -> str:
        """Calculate fire intensity category based on weather conditions"""
        
        # Fire Weather Index calculation (simplified)
        fw_index = (temperature - humidity + wind) / 3
        
        if fw_index < 10:
            return 'Low'
        elif fw_index < 20:
            return 'Moderate'
        elif fw_index < 30:
            return 'High'
        elif fw_index < 40:
            return 'Very High'
        else:
            return 'Extreme'
    
    def _estimate_fire_size(self, intensity: str, wind_speed: float) -> float:
        """Estimate fire size based on intensity and wind"""
        
        # Base sizes for different intensities (acres)
        base_sizes = {
            'Low': 2.0,
            'Moderate': 8.0,
            'High': 25.0,
            'Very High': 75.0,
            'Extreme': 200.0
        }
        
        base_size = base_sizes.get(intensity, 10.0)
        
        # Wind increases fire spread
        wind_multiplier = 1 + (wind_speed / 20.0)
        
        # Add random variation
        size_variation = np.random.lognormal(0, 0.5)
        
        final_size = base_size * wind_multiplier * size_variation
        
        # Cap at reasonable maximums for initial detection
        return min(final_size, 1000.0)
    
    def _generate_fire_cause(self) -> str:
        """Generate realistic fire cause"""
        causes = [
            'Lightning', 'Human - Campfire', 'Human - Equipment', 
            'Human - Debris Burning', 'Human - Arson', 'Human - Other',
            'Unknown'
        ]
        
        # Weight causes realistically
        weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]
        
        return np.random.choice(causes, p=weights)
    
    def _estimate_suppression_difficulty(self, intensity: str, wind: float, elevation: float) -> str:
        """Estimate suppression difficulty based on fire and terrain characteristics"""
        
        difficulty_score = 0
        
        # Intensity factor
        intensity_scores = {
            'Low': 1, 'Moderate': 2, 'High': 3, 'Very High': 4, 'Extreme': 5
        }
        difficulty_score += intensity_scores.get(intensity, 2)
        
        # Wind factor
        if wind > 20:
            difficulty_score += 3
        elif wind > 10:
            difficulty_score += 2
        elif wind > 5:
            difficulty_score += 1
        
        # Elevation factor (access difficulty)
        if elevation > 6000:
            difficulty_score += 2
        elif elevation > 3000:
            difficulty_score += 1
        
        # Classify difficulty
        if difficulty_score <= 3:
            return 'Easy'
        elif difficulty_score <= 5:
            return 'Moderate'
        elif difficulty_score <= 7:
            return 'Difficult'
        else:
            return 'Extreme'
    
    def _determine_region(self, latitude: float, longitude: float) -> str:
        """Determine geographic region based on coordinates"""
        
        # Simplified regional classification
        if latitude > 45:
            return 'Pacific Northwest'
        elif latitude > 42 and longitude < -120:
            return 'Northern California'
        elif latitude > 37 and longitude < -120:
            return 'Central California'
        elif latitude > 32 and longitude < -115:
            return 'Southern California'
        elif longitude > -110:
            return 'Southwest'
        elif latitude > 40:
            return 'Mountain West'
        else:
            return 'Other' 