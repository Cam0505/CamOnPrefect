import os
from dlt.sources.helpers import requests as dlt_requests
from dotenv import load_dotenv
import dlt
import time
from prefect import flow, task, get_run_logger
from dlt.pipeline.exceptions import PipelineNeverRan
from dlt.destinations.exceptions import DatabaseUndefinedRelation
import json
from datetime import datetime, timedelta
from helper_functions import dbt_run_task, sanitize_filename, flow_summary
from path_config import get_project_root, set_dlt_env_vars

# Load environment variables and set DLT config
paths = get_project_root()
set_dlt_env_vars(paths)

DLT_PIPELINE_DIR = paths["DLT_PIPELINE_DIR"]
ENV_FILE = paths["ENV_FILE"]
REQUEST_CACHE_DIR = paths["REQUEST_CACHE_DIR"]

load_dotenv(dotenv_path=ENV_FILE)


API_KEY = os.getenv("BEVERAGE_API_KEY")
if not API_KEY:
    raise ValueError("Environment variable BEVERAGE_API_KEY is not set.")


TABLE_PARAMS = {
    "beverages": ("c=list", "strCategory"),
    "glasses": ("g=list", "strGlass"),
    "ingredients": ("i=list", "strIngredient1"),
    "alcoholic": ("a=list", "strAlcoholic")
}

DIMENSION_CONFIG = {
    "ingredients": {
        "sql_column": "strIngredient1",
        "query_param": "i",
        "source_key": "source_ingredient",
        "resource_name": "ingredients_table",
        "primary_key": ["id_drink", "source_ingredient"]
    },
    "alcoholic": {
        "sql_column": "strAlcoholic",
        "query_param": "a",
        "source_key": "source_alcohol_type",
        "resource_name": "alcoholic_table",
        "primary_key": ["id_drink"]
    },
    "beverages": {
        "sql_column": "strCategory",
        "query_param": "c",
        "source_key": "source_beverage_type",
        "resource_name": "beverages_table",
        "primary_key": ["id_drink"]
    },
    "glasses": {
        "sql_column": "strGlass",
        "query_param": "g",
        "source_key": "source_glass",
        "resource_name": "glass_table",
        "primary_key": ["id_drink"]
    }
}

# Would need to cache these in a Docker Image to work


def fetch_and_extract(table: str, logger) -> list:
    # Check if the cache directory exists, if not, create it
    REQUEST_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = REQUEST_CACHE_DIR / f"{table}.json"

    if table not in TABLE_PARAMS:
        raise ValueError(
            f"Unsupported table: {table}. Valid options: {list(TABLE_PARAMS.keys())}")
    param, field = TABLE_PARAMS[table]

    # Check if the cache file exists and is less than 74 hours old
    if cache_file.exists():
        logger.info(
            f"✅ Using cached response for table: {table} Param: {param} field: {field}")
        file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - file_mtime < timedelta(hours=72):
            with open(cache_file, "r") as f:
                data = json.load(f)
                for key, value in data.items():
                    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                        return [item.get(field) for item in value if field in item]

    url = f"https://www.thecocktaildb.com/api/json/v2/{API_KEY}/list.php?{param}"

    response = dlt_requests.get(url)
    response.raise_for_status()  # Raise exception on error
    data = response.json()

    # Cache the response
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)

    # Find the first key containing a list of dicts
    for key, value in data.items():
        if isinstance(value, list) and all(isinstance(item, dict) for item in value):
            return [item.get(field) for item in value if field in item]

    return []


def resource_dim_request_cache(resource, query_param, value, logger):
    REQUEST_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = REQUEST_CACHE_DIR / \
        f"{resource}_{query_param}_{sanitize_filename(value)}.json"

    # Check if the cache file exists and is less than 72 hours old
    if cache_file.exists():
        # logger.info(f"✅ Using cached response for {query_param}={sanitize_filename(value)}")
        file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - file_mtime < timedelta(hours=72):
            with open(cache_file, "r") as f:
                return json.load(f)
    else:
        logger.info(
            f"❌ No cache found for {query_param}={value}, fetching from API...")

    url = f"https://www.thecocktaildb.com/api/json/v2/{API_KEY}/filter.php?{query_param}={value}"

    try:
        response = dlt_requests.get(url)
        response.raise_for_status()  # Raise exception on error
        data = response.json()["drinks"]
    except Exception as e:
        logger.warning(
            f"❌ Failed to fetch drinks for value '{value}': {e}")
        return []

    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)

    return data


def create_dimension_resource(table_name, config, values, currentdbcount, logger):
    @dlt.resource(name=config["resource_name"], write_disposition="merge", primary_key=config["primary_key"])
    def resource_func():

        state = dlt.current.source_state().setdefault(config["resource_name"], {
            "processed_records": 0,
            "last_run_status": None
        })
        # if currentdbcount == state["processed_records"]:
        #     logger.info(
        #         f"🔁 SKIPPED LOAD for {config['resource_name']}:\n"
        #         f"📅 Previous: {state['processed_records']}\n"
        #         f"📦 Current: {currentdbcount}\n"
        #         f"⏳ No new data for {config['resource_name']}. Skipping..."
        #     )
        #     state["last_run_status"] = "skipped_no_new_data"
        #     return

        total_records = 0
        logger.info(
            f"Processing {len(values)} values for {config['resource_name']}...")
        for value in values:
            try:
                drinks = resource_dim_request_cache(
                    config['resource_name'], config['query_param'], value, logger)
            except Exception as e:
                logger.error(
                    f"❌ Failed to fetch drinks for {config['query_param']}={value}: {e}")
                continue

            if not drinks:
                logger.warning(
                    f"No drinks found for {config['query_param']}={value}")
                continue
            for drink in drinks:
                if isinstance(drink, dict):  # Ensure it's a dictionary
                    drink[config["source_key"]] = value
                    yield drink
                    total_records += 1

        # Check Previous State:
        previous_value = state.get("processed_records", 0)
        if total_records == previous_value and currentdbcount == previous_value:
            logger.info(
                f"🔁 SKIPPED LOAD for {config['resource_name']}:\n"
                f"📅 Previous: {previous_value}\n"
                f"📦 Current: {total_records}\n"
                f"⏳ No new data for {config['resource_name']}. Skipping..."
            )
            state["last_run_status"] = "skipped_no_new_data"
            return
        elif total_records == 0:
            logger.warning(
                f"⚠️ No data loaded for {config['resource_name']}. Marking as failed.")
            state["last_run_status"] = "failed"
        else:
            logger.info(
                f"✅ Loaded {total_records} records for {config['resource_name']}:\n"
                f"📅 Previous: {previous_value}\n"
                f"📦 Current: {total_records}\n"
                f"Database: {currentdbcount}\n"
                f"⏳ New data loaded for {config['resource_name']}."
            )
            state["processed_records"] = total_records
            state["last_run_status"] = "success"

    return resource_func


@dlt.source
def dimension_data_source(logger, row_counts_dict: dict):

    for table_name, config in DIMENSION_CONFIG.items():
        logger.info(f"Creating resource: {table_name}")
        values = fetch_and_extract(table_name, logger)
        yield create_dimension_resource(table_name, config, values, row_counts_dict.get(config['resource_name'], 0), logger)


@task
def dimension_data(logger) -> bool:

    logger.info("Starting DLT pipeline...")
    pipeline = dlt.pipeline(
        pipeline_name="beverage_pipeline",
        destination=os.environ.get(
            "DLT_DESTINATION") or os.getenv("DLT_DESTINATION"),
        dataset_name="beverage_data",
        pipelines_dir=str(DLT_PIPELINE_DIR),
        dev_mode=False
    )

    try:
        row_counts = pipeline.dataset().row_counts().df()
        logger.info(
            f"📊 Row counts for existing tables: {row_counts}")
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
        logger.info(f"Row counts: {row_counts_dict}")
    else:
        logger.warning(
            "⚠️ No tables found yet in dataset — assuming first run.")
        row_counts_dict = {}

    source = dimension_data_source(logger, row_counts_dict)
    # run pipeline
    try:
        load_info = pipeline.run(source)
        logger.info("Beverage State:\n" +
                    json.dumps(source.state, indent=2))
        statuses = [source.state.get(config["resource_name"], {}).get(
            'last_run_status', None) for config in DIMENSION_CONFIG.values()]
        logger.info(f"Resource Statuses: {statuses}")
        logger.info(f"Pipeline Load Info: {load_info}")

        if any(s == "success" for s in statuses):
            logger.info(f"Pipeline Load Info: {load_info}")
            return True
        elif all(s == "skipped_no_new_data" for s in statuses):
            return False
        else:
            logger.error(
                "💥  Pipeline Failures — check Logic, API or network.")
            return False
    except Exception as e:
        logger.error(f"❌ Pipeline run failed: {e}")
        return False


@task
def beverage_fact_data(logger, dimension_data: bool) -> bool:
    # return False
    if not dimension_data:
        logger.warning(
            "\n⚠️  WARNING: dimension_data SKIPPED\n"
            "📉 No data was loaded from dimension_data.\n"
            "🚫 Skipping beverage_fact_data run.\n"
            "----------------------------------------"
        )
        return False

    @dlt.resource(name="consumption", write_disposition="append")
    def beverages_api():

        url = f"https://www.thecocktaildb.com/api/json/v2/{API_KEY}/randomselection.php"

        for i in range(5):
            try:
                response = dlt_requests.get(url, timeout=10)
                response.raise_for_status()
                drinks = response.json().get("drinks", [])

                if not drinks:
                    logger.warning(
                        f"No drinks returned in iteration {i+1}")
                    continue

                yield drinks

                time.sleep(0.2)  # Prevent throttling
            except dlt_requests.RequestException as e:
                logger.error(
                    f"Request failed on iteration {i+1}: {e}", exc_info=True)
            except Exception as e:
                logger.error(
                    f"Unexpected error on iteration {i+1}: {e}", exc_info=True)

    @dlt.source
    def alcoholic_beverages():
        return beverages_api()

    try:
        pipeline = dlt.pipeline(
            pipeline_name="beverage_pipeline",
            destination=os.getenv("DLT_DESTINATION", "duckdb"),
            dataset_name="beverage_data",
            pipelines_dir=str(DLT_PIPELINE_DIR),
            dev_mode=False
        )

        load_info = pipeline.run(alcoholic_beverages())
        logger.info(f"DLT pipeline run complete: {load_info}")
        return bool(load_info)

    except Exception as e:
        logger.error("DLT pipeline run failed", exc_info=True)
        raise


@flow(name="beverages-flow", on_completion=[flow_summary], on_failure=[flow_summary])
def beverages_flow():
    """Main flow to load data from Beverages API and run dbt models."""
    logger = get_run_logger()
    logger.info("🚀 Starting Beverages flow")

    try:
        # Load data from Beverages API
        beverages_task_result = dimension_data(logger)

        # Load fact data
        beverage_fact_result = beverage_fact_data(
            logger, beverages_task_result)

        # Run dbt models
        return dbt_run_task(logger, dbt_trigger=beverage_fact_result, select_target="source:beverages+")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    # os.environ["PREFECT_API_URL"] = ""
    beverages_flow()
