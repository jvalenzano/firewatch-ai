"""
NASA FIRMS API Client for Real-Time Fire Detection

Phase III Sprint 1 Implementation  
FIRMS: Fire Information for Resource Management System
API: https://firms.modaps.eosdis.nasa.gov/
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import aiohttp
import csv
from io import StringIO

logger = logging.getLogger(__name__)

@dataclass
class ActiveFire:
    """Active fire detection data structure"""
    fire_id: str
    latitude: float
    longitude: float
    brightness: float  # Brightness temperature (Kelvin)
    scan: float        # Along-scan pixel size
    track: float       # Along-track pixel size
    acq_date: str      # Acquisition date
    acq_time: str      # Acquisition time
    satellite: str     # Satellite (Terra, Aqua, etc.)
    confidence: int    # Detection confidence (0-100)
    version: str       # Collection version
    bright_t31: Optional[float] = None  # Brightness temperature band 31
    frp: Optional[float] = None         # Fire Radiative Power (MW)
    daynight: str = "D"                 # Day/Night flag

class NASAFIRMSClient:
    """
    NASA FIRMS API client for real-time active fire detection
    
    Integrates with existing fire risk analysis system
    Provides near real-time fire alerts for enhanced situational awareness
    """
    
    # FIRMS data URLs (24-hour active fires)
    BASE_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire"
    
    # Available data sources
    SOURCES = {
        'MODIS_C6': 'modis-c6',      # MODIS Collection 6 (Terra/Aqua)
        'VIIRS_SNPP': 'viirs-snpp',  # VIIRS S-NPP 
        'VIIRS_NOAA20': 'viirs-noaa20'  # VIIRS NOAA-20
    }
    
    def __init__(self, update_interval_minutes: int = 30):
        """
        Initialize NASA FIRMS client
        
        Args:
            update_interval_minutes: How often to refresh fire data (default: 30 minutes)
        """
        self.update_interval = timedelta(minutes=update_interval_minutes)
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, List[ActiveFire]] = {}
        self.last_update: Dict[str, datetime] = {}
        
        # Headers for API requests
        self.headers = {
            'User-Agent': 'RisenOne-Fire-Risk-Agent/3.0 (usda-ai-innovation-hub@techtrend.us)',
            'Accept': 'text/csv'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_active_fires_region(self, 
                                    south: float, west: float, 
                                    north: float, east: float,
                                    source: str = 'MODIS_C6') -> List[ActiveFire]:
        """
        Get active fires for a geographic region
        
        Args:
            south, west, north, east: Bounding box coordinates (lat/lon)
            source: Data source (MODIS_C6, VIIRS_SNPP, VIIRS_NOAA20)
            
        Returns:
            List of ActiveFire objects in the region
        """
        if not self.session:
            raise RuntimeError("NASAFIRMSClient must be used as async context manager")
        
        # Check cache freshness
        cache_key = f"{source}_{south}_{west}_{north}_{east}"
        if self._is_data_fresh(cache_key):
            return self.cache.get(cache_key, [])
        
        try:
            # Build URL for regional data (24-hour active fires)
            source_code = self.SOURCES.get(source, 'modis-c6')
            url = f"{self.BASE_URL}/csv/{source_code}/World_24h.csv"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"FIRMS API error {response.status}")
                    return []
                
                csv_data = await response.text()
                fires = self._parse_csv_data(csv_data)
                
                # Filter to region
                regional_fires = [
                    fire for fire in fires
                    if south <= fire.latitude <= north and west <= fire.longitude <= east
                ]
                
                # Update cache
                self.cache[cache_key] = regional_fires
                self.last_update[cache_key] = datetime.utcnow()
                
                logger.info(f"Retrieved {len(regional_fires)} active fires for region")
                return regional_fires
                
        except Exception as e:
            logger.error(f"Error fetching active fires: {e}")
            return []
    
    async def get_active_fires_usa(self, source: str = 'MODIS_C6') -> List[ActiveFire]:
        """
        Get active fires for continental USA
        
        Args:
            source: Data source (MODIS_C6, VIIRS_SNPP, VIIRS_NOAA20)
            
        Returns:
            List of ActiveFire objects in USA
        """
        # Continental USA bounding box
        return await self.get_active_fires_region(
            south=24.0, west=-126.0,
            north=49.0, east=-66.0,
            source=source
        )
    
    async def get_active_fires_california(self, source: str = 'MODIS_C6') -> List[ActiveFire]:
        """
        Get active fires for California (high fire risk state)
        
        Args:
            source: Data source
            
        Returns:
            List of ActiveFire objects in California
        """
        # California bounding box
        return await self.get_active_fires_region(
            south=32.5, west=-124.5,
            north=42.0, east=-114.0,
            source=source
        )
    
    def _parse_csv_data(self, csv_data: str) -> List[ActiveFire]:
        """Parse CSV data from FIRMS API"""
        fires = []
        
        try:
            reader = csv.DictReader(StringIO(csv_data))
            
            for row in reader:
                try:
                    # Generate unique fire ID
                    fire_id = f"{row.get('latitude', '0')}_{row.get('longitude', '0')}_{row.get('acq_date', '')}_{row.get('acq_time', '')}"
                    
                    fire = ActiveFire(
                        fire_id=fire_id,
                        latitude=float(row.get('latitude', 0)),
                        longitude=float(row.get('longitude', 0)),
                        brightness=float(row.get('brightness', 0)),
                        scan=float(row.get('scan', 0)),
                        track=float(row.get('track', 0)),
                        acq_date=row.get('acq_date', ''),
                        acq_time=row.get('acq_time', ''),
                        satellite=row.get('satellite', ''),
                        confidence=int(row.get('confidence', 0)),
                        version=row.get('version', ''),
                        bright_t31=float(row.get('bright_t31', 0)) if row.get('bright_t31') else None,
                        frp=float(row.get('frp', 0)) if row.get('frp') else None,
                        daynight=row.get('daynight', 'D')
                    )
                    
                    fires.append(fire)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing fire record: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing CSV data: {e}")
        
        return fires
    
    def _is_data_fresh(self, cache_key: str) -> bool:
        """Check if cached data is still fresh"""
        if cache_key not in self.last_update:
            return False
        
        time_since_update = datetime.utcnow() - self.last_update[cache_key]
        return time_since_update < self.update_interval

class FireAnalyzer:
    """
    Analyze active fire data for risk assessment
    Integrates with existing fire weather analysis
    """
    
    @staticmethod
    def analyze_fire_intensity(fires: List[ActiveFire]) -> Dict:
        """
        Analyze fire intensity and risk from active fire detections
        
        Args:
            fires: List of active fire detections
            
        Returns:
            Dictionary with fire analysis results
        """
        if not fires:
            return {
                'total_fires': 0,
                'high_confidence_fires': 0,
                'average_confidence': 0,
                'risk_level': 'NORMAL',
                'hotspots': []
            }
        
        # Basic statistics
        total_fires = len(fires)
        high_confidence_fires = sum(1 for f in fires if f.confidence >= 80)
        average_confidence = sum(f.confidence for f in fires) / total_fires
        
        # Calculate average brightness (fire intensity)
        average_brightness = sum(f.brightness for f in fires) / total_fires
        
        # Determine risk level based on fire count and confidence
        if total_fires >= 20 and average_confidence >= 80:
            risk_level = 'EXTREME'
        elif total_fires >= 10 and average_confidence >= 70:
            risk_level = 'HIGH'
        elif total_fires >= 5 and average_confidence >= 60:
            risk_level = 'MODERATE'
        else:
            risk_level = 'NORMAL'
        
        # Identify hotspots (clusters of high-confidence fires)
        hotspots = []
        high_conf_fires = [f for f in fires if f.confidence >= 75]
        
        if high_conf_fires:
            # Simple hotspot identification (can be enhanced with clustering)
            hotspots = [
                {
                    'latitude': fire.latitude,
                    'longitude': fire.longitude, 
                    'confidence': fire.confidence,
                    'brightness': fire.brightness,
                    'satellite': fire.satellite
                }
                for fire in high_conf_fires[:5]  # Top 5 hotspots
            ]
        
        return {
            'total_fires': total_fires,
            'high_confidence_fires': high_confidence_fires,
            'average_confidence': round(average_confidence, 1),
            'average_brightness': round(average_brightness, 1),
            'risk_level': risk_level,
            'hotspots': hotspots,
            'satellites_reporting': list(set(f.satellite for f in fires))
        }

# Integration functions for main agent system
async def get_fire_detection_analysis(region: str = 'california') -> Dict:
    """
    Get fire detection analysis for integration with main fire risk agent
    
    Args:
        region: Region to analyze ('california', 'usa', or custom coordinates)
        
    Returns:
        Dictionary with fire detection analysis
    """
    async with NASAFIRMSClient() as client:
        # Get active fires based on region
        if region.lower() == 'california':
            fires = await client.get_active_fires_california()
        elif region.lower() == 'usa':
            fires = await client.get_active_fires_usa()
        else:
            # Default to California for testing
            fires = await client.get_active_fires_california()
        
        # Analyze fire activity
        analysis = FireAnalyzer.analyze_fire_intensity(fires)
        
        return {
            'region': region,
            'analysis': analysis,
            'active_fires': len(fires),
            'timestamp': datetime.utcnow().isoformat(),
            'data_source': 'NASA FIRMS MODIS'
        }

# Example usage for testing
if __name__ == "__main__":
    async def test_nasa_firms():
        """Test NASA FIRMS integration"""
        print("🛰️ Testing NASA FIRMS Active Fire Detection...")
        
        # Test California fire detection
        result = await get_fire_detection_analysis('california')
        
        print(f"\n🔥 Active Fire Analysis for {result['region'].title()}:")
        analysis = result['analysis']
        print(f"   Total Active Fires: {analysis['total_fires']}")
        print(f"   High Confidence Fires: {analysis['high_confidence_fires']}")
        print(f"   Average Confidence: {analysis['average_confidence']}%")
        print(f"   Risk Level: {analysis['risk_level']}")
        print(f"   Satellites: {', '.join(analysis['satellites_reporting'])}")
        
        if analysis['hotspots']:
            print(f"\n🔥 Fire Hotspots:")
            for i, hotspot in enumerate(analysis['hotspots'][:3], 1):
                print(f"   {i}. Lat: {hotspot['latitude']:.3f}, Lon: {hotspot['longitude']:.3f}")
                print(f"      Confidence: {hotspot['confidence']}%, Brightness: {hotspot['brightness']:.1f}K")
    
    # Run test
    asyncio.run(test_nasa_firms())