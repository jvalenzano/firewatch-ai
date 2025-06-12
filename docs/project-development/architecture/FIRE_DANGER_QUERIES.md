# Fire Danger Query Examples

## Available Queries:

### 1. **General Fire Danger Calculation**
- "Calculate fire danger for temperature 85°F, humidity 25%, wind speed 12 mph"
- "What's the fire danger with 90 degree heat and 20% humidity?"
- "Calculate burning index for hot dry conditions"

### 2. **Station-Specific Fire Danger**
- "What's the fire danger for station BROWNSBORO?"
- "Calculate fire danger for BONSECOUR station"
- "Show me the latest fire risk at station BANKHEAD"
- "Get fire danger for any weather station"

### 3. **Weather Station Data Queries**
- "How many weather stations do we have fire data for?" (277 stations)
- "List weather stations with fire data"
- "Show me stations in Alabama"

### 4. **Recent Fire Conditions**
- "What are the latest fire danger levels?"
- "Show recent fire danger calculations"
- "Get the most recent fire risk assessments"

## Expected Responses:

### Fire Danger Components:
- **Dead Fuel Moisture**: 1-hour timelag fuel moisture percentage
- **Live Fuel Moisture**: Living vegetation moisture content
- **Spread Component**: Fire spread potential (0-99 scale)
- **Energy Release Component**: Available energy for combustion (0-97 scale)
- **Burning Index**: Overall fire intensity potential (0-999 scale)

### Fire Danger Classifications:
- **LOW**: BI < 25 (Minimal fire activity expected)
- **MODERATE**: BI 25-49 (Fires readily ignite, spread moderate)
- **HIGH**: BI 50-74 (Fires start easily, spread rapidly)
- **VERY HIGH**: BI 75-89 (Explosive fire growth potential)
- **EXTREME**: BI 90+ (Catastrophic fire conditions)

## Technical Details:
- Uses NFDRS (National Fire Danger Rating System) standard formulas
- Calculates from real BigQuery weather station data
- Compares calculated values with actual database values
- Provides both estimated weather conditions and fire danger metrics

## Sample Response Format:
```
🔥 Fire Danger Analysis Results:

📍 Station: BROWNSBORO (ID: 10402)
📅 Date: 2025-06-05

Weather Conditions:
- Temperature: 80°F
- Relative Humidity: 40%
- Wind Speed: 10 mph

Calculated Fire Danger:
- Dead Fuel Moisture: 3.5%
- Spread Component: 2.8
- Burning Index: 15.2
- **Fire Danger Class: LOW**
```

## Integration with Database:
The agent can:
- Query real weather station data from BigQuery
- Calculate fire danger using NFDRS formulas
- Compare calculations with stored fire danger values
- Analyze trends across multiple stations
- Provide Forest Service standard assessments 