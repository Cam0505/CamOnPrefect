from path_config import get_project_root, set_dlt_env_vars
from helper_functions import dbt_run_task, flow_summary
from dlt.destinations.exceptions import DatabaseUndefinedRelation
import os
from dotenv import load_dotenv
import dlt
import json
from dlt.sources.helpers.requests import get
from prefect import flow, task, get_run_logger
from dlt.pipeline.exceptions import PipelineNeverRan
from helper_functions import dbt_run_task, flow_summary
from path_config import get_project_root, set_dlt_env_vars

# Load environment variables and set DLT config
paths = get_project_root()
set_dlt_env_vars(paths)

DLT_PIPELINE_DIR = paths["DLT_PIPELINE_DIR"]
ENV_FILE = paths["ENV_FILE"]
DBT_DIR = paths["DBT_DIR"]

load_dotenv(dotenv_path=ENV_FILE)
COUNTRIES = ["NZ", "AU", "GB", "CA"]


@dlt.source
def geo_source(logger, row_counts_dict: dict):
    @dlt.resource(name="geo_cities", write_disposition="merge", primary_key="city_id")
    def cities():
        # Initialize state at the start of each run
        state = dlt.current.source_state().setdefault("geo_cities", {
            "processed_records": {},
            "country_status": {}
        })

        # context.log.info(f"Current state at the beginning of the run: {state}")

        # API credentials and URL for GeoNames
        USERNAME = os.getenv("GEONAMES_USERNAME")
        if not USERNAME:
            raise ValueError("Missing GEONAMES_USERNAME in environment.")

        BASE_URL = "http://api.geonames.org/citiesJSON"
        DETAILS_URL = "http://api.geonames.org/getJSON"

        def fetch_city_details(geoname_id):
            params = {
                "geonameId": geoname_id,
                "username": USERNAME
            }
            return get(DETAILS_URL, params=params).json()

        def fetch_cities(country_code):
            max_rows = 100
            total_fetched = 0

            logger.info(f"Starting fetch for country: {country_code}")

            params = {
                "formatted": "true",
                "lat": "0",
                "lng": "0",
                "maxRows": max_rows,
                "lang": "en",
                "username": USERNAME
            }

            # Country-specific bounding boxes
            bboxes = {
                "AU": {"north": "-10.0", "south": "-44.0", "east": "155.0", "west": "112.0"},
                "NZ": {"north": "-33.0", "south": "-47.0", "east": "180.0", "west": "166.0"},
                "GB": {"north": "60.0", "south": "49.0", "east": "1.0", "west": "-8.0"},
                "CA": {"north": "83.0", "south": "42.0", "east": "-52.0", "west": "-140.0"}
            }

            if country_code in bboxes:
                params.update(bboxes[country_code])
            try:
                # logger.info(f"Fetching cities for {country_code} with params: {params}")
                cities_data = get(BASE_URL, params=params).json().get(
                    "geonames", [])
                # logger.info(
                #     f"Fetched {cities_data} cities for {country_code}")
            except Exception as e:
                logger.error(
                    f"Failed to fetch cities for {country_code}: {e}")
                state["country_status"][country_code] = "failed"
                raise
            database_rowcount = row_counts_dict.get(country_code, 0)

            current_count = len(cities_data)

            previous_count = state["processed_records"].get(country_code, 0)

            if database_rowcount < previous_count or database_rowcount == 0:
                logger.info(
                    f"⚠️ GeoAPI data for `{country_code}` row count dropped from {previous_count} to {database_rowcount}. Forcing reload.")
                state["country_status"][country_code] = "database_row_count"
            elif (current_count == previous_count):
                logger.info(f"\n🔁 SKIPPED LOAD:\n"
                            f"📅 Previous Run for {country_code}: {previous_count}\n"
                            f"📦 API Cities for {country_code}: {current_count}\n"
                            f"⏳ No new data for {country_code}. Skipping... \n"
                            f"{'-'*45}")
                state["country_status"][country_code] = "skipped_no_new_data"
                return

            for city in cities_data:
                total_fetched += 1
                details = fetch_city_details(city.get("geonameId")) or {}

                yield {
                    "city_id": city.get("geonameId"),
                    "city": city.get("name"),
                    "latitude": city.get("lat"),
                    "longitude": city.get("lng"),
                    "country": details.get("countryName") or city.get("countryName"),
                    "country_code": country_code,
                    "region": details.get("adminName1"),
                    "region_code": details.get("adminCode1"),
                    "continent": details.get("continentCode")
                }

            # Update the state with the number of records processed in this run
            state["processed_records"][country_code] = total_fetched
            state["country_status"][country_code] = "success"
            logger.info(
                f"Total cities fetched for {country_code}: {total_fetched}")

        try:
            for country in COUNTRIES:
                try:
                    yield from fetch_cities(country)
                except Exception as e:
                    logger.error(
                        f"Error while processing country {country}: {e}")
                    raise
            logger.info(f"Current state after successful run: {state}")
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
    return cities


@task
def get_geo_data(logger) -> bool:

    logger.info("Starting DLT pipeline...")
    pipeline = dlt.pipeline(
        pipeline_name="geo_cities_pipeline",
        destination=os.getenv("DLT_DESTINATION"),
        dataset_name="geo_data",
        pipelines_dir=str(DLT_PIPELINE_DIR),
        dev_mode=False
    )
    row_counts = None
    try:
        dataset = pipeline.dataset()["geo_cities"].df()
        if dataset is not None:
            row_counts = dataset.groupby(
                "country_code").size().reset_index(name="count")
            logger.info(f"Grouped Row Counts:\n{row_counts}")
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
            zip(row_counts["country_code"], row_counts["count"]))
    else:
        logger.warning(
            "⚠️ No tables found yet in dataset — assuming first run.")
        row_counts_dict = {}

    source = geo_source(logger, row_counts_dict)
    try:
        load_info = pipeline.run(source)

        outcome_data = source.state.get(
            'geo_cities', {}).get("country_status", {})

        logger.info("Country Status:\n" +
                    json.dumps(outcome_data, indent=2))

        statuses = [outcome_data.get(resource, 0) for resource in COUNTRIES]

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


@flow(name="geo-flow", on_completion=[flow_summary], on_failure=[flow_summary])
def Geo_Flow():
    """
    Main flow to run the pipeline and dbt transformations.
    """
    logger = get_run_logger()

    # Run the DLT pipeline
    should_run = get_geo_data(logger=logger)

    # Run dbt transformations
    return dbt_run_task(logger, dbt_trigger=should_run, select_target="source:geo+")


if __name__ == "__main__":
    os.environ["PREFECT_API_URL"] = ""
    Geo_Flow()
