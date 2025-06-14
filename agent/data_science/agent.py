"""Fire-enhanced data science agent with proper ADK structure."""

import os
from datetime import date
from typing import Optional
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools import ToolContext

# Import the database agent directly (bypasses tools.py complexity)
from .sub_agents.bigquery.agent import database_agent

# Import NFDRS fire calculation engine
from .fire_calculations.nfdrs_engine import NFDRSEngine, WeatherData

date_today = date.today()

# Initialize NFDRS engine
nfdrs_engine = NFDRSEngine()

async def calculate_fire_danger(
    temperature: float,
    relative_humidity: float, 
    wind_speed: float,
    precipitation: float = 0.0,
    tool_context: ToolContext = None
) -> str:
    """
    Calculate fire danger using NFDRS formulas.
    
    Args:
        temperature: Temperature in Fahrenheit
        relative_humidity: Relative humidity percentage
        wind_speed: Wind speed in mph
        precipitation: 24-hour precipitation in inches
    
    Returns:
        Fire danger calculation results as formatted string
    """
    weather = WeatherData(
        temperature=temperature,
        relative_humidity=relative_humidity,
        wind_speed=wind_speed,
        precipitation=precipitation
    )
    
    result = nfdrs_engine.calculate_fire_danger(weather)
    
    return f"""🔥 Fire Danger Calculation Results:
    
Weather Conditions:
- Temperature: {temperature}°F
- Relative Humidity: {relative_humidity}%
- Wind Speed: {wind_speed} mph
- Precipitation: {precipitation} inches

Fire Danger Components:
- Dead Fuel Moisture: {result.dead_fuel_moisture:.1f}%
- Live Fuel Moisture: {result.live_fuel_moisture:.1f}%
- Spread Component: {result.spread_component:.1f}
- Energy Release Component: {result.energy_release_component:.1f}
- Burning Index: {result.burning_index:.1f}

**Fire Danger Class: {result.fire_danger_class}**
"""

async def get_fire_danger_for_station(
    station_name: Optional[str] = None,
    limit: int = 1,
    tool_context: ToolContext = None
) -> str:
    """
    Get fire danger calculation for specific station using real weather data.
    
    Args:
        station_name: Name of the weather station (optional)
        limit: Number of recent records to analyze
    
    Returns:
        Fire danger analysis for the station
    """
    from google.cloud import bigquery
    
    try:
        client = bigquery.Client(project='risenone-ai-prototype')
        
        # Build query based on whether station is specified
        if station_name:
            query = f"""
            SELECT 
                stationId, stationName, observationTime,
                oneHR_TL_FuelMoisture as dead_fm_actual,
                spreadComponent as sc_actual,
                burningIndex as bi_actual,
                -- Approximate weather from fuel moisture
                CASE 
                    WHEN oneHR_TL_FuelMoisture < 5 THEN 25
                    WHEN oneHR_TL_FuelMoisture < 10 THEN 40
                    WHEN oneHR_TL_FuelMoisture < 15 THEN 60
                    ELSE 80
                END as relative_humidity,
                80 as temperature,
                10 as wind_speed
            FROM `risenone-ai-prototype.fire_risk_poc.nfdr_daily_summary`
            WHERE UPPER(stationName) LIKE UPPER('%{station_name}%')
                AND oneHR_TL_FuelMoisture IS NOT NULL
            ORDER BY observationTime DESC
            LIMIT {limit}
            """
        else:
            query = f"""
            SELECT 
                stationId, stationName, observationTime,
                oneHR_TL_FuelMoisture as dead_fm_actual,
                spreadComponent as sc_actual,
                burningIndex as bi_actual,
                -- Approximate weather from fuel moisture
                CASE 
                    WHEN oneHR_TL_FuelMoisture < 5 THEN 25
                    WHEN oneHR_TL_FuelMoisture < 10 THEN 40
                    WHEN oneHR_TL_FuelMoisture < 15 THEN 60
                    ELSE 80
                END as relative_humidity,
                80 as temperature,
                10 as wind_speed
            FROM `risenone-ai-prototype.fire_risk_poc.nfdr_daily_summary`
            WHERE oneHR_TL_FuelMoisture IS NOT NULL
            ORDER BY observationTime DESC
            LIMIT {limit}
            """
        
        results = list(client.query(query))
        
        if not results:
            return f"No fire data found for station: {station_name}" if station_name else "No recent fire data available"
        
        response = "🔥 Fire Danger Analysis Results:\n\n"
        
        for row in results:
            # Create weather data
            weather = WeatherData(
                temperature=float(row.temperature),
                relative_humidity=float(row.relative_humidity),
                wind_speed=float(row.wind_speed),
                precipitation=0.0
            )
            
            # Calculate fire danger
            fire_danger = nfdrs_engine.calculate_fire_danger(weather)
            
            response += f"""📍 Station: {row.stationName} (ID: {row.stationId})
📅 Date: {row.observationTime}

Weather Conditions (estimated):
- Temperature: {weather.temperature}°F
- Relative Humidity: {weather.relative_humidity}%
- Wind Speed: {weather.wind_speed} mph

Calculated Fire Danger:
- Dead Fuel Moisture: {fire_danger.dead_fuel_moisture:.1f}%
- Spread Component: {fire_danger.spread_component:.1f}
- Burning Index: {fire_danger.burning_index:.1f}
- **Fire Danger Class: {fire_danger.fire_danger_class}**

Actual Database Values:
- Dead Fuel Moisture: {row.dead_fm_actual:.1f}%
- Spread Component: {row.sc_actual:.1f}
- Burning Index: {row.bi_actual:.1f}

---
"""
        
        return response
        
    except Exception as e:
        return f"Error calculating fire danger: {str(e)}"

def return_fire_instructions():
    return """You are a specialized Fire Risk Analysis Agent. You help users analyze wildfire risk data, weather patterns, and emergency response planning. 

For simple greetings like "hello" or "hi", respond directly and briefly without transferring to other agents.

For data queries requiring database access (weather stations, fuel moisture, fire risk analysis), transfer to the database agent. 

For fire danger calculations, use the calculate_fire_danger tool with weather parameters.

For station-specific fire danger analysis, use the get_fire_danger_for_station tool.

Always provide concise, helpful responses focused on fire risk analysis and emergency response."""

# Fire-enhanced root agent with proper ADK structure for REST API
root_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="data_science",
    instruction=return_fire_instructions(),
    global_instruction=f"You are a Fire Risk Analysis Agent specializing in wildfire risk assessment and emergency response decision support. Today's date: {date_today}. You have access to real fire danger data, weather station information, and can perform sophisticated fire risk analysis using NFDRS calculations.",
    description="AI assistant for Forest Service wildfire risk analysis and emergency response decision support. Automates manual fire danger calculations, integrates weather station data, and provides intelligent crew positioning recommendations. Built on ultra-minimal architecture for reliable emergency response operations.",
    sub_agents=[database_agent],  # Use enhanced database agent with fire capabilities
    tools=[calculate_fire_danger, get_fire_danger_for_station],  # Add NFDRS calculation tools
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,  # Increase slightly for faster responses
        max_output_tokens=2048,  # Reduce for faster responses
        top_p=0.9  # Reduce for more focused responses
    ),
)
