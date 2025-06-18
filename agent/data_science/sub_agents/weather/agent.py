"""
Weather Analysis Agent for Real-Time Weather Integration

Phase III Sprint 1 - Weather Agent Implementation
Built on Phase II optimized architecture for sub-10s response times
"""

import asyncio
from typing import Dict, List, Optional
import logging

from google.adk.core import BaseAgent, BaseModel, prompt_template
from .weather_api import WeatherGovAPIClient, get_real_time_fire_weather, WeatherStationData

logger = logging.getLogger(__name__)

class WeatherQuery(BaseModel):
    """Weather query model for agent input"""
    query: str
    station_ids: Optional[List[str]] = None
    location: Optional[str] = None
    include_fire_weather: bool = True

class WeatherResponse(BaseModel):
    """Weather response model for agent output"""
    summary: str
    stations: Dict[str, Dict] = {}
    fire_weather_analysis: Optional[str] = None
    data_quality_notes: List[str] = []

class WeatherAgent(BaseAgent[WeatherQuery, WeatherResponse]):
    """
    Real-time weather analysis agent for fire risk assessment
    
    Integrates Weather.gov API data with existing BigQuery fire data
    Maintains Phase II performance optimizations (4.86s baseline)
    """
    
    model_name = "gemini-2.0-flash-001"
    
    # Common fire weather stations across major fire regions
    DEFAULT_FIRE_STATIONS = [
        'KCEC',  # Jack McNamara Field, Crescent City, CA (Northern CA fires)
        'KSTS',  # Charles M. Schulz Sonoma County, Santa Rosa, CA (Wine Country)
        'KMRY',  # Monterey Peninsula, Monterey, CA (Central CA coast)
        'KSMX',  # Santa Maria Public, Santa Maria, CA (Central CA)
        'KBUR',  # Hollywood Burbank, Burbank, CA (Southern CA)
        'KPSP',  # Palm Springs Regional, Palm Springs, CA (Desert fires)
        'KPHX',  # Phoenix Sky Harbor, Phoenix, AZ (Southwest)
        'KDEN',  # Denver International, Denver, CO (Mountain West)
        'KBOI',  # Boise Air Terminal, Boise, ID (Intermountain)
        'KPDX',  # Portland International, Portland, OR (Pacific Northwest)
    ]
    
    @prompt_template
    def system_prompt(self) -> str:
        return """You are a specialized Weather Analysis Agent for fire risk assessment.
        
        Your role:
        - Analyze real-time weather data from Weather.gov API
        - Calculate fire weather indices and risk factors
        - Integrate with existing fire danger calculations
        - Provide concise, actionable weather intelligence
        
        Key capabilities:
        - Real-time weather data from 1000+ stations
        - Fire weather index calculations
        - Wind, temperature, humidity analysis for fire risk
        - Data quality assessment and recommendations
        
        Response format:
        - Lead with key fire weather insights
        - Include specific station data when relevant
        - Note data quality and any limitations
        - Keep responses under 200 words for optimal performance
        
        Context: This agent operates within an optimized multi-agent fire risk system
        with sub-10 second response time requirements."""
    
    @prompt_template
    def user_prompt(self, query: WeatherQuery) -> str:
        return f"""Analyze weather conditions for fire risk assessment.

Query: {query.query}

Instructions:
- Focus on fire weather parameters (temperature, humidity, wind speed/direction)
- Calculate fire weather indices when possible
- Assess data quality and note any limitations
- Provide actionable insights for fire risk management

Station focus: {', '.join(query.station_ids) if query.station_ids else 'General fire weather stations'}
Location context: {query.location if query.location else 'Multi-region analysis'}
Include fire weather calculations: {query.include_fire_weather}

Provide a concise analysis suitable for fire management decision-making."""

    async def run(self, query: WeatherQuery) -> WeatherResponse:
        """
        Execute weather analysis with real-time data integration
        
        Args:
            query: Weather analysis request
            
        Returns:
            WeatherResponse with real-time weather analysis
        """
        try:
            # Determine stations to query
            station_ids = query.station_ids or self.DEFAULT_FIRE_STATIONS[:5]  # Limit for performance
            
            # Get real-time weather data
            logger.info(f"Fetching real-time weather for {len(station_ids)} stations")
            weather_data = await get_real_time_fire_weather(station_ids)
            
            if not weather_data:
                return WeatherResponse(
                    summary="Unable to retrieve real-time weather data. API may be unavailable.",
                    data_quality_notes=["Weather.gov API unreachable"]
                )
            
            # Analyze fire weather conditions
            fire_weather_analysis = self._analyze_fire_weather_conditions(weather_data)
            data_quality_notes = self._assess_overall_data_quality(weather_data)
            
            # Generate AI-powered analysis summary
            analysis_context = self._prepare_analysis_context(query, weather_data, fire_weather_analysis)
            ai_summary = await self._generate_ai_summary(analysis_context)
            
            return WeatherResponse(
                summary=ai_summary,
                stations=weather_data,
                fire_weather_analysis=fire_weather_analysis,
                data_quality_notes=data_quality_notes
            )
            
        except Exception as e:
            logger.error(f"Weather analysis error: {e}")
            return WeatherResponse(
                summary=f"Weather analysis encountered an error: {str(e)}",
                data_quality_notes=["Analysis error - check logs"]
            )
    
    def _analyze_fire_weather_conditions(self, weather_data: Dict[str, Dict]) -> str:
        """Analyze fire weather conditions across stations"""
        if not weather_data:
            return "No weather data available for analysis."
        
        fire_indices = []
        high_risk_stations = []
        
        for station_id, data in weather_data.items():
            fire_weather = data.get('fire_weather', {})
            fire_index = fire_weather.get('fire_weather_index', 0)
            fire_indices.append(fire_index)
            
            # High risk threshold
            if fire_index > 6.0:
                high_risk_stations.append(f"{data.get('station_name', station_id)} ({fire_index:.1f})")
        
        if fire_indices:
            avg_index = sum(fire_indices) / len(fire_indices)
            max_index = max(fire_indices)
            
            analysis = f"Fire Weather Analysis: Average index {avg_index:.1f}, Maximum {max_index:.1f}. "
            
            if high_risk_stations:
                analysis += f"High risk stations: {', '.join(high_risk_stations[:3])}. "
            else:
                analysis += "No stations currently at high fire risk. "
                
            return analysis
        
        return "Insufficient data for fire weather analysis."
    
    def _assess_overall_data_quality(self, weather_data: Dict[str, Dict]) -> List[str]:
        """Assess data quality across all stations"""
        quality_notes = []
        
        if not weather_data:
            quality_notes.append("No weather data received")
            return quality_notes
        
        total_stations = len(weather_data)
        quality_counts = {}
        
        for station_id, data in weather_data.items():
            quality = data.get('fire_weather', {}).get('data_quality', 'UNKNOWN')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        if quality_counts.get('POOR', 0) > total_stations * 0.3:
            quality_notes.append("Data quality concerns: >30% of stations have poor data")
        
        if quality_counts.get('EXCELLENT', 0) > total_stations * 0.7:
            quality_notes.append("Excellent data quality: >70% of stations have complete data")
        
        if total_stations < 3:
            quality_notes.append("Limited station coverage - consider additional stations")
        
        return quality_notes
    
    def _prepare_analysis_context(self, query: WeatherQuery, weather_data: Dict, fire_analysis: str) -> str:
        """Prepare context for AI analysis"""
        context_parts = [
            f"Weather Query: {query.query}",
            f"Stations Analyzed: {len(weather_data)}",
            f"Fire Weather Analysis: {fire_analysis}",
        ]
        
        # Add sample station data
        if weather_data:
            sample_station = next(iter(weather_data.values()))
            conditions = sample_station.get('current_conditions', {})
            context_parts.append(
                f"Sample Conditions: {conditions.get('temperature', 'N/A')}°F, "
                f"{conditions.get('humidity', 'N/A')}% RH, "
                f"{conditions.get('wind_speed', 'N/A')} mph"
            )
        
        return " | ".join(context_parts)
    
    async def _generate_ai_summary(self, context: str) -> str:
        """Generate AI-powered weather analysis summary"""
        try:
            # Use the existing model to generate analysis
            analysis_prompt = f"""Provide a concise fire weather analysis based on:

{context}

Focus on:
1. Current fire weather conditions and risk level
2. Key factors affecting fire behavior (wind, humidity, temperature)
3. Actionable recommendations for fire management

Keep response under 150 words for optimal performance."""

            # This would integrate with the existing model infrastructure
            # For now, return a structured summary based on available data
            if "High risk stations" in context:
                return "⚠️ ELEVATED FIRE WEATHER CONDITIONS detected. Multiple stations showing high fire weather indices. Recommend increased fire weather monitoring and readiness. Wind and low humidity are primary risk factors."
            elif "Average index" in context and "4." in context:
                return "🔥 MODERATE FIRE WEATHER CONDITIONS across monitored stations. Fire weather indices in moderate range. Standard fire weather precautions recommended."
            else:
                return "✅ NORMAL FIRE WEATHER CONDITIONS with low to moderate fire weather indices. Continue routine fire weather monitoring."
                
        except Exception as e:
            logger.error(f"AI summary generation error: {e}")
            return f"Weather data analysis complete. {len(weather_data) if 'weather_data' in locals() else 0} stations processed. See detailed data for specific conditions."

# Create agent instance
weather_agent = WeatherAgent()

# Integration functions for main agent system
async def get_weather_analysis(query: str, station_ids: Optional[List[str]] = None) -> Dict:
    """
    Get weather analysis for integration with main fire risk agent
    
    Args:
        query: Weather analysis query
        station_ids: Optional list of specific stations to analyze
        
    Returns:
        Dictionary with weather analysis results
    """
    weather_query = WeatherQuery(
        query=query,
        station_ids=station_ids,
        include_fire_weather=True
    )
    
    response = await weather_agent.run(weather_query)
    
    return {
        'summary': response.summary,
        'stations': response.stations,
        'fire_weather_analysis': response.fire_weather_analysis,
        'data_quality': response.data_quality_notes,
        'timestamp': 'real-time'
    }

# Example usage and testing
if __name__ == "__main__":
    async def test_weather_agent():
        """Test the weather analysis agent"""
        print("🌡️ Testing Weather Analysis Agent...")
        
        # Test query
        result = await get_weather_analysis(
            "What are current fire weather conditions in California?",
            station_ids=['KCEC', 'KSTS', 'KBUR']  # Northern, Central, Southern CA
        )
        
        print(f"\n📊 Analysis Summary:")
        print(result['summary'])
        
        print(f"\n🔥 Fire Weather Analysis:")
        print(result['fire_weather_analysis'])
        
        print(f"\n📍 Station Count: {len(result['stations'])}")
        
        if result['data_quality']:
            print(f"\n⚠️ Data Quality Notes:")
            for note in result['data_quality']:
                print(f"   - {note}")
    
    # Run test
    asyncio.run(test_weather_agent())