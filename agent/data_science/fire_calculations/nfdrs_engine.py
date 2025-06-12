"""
NFDRS (National Fire Danger Rating System) Calculation Engine
Forest Service Standard Formulas Implementation
"""
import math
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class WeatherData:
    """Weather station data for fire calculations"""
    temperature: float  # °F
    relative_humidity: float  # %
    wind_speed: float  # mph
    precipitation: float  # inches (24hr)
    solar_radiation: Optional[float] = None  # Langleys

@dataclass
class FireDangerResult:
    """Complete fire danger calculation results"""
    dead_fuel_moisture: float
    live_fuel_moisture: float
    spread_component: float
    energy_release_component: float
    burning_index: float
    fire_danger_class: str  # LOW, MODERATE, HIGH, VERY HIGH, EXTREME

class NFDRSEngine:
    """Core NFDRS calculation engine following Forest Service standards"""
    
    def __init__(self):
        self.fuel_model = "G"  # Standard grass fuel model
        
    def calculate_dead_fuel_moisture(self, weather: WeatherData) -> float:
        """
        Calculate 1-hour dead fuel moisture content
        Formula: FM₁ₕ = f(RH, T, rain)
        """
        # Basic EMC (Equilibrium Moisture Content) calculation
        rh = weather.relative_humidity
        temp = weather.temperature
        
        # Simplified EMC formula (Forest Service standard)
        if rh < 10:
            emc = 0.03 * rh
        elif rh < 50:
            emc = 2.22 * (rh/100) - 0.16
        else:
            emc = 21.06 * (rh/100) - 7.39
            
        # Adjust for temperature
        temp_factor = 1 + 0.0154 * (temp - 70)
        dead_fm = emc * temp_factor
        
        # Precipitation adjustment
        if weather.precipitation > 0.1:
            dead_fm += weather.precipitation * 2
            
        return max(1, min(dead_fm, 35))  # Clamp between 1-35%
    
    def calculate_spread_component(self, wind_speed: float, dead_fm: float) -> float:
        """
        Calculate Spread Component
        Formula: SC = 0.560 × ROS (Rate of Spread)
        """
        # Wind factor calculation
        wind_factor = math.pow(wind_speed, 1.5) / 5.0
        
        # Fuel moisture factor
        fm_factor = math.exp(-0.108 * dead_fm)
        
        # Base spread rate
        spread_rate = wind_factor * fm_factor
        
        # Convert to spread component
        spread_component = 0.560 * spread_rate
        
        return max(0, min(spread_component, 99))  # Clamp 0-99
    
    def calculate_energy_release_component(self, dead_fm: float, live_fm: float) -> float:
        """
        Calculate Energy Release Component (ERC)
        Formula: ERC = Σ(wᵢ × (1-FMᵢ))
        """
        # Weighted fuel moisture calculation
        dead_weight = 0.7  # 70% dead fuel
        live_weight = 0.3  # 30% live fuel
        
        dead_factor = dead_weight * (1 - dead_fm/100)
        live_factor = live_weight * (1 - live_fm/100)
        
        erc = (dead_factor + live_factor) * 100
        
        return max(0, min(erc, 97))  # Clamp 0-97
    
    def calculate_burning_index(self, spread_component: float, erc: float) -> float:
        """
        Calculate Burning Index
        Formula: BI = 10 × SC × ERC
        """
        burning_index = 10 * spread_component * erc / 100
        
        return max(0, min(burning_index, 999))  # Clamp 0-999
    
    def determine_fire_danger_class(self, burning_index: float) -> str:
        """Determine fire danger class from burning index"""
        if burning_index < 25:
            return "LOW"
        elif burning_index < 50:
            return "MODERATE"  
        elif burning_index < 75:
            return "HIGH"
        elif burning_index < 90:
            return "VERY HIGH"
        else:
            return "EXTREME"
    
    def calculate_fire_danger(self, weather: WeatherData, live_fm: float = 120) -> FireDangerResult:
        """
        Complete fire danger calculation
        """
        # Calculate all components
        dead_fm = self.calculate_dead_fuel_moisture(weather)
        spread_comp = self.calculate_spread_component(weather.wind_speed, dead_fm)
        erc = self.calculate_energy_release_component(dead_fm, live_fm)
        burning_idx = self.calculate_burning_index(spread_comp, erc)
        danger_class = self.determine_fire_danger_class(burning_idx)
        
        return FireDangerResult(
            dead_fuel_moisture=dead_fm,
            live_fuel_moisture=live_fm,
            spread_component=spread_comp,
            energy_release_component=erc,
            burning_index=burning_idx,
            fire_danger_class=danger_class
        )
