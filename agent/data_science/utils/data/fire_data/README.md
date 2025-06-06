# Fire Analysis Data

This directory will contain fire-related datasets for the RisenOne Fire Analysis Agent:

## Planned Data Sources:
- **Weather Stations**: Temperature, humidity, wind speed/direction, precipitation
- **Fire Danger Indices**: Current fire detection, danger ratings, fuel moisture
- **Field Observations**: Scientist-collected vegetation, soil, fuel load data
- **Historical Data**: Fire spread patterns, weather correlations, seasonal trends

## Data Format:
CSV files with standardized schemas for integration with BigQuery ML models.

## Usage:
Data files will be loaded via `agent/data_science/utils/create_bq_table.py` for BigQuery integration.
