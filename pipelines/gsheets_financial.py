import dlt
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from prefect import flow, task
import os 
import subprocess
from dotenv import load_dotenv
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable Prefect server communication
os.environ["PREFECT_API_ENABLE"] = "false"

# Load environment variables
load_dotenv(dotenv_path="/workspaces/CamOnPrefect/.env")

@task
def extract_data_from_gsheet(sheet_name: str) -> pd.DataFrame:
    """Extract data from Google Sheets and return as DataFrame"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_file = os.getenv("CREDENTIALS_FILE")
        if not creds_file:
            raise ValueError("CREDENTIALS_FILE environment variable not set")
            
        creds = Credentials.from_service_account_file(creds_file, scopes=scope)
        client = gspread.authorize(creds)

        logger.info(f"Accessing Google Sheet: {sheet_name}")
        sheet = client.open(sheet_name).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
        
    except Exception as e:
        logger.error(f"Error extracting data from Google Sheet: {e}")
        raise

@task
def load_data_to_duckdb(df: pd.DataFrame) -> None:
    """Load data into DuckDB using dlt"""
    try:
        gsheets_pipeline = dlt.pipeline(
            pipeline_name="gsheets_to_pg",
            destination="motherduck",
            dataset_name="google_sheets",
            dev_mode=False
        )

        logger.info("Loading data into DuckDB")
        gsheets_pipeline.run(
            df, 
            table_name="gsheetFinance", 
            write_disposition="merge", 
            primary_key="id"
        )
    except Exception as e:
        logger.error(f"Error loading data to DuckDB: {e}")
        raise

@task
def run_dbt_command() -> str:
    """Execute dbt transformation"""
    DBT_PROJECT_DIR = "/workspaces/CamOnPrefect/dbt"
    try:
        logger.info("Running dbt transformations")
        result = subprocess.run(
            "dbt run --select base_gsheets_finance+", 
            shell=True, 
            cwd=DBT_PROJECT_DIR, 
            capture_output=True, 
            text=True
        )
        
        logger.info(result.stdout)
        if result.returncode != 0:
            raise Exception(f"dbt command failed: {result.stderr}")
        return result.stdout
    except Exception as e:
        logger.error(f"Error running dbt: {e}")
        raise

@flow(name="gsheets-financial-flow")
def main_flow() -> None:
    """Main pipeline flow"""
    os.environ["PREFECT_API_URL"] = ""
    try:
        sheet_name = os.getenv("GOOGLE_SHEET_NAME")
        if not sheet_name:
            raise ValueError("GOOGLE_SHEET_NAME environment variable not set")
            
        logger.info("Starting gsheets financial pipeline")
        df = extract_data_from_gsheet(sheet_name)
        load_data_to_duckdb(df)
        run_dbt_command()
        logger.info("Pipeline completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    os.environ["PREFECT_API_URL"] = ""
    main_flow()