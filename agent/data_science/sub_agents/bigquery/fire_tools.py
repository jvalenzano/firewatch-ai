# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
POC-AD-1: Enhanced BigQuery Tools for Fire Risk Data
Fire-specific database tools for the Database Agent
"""

import os
import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple
from google.adk.tools import ToolContext
from google.cloud import bigquery
from data_science.utils.utils import get_env_var

logger = logging.getLogger(__name__)

# Fire data configuration
FIRE_DATASET_ID = "poc_fire_data"
FIRE_TABLES = {
    'nfdr': 'nfdr_daily_summary',
    'stations': 'station_metadata',
    'weather': 'weather_daily_summary',
    'fuel_samples': 'fuel_samples'
}

def get_fire_database_settings() -> Dict:
    """Get POC fire data database settings"""
    try:
        # Emergency hardcoded configuration - deployed agents don't have env vars
        try:
            project_id = get_env_var("BQ_PROJECT_ID")
        except (ValueError, KeyError):
            project_id = "risenone-ai-prototype"  # EMERGENCY FALLBACK
        
        # Get fire data schema
        fire_schema = get_fire_bigquery_schema(FIRE_DATASET_ID, project_id)
        
        return {
            'fire_project_id': project_id,
            'fire_dataset_id': FIRE_DATASET_ID,
            'fire_tables': FIRE_TABLES,
            'fire_schema': fire_schema,
            'fire_enabled': True if fire_schema else False
        }
    except Exception as e:
        logger.warning(f"Fire data not available: {e}")
        return {
            'fire_project_id': None,
            'fire_dataset_id': FIRE_DATASET_ID,
            'fire_tables': FIRE_TABLES,
            'fire_schema': '',
            'fire_enabled': False
        }

def get_fire_bigquery_schema(dataset_id: str, project_id: str) -> str:
    """Get schema for fire data tables with sample data"""
    try:
        client = bigquery.Client(project=project_id)
        dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
        
        fire_schema = ""
        
        for table_type, table_name in FIRE_TABLES.items():
            try:
                table_ref = dataset_ref.table(table_name)
                table_obj = client.get_table(table_ref)
                
                # Generate DDL
                ddl_statement = f"-- FIRE DATA TABLE: {table_name.upper()}\n"
                ddl_statement += f"CREATE OR REPLACE TABLE `{table_ref}` (\n"
                
                for field in table_obj.schema:
                    ddl_statement += f"  `{field.name}` {field.field_type}"
                    if field.mode == "REPEATED":
                        ddl_statement += " ARRAY"
                    if field.description:
                        ddl_statement += f" COMMENT '{field.description}'"
                    ddl_statement += ",\n"
                
                ddl_statement = ddl_statement[:-2] + "\n);\n\n"
                
                # Add sample data
                rows = client.list_rows(table_ref, max_results=3).to_dataframe()
                if not rows.empty:
                    ddl_statement += f"-- Sample data from {table_name}:\n"
                    for _, row in rows.head(3).iterrows():
                        sample_values = []
                        for col in rows.columns:
                            value = row[col]
                            if pd.isna(value):
                                sample_values.append("NULL")
                            elif isinstance(value, str):
                                sample_values.append(f"'{value}'")
                            else:
                                sample_values.append(str(value))
                        ddl_statement += f"-- Example: ({', '.join(sample_values)})\n"
                    ddl_statement += "\n"
                
                fire_schema += ddl_statement
                
            except Exception as table_error:
                logger.warning(f"Could not get schema for {table_name}: {table_error}")
                continue
        
        return fire_schema
        
    except Exception as e:
        logger.warning(f"Could not get fire schema: {e}")
        return ""

def get_fire_query_templates() -> Dict[str, str]:
    """Get fire-specific query templates for common analysis"""
    project_placeholder = "{project}"
    dataset = FIRE_DATASET_ID
    
    return {
        # Station Information Queries
        'all_stations': f"""
            SELECT station_id, station_name, latitude, longitude, elevation, 
                   elevation_risk_class, state, region, cluster_id
            FROM `{project_placeholder}.{dataset}.station_metadata`
            ORDER BY station_name
        """,
        
        'high_risk_stations': f"""
            SELECT station_id, station_name, latitude, longitude, elevation,
                   elevation_risk_class, state, region
            FROM `{project_placeholder}.{dataset}.station_metadata`
            WHERE elevation_risk_class = 'High'
            ORDER BY elevation DESC
        """,
        
        'stations_by_state': f"""
            SELECT state, COUNT(*) as station_count,
                   AVG(elevation) as avg_elevation,
                   COUNT(CASE WHEN elevation_risk_class = 'High' THEN 1 END) as high_risk_count
            FROM `{project_placeholder}.{dataset}.station_metadata`
            WHERE state != 'Unknown'
            GROUP BY state
            ORDER BY station_count DESC
        """,
        
        # Fire Danger Analysis Queries
        'latest_fire_danger': f"""
            SELECT n.station_id, s.station_name, s.state, n.observation_time,
                   n.burning_index, n.fire_danger_class,
                   n.energy_release_component, n.spread_component,
                   n.ignition_component
            FROM `{project_placeholder}.{dataset}.nfdr_daily_summary` n
            JOIN `{project_placeholder}.{dataset}.station_metadata` s
                ON n.station_id = s.station_id
            WHERE DATE(n.observation_time) = (
                SELECT MAX(DATE(observation_time)) 
                FROM `{project_placeholder}.{dataset}.nfdr_daily_summary`
            )
            ORDER BY n.burning_index DESC
        """,
        
        'extreme_fire_danger': f"""
            SELECT n.station_id, s.station_name, s.state, s.elevation,
                   n.observation_time, n.burning_index, n.fire_danger_class,
                   n.one_hr_fuel_moisture, n.ten_hr_fuel_moisture
            FROM `{project_placeholder}.{dataset}.nfdr_daily_summary` n
            JOIN `{project_placeholder}.{dataset}.station_metadata` s
                ON n.station_id = s.station_id
            WHERE n.fire_danger_class IN ('Extreme', 'Very High')
            ORDER BY n.observation_time DESC, n.burning_index DESC
        """,
        
        'fire_danger_trends': f"""
            SELECT DATE(n.observation_time) as date,
                   COUNT(*) as total_stations,
                   AVG(n.burning_index) as avg_burning_index,
                   COUNT(CASE WHEN n.fire_danger_class = 'Extreme' THEN 1 END) as extreme_count,
                   COUNT(CASE WHEN n.fire_danger_class = 'Very High' THEN 1 END) as very_high_count,
                   COUNT(CASE WHEN n.fire_danger_class = 'High' THEN 1 END) as high_count
            FROM `{project_placeholder}.{dataset}.nfdr_daily_summary` n
            GROUP BY DATE(n.observation_time)
            ORDER BY date DESC
        """,
        
        # Weather Correlation Queries
        'weather_fire_correlation': f"""
            SELECT w.station_id, s.station_name, w.observation_date,
                   w.temperature_max_f, w.relative_humidity_min_pct,
                   w.wind_speed_max_mph, w.precipitation_24hr_in,
                   n.burning_index, n.fire_danger_class
            FROM `{project_placeholder}.{dataset}.weather_daily_summary` w
            JOIN `{project_placeholder}.{dataset}.station_metadata` s
                ON w.station_id = s.station_id
            LEFT JOIN `{project_placeholder}.{dataset}.nfdr_daily_summary` n
                ON w.station_id = n.station_id 
                AND DATE(w.observation_date) = DATE(n.observation_time)
            WHERE w.observation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)
            ORDER BY w.observation_date DESC, n.burning_index DESC
        """,
        
        'dry_conditions_analysis': f"""
            SELECT w.station_id, s.station_name, s.state,
                   AVG(w.temperature_max_f) as avg_max_temp,
                   AVG(w.relative_humidity_min_pct) as avg_min_humidity,
                   SUM(w.precipitation_24hr_in) as total_precip,
                   COUNT(CASE WHEN w.precipitation_24hr_in = 0 THEN 1 END) as dry_days,
                   AVG(n.burning_index) as avg_burning_index
            FROM `{project_placeholder}.{dataset}.weather_daily_summary` w
            JOIN `{project_placeholder}.{dataset}.station_metadata` s
                ON w.station_id = s.station_id
            LEFT JOIN `{project_placeholder}.{dataset}.nfdr_daily_summary` n
                ON w.station_id = n.station_id 
                AND DATE(w.observation_date) = DATE(n.observation_time)
            WHERE w.observation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)
            GROUP BY w.station_id, s.station_name, s.state
            HAVING dry_days >= 10  -- 10+ dry days out of 14
            ORDER BY avg_burning_index DESC
        """,
        
        # Fuel Moisture Analysis
        'fuel_moisture_analysis': f"""
            SELECT n.station_id, s.station_name, s.elevation_risk_class,
                   DATE(n.observation_time) as date,
                   n.one_hr_fuel_moisture, n.ten_hr_fuel_moisture,
                   n.hundred_hr_fuel_moisture, n.thousand_hr_fuel_moisture,
                   n.burning_index, n.fire_danger_class
            FROM `{project_placeholder}.{dataset}.nfdr_daily_summary` n
            JOIN `{project_placeholder}.{dataset}.station_metadata` s
                ON n.station_id = s.station_id
            WHERE n.one_hr_fuel_moisture IS NOT NULL
              AND n.one_hr_fuel_moisture < 10  -- Critical fuel moisture threshold
            ORDER BY n.observation_time DESC, n.one_hr_fuel_moisture ASC
        """,
        
        'geographic_fire_risk_summary': f"""
            SELECT s.region, s.state,
                   COUNT(DISTINCT s.station_id) as station_count,
                   AVG(s.elevation) as avg_elevation,
                   COUNT(CASE WHEN s.elevation_risk_class = 'High' THEN 1 END) as high_elev_stations,
                   AVG(n.burning_index) as avg_burning_index,
                   COUNT(CASE WHEN n.fire_danger_class IN ('Extreme', 'Very High') THEN 1 END) as high_danger_readings
            FROM `{project_placeholder}.{dataset}.station_metadata` s
            LEFT JOIN `{project_placeholder}.{dataset}.nfdr_daily_summary` n
                ON s.station_id = n.station_id
                AND DATE(n.observation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            WHERE s.region != 'Unknown'
            GROUP BY s.region, s.state
            ORDER BY avg_burning_index DESC NULLS LAST
        """
    }

def format_fire_query(template_name: str, project_id: str, **kwargs) -> str:
    """Format a fire query template with project ID and optional parameters"""
    templates = get_fire_query_templates()
    
    if template_name not in templates:
        raise ValueError(f"Unknown fire query template: {template_name}")
    
    query = templates[template_name]
    query = query.replace("{project}", project_id)
    
    # Replace any additional parameters
    for key, value in kwargs.items():
        query = query.replace(f"{{{key}}}", str(value))
    
    return query

def get_fire_query_suggestions(user_intent: str) -> List[str]:
    """Suggest fire-specific queries based on user intent"""
    intent_lower = user_intent.lower()
    suggestions = []
    
    # Station-related queries
    if any(word in intent_lower for word in ['station', 'location', 'where', 'geographic']):
        suggestions.extend(['all_stations', 'stations_by_state', 'high_risk_stations'])
    
    # Fire danger queries
    if any(word in intent_lower for word in ['fire danger', 'burning index', 'risk', 'danger']):
        suggestions.extend(['latest_fire_danger', 'extreme_fire_danger', 'fire_danger_trends'])
    
    # Weather correlation
    if any(word in intent_lower for word in ['weather', 'temperature', 'humidity', 'wind', 'rain']):
        suggestions.extend(['weather_fire_correlation', 'dry_conditions_analysis'])
    
    # Fuel moisture
    if any(word in intent_lower for word in ['fuel', 'moisture', 'dry', 'drought']):
        suggestions.extend(['fuel_moisture_analysis'])
    
    # Geographic analysis
    if any(word in intent_lower for word in ['region', 'state', 'area', 'cluster', 'geographic']):
        suggestions.extend(['geographic_fire_risk_summary', 'stations_by_state'])
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(suggestions))

def enhance_database_settings_with_fire_data(existing_settings: Dict) -> Dict:
    """Enhance existing database settings with fire data capabilities"""
    fire_settings = get_fire_database_settings()
    
    # Merge fire settings into existing settings
    enhanced_settings = existing_settings.copy()
    enhanced_settings.update(fire_settings)
    
    # Enhance schema with fire data
    if fire_settings['fire_enabled']:
        enhanced_settings['combined_schema'] = (
            existing_settings.get('bq_ddl_schema', '') + 
            "\n\n-- FIRE RISK DATA TABLES --\n" +
            fire_settings['fire_schema']
        )
    else:
        enhanced_settings['combined_schema'] = existing_settings.get('bq_ddl_schema', '')
    
    return enhanced_settings 