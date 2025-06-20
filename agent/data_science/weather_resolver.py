"""
Comprehensive Weather Location Resolver for Fire Weather System
Handles multiple input formats: cities, stations, ICAO codes, coordinates, etc.
Phase III Enhancement - Flexible location handling
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
import asyncio
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

class LocationType(Enum):
    """Types of location inputs we can handle"""
    ICAO_CODE = "icao_code"
    CITY_STATE = "city_state"
    COORDINATES = "coordinates"
    ZIP_CODE = "zip_code"
    STATION_NAME = "station_name"
    REGION = "region"
    LANDMARK = "landmark"
    UNKNOWN = "unknown"

@dataclass
class LocationInfo:
    """Standardized location information"""
    name: str
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    icao_code: Optional[str] = None
    station_id: Optional[str] = None
    region: Optional[str] = None
    location_type: LocationType = LocationType.UNKNOWN
    confidence: float = 0.0
    raw_input: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'state': self.state,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'icao_code': self.icao_code,
            'station_id': self.station_id,
            'region': self.region,
            'location_type': self.location_type.value,
            'confidence': self.confidence,
            'raw_input': self.raw_input
        }

class WeatherLocationResolver:
    """
    Intelligent location resolver that handles multiple input formats
    and maps them to Weather.gov station IDs
    """
    
    # Comprehensive city to ICAO mapping
    CITY_TO_ICAO = {
        # California
        'los angeles': 'KLAX', 'san francisco': 'KSFO', 'san diego': 'KSAN',
        'sacramento': 'KSAC', 'fresno': 'KFAT', 'oakland': 'KOAK',
        'san jose': 'KSJC', 'long beach': 'KLGB', 'bakersfield': 'KBFL',
        'anaheim': 'KSNA', 'santa ana': 'KSNA', 'riverside': 'KRAL',
        'stockton': 'KSCK', 'modesto': 'KMOD', 'burbank': 'KBUR',
        'santa barbara': 'KSBA', 'palm springs': 'KPSP', 'eureka': 'KACV',
        'crescent city': 'KCEC', 'santa rosa': 'KSTS', 'monterey': 'KMRY',
        
        # Oregon
        'portland': 'KPDX', 'eugene': 'KEUG', 'salem': 'KSLE',
        'gresham': 'KTTD', 'hillsboro': 'KHIO', 'bend': 'KBDN',
        'medford': 'KMFR', 'springfield': 'KEUG', 'corvallis': 'KCVO',
        'albany': 'KALE', 'klamath falls': 'KLMT', 'redmond': 'KRDM',
        
        # Washington
        'seattle': 'KSEA', 'spokane': 'KGEG', 'tacoma': 'KTIW',
        'vancouver': 'KVUO', 'bellevue': 'KBFI', 'everett': 'KPAE',
        'spokane valley': 'KGEG', 'kent': 'KSEA', 'yakima': 'KYKM',
        'bellingham': 'KBLI', 'olympia': 'KOLM', 'pullman': 'KPUW',
        
        # Colorado
        'denver': 'KDEN', 'colorado springs': 'KCOS', 'aurora': 'KAPA',
        'fort collins': 'KFNL', 'lakewood': 'KBJC', 'thornton': 'KBJC',
        'arvada': 'KBJC', 'westminster': 'KBJC', 'pueblo': 'KPUB',
        'grand junction': 'KGJT', 'boulder': 'KBDU', 'durango': 'KDRO',
        'aspen': 'KASE', 'alamosa': 'KALS', 'vail': 'KEGE',
        
        # Arizona
        'phoenix': 'KPHX', 'tucson': 'KTUS', 'mesa': 'KIWA',
        'chandler': 'KCHD', 'scottsdale': 'KSDL', 'glendale': 'KGEU',
        'tempe': 'KPHX', 'flagstaff': 'KFLG', 'yuma': 'KYUM',
        'prescott': 'KPRC', 'sedona': 'KSEZ', 'kingman': 'KIGM',
        
        # Nevada
        'las vegas': 'KLAS', 'henderson': 'KHND', 'reno': 'KRNO',
        'north las vegas': 'KVGT', 'sparks': 'KRNO', 'carson city': 'KCXP',
        'elko': 'KEKO', 'ely': 'KELY', 'fallon': 'KFLX',
        
        # Montana
        'billings': 'KBIL', 'missoula': 'KMSO', 'great falls': 'KGTF',
        'bozeman': 'KBZN', 'butte': 'KBTM', 'helena': 'KHLN',
        'kalispell': 'KGPI', 'havre': 'KHVR', 'livingston': 'KLVM',
        
        # Utah
        'salt lake city': 'KSLC', 'west valley city': 'KSLC', 'provo': 'KPVU',
        'west jordan': 'KSLC', 'orem': 'KPVU', 'sandy': 'KSLC',
        'ogden': 'KOGD', 'st george': 'KSGU', 'cedar city': 'KCDC',
        'park city': 'KSLC', 'logan': 'KLGU', 'vernal': 'KVEL',
        
        # Idaho
        'boise': 'KBOI', 'meridian': 'KBOI', 'nampa': 'KMAN',
        'idaho falls': 'KIDA', 'pocatello': 'KPIH', 'caldwell': 'KEUL',
        'coeur d\'alene': 'KCOE', 'twin falls': 'KTWF', 'lewiston': 'KLWS',
        'moscow': 'KPUW', 'sun valley': 'KSUN', 'mccall': 'KMYL',
        
        # New Mexico
        'albuquerque': 'KABQ', 'las cruces': 'KLRU', 'rio rancho': 'KABQ',
        'santa fe': 'KSAF', 'roswell': 'KROW', 'farmington': 'KFMN',
        'clovis': 'KCVN', 'carlsbad': 'KCNM', 'taos': 'KSKX',
        
        # Wyoming
        'cheyenne': 'KCYS', 'casper': 'KCPR', 'laramie': 'KLAR',
        'gillette': 'KGCC', 'rock springs': 'KRKS', 'sheridan': 'KSHR',
        'jackson': 'KJAC', 'cody': 'KCOD', 'riverton': 'KRIW'
    }
    
    # Fire station name to ICAO mapping (from existing system)
    STATION_NAME_TO_ICAO = {
        "BROWNSBORO": "KSDF",      # Louisville area, KY
        "BLACK HILLS": "KRAP",     # Rapid City, SD
        "BISON CREEK": "KDEN",     # Denver area, CO
        "BURNS CITY": "KBNO",      # Burns, OR
        "BROOKS": "KBIL",          # Billings, MT area
        "BURKESVILLE": "KEKQ",     # Kentucky area
        "CEDAR CREEK": "KCOS",     # Colorado Springs area
        "HIGHLAND": "KGJT",        # Grand Junction, CO area
        "WESTWOOD": "KBUR",        # Los Angeles area
        "CANYON VIEW": "KLAS",     # Las Vegas area
        "PINE RIDGE": "KPHX",      # Phoenix area
        "OAK VALLEY": "KFAT",      # Fresno area
        "BEAR CREEK": "KDEN",      # Denver area
        "EAGLE CANYON": "KFLG",    # Flagstaff area
        "WOLF MOUNTAIN": "KBZN",   # Bozeman area
        "DEER VALLEY": "KSLC",     # Salt Lake City area
        "ELK RIDGE": "KGEG",       # Spokane area
        "COUGAR CREEK": "KPDX",    # Portland area
        "MESA VERDE": "KDRO",      # Durango area
        "SILVER PEAK": "KRNO",     # Reno area
    }
    
    # Common landmarks to coordinates
    LANDMARKS = {
        'yosemite': (37.8651, -119.5383),
        'grand canyon': (36.1069, -112.1129),
        'yellowstone': (44.4280, -110.5885),
        'mount rainier': (46.8523, -121.7603),
        'crater lake': (42.9446, -122.1090),
        'mount hood': (45.3738, -121.6958),
        'lake tahoe': (39.0968, -120.0324),
        'big sur': (36.2704, -121.8081),
        'death valley': (36.5323, -116.9325),
        'zion': (37.2982, -113.0263),
        'bryce canyon': (37.5930, -112.1871),
        'glacier national park': (48.7596, -113.7870),
        'rocky mountain national park': (40.3428, -105.6836),
        'sequoia': (36.4864, -118.5658),
        'joshua tree': (33.8734, -115.9010),
        'redwood': (41.2132, -124.0046),
        'olympic': (47.8021, -123.6044),
        'north cascades': (48.7718, -121.2985),
        'mount shasta': (41.3099, -122.3106),
        'lassen volcanic': (40.4977, -121.4207)
    }
    
    # Regional definitions with multiple stations
    REGIONS = {
        'northern california': ['KCEC', 'KSTS', 'KSAC', 'KACV'],
        'southern california': ['KLAX', 'KSAN', 'KBUR', 'KPSP'],
        'central california': ['KFAT', 'KMOD', 'KBFL'],
        'bay area': ['KSFO', 'KOAK', 'KSJC'],
        'california coast': ['KMRY', 'KSBA', 'KSMF'],
        'sierra nevada': ['KMMH', 'KTVL', 'KBIH'],
        'western oregon': ['KPDX', 'KEUG', 'KSLE'],
        'eastern oregon': ['KBDN', 'KRDM', 'KPDT'],
        'oregon coast': ['KOTH', 'KONP', 'KAST'],
        'western washington': ['KSEA', 'KOLM', 'KBLI'],
        'eastern washington': ['KGEG', 'KPUW', 'KYKM'],
        'puget sound': ['KSEA', 'KTIW', 'KPAE'],
        'front range': ['KDEN', 'KCOS', 'KFNL'],
        'western slope': ['KGJT', 'KASE', 'KEGE'],
        'southern arizona': ['KTUS', 'KDUG', 'KOLS'],
        'northern arizona': ['KFLG', 'KSEZ', 'KPGA'],
        'mojave desert': ['KDAG', 'KEDW', 'KBYS'],
        'great basin': ['KRNO', 'KELY', 'KLOL'],
        'rocky mountains': ['KDEN', 'KBZN', 'KJAC'],
        'cascade range': ['KBDN', 'KYKM', 'KBLI']
    }
    
    def __init__(self):
        """Initialize the weather location resolver"""
        self.headers = {
            'User-Agent': 'RisenOne-Fire-Risk-Agent/3.0 (usda-ai-innovation-hub@techtrend.us)',
            'Accept': 'application/json'
        }
        
    def resolve_location(self, location_input: str) -> List[LocationInfo]:
        """
        Main entry point - resolves any location input to standardized LocationInfo
        
        Args:
            location_input: User input (city, coordinates, ICAO code, etc.)
            
        Returns:
            List of LocationInfo objects with resolved locations
        """
        if not location_input:
            return []
            
        location_input = location_input.strip()
        results = []
        
        # Try different resolution strategies in order of specificity
        
        # 1. Check if it's an ICAO code
        if self._is_icao_code(location_input):
            results.append(self._resolve_icao(location_input))
            
        # 2. Check if it's coordinates
        elif self._is_coordinates(location_input):
            coords = self._parse_coordinates(location_input)
            if coords:
                results.append(self._resolve_coordinates(*coords, location_input))
                
        # 3. Check if it's a fire station name
        elif location_input.upper() in self.STATION_NAME_TO_ICAO:
            results.append(self._resolve_station_name(location_input))
            
        # 4. Check if it's a landmark
        elif location_input.lower() in self.LANDMARKS:
            results.append(self._resolve_landmark(location_input))
            
        # 5. Check if it's a region
        elif self._is_region(location_input):
            results.extend(self._resolve_region(location_input))
            
        # 6. Check if it's a zip code
        elif self._is_zip_code(location_input):
            result = self._resolve_zip_code(location_input)
            if result:
                results.append(result)
                
        # 7. Try to parse as city/state
        else:
            city_results = self._resolve_city(location_input)
            if city_results:
                results.extend(city_results)
            else:
                # Last resort - fuzzy match against known locations
                fuzzy_results = self._fuzzy_match_location(location_input)
                results.extend(fuzzy_results)
        
        # Remove duplicates and sort by confidence
        unique_results = self._deduplicate_results(results)
        return sorted(unique_results, key=lambda x: x.confidence, reverse=True)
    
    def _is_icao_code(self, text: str) -> bool:
        """Check if input is an ICAO code (4 letters starting with K for US)"""
        return bool(re.match(r'^K[A-Z]{3}$', text.upper()))
    
    def _is_coordinates(self, text: str) -> bool:
        """Check if input contains coordinates"""
        # Match various coordinate formats
        coord_patterns = [
            r'[-+]?\d+\.?\d*\s*,\s*[-+]?\d+\.?\d*',  # 37.7749, -122.4194
            r'[-+]?\d+°?\d*\'?\d*"?\s*[NS]?\s*,?\s*[-+]?\d+°?\d*\'?\d*"?\s*[EW]?',  # 37°46'N, 122°25'W
            r'\d+\.?\d*\s*[NS]\s*\d+\.?\d*\s*[EW]'  # 37.7749N 122.4194W
        ]
        return any(re.search(pattern, text) for pattern in coord_patterns)
    
    def _is_zip_code(self, text: str) -> bool:
        """Check if input is a US zip code"""
        return bool(re.match(r'^\d{5}(-\d{4})?$', text.strip()))
    
    def _is_region(self, text: str) -> bool:
        """Check if input matches a known region"""
        text_lower = text.lower()
        return any(region in text_lower for region in self.REGIONS.keys())
    
    def _parse_coordinates(self, text: str) -> Optional[Tuple[float, float]]:
        """Parse coordinate string into lat/lon tuple"""
        try:
            # Simple comma-separated format
            if ',' in text:
                parts = text.split(',')
                lat = float(re.sub(r'[^\d.-]', '', parts[0]))
                lon = float(re.sub(r'[^\d.-]', '', parts[1]))
                return (lat, lon)
            
            # Space-separated with N/S E/W indicators
            match = re.search(r'([\d.]+)\s*([NS])\s*([\d.]+)\s*([EW])', text.upper())
            if match:
                lat = float(match.group(1))
                if match.group(2) == 'S':
                    lat = -lat
                lon = float(match.group(3))
                if match.group(4) == 'W':
                    lon = -lon
                return (lat, lon)
                
        except Exception as e:
            logger.warning(f"Failed to parse coordinates from '{text}': {e}")
        return None
    
    def _resolve_icao(self, icao_code: str) -> LocationInfo:
        """Resolve ICAO code to LocationInfo"""
        icao_upper = icao_code.upper()
        
        # Find city name from reverse mapping
        city_name = None
        state = None
        
        for city, code in self.CITY_TO_ICAO.items():
            if code == icao_upper:
                city_name = city.title()
                # Try to determine state from city
                state = self._get_state_from_city(city)
                break
        
        if not city_name:
            city_name = f"Station {icao_upper}"
        
        return LocationInfo(
            name=city_name,
            state=state,
            icao_code=icao_upper,
            station_id=icao_upper,
            location_type=LocationType.ICAO_CODE,
            confidence=1.0,
            raw_input=icao_code
        )
    
    def _resolve_coordinates(self, lat: float, lon: float, raw_input: str) -> LocationInfo:
        """Resolve coordinates to nearest weather station"""
        # Find nearest station (simplified - in production would use proper distance calculation)
        nearest_city = self._find_nearest_city(lat, lon)
        
        return LocationInfo(
            name=f"Location near {nearest_city}",
            latitude=lat,
            longitude=lon,
            icao_code=self.CITY_TO_ICAO.get(nearest_city.lower()),
            location_type=LocationType.COORDINATES,
            confidence=0.8,
            raw_input=raw_input
        )
    
    def _resolve_station_name(self, station_name: str) -> LocationInfo:
        """Resolve fire station name to ICAO code"""
        station_upper = station_name.upper()
        icao_code = self.STATION_NAME_TO_ICAO.get(station_upper)
        
        return LocationInfo(
            name=station_name.title(),
            icao_code=icao_code,
            station_id=icao_code,
            location_type=LocationType.STATION_NAME,
            confidence=0.95,
            raw_input=station_name
        )
    
    def _resolve_landmark(self, landmark: str) -> LocationInfo:
        """Resolve landmark to location"""
        landmark_lower = landmark.lower()
        coords = self.LANDMARKS.get(landmark_lower)
        
        if coords:
            lat, lon = coords
            nearest_city = self._find_nearest_city(lat, lon)
            
            return LocationInfo(
                name=landmark.title(),
                latitude=lat,
                longitude=lon,
                icao_code=self.CITY_TO_ICAO.get(nearest_city.lower()),
                location_type=LocationType.LANDMARK,
                confidence=0.9,
                raw_input=landmark
            )
        
        return None
    
    def _resolve_region(self, region: str) -> List[LocationInfo]:
        """Resolve region to multiple stations"""
        region_lower = region.lower()
        results = []
        
        for region_name, station_codes in self.REGIONS.items():
            if region_name in region_lower:
                for icao_code in station_codes:
                    info = self._resolve_icao(icao_code)
                    info.region = region_name
                    info.location_type = LocationType.REGION
                    info.confidence = 0.85
                    info.raw_input = region
                    results.append(info)
                break
        
        return results
    
    def _resolve_city(self, city_input: str) -> List[LocationInfo]:
        """Resolve city name to location(s)"""
        results = []
        city_lower = city_input.lower()
        
        # Check for state in input
        state = None
        city_name = city_lower
        
        # Common state abbreviations and full names
        state_patterns = {
            r',\s*ca\b': 'California',
            r',\s*california': 'California',
            r',\s*or\b': 'Oregon',
            r',\s*oregon': 'Oregon',
            r',\s*wa\b': 'Washington',
            r',\s*washington': 'Washington',
            r',\s*co\b': 'Colorado',
            r',\s*colorado': 'Colorado',
            r',\s*az\b': 'Arizona',
            r',\s*arizona': 'Arizona',
            r',\s*nv\b': 'Nevada',
            r',\s*nevada': 'Nevada',
            r',\s*mt\b': 'Montana',
            r',\s*montana': 'Montana',
            r',\s*ut\b': 'Utah',
            r',\s*utah': 'Utah',
            r',\s*id\b': 'Idaho',
            r',\s*idaho': 'Idaho',
            r',\s*nm\b': 'New Mexico',
            r',\s*new mexico': 'New Mexico',
            r',\s*wy\b': 'Wyoming',
            r',\s*wyoming': 'Wyoming'
        }
        
        for pattern, state_name in state_patterns.items():
            if re.search(pattern, city_lower):
                state = state_name
                city_name = re.sub(pattern, '', city_lower).strip()
                break
        
        # Look up city
        if city_name in self.CITY_TO_ICAO:
            icao_code = self.CITY_TO_ICAO[city_name]
            
            results.append(LocationInfo(
                name=city_name.title(),
                state=state or self._get_state_from_city(city_name),
                icao_code=icao_code,
                station_id=icao_code,
                location_type=LocationType.CITY_STATE,
                confidence=0.95 if state else 0.85,
                raw_input=city_input
            ))
        
        return results
    
    def _resolve_zip_code(self, zip_code: str) -> Optional[LocationInfo]:
        """Resolve zip code to location (simplified implementation)"""
        # In production, this would use a zip code database
        # For now, return a placeholder
        return LocationInfo(
            name=f"ZIP {zip_code}",
            location_type=LocationType.ZIP_CODE,
            confidence=0.7,
            raw_input=zip_code
        )
    
    def _fuzzy_match_location(self, input_text: str) -> List[LocationInfo]:
        """Fuzzy match against known locations"""
        results = []
        input_lower = input_text.lower()
        
        # Check cities
        for city, icao in self.CITY_TO_ICAO.items():
            if input_lower in city or city in input_lower:
                results.append(LocationInfo(
                    name=city.title(),
                    icao_code=icao,
                    station_id=icao,
                    location_type=LocationType.CITY_STATE,
                    confidence=0.6,
                    raw_input=input_text
                ))
        
        # Check regions
        for region, stations in self.REGIONS.items():
            if input_lower in region or region in input_lower:
                for station in stations[:2]:  # Limit to first 2 stations
                    info = self._resolve_icao(station)
                    info.region = region
                    info.confidence = 0.5
                    info.raw_input = input_text
                    results.append(info)
        
        return results[:5]  # Limit results
    
    def _find_nearest_city(self, lat: float, lon: float) -> str:
        """Find nearest city to coordinates (simplified)"""
        # In production, this would use proper distance calculations
        # For now, return a default based on rough regions
        if lat > 45:
            return "Seattle" if lon < -110 else "Billings"
        elif lat > 40:
            return "Portland" if lon < -110 else "Denver"
        elif lat > 35:
            return "San Francisco" if lon < -115 else "Phoenix"
        else:
            return "Los Angeles" if lon < -110 else "Tucson"
    
    def _get_state_from_city(self, city: str) -> Optional[str]:
        """Determine state from city name"""
        # Simplified state mapping
        state_cities = {
            'California': ['los angeles', 'san francisco', 'san diego', 'sacramento', 
                          'fresno', 'oakland', 'san jose', 'bakersfield'],
            'Oregon': ['portland', 'eugene', 'salem', 'bend', 'medford'],
            'Washington': ['seattle', 'spokane', 'tacoma', 'vancouver', 'bellevue'],
            'Colorado': ['denver', 'colorado springs', 'aurora', 'fort collins'],
            'Arizona': ['phoenix', 'tucson', 'mesa', 'chandler', 'scottsdale'],
            'Nevada': ['las vegas', 'henderson', 'reno'],
            'Montana': ['billings', 'missoula', 'great falls', 'bozeman'],
            'Utah': ['salt lake city', 'provo', 'west valley city'],
            'Idaho': ['boise', 'meridian', 'nampa', 'idaho falls'],
            'New Mexico': ['albuquerque', 'las cruces', 'santa fe'],
            'Wyoming': ['cheyenne', 'casper', 'laramie']
        }
        
        city_lower = city.lower()
        for state, cities in state_cities.items():
            if city_lower in cities:
                return state
        return None
    
    def _deduplicate_results(self, results: List[LocationInfo]) -> List[LocationInfo]:
        """Remove duplicate locations, keeping highest confidence"""
        unique = {}
        
        for result in results:
            if result:
                key = (result.icao_code or result.name)
                if key not in unique or result.confidence > unique[key].confidence:
                    unique[key] = result
        
        return list(unique.values())
    
    async def validate_stations(self, locations: List[LocationInfo]) -> List[LocationInfo]:
        """
        Validate that weather stations are actually available
        Returns only stations that respond successfully
        """
        validated = []
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for location in locations:
                if location.icao_code:
                    try:
                        url = f"https://api.weather.gov/stations/{location.icao_code}"
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                data = await response.json()
                                # Update location with station metadata
                                properties = data.get('properties', {})
                                location.name = properties.get('name', location.name)
                                if 'coordinates' in data.get('geometry', {}):
                                    coords = data['geometry']['coordinates']
                                    location.longitude = coords[0]
                                    location.latitude = coords[1]
                                validated.append(location)
                    except Exception as e:
                        logger.warning(f"Failed to validate station {location.icao_code}: {e}")
                        continue
        
        return validated
    
    def format_locations_for_display(self, locations: List[LocationInfo]) -> str:
        """Format resolved locations for user display"""
        if not locations:
            return "No locations found"
        
        lines = ["📍 **Resolved Weather Locations**\n"]
        
        for i, loc in enumerate(locations, 1):
            confidence_emoji = "🟢" if loc.confidence > 0.8 else "🟡" if loc.confidence > 0.6 else "🔴"
            
            lines.append(f"{i}. **{loc.name}**")
            if loc.state:
                lines.append(f"   State: {loc.state}")
            if loc.icao_code:
                lines.append(f"   Station: {loc.icao_code}")
            if loc.latitude and loc.longitude:
                lines.append(f"   Coordinates: {loc.latitude:.4f}, {loc.longitude:.4f}")
            lines.append(f"   {confidence_emoji} Confidence: {loc.confidence:.0%}")
            lines.append("")
        
        return "\n".join(lines)


# Convenience function for sync usage
def resolve_weather_location(location_input: str) -> List[LocationInfo]:
    """
    Simple sync wrapper for location resolution
    
    Args:
        location_input: Any location format (city, ICAO, coordinates, etc.)
        
    Returns:
        List of resolved LocationInfo objects
    """
    resolver = WeatherLocationResolver()
    return resolver.resolve_location(location_input)


# Example usage and testing
if __name__ == "__main__":
    # Test various input formats
    test_inputs = [
        "KSFO",                          # ICAO code
        "Denver, CO",                    # City, State
        "37.7749, -122.4194",           # Coordinates
        "northern california",           # Region
        "Yosemite",                     # Landmark
        "BROWNSBORO",                   # Fire station name
        "90210",                        # ZIP code
        "Portland Oregon",              # City state without comma
        "bay area",                     # Region
        "seattle tacoma",               # Multiple cities
        "37°46'N, 122°25'W",           # Formatted coordinates
        "front range colorado",         # Region with state
        "Los Angeles",                  # City only
        "mount hood",                   # Landmark
        "random unknown place"          # Unknown location
    ]
    
    resolver = WeatherLocationResolver()
    
    print("Weather Location Resolver Test Results")
    print("=" * 80)
    
    for test_input in test_inputs:
        print(f"\n🔍 Testing: '{test_input}'")
        print("-" * 40)
        
        results = resolver.resolve_location(test_input)
        
        if results:
            print(resolver.format_locations_for_display(results))
        else:
            print("❌ No results found")
    
    # Test async validation
    import asyncio
    
    async def test_validation():
        locations = resolver.resolve_location("California")
        validated = await resolver.validate_stations(locations)
        print(f"\n✅ Validated {len(validated)} of {len(locations)} stations")
    
    asyncio.run(test_validation())