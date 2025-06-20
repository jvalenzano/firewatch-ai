# Station Format Guide - Updated with Automatic Mapping

**Last Updated:** June 19, 2025  
**Status:** Station mapping feature now active! 🎉

## Key Update: Automatic Station Name Mapping

The system now **automatically converts** fire station names to Weather.gov airport codes! You can use either format and the system will handle the conversion.

## How It Works

### 🎯 Fire Station Names → Automatically Mapped
```
User: "What's the weather at BROWNSBORO?"
System: Automatically converts BROWNSBORO → KSDF (Louisville)
Result: Returns real-time weather from Louisville International Airport
```

### ✈️ Airport Codes → Work Directly  
```
User: "What's the weather at KDEN?"
System: Uses KDEN directly
Result: Returns real-time weather from Denver International Airport
```

## Supported Station Mappings

| Fire Station Name | Maps to Airport | Location |
|------------------|-----------------|----------|
| BROWNSBORO | KSDF | Louisville, KY |
| BLACK HILLS | KRAP | Rapid City, SD |
| BISON CREEK | KDEN | Denver, CO |
| BURNS CITY | KBNO | Burns, OR |
| BROOKS | KBIL | Billings, MT |
| BURKESVILLE | KEKQ | Kentucky area |
| CEDAR CREEK | KCOS | Colorado Springs, CO |
| HIGHLAND | KGJT | Grand Junction, CO |
| WESTWOOD | KBUR | Los Angeles/Burbank, CA |
| CANYON VIEW | KLAS | Las Vegas, NV |
| PINE RIDGE | KPHX | Phoenix, AZ |
| OAK VALLEY | KFAT | Fresno, CA |

## Query Examples

### ✅ All These Queries Now Work:

**Using Fire Station Names (Automatic Mapping):**
- "Get weather for BROWNSBORO"
- "Show conditions at BLACK HILLS station"
- "What's the temperature at BISON CREEK?"
- "Compare weather at WESTWOOD and PINE RIDGE"

**Using Airport Codes (Direct):**
- "Get weather for KDEN"
- "Show me KBUR conditions"
- "What's the weather at station KSEA?"

**Mixed Queries:**
- "Compare BROWNSBORO with KDEN"
- "Show me BLACK HILLS and KBUR"

## System Components

### 1. Real-Time Weather (Weather.gov API)
- **Tool:** `get_real_time_fire_weather_conditions`
- **Accepts:** Both fire station names AND airport codes
- **Mapping:** Automatic conversion happens behind the scenes
- **Coverage:** 21+ validated weather stations

### 2. Historical Fire Data (BigQuery)
- **Tool:** `get_fire_danger_for_station`
- **Format:** Fire station names (e.g., BROWNSBORO, BLACK HILLS)
- **Data:** 17,386 historical fire records from 278 stations

### 3. Fire Danger Calculations
- **Tool:** `calculate_fire_danger`
- **Input:** Temperature, humidity, wind speed, precipitation
- **Output:** NFDRS-compliant fire danger ratings

## Tips for Best Results

1. **Station Names Are Case-Insensitive**
   - "brownsboro" = "BROWNSBORO" = "Brownsboro"

2. **Partial Matches Not Supported**
   - Use full station names: "BLACK HILLS" not "BLACK"

3. **Unknown Stations**
   - If a station isn't in the mapping table, the system will try it as-is
   - May fail if it's not a valid ICAO code

4. **Regional Queries Work Too**
   - "Get weather for California stations"
   - "Show me Colorado fire conditions"

## Technical Implementation

The mapping happens in the `get_real_time_fire_weather_conditions` function:

```python
# Automatic station mapping
if station_id and not (len(station_id) == 4 and station_id.startswith('K')):
    mapped_id = STATION_TO_ICAO_MAPPING.get(station_id.upper(), station_id)
    station_ids[i] = mapped_id
```

## Troubleshooting

**Issue:** "Unable to retrieve real-time weather data"
- **Cause:** Station not in mapping table and not a valid ICAO code
- **Solution:** Check the supported stations list above

**Issue:** No historical data for a station
- **Cause:** Station exists in Weather.gov but not in BigQuery
- **Solution:** Use a nearby station or request by conditions

## Future Enhancements

1. **Expand Mapping Table** - Add more station pairs as discovered
2. **Fuzzy Matching** - Support partial station names
3. **Reverse Mapping** - Show user-friendly names in responses
4. **Auto-Discovery** - Query BigQuery to find nearest airports