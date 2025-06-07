import os
from dotenv import load_dotenv
import dlt
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator
from dlt.sources.helpers.rest_client.client import RESTClient
from dlt.sources.helpers import requests
from prefect import flow, task, get_run_logger
from dlt.pipeline.exceptions import PipelineNeverRan
from dlt.destinations.exceptions import DatabaseUndefinedRelation
from helper_functions import dbt_run_task, flow_summary
from path_config import get_project_root, set_dlt_env_vars

# Load environment variables and set DLT config
paths = get_project_root()
set_dlt_env_vars(paths)

DLT_PIPELINE_DIR = paths["DLT_PIPELINE_DIR"]
ENV_FILE = paths["ENV_FILE"]
DBT_DIR = paths["DBT_DIR"]

# load_dotenv(ENV_FILE)

BASE_URL = "https://api.fbi.gov/wanted/v1/list"
PAGE_LIMIT = 50


def get_total_count(base_url, timeout=10):
    response = requests.get(base_url, timeout=timeout)
    response.raise_for_status()
    return int(response.json().get("total", 0))


@dlt.resource(name="wanted", write_disposition="merge", primary_key="uid", table_name="wanted")
def wanted(logger, db_count: int):
    state = dlt.current.source_state().setdefault("wanted", {
        # we will store tuples like f"{uid}|{status}"
        "seen_keys": [],
        'last_run_Status': None
    })
    # logger.info(f"Current state: {len(state.get('seen_keys', []))}")
    seen_keys = set(state.setdefault("seen_keys", []))
    state["seen_keys"] = list(seen_keys)  # Testing
    # logger.info(f"Current state after deduplication: {len(state.get('seen_keys', []))}")
    new_keys = set()

    count = get_total_count(BASE_URL)
    max_pages = (count + PAGE_LIMIT - 1) // PAGE_LIMIT

    client = RESTClient(
        base_url=BASE_URL,
        paginator=PageNumberPaginator(
            base_page=1,
            page_param="page",
            page=1,
            total_path=None,
            stop_after_empty_page=True,
            maximum_page=max_pages
        ),
        data_selector="items",
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
        }
    )
    try:
        for page in client.paginate(data_selector="items"):
            for item in page:
                # Prevents repeatedly processing the same item while allowing for updates of dbt snapshot columns
                # Status and Poster Classification
                key = f"{item['uid']}|{item.get('status', '').lower()}|{item.get('poster_classification', '').lower()}"
                if key in seen_keys and db_count != 0:
                    # logger.info(f"Skipping seen key: {key}")
                    continue
                logger.info(f"Processing new key: {key}")
                new_keys.add(key)
                yield item
        # Ok lets troubleshoot why it's not working by seeing all keys

        if new_keys:
            # update persistent state with new keys
            state["seen_keys"] = list(seen_keys.union(new_keys))
            state["last_run_Status"] = "success"
        else:
            state["last_run_Status"] = "skipped"
    except Exception as e:
        logger.error(f"❌ Error during resource extraction: {e}")
        state["last_run_Status"] = "failed"
    return


@dlt.source(name="fbi_wanted")
def fbi_wanted_source(logger, db_count):
    return wanted(logger=logger, db_count=db_count)


@task
def run_dlt_pipeline(logger):

    pipeline = dlt.pipeline(
        pipeline_name="fbi_wanted_pipeline",
        destination=os.environ.get(
            "DLT_DESTINATION") or os.getenv("DLT_DESTINATION"),
        dataset_name="fbi_data",
        dev_mode=False,
        pipelines_dir=str(DLT_PIPELINE_DIR)
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
    else:
        logger.warning(
            "⚠️ No tables found yet in dataset — assuming first run.")
        row_counts_dict = {}

    source = fbi_wanted_source(
        logger, db_count=row_counts_dict.get('wanted', -1))

    try:
        pipeline.run(source)
        run_status = source.state.get('wanted', {}).get('last_run_Status', [])
        if run_status == "skipped":
            logger.info(
                "⏭️ All resources skipped — no data loaded.")
            return False
        elif run_status == "success":
            logger.info(
                f"✅ New data to merge — {len(source.state['wanted']['seen_keys'])} new keys found.")
            return True
        else:
            logger.info(
                f"❌ DLT pipeline run failed with status: {run_status}")
            return False
    except Exception as e:
        logger.error(f"❌ Pipeline run failed: {e}")
        return False


@flow(name="fbi_flow", on_completion=[flow_summary], on_failure=[flow_summary])
def fbi_flow():
    logger = get_run_logger()
    pipeline_outcome = run_dlt_pipeline(logger=logger)

    return dbt_run_task(logger, dbt_trigger=pipeline_outcome, select_target="source:fbi+")


if __name__ == "__main__":
    fbi_flow()
