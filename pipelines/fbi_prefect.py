import os
from dotenv import load_dotenv
import dlt
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator
from dlt.sources.helpers.rest_client.client import RESTClient
from prefect import flow, task, get_run_logger
from dlt.pipeline.exceptions import PipelineNeverRan
from dlt.destinations.exceptions import DatabaseUndefinedRelation
import subprocess
import time
from path_config import DBT_DIR, ENV_FILE, DLT_PIPELINE_DIR

# load_dotenv(ENV_FILE)

BASE_URL = "https://api.fbi.gov/"
ENDPOINT = "/wanted/v1/list"


def write_profiles_yml(logger) -> bool:
    """Write dbt/profiles.yml from the DBT_PROFILES_YML environment variable, only in Prefect Cloud."""
    profiles_content = os.environ.get("DBT_PROFILES_YML")
    logger.info(f"DBT_PROFILES_YML content: {profiles_content}")
    if profiles_content:
        dbt_dir = os.path.join(os.getcwd(), "dbt")
        os.makedirs(dbt_dir, exist_ok=True)
        profiles_path = os.path.join(dbt_dir, "profiles.yml")
        with open(profiles_path, "w") as f:
            f.write(profiles_content)
        logger.info(f"Wrote profiles.yml to: {profiles_path}")
        return True
    else:
        logger.info("DBT_PROFILES_YML not set; not overwriting local profiles.yml")
        return False



@dlt.resource(name="wanted", write_disposition="merge", primary_key="uid", table_name="wanted")
def wanted(logger, db_count: int):
    state = dlt.current.source_state().setdefault("wanted", {
                # we will store tuples like f"{uid}|{status}"
        "seen_keys": [],
        'last_run_Status': None
    })
    # logger.info(f"Current state: {len(state.get('seen_keys', []))}")
    seen_keys = set(state.setdefault("seen_keys", []))
    state["seen_keys"] = list(seen_keys) # Testing
    # logger.info(f"Current state after deduplication: {len(state.get('seen_keys', []))}")
    new_keys = set()


    client = RESTClient(
        base_url=BASE_URL,
        paginator=PageNumberPaginator(
            page_param="page", 
            page=1, 
            maximum_page=5,
            stop_after_empty_page=True
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
        for page in client.paginate(ENDPOINT):
            for item in page:
                # Prevents repeatedly processing the same item while allowing for updates of dbt snapshot columns
                # Status and Poster Classification
                key = f"{item['uid']}|{item.get('status', '').lower()}|{item.get('poster_classification', '').lower()}"
                if key in seen_keys and db_count != 0:
                    logger.info(f"Skipping seen key: {key}")
                    continue
                logger.info(f"Processing new key: {key}")
                new_keys.add(key)
                yield item
        # Ok lets troubleshoot why it's not working by seeing all keys
        
        if new_keys:
            state["seen_keys"] = list(seen_keys.union(new_keys))  # update persistent state with new keys
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
        destination=os.environ.get("DLT_DESTINATION") or os.getenv("DLT_DESTINATION"),
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


    source = fbi_wanted_source(logger, db_count=row_counts_dict.get('wanted', -1))

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



@task
def dbt_fbi(logger, run_dlt_pipeline: bool) -> None:
    """Runs dbt models for FBI data after loading data."""

    if not run_dlt_pipeline:
        logger.warning(
            "\n⚠️  WARNING: DBT SKIPPED\n"
            "📉 No data was loaded from Rick and Morty API.\n"
            "🚫 Skipping dbt run.\n"
        )
        return
    
    iscloudrun = write_profiles_yml(logger=logger)

    logger.info(f"📁 DBT Project Directory: {DBT_DIR}")

    try:
        start = time.time()
        if iscloudrun:
            subprocess.run(
                "dbt deps",
                shell=True,
                cwd=DBT_DIR,
                capture_output=True,
                text=True,
                check=True
            )

        subprocess.run(
            "dbt build --select source:fbi+ --profiles-dir .",
            shell=True,
            cwd=DBT_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        duration = round(time.time() - start, 2)
        logger.info(f"✅ dbt build completed in {duration}s")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ dbt build failed:\n{e.stdout}\n{e.stderr}")
        raise



@flow(name="fbi_flow")
def fbi_flow():
    logger = get_run_logger()
    pipeline_outcome = run_dlt_pipeline(logger=logger)

    dbt_fbi(run_dlt_pipeline=pipeline_outcome, logger=logger)


if __name__ == "__main__":
    # os.environ["PREFECT_API_URL"] = ""
    fbi_flow()