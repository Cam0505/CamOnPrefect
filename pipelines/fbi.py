import os
from dotenv import load_dotenv
import dlt
import json
import dlt
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator
from dlt.sources.helpers.rest_client.client import RESTClient
from prefect import flow, task, get_run_logger
from dlt.pipeline.exceptions import PipelineNeverRan

load_dotenv(dotenv_path="/workspaces/CamOnPrefect/.env")


BASE_URL = "https://api.fbi.gov/"
ENDPOINT = "/wanted/v1/list"



@dlt.resource(name="wanted", write_disposition="merge", primary_key="uid", table_name="wanted")
def wanted(logger):
    state = dlt.current.source_state().setdefault("wanted", {
            "uid": []
        })
    seen_uids = set(state["uid"])
    new_uids = set()

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

    for page in client.paginate(ENDPOINT):
        for item in page:
            if item["uid"] in seen_uids:
                # Debugging log for skipped items
                # logger.info(f"SKIPPED LOAD: `{item['uid']}` — Already exists.")
                continue  # skip duplicates (already processed)
            new_uids.add(item["uid"])  # new uid found, add to batch
            yield item  # send item downstream

    # After all pages:
    if new_uids:
        state["uid"].extend(list(new_uids))  # update persistent state with new uids
    return

@dlt.source(name="fbi_wanted")
def fbi_wanted_source(logger):
    return wanted(logger=logger)




@task
def run_dlt_pipeline(logger):
    pipeline = dlt.pipeline(
        pipeline_name="fbi_wanted_pipeline",
        destination=os.getenv("DLT_DESTINATION", "duckdb"),
        dataset_name="fbi_data"
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

    logger.info(f"Row counts: {row_counts_dict}")   

    source = fbi_wanted_source(logger)

    try:
        pipeline.run(source)
        current_id = len(source.state.get('wanted', {}).get('uid', []))
        logger.info(f"Current State Length: {current_id}")
        if current_id == row_counts_dict['wanted']:
            logger.info(
                "⏭️ All resources skipped — no data loaded.")
            return False
        elif current_id > row_counts_dict['wanted']:
            logger.info(
                f"✅ New data for `wanted`: {row_counts_dict['wanted']} ➝ {current_id}")
            return True
        else:
            logger.info(
                f"❌ DLT State Reset, DB Count: {row_counts_dict['wanted']} ➝ State Count: {current_id}")
            return True
    except Exception as e:
        logger.error(f"❌ Pipeline run failed: {e}")
        return False

@flow(name="FBI Wanted Pipeline")
def fbi_prefect_flow():
    run_dlt_pipeline(logger=get_run_logger())

if __name__ == "__main__":
    os.environ["PREFECT_API_URL"] = ""
    fbi_prefect_flow()