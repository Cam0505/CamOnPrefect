import dlt
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from prefect import flow, task
import os 
import subprocess
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")


# Set dlt credentials
# os.environ["DESTINATION__DUCKDB__CREDENTIALS"] = os.getenv("DESTINATION__DUCKDB__CREDENTIALS")

@task
def extract_data_from_gsheet(sheet_name: str) -> pd.DataFrame:
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    creds = Credentials.from_service_account_file(os.getenv("CREDENTIALS_FILE"), scopes=scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df


@task
def load_data_to_duckdb(df: pd.DataFrame):

    gsheets_pipeline = dlt.pipeline(
        pipeline_name="gsheets_to_pg",
        destination="duckdb",
        dataset_name="google_sheets",
        dev_mode=False
    )

    gsheets_pipeline.run(df, table_name="gsheetFinance", write_disposition="merge", primary_key="id")


DBT_PROJECT_DIR = "/workspaces/CamOnPrefect/dbt"

@task
def run_dbt_command():
    result = subprocess.run(f"dbt run --select base_gsheets_finance+", shell=True, cwd=DBT_PROJECT_DIR, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise Exception(f"dbt command failed: {result.stderr}")
    return result.stdout

@flow(name="gsheets-financial-flow")
def main_flow():
    # os.environ["PREFECT_API_ENABLE"] = "false" # IF you wanna run it locally without a prefect server
    df = extract_data_from_gsheet(os.getenv("GOOGLE_SHEET_NAME"))
    load_data_to_duckdb(df)
    run_dbt_command()

if __name__ == "__main__":
    main_flow()