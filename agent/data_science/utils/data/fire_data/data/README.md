## Data Sources

### CSV Data Files

The "data" folder contains 5 spreadsheets, relating to fire danger prediction and related data.

## Sources
- `wxDailySummary2025-06-02_2025-06-16.csv`
- `fieldSample.csv`
- `StationMetaData.csv`
- `Site_Metadata.csv`
- `nfdrDailySummary2025-06-05_2025-06-17.csv`

## Summary Table of Files from the "data" Folder
| File Name                        | Description                                                                 | Key Data Points                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| `fieldSample.csv`                | Contains data on field samples collected, including Sample ID, Date-Time, Site Name, SiteId, Fuel Type, Category, Sub-Category, Method, Sample Avg Value, and Sample Status. Most samples are "Dead" fuel type. | Sample Id, Date-Time, Site Name, SiteId, Fuel Type, Category, Sub-Category, Method, Sample Avg Value, Sample Status |
| `StationMetaData.csv`            | Lists weather stations with their Station ID, Station Name, Latitude, Longitude, Elevation, and Aspect. | Station ID, Station Name, Latitude, Longitude, Elevation, Aspect |
| `nfdrDailySummary2025-06-05_2025-06-17.csv` | Contains daily National Fire Danger Rating (NFDR) summaries for various weather stations, including fuel moisture, ignition components, and burning indices. | StationId, StationName, observationTime, NFDRType, fuelModelType, oneHR_TL_FuelMoisture, tenHR_TL_FuelMoisture, hundredHR_TL_FuelMoisture, thousandHR_TL_FuelMoisture, kbdi, gsi, woodyLFI_fuelMoisture, herbaceousLFI_fuelMoisture, ignitionComponent, energyReleaseComponent, spreadComponent, burningIndex |
| `Site_Metadata.csv`              | Provides metadata for fire danger observation sites, including Site ID, Site Name, Latitude, Longitude, Elevation, Remarks, Agency Landowner, Aspect, Created Date, Area Name, Group Name, State, Status, and Slope. | Site ID, Site Name, Latitude, Longitude, Elevation, Remarks, Agency Landowner, Aspect, Created Date, Area Name, Group Name, State, Status, Slope |
| `wxDailySummary2025-06-02_2025-06-16.csv` | Contains daily weather summaries for various weather stations, including temperature, relative humidity, precipitation, wind speed, gust speed, gust direction, max solar radiation, and daily snow flag. | StationId, Date, ObservationType, TemperatureMin(F), TemperatureMax(F), RelativeHumidityMin(%), RelativeHumidityMax(%), Precipitation24hr(in), WindSpeedMax(mph), GustSpeedMax(mph), GustDirection(degrees), GustDirectionMaxTime(hh), MaxSolarRadiation(W/m2), DailySnowFlag |

### Public APIs

#### Weather Data

- **National Weather Service API**: https://api.weather.gov/
  - Forecast and historical weather data

#### Real-time Weather Observations
- **ArcGIS RAWS Stations**: https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/PublicView_RAWS/FeatureServer/1/query
  - Current weather station observations

#### Fire Detection
- **NASA LANCE FIRMS**: https://lance.modaps.eosdis.nasa.gov/ | FIRMS US/Canada
  - Fire detections

#### Geographic Boundaries
- **GACC Boundaries**: https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/DMP_NationalGACCBoundaries_Public/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson

---

## Technical Details

### RAWS Data Inputs

RAWS (Remote Automated Weather Stations) provide critical daily observations for NFDRS:

| Parameter | Typical Frequency | Used For |
|-----------|------------------|----------|
| Air Temperature (°F) | Hourly | Fuel moisture |
| Relative Humidity (%) | Hourly | Fuel moisture |
| Wind Speed (mph) | Hourly or Avg | Spread component |
| Rainfall (inches) | 24-hour total | Fuel moisture recovery |
| Solar Radiation | Optional | Fuel drying rate estimation |

### Core Calculations and Formulas

#### 1. Dead Fuel Moisture (1-Hour Time Lag Fuels)

Calculated from RH, temperature, and time since wetting rain using the empirical model:

```
FM1h = (1 + e^(0.115×(RH−100))) / (0.942×RH^0.679 + 11×e^((RH−100)/10) + 0.18×(21.1−T)×(1−e^(−0.115×RH)))
```

Where:
- **RH** = Relative humidity
- **T** = Air temperature (°C)

This gives the percent moisture content of 1-hour fuels (fine twigs, needles, grasses).

*Note: Longer lag fuels (10h, 100h, 1000h) have more complex lag equations and incorporate multi-day rainfall and drying trends.*

#### 2. Spread Component (SC)

```
SC = 0.560 × ROS
```

Where Rate of Spread (ROS) is calculated from:

```
ROS = a × e^(b×WindSpeed) × f(FuelMoisture)
```

- **a,b**: Empirically derived constants based on fuel model
- **f**: Fuel moisture reduction function

The SC ranges from 0 to 100 and indicates how fast the fire can spread in the first hour after ignition.

#### 3. Energy Release Component (ERC)

ERC is derived from:

```
ERC ∝ Σ(Fuel Load / Fuel Moisture Content)
```

More precisely:

```
ERC = Σ(wi × (1−FMi))

Where:

- **w<sub>i</sub>** = Weight of fuel model component (live vs dead)
- **FM<sub>i</sub>** = Moisture content of that component

ERC increases over time during dry periods and reflects cumulative dryness of vegetation (not affected by wind).
```

Where:
- **wi** = Weight of fuel model component (live vs dead)
- **FMi** = Moisture content of that component

ERC increases over time during dry periods and reflects cumulative dryness of vegetation (not affected by wind).

#### 4. Burning Index (BI)

```
BI = 10 × SC × ERC
```

BI is directly related to flame length and suppression difficulty.

### Example Calculation

**Sample RAWS Data:**

| Parameter | Value |
|-----------|-------|
| Temperature | 90°F (32.2°C) |
| Relative Humidity | 20% |
| Wind Speed | 15 mph |
| 24h Rainfall | 0.00 in |
| Fuel Model | G (dense brush) |

**Results:**
- **FM₁h**: ≈ 3–5%
- **SC**: High due to wind and low fuel moisture
- **ERC**: Increasing due to dry conditions and no rain
- **BI**: Will likely exceed 50 → Very High to Extreme Fire Danger

## AI Model Requirements

### Objective
Develop AI models to perform fire danger calculations and create projected forecasts and analysis.

### Example Use Cases

#### 1. Probability Modeling
> "Generate a model based on yesterday's weather station data in Missoula Montana, what is the probability of a fire in the western zone of the Northern Rockies GACC Boundary?"

#### 2. Wildfire Boundary Projection
> "With the current high fire risk in the Southern CA GACC Boundary and the active wildfires in the northern zone, generate the projected wildfire boundary over the next 5 days based on current fuel moisture and weather forecast."

