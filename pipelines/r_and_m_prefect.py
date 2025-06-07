
import os
from dotenv import load_dotenv
from prefect import flow, task, get_run_logger
import dlt
from dlt.sources.helpers.rest_client.paginators import JSONLinkPaginator
from dlt.sources.helpers.rest_client.client import RESTClient
from dlt.pipeline.exceptions import PipelineNeverRan
from helper_functions import flow_summary, dbt_run_task
from path_config import get_project_root, set_dlt_env_vars

# Load environment variables and set DLT config
paths = get_project_root()
set_dlt_env_vars(paths)

DLT_PIPELINE_DIR = paths["DLT_PIPELINE_DIR"]
ENV_FILE = paths["ENV_FILE"]
DBT_DIR = paths["DBT_DIR"]

load_dotenv(dotenv_path="/workspaces/CamOnPrefect/.env")


BASE_URL = "https://rickandmortyapi.com/api"

# Configuration for resources: endpoint -> primary key
RESOURCE_CONFIG: dict[str, str] = {
    "character": "id",
    "episode": "id",
    "location": "id"
}


def make_resource(table_name: str, primary_key: str, existing_count: int):

    @dlt.resource(name=table_name, write_disposition="merge", primary_key=primary_key)
    def _resource(logger):
        state = dlt.current.source_state().setdefault(table_name, {
            "count": 0,
            "last_run_status": None
        })

        client = RESTClient(
            base_url=f"{BASE_URL}/",
            paginator=JSONLinkPaginator(
                next_url_path="info.next"
            )
        )

        # Only fetch first page to check count
        try:
            response = client.session.get(
                f"{BASE_URL}/{table_name}", timeout=15)
            response.raise_for_status()
            first_page = response.json()
            info = first_page.get("info", {})
            new_count = info.get("count", 0)
        except Exception as e:
            logger.error(
                f"❌ Failed to fetch API count for `{table_name}`: {e}")
            state["last_run_status"] = "failed"
            raise

        if existing_count < state["count"]:
            logger.info(
                f"⚠️ Table `{table_name}` row count dropped from {state['count']} to {existing_count}. Forcing reload.")
        elif new_count == state["count"]:
            logger.info(f"🔁 SKIPPED LOAD: `{table_name}` — No new data.")
            state["last_run_status"] = "skipped_no_new_data"
            return

        logger.info(
            f"✅ New data for `{table_name}`: {state['count']} ➝ {new_count}")

        state["count"] = new_count
        state["last_run_status"] = "success"
        logger.info(
            f"📊 Loading `{table_name}` data from Rick and Morty API...")
        for page in client.paginate(table_name):
            yield page

    return _resource


@dlt.source
def rick_and_morty_source(logger, current_counts):
    for endpoint, primary_key in RESOURCE_CONFIG.items():
        yield make_resource(endpoint, primary_key, current_counts.get(endpoint, 0))(logger)


@task
def rick_and_morty_task(logger) -> bool:
    """Loads characters, episodes, and locations from Rick and Morty API using DLT."""
    logger.info("🚀 Starting DLT pipeline for Rick and Morty API")

    pipeline = dlt.pipeline(
        pipeline_name="rick_and_morty_pipeline",
        destination=os.getenv("DLT_DESTINATION", "duckdb"),
        dataset_name="rick_and_morty_data",
        dev_mode=False,
        pipelines_dir=str(DLT_PIPELINE_DIR)
    )
    try:
        row_counts = pipeline.dataset().row_counts().df()
    except PipelineNeverRan:
        logger.warning(
            "⚠️ No previous runs found for this pipeline. Assuming first run.")
        row_counts = None

    if row_counts is not None:
        row_counts_dict = dict(
            zip(row_counts["table_name"], row_counts["row_count"]))
    else:
        logger.warning(
            "⚠️ No tables found yet in dataset — assuming first run.")
        row_counts_dict = {}

    source = rick_and_morty_source(logger, row_counts_dict)
    try:
        pipeline.run(source)

        statuses = [source.state.get(resource, {}).get(
            "last_run_status") for resource in RESOURCE_CONFIG.keys()]

        if all(s == "skipped_no_new_data" for s in statuses):
            logger.info(
                "⏭️ All resources skipped — no data loaded.")
            return False
        elif all(s == "failed" for s in statuses):
            logger.error(
                "💥 All resources failed to load — check API or network.")
            return False

        loaded_count = sum(1 for s in statuses if s == "success")
        logger.info(f"✅ Number of resources loaded: {loaded_count}")

        return True
    except Exception as e:
        logger.error(f"❌ Pipeline run failed: {e}")
        return False


@flow(name="rick-and-morty-flow", on_completion=[flow_summary], on_failure=[flow_summary])
def rick_and_morty_flow():
    """Main flow to load data from Rick and Morty API and run dbt models."""
    logger = get_run_logger()
    logger.info("🚀 Starting Rick and Morty flow")

    try:
        # Load data from Rick and Morty API
        rick_and_morty_asset_result = rick_and_morty_task(logger)

        # Run dbt models
        return dbt_run_task(logger, dbt_trigger=rick_and_morty_asset_result, select_target="source:rick_and_morty+")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    rick_and_morty_flow()
