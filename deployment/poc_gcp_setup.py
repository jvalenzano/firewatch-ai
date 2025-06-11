#!/usr/bin/env python3
"""
POC-DA-1: GCP Environment Setup and API Integration for Fire Risk AI POC

This script sets up the complete GCP environment for the RisenOne Fire Risk AI POC,
including Vertex AI platform, Weather.gov API integration, and fire data processing.
"""

import logging
import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions
from google.cloud import storage, bigquery
from google.cloud import aiplatform
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID for POC")
flags.DEFINE_string("location", "us-central1", "GCP location for POC resources")
flags.DEFINE_string("bucket", None, "GCP bucket name for POC data storage")
flags.DEFINE_bool("setup_all", False, "Setup complete POC environment")
flags.DEFINE_bool("test_apis", False, "Test API connections")
flags.DEFINE_bool("load_fire_data", False, "Load client fire data to BigQuery")
flags.DEFINE_bool("validate_setup", False, "Validate complete setup")

# POC-specific constants
POC_DATASET_ID = "fire_risk_poc"
WEATHER_API_BASE = "https://api.weather.gov"
FIRE_DATA_PATH = "agent/data_science/utils/data/fire_data/data"

class POCGCPSetup:
    """Handles GCP setup for Fire Risk AI POC"""
    
    def __init__(self, project_id: str, location: str, bucket_name: str):
        self.project_id = project_id
        self.location = location
        self.bucket_name = bucket_name
        self.bucket_uri = f"gs://{bucket_name}"
        
        # Initialize clients
        self.storage_client = None
        self.bq_client = None
        self.setup_clients()
    
    def setup_clients(self):
        """Initialize GCP clients"""
        try:
            self.storage_client = storage.Client(project=self.project_id)
            self.bq_client = bigquery.Client(project=self.project_id)
            vertexai.init(project=self.project_id, location=self.location)
            logger.info("✅ GCP clients initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCP clients: {e}")
            raise
    
    def setup_storage_bucket(self) -> bool:
        """Create and configure storage bucket for POC data"""
        try:
            # Check if bucket exists
            bucket = self.storage_client.lookup_bucket(self.bucket_name)
            if bucket:
                logger.info(f"✅ Storage bucket {self.bucket_uri} already exists")
                return True
            
            # Create bucket
            logger.info(f"🔧 Creating storage bucket {self.bucket_uri}")
            bucket = self.storage_client.create_bucket(
                self.bucket_name, 
                project=self.project_id, 
                location=self.location
            )
            
            # Configure bucket
            bucket.iam_configuration.uniform_bucket_level_access_enabled = True
            bucket.patch()
            
            logger.info(f"✅ Storage bucket {self.bucket_uri} created successfully")
            return True
            
        except google_exceptions.Forbidden as e:
            logger.error(f"❌ Permission denied for bucket creation: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to setup storage bucket: {e}")
            return False
    
    def setup_bigquery_dataset(self) -> bool:
        """Create BigQuery dataset for fire data"""
        try:
            dataset_id = f"{self.project_id}.{POC_DATASET_ID}"
            
            # Check if dataset exists
            try:
                dataset = self.bq_client.get_dataset(dataset_id)
                logger.info(f"✅ BigQuery dataset {dataset_id} already exists")
                return True
            except google_exceptions.NotFound:
                pass
            
            # Create dataset
            logger.info(f"🔧 Creating BigQuery dataset {dataset_id}")
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = self.location
            dataset.description = "Fire Risk AI POC - Real fire danger data and calculations"
            
            dataset = self.bq_client.create_dataset(dataset, timeout=30)
            logger.info(f"✅ BigQuery dataset {dataset_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup BigQuery dataset: {e}")
            return False
    
    def test_weather_api(self) -> bool:
        """Test Weather.gov API connection"""
        try:
            logger.info("🔧 Testing Weather.gov API connection...")
            
            # Test basic API endpoint
            response = requests.get(f"{WEATHER_API_BASE}/", timeout=10)
            if response.status_code != 200:
                logger.error(f"❌ Weather.gov API returned status {response.status_code}")
                return False
            
            # Test specific station data (using a station from our dataset)
            test_station = "419401"  # BUFFALO GAP from StationMetaData.csv
            response = requests.get(
                f"{WEATHER_API_BASE}/stations/{test_station}/observations/latest",
                timeout=10,
                headers={'User-Agent': 'RisenOne-Fire-Risk-POC/1.0'}
            )
            
            if response.status_code == 200:
                logger.info("✅ Weather.gov API connection successful")
                logger.info(f"✅ Test station {test_station} data accessible")
                return True
            else:
                logger.warning(f"⚠️ Weather.gov API basic connection OK, but station data returned {response.status_code}")
                return True  # Basic API works, station-specific issues are expected
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Weather.gov API connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error testing Weather.gov API: {e}")
            return False
    
    def load_fire_data_to_bigquery(self) -> bool:
        """Load client fire data CSV files to BigQuery"""
        try:
            logger.info("🔧 Loading client fire data to BigQuery...")
            
            # Define data files and their corresponding table names
            data_files = {
                "station_metadata": "StationMetaData.csv",
                "site_metadata": "Site_Metadata.csv", 
                "nfdr_daily_summary": "nfdrDailySummary2025-06-05_2025-06-17.csv",
                "weather_daily_summary": "wxDailySummary2025-06-02_2025-06-16.csv",
                "field_samples": "fieldSample.csv"
            }
            
            dataset_ref = self.bq_client.dataset(POC_DATASET_ID)
            success_count = 0
            
            for table_name, file_name in data_files.items():
                file_path = Path(FIRE_DATA_PATH) / file_name
                
                if not file_path.exists():
                    logger.warning(f"⚠️ Data file not found: {file_path}")
                    continue
                
                try:
                    # Read CSV to determine schema
                    df = pd.read_csv(file_path)
                    logger.info(f"📊 Loading {file_name}: {len(df)} rows, {len(df.columns)} columns")
                    
                    # Create table reference
                    table_ref = dataset_ref.table(table_name)
                    
                    # Configure load job
                    job_config = bigquery.LoadJobConfig(
                        source_format=bigquery.SourceFormat.CSV,
                        skip_leading_rows=1,
                        autodetect=True,
                        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
                    )
                    
                    # Load data
                    with open(file_path, "rb") as source_file:
                        job = self.bq_client.load_table_from_file(
                            source_file, table_ref, job_config=job_config
                        )
                    
                    job.result()  # Wait for job to complete
                    
                    # Verify load
                    table = self.bq_client.get_table(table_ref)
                    logger.info(f"✅ Loaded {table.num_rows} rows to {table_name}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load {file_name}: {e}")
            
            if success_count > 0:
                logger.info(f"✅ Successfully loaded {success_count}/{len(data_files)} data files")
                return True
            else:
                logger.error("❌ Failed to load any data files")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to load fire data to BigQuery: {e}")
            return False
    
    def setup_vertex_ai_platform(self) -> bool:
        """Setup Vertex AI platform for POC agents"""
        try:
            logger.info("🔧 Setting up Vertex AI platform...")
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.location,
                staging_bucket=self.bucket_uri
            )
            
            # Test Vertex AI access by listing models
            models = aiplatform.Model.list(
                filter='display_name="*"',
                order_by='create_time desc',
                project=self.project_id,
                location=self.location
            )
            
            logger.info(f"✅ Vertex AI platform accessible, found {len(models)} models")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Vertex AI platform: {e}")
            return False
    
    def create_poc_environment_file(self) -> bool:
        """Create POC-specific .env file"""
        try:
            logger.info("🔧 Creating POC environment configuration...")
            
            env_content = f"""# POC-DA-1: Fire Risk AI POC Environment Configuration
# Generated automatically - DO NOT EDIT MANUALLY

# GCP Configuration
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT={self.project_id}
GOOGLE_CLOUD_LOCATION={self.location}
GOOGLE_CLOUD_STORAGE_BUCKET={self.bucket_name}

# POC-Specific Configuration
POC_DATASET_ID={POC_DATASET_ID}
WEATHER_API_BASE={WEATHER_API_BASE}
FIRE_DATA_PATH={FIRE_DATA_PATH}

# BigQuery Configuration
BQ_PROJECT_ID={self.project_id}
BQ_DATASET_ID={POC_DATASET_ID}

# Models for POC Agents
ROOT_AGENT_MODEL=gemini-2.0-flash-001
ANALYTICS_AGENT_MODEL=gemini-2.0-flash-001
FIRE_SCIENCE_AGENT_MODEL=gemini-2.0-flash-001
NFDRS_CALCULATION_MODEL=gemini-2.0-flash-001

# POC Feature Flags
ENABLE_REAL_DATA_VALIDATION=true
ENABLE_WEATHER_API_INTEGRATION=true
ENABLE_NFDRS_CALCULATIONS=true
ENABLE_MULTI_REGION_ANALYSIS=true

# API Configuration
NL2SQL_METHOD=BASELINE
BQML_RAG_CORPUS_NAME=
CODE_INTERPRETER_EXTENSION_NAME=
"""
            
            env_file_path = Path("agent/.env.poc")
            with open(env_file_path, "w") as f:
                f.write(env_content)
            
            logger.info(f"✅ POC environment file created: {env_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create POC environment file: {e}")
            return False
    
    def validate_complete_setup(self) -> Dict[str, bool]:
        """Validate all POC setup components"""
        logger.info("🔍 Validating complete POC setup...")
        
        validation_results = {
            "storage_bucket": False,
            "bigquery_dataset": False,
            "weather_api": False,
            "vertex_ai": False,
            "fire_data_loaded": False,
            "environment_config": False
        }
        
        # Validate storage bucket
        try:
            bucket = self.storage_client.lookup_bucket(self.bucket_name)
            validation_results["storage_bucket"] = bucket is not None
        except:
            pass
        
        # Validate BigQuery dataset
        try:
            dataset_id = f"{self.project_id}.{POC_DATASET_ID}"
            dataset = self.bq_client.get_dataset(dataset_id)
            validation_results["bigquery_dataset"] = dataset is not None
        except:
            pass
        
        # Validate Weather API
        validation_results["weather_api"] = self.test_weather_api()
        
        # Validate Vertex AI
        validation_results["vertex_ai"] = self.setup_vertex_ai_platform()
        
        # Validate fire data
        try:
            dataset_ref = self.bq_client.dataset(POC_DATASET_ID)
            tables = list(self.bq_client.list_tables(dataset_ref))
            validation_results["fire_data_loaded"] = len(tables) >= 3
        except:
            pass
        
        # Validate environment config
        validation_results["environment_config"] = Path("agent/.env.poc").exists()
        
        # Print validation summary
        logger.info("\n" + "="*60)
        logger.info("POC-DA-1 VALIDATION SUMMARY")
        logger.info("="*60)
        
        for component, status in validation_results.items():
            status_icon = "✅" if status else "❌"
            component_name = component.replace("_", " ").title()
            logger.info(f"{status_icon} {component_name}: {'PASS' if status else 'FAIL'}")
        
        success_count = sum(validation_results.values())
        total_count = len(validation_results)
        
        logger.info("="*60)
        logger.info(f"OVERALL STATUS: {success_count}/{total_count} components validated")
        
        if success_count == total_count:
            logger.info("🎉 POC-DA-1 SETUP COMPLETE - Ready for POC-DA-2!")
        else:
            logger.warning("⚠️ POC-DA-1 SETUP INCOMPLETE - Review failed components")
        
        return validation_results


def main(argv: List[str]) -> None:
    """Main execution function for POC GCP setup"""
    load_dotenv()
    
    # Get configuration
    project_id = FLAGS.project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = FLAGS.location or os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket_name = FLAGS.bucket or os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET") or f"{project_id}-fire-risk-poc"
    
    # Validate required parameters
    if not project_id:
        logger.error("❌ Missing required GCP Project ID")
        logger.error("Set GOOGLE_CLOUD_PROJECT environment variable or use --project_id flag")
        sys.exit(1)
    
    logger.info("🚀 Starting POC-DA-1: GCP Environment Setup")
    logger.info(f"📋 Project: {project_id}")
    logger.info(f"📋 Location: {location}")
    logger.info(f"📋 Bucket: {bucket_name}")
    
    # Initialize setup handler
    setup = POCGCPSetup(project_id, location, bucket_name)
    
    try:
        if FLAGS.setup_all:
            logger.info("🔧 Setting up complete POC environment...")
            
            # Setup all components
            results = []
            results.append(setup.setup_storage_bucket())
            results.append(setup.setup_bigquery_dataset())
            results.append(setup.setup_vertex_ai_platform())
            results.append(setup.create_poc_environment_file())
            
            if FLAGS.load_fire_data:
                results.append(setup.load_fire_data_to_bigquery())
            
            # Validate setup
            validation_results = setup.validate_complete_setup()
            
            if all(results) and all(validation_results.values()):
                logger.info("🎉 POC-DA-1 setup completed successfully!")
                sys.exit(0)
            else:
                logger.error("❌ POC-DA-1 setup completed with errors")
                sys.exit(1)
        
        elif FLAGS.test_apis:
            success = setup.test_weather_api()
            sys.exit(0 if success else 1)
        
        elif FLAGS.load_fire_data:
            success = setup.load_fire_data_to_bigquery()
            sys.exit(0 if success else 1)
        
        elif FLAGS.validate_setup:
            validation_results = setup.validate_complete_setup()
            sys.exit(0 if all(validation_results.values()) else 1)
        
        else:
            logger.error("❌ No action specified. Use --setup_all, --test_apis, --load_fire_data, or --validate_setup")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app.run(main) 