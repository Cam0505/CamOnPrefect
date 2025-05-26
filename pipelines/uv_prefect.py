import os
from dotenv import load_dotenv
import dlt
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import json
from dlt.sources.helpers import requests
from prefect import flow, task, get_run_logger
from dlt.pipeline.exceptions import PipelineNeverRan
from path_config import DBT_DIR, ENV_FILE, DLT_PIPELINE_DIR
from helper_functions import write_profiles_yml

load_dotenv(dotenv_path=ENV_FILE)
BASE_URL = "https://api.openuv.io/api/v1/uv"

cities = [
    {"city": "Sydney", "lat": -33.8688, "lng": 151.2093},
    {"city": "Melbourne", "lat": -37.8136, "lng": 144.9631},
    {"city": "Brisbane", "lat": -27.4698, "lng": 153.0251},
    {"city": "Perth", "lat": -31.9505, "lng": 115.8605},
    {"city": "Adelaide", "lat": -34.9285, "lng": 138.6007},
    {"city": "Canberra", "lat": -35.2809, "lng": 149.1300},
    {"city": "Hobart", "lat": -42.8821, "lng": 147.3272},
    {"city": "Darwin", "lat": -12.4634, "lng": 130.8456}
]

    

def get_dates(logger):
    try:
        pipeline = dlt.current.pipeline()
        with pipeline.sql_client() as client:
            result = client.execute_sql(
                f"SELECT date_col FROM public_staging.staging_uv_data_dates")
            return [row[0] for row in result] if result else []
    except Exception as e:
        logger.info("Failed to retrieve missing dates from the database.")
        return []


def get_uv_data(lat: float, lng: float, dt: datetime, logger):
    dt_local = datetime.combine(dt, datetime.min.time(
    ), tzinfo=ZoneInfo("Australia/Sydney")).replace(hour=12)
    headers = {"x-access-token": os.getenv("UV_API_KEY")}
    params = {
        "lat": lat,
        "lng": lng,
        "alt": 100,
        "dt": dt_local.astimezone(ZoneInfo("UTC")).strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    try:
        response = requests.get(BASE_URL, headers=headers,
                                params=params, timeout=10)
        response.raise_for_status()
        return [response.json()]
    except Exception as e:
        logger.log.warning(
            f"Failed to fetch UV data for ({lat}, {lng}, {dt}): {e}")
        return []




@dlt.source
def openuv_source(cities: list[dict], dates: list[datetime], logger):

    @dlt.resource(name="uv_index", write_disposition="merge", primary_key=["uv_time", "City"])
    def uv_resource():
        for dt in dates:
            for city_info in cities:
                logger.info(
                    f"Fetching UV for {city_info['city']} on {dt}")
                uv_data = get_uv_data(
                    city_info["lat"], city_info["lng"], dt, logger)
                for entry in uv_data:
                    yield {
                        "uv": entry["result"]["uv"],
                        "uv_max": entry["result"]["uv_max"],
                        "uv_time": entry["result"]["uv_time"],
                        "ozone": entry["result"]["ozone"],
                        "City": city_info["city"],
                        "location": {
                            "lat": city_info["lat"],
                            "lng": city_info["lng"]
                        },
                        "timestamp": datetime.now(ZoneInfo("Australia/Sydney")).isoformat()
                    }
    return uv_resource()



@task
def uv_task(logger) -> bool:
    """Loads UV data from OpenUV API using DLT."""
    logger.info("🚀 Starting DLT pipeline for OpenUV API")

    pipeline = dlt.pipeline(
        pipeline_name="openuv_pipeline",
        destination=os.environ.get("DLT_DESTINATION") or os.getenv("DLT_DESTINATION"),
        dataset_name="uv_data",
        dev_mode=False,
        pipelines_dir=str(DLT_PIPELINE_DIR)
    )

    try:
        missing_dates = get_dates(logger)
        source = openuv_source(cities, missing_dates, logger)
        pipeline.run(source)
        logger.info("✅ DLT pipeline completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to run DLT pipeline: {e}")
        return False




@task
def dbt_uv_data(logger, uv_task: bool) -> None:
    """Runs the dbt command after loading the data from UV API."""

    if not uv_task:
        logger.warning(
            "\n⚠️  WARNING: DBT SKIPPED\n"
            "📉 No data was loaded from UV API.\n"
            "🚫 Skipping dbt run.\n"
            "----------------------------------------"
        )
        return
    
    iscloudrun = write_profiles_yml(logger=logger)

    logger.info(f"DBT Project Directory: {DBT_DIR}")

    start = time.time()
    try:
        if iscloudrun:
            subprocess.run(
                "dbt deps",
                shell=True,
                cwd=DBT_DIR,
                capture_output=True,
                text=True,
                check=True
            )
            
        result = subprocess.run(
            "dbt build --select source:uv+",
            shell=True,
            cwd=DBT_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        duration = round(time.time() - start, 2)
        logger.info(f"dbt build completed in {duration}s")
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"dbt build failed:\n{e.stdout}\n{e.stderr}")
        raise
    finally:
        import sys
        sys.stdout.flush()
        sys.stderr.flush()





@flow(name="uv-flow")
def uv_flow():
    """
    Main flow to run the pipeline and dbt transformations.
    """
    logger = get_run_logger()
    logger.info("Starting the UV Flow...")

    # Run the DLT pipeline
    should_run = uv_task(logger=logger)

    # Run dbt transformations
    dbt_uv_data(logger, uv_task=should_run)


if __name__ == "__main__":
    os.environ["PREFECT_API_URL"] = ""
    uv_flow()