import os
from typing import Iterator, Dict, List
from prefect import flow, task, get_run_logger
from datetime import datetime, timedelta
from dlt.pipeline.exceptions import PipelineNeverRan
import dlt
import json
from dlt.sources.helpers import requests
from path_config import DBT_DIR, ENV_FILE, REQUEST_CACHE_DIR, DLT_PIPELINE_DIR
from helper_functions import write_profiles_yml, sanitize_filename
from dlt.destinations.exceptions import DatabaseUndefinedRelation

# Constants
API_BASE_URL = "http://universities.hipolabs.com/search"
CACHE_EXPIRY_HOURS = 72

ALL_COUNTRIES = [
    # "United States", 
    "Canada", "Australia", "New Zealand", "United Kingdom"
    # , "Germany", "France", "Italy",
    # "Spain", "Mexico", "China", "Japan", "South Korea",
    # "Russia", "Netherlands", "Sweden", "Norway", "Finland"
]



def fetch_and_cache_universities(country: str, logger) -> List[Dict]:
    REQUEST_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(f"Universities_{country}") + ".json"
    cache_file = REQUEST_CACHE_DIR / filename

    if cache_file.exists():
        file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - file_mtime < timedelta(hours=CACHE_EXPIRY_HOURS):
            logger.info(f"✅ Using cached response for {country}")
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)

    logger.info(f"🌍 Fetching universities for {country}")
    response = requests.get(API_BASE_URL, params={"country": country})
    response.raise_for_status()
    data = response.json()

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        logger.warning(f"⚠️ Cache for {country} is corrupted. Refetching...")

    return data


@dlt.source(name="university_domains")
def university_source(logger):
    @dlt.resource(name="universities", write_disposition="replace")
    def universities_resource(countries: List[str] = ALL_COUNTRIES) -> Iterator[List[Dict]]:
    
        state = dlt.current.source_state().setdefault("universities", {
            "processed_records": 0,
            "last_run_status": None,
            "failed_countries": []
        })
        state["failed_countries"] = []

        total_processed = 0
        any_success = False

        for country in countries:
            logger.info(f"🔍 Processing universities for {country}")
            try:
                universities = fetch_and_cache_universities(country, logger)
                logger.info(f"✅ Found {len(universities)} universities in {country}")
                if universities:
                    yield universities  # yield list of dicts as one resource
                    total_processed += len(universities)
                    any_success = True
                    logger.info(f"✅ Successfully processed {len(universities)} universities for {country}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch universities for {country}: {str(e)}")
                state["failed_countries"].append(country)

        state["processed_records"] += total_processed
        state["last_run_status"] = "success" if any_success else "failed"
        if not any_success:
            logger.warning("🚫 No data yielded — all countries failed.")
            return
        logger.info(f"✅ {total_processed} records processed. ❌ Failed countries: {state['failed_countries']}")
    return universities_resource



@task
def university_task(logger) -> bool:
    pipeline = dlt.pipeline(
        pipeline_name="universities_pipeline",
        destination=os.environ.get("DLT_DESTINATION") or os.getenv("DLT_DESTINATION"),
        pipelines_dir=str(DLT_PIPELINE_DIR),
        dev_mode=False
    )
    try:
        row_counts = pipeline.dataset().row_counts().df()
    except PipelineNeverRan:
        logger.warning(
            "⚠️ No previous runs found for this pipeline. Assuming first run.")
        row_counts = None
    except DatabaseUndefinedRelation:
        logger.warning(
            "⚠️ Table Doesn't Exist. Assuming truncation.")
        row_counts = None

    if row_counts is not None:
        row_counts_dict = dict(
            zip(row_counts["table_name"], row_counts["row_count"]))
    else:
        logger.warning(
            "⚠️ No tables found yet in dataset — assuming first run.")
        row_counts_dict = {}

    logger.info(f"Row counts: {row_counts_dict}")
    source = university_source(logger)

    try:
        pipeline.run(source)
        logger.info(f"Source state: {source.state}")
        return True
    except Exception as e:
        logger.error(f"❌ Pipeline run failed: {e}")
        return False


@flow(name="university-flow")
def university_flow():
    """Main flow to load data from University API and run dbt models."""
    logger = get_run_logger()
    logger.info("🚀 Starting University flow")

    try:
        # Load data from University API
        university_asset_result = university_task(logger)

        # Run dbt models
        # dbt_university_data(logger, university_asset_result)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    os.environ["PREFECT_API_URL"] = ""
    university_flow()