# Weather Location Guide - Flexible Input System

## Overview

The RisenOne Fire Analysis Agent now supports an extremely flexible weather location system that can understand virtually any location format. This enhancement makes the weather API user-friendly and accessible to users regardless of how they express locations.

## Supported Location Formats

### 1. **ICAO Airport Codes**
Standard 4-letter aviation codes starting with 'K' for US stations.
```
Examples:
- KDEN (Denver International)
- KSFO (San Francisco International)
- KLAX (Los Angeles International)
- KSEA (Seattle-Tacoma International)
```

### 2. **City Names**
Just type the city name - no special formatting required.
```
Examples:
- Denver
- Los Angeles
- San Francisco
- Portland
- Phoenix
```

### 3. **City + State**
Various formats are supported - with or without commas, abbreviated or full state names.
```
Examples:
- Seattle, WA
- Portland, Oregon
- Denver CO
- Phoenix Arizona
- San Francisco, California
```

### 4. **Geographic Coordinates**
Multiple coordinate formats are accepted.
```
Examples:
- 37.7749, -122.4194 (decimal degrees)
- 45°30'N 122°40'W (degrees, minutes)
- 40.7128N 74.0060W (with direction indicators)
- 37°46'N, 122°25'W (formatted with symbols)
```

### 5. **Famous Landmarks**
Popular landmarks and national parks are recognized.
```
Examples:
- Yosemite
- Grand Canyon
- Mount Rainier
- Lake Tahoe
- Mount Hood
- Death Valley
- Yellowstone
```

### 6. **Fire Station Names**
Historic fire station names from the database are mapped to nearest weather stations.
```
Examples:
- BROWNSBORO
- BLACK HILLS
- PINE RIDGE
- CEDAR CREEK
- WESTWOOD
- CANYON VIEW
```

### 7. **Geographic Regions**
Broad regional descriptions return multiple relevant stations.
```
Examples:
- northern california
- bay area
- front range
- puget sound
- southern arizona
- cascade range
- mojave desert
```

### 8. **ZIP Codes**
US postal codes (5-digit format).
```
Examples:
- 90210 (Beverly Hills)
- 10001 (New York)
- 60601 (Chicago)
- 80202 (Denver)
```

## Using the Weather Tools

### New Flexible Tool: `get_weather_by_location`

The most user-friendly tool that accepts any location format:

```python
# Current conditions only
get_weather_by_location("Denver")
get_weather_by_location("37.7749, -122.4194")
get_weather_by_location("Yosemite")

# With forecast
get_weather_by_location("Seattle", forecast_days=3)
get_weather_by_location("Grand Canyon", forecast_days=7)
get_weather_by_location("KPHX", forecast_days=5)
```

### Enhanced Existing Tools

The existing tools now also support flexible location input:

1. **`get_real_time_fire_weather_conditions`**
   - The `region` parameter now accepts cities, landmarks, and other formats
   - The `station_ids` list can include fire station names and cities

2. **`get_fire_weather_forecast`**
   - The `station_id` parameter now accepts any location format

## Examples of Natural Language Queries

The agent can now understand queries like:

- "What's the fire weather in Denver?"
- "Show me conditions for Yosemite National Park"
- "Fire risk near 37.7749, -122.4194"
- "Get weather for the Grand Canyon area"
- "Fire conditions in northern California"
- "What's the forecast for Mount Hood next week?"
- "Check fire danger at BROWNSBORO station"
- "Bay Area fire weather outlook"

## Location Resolution Intelligence

### Confidence Scoring
Each resolved location has a confidence score:
- 🟢 **High (>80%)**: Direct matches (ICAO codes, exact city names)
- 🟡 **Medium (60-80%)**: Partial matches, regions
- 🔴 **Low (<60%)**: Fuzzy matches, approximations

### Multiple Results
When a location could refer to multiple places, the system returns ranked results:
- Best match is used by default
- Regional queries return multiple stations for comprehensive coverage

### Smart Fallbacks
If an exact match isn't found:
1. Fuzzy matching against known cities
2. Regional approximation
3. Nearest station by coordinates
4. Helpful error message with examples

## Coverage Areas

### Primary Coverage (High Station Density)
- California (All regions)
- Oregon
- Washington
- Colorado
- Arizona
- Nevada

### Extended Coverage (Good Station Coverage)
- Montana
- Utah
- Idaho
- New Mexico
- Wyoming

### Station Validation
The system validates that weather stations are actually responding before using them, ensuring reliable data.

## Error Handling

If a location cannot be resolved, users receive helpful guidance:
```
❌ Unable to resolve location: "unknown place"

I couldn't find any weather stations for that location. Please try:
- City name: "Denver", "Los Angeles", "Portland"
- City + State: "Seattle, WA", "Phoenix, AZ"
- ICAO code: "KDEN", "KSFO"
- Coordinates: "45.5152, -122.6784"
- Landmark: "Grand Canyon", "Yosemite"
- Region: "northern california", "front range"
```

## Performance

- Location resolution: <100ms typical
- Caching: Recently resolved locations are cached
- Batch processing: Regional queries efficiently handle multiple stations

## Future Enhancements

Planned improvements:
1. International location support
2. Street address resolution
3. Natural language parsing ("50 miles north of Denver")
4. Historical location names
5. Military base weather stations
6. Offshore/marine locations