import os
from prefect import flow, task, get_run_logger
from dlt.pipeline.exceptions import PipelineNeverRan
import dlt
import json
import subprocess
import time
from dlt.sources.helpers import requests
from typing import Iterator, Dict
from path_config import DBT_DIR, ENV_FILE, REQUEST_CACHE_DIR, DLT_PIPELINE_DIR
from helper_functions import write_profiles_yml, sanitize_filename, flow_summary
from dlt.destinations.exceptions import DatabaseUndefinedRelation
from dlt.sources.helpers.rest_client.client import RESTClient
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator

BASE_URL = "https://openlibrary.org/search.json"

# Define your search terms and topics
SEARCH_TOPICS = [
    "Python",
    "Apache Airflow",
    "Data Engineering",
    "Data Warehousing",
    "SQL",
    "Dbt",
    "JavaScript",
]

PAGE_LIMIT = 100  # Number of results per page


@dlt.source
def openlibrary_dim_source(logger, current_table):

    @dlt.resource(name="books", write_disposition="merge", primary_key="key")
    def resource_func():
        state = dlt.current.source_state().setdefault("books", {
            "count": {},
            "last_run_status": {}
        })

        for term in SEARCH_TOPICS:

            if current_table is None:
                current_table_count = 0
            else:
                current_table_count = current_table.get(term, 0)
            logger.info(
                f"📊 Current table count for '{term}': {current_table_count}")
            try:

                initial_response = requests.get(
                    BASE_URL, params={"q": term, "limit": PAGE_LIMIT}, timeout=15)
                initial_response.raise_for_status()
                count = initial_response.json().get("numFound", 0)

                # Step 2: Calculate max pages
                max_pages = (count + PAGE_LIMIT - 1) // PAGE_LIMIT

                previous_count = state["count"].get(term, 0)

                if previous_count < count:
                    logger.info(
                        f"⚠️ Detected more data from API ({count})"
                        f" than previous count ({previous_count}). Forcing reload."
                    )
                    # Need to fix this, to tired, merge is preventing duplicate rows
                elif current_table_count > 0 and count == previous_count:
                    logger.info(
                        f"🔁 SKIPPED LOAD for {term}:\n"
                        f"📊 Current table count: {current_table_count}\n"
                        f"📅 Previous filtered count: {previous_count}\n"
                        f"📦 Current filtered count: {count}\n"
                        f"⏳ No new data. Skipping..."
                    )
                    state["last_run_status"][term] = "skipped_no_new_data"
                    continue

                client = RESTClient(
                    base_url="https://openlibrary.org/search.json?",
                    paginator=PageNumberPaginator(
                        base_page=1,
                        page=1,
                        total_path=None,
                        page_param="page",
                        stop_after_empty_page=True,
                        maximum_page=max_pages,
                    ), data_selector="docs"
                )

                logger.info(
                    f"📚 Loading paginated data for '{term}' ({current_table_count} ➝ {count})")

                for page in client.paginate(params={"q": term, "limit": 100}, data_selector="docs"):
                    for doc in page.response.json()["docs"]:
                        # Main Table
                        yield {
                            "search_term": term,
                            "key": doc.get("key"),
                            "title": doc.get("title"),
                            "ebook_access": doc.get("ebook_access"),
                            "first_publish_year": doc.get("first_publish_year"),
                            "has_fulltext": doc.get("has_fulltext", False),
                            "authors": [{"name": a} for a in doc.get("author_name", [])],
                            "languages": [{"code": l} for l in doc.get("language", [])]
                        }

                state["count"][term] = count
                state["last_run_status"][term] = "success"

            except Exception as e:
                logger.error(f"❌ Fetch failed for '{term}': {e}")
                state["last_run_status"][term] = "failed"
                return

    return resource_func


@task
def openlibrary_books_task(logger) -> bool:

    logger.info("Starting DLT pipeline...")
    pipeline = dlt.pipeline(
        pipeline_name="openlibrary_incremental",
        destination=os.environ.get(
            "DLT_DESTINATION") or os.getenv("DLT_DESTINATION"),
        pipelines_dir=str(DLT_PIPELINE_DIR),
        dataset_name="openlibrary_data"
    )

    try:
        dataset = pipeline.dataset()["books"].df()
        if dataset is not None:
            row_count = dataset.groupby("search_term").size().to_dict()
            logger.info(f"Grouped Row Counts:\n{row_count}")
    except PipelineNeverRan:
        logger.warning(
            "⚠️ No previous runs found for this pipeline. Assuming first run.")
        row_count = None
    except DatabaseUndefinedRelation:
        logger.warning(
            "⚠️ Table Doesn't Exist. Assuming truncation.")
        row_count = None

    source = openlibrary_dim_source(logger, row_count)

    try:
        load_info = pipeline.run(source)

        statuses = [source.state.get("books", {}).get(
            "last_run_status", {}).get(term, '') for term in SEARCH_TOPICS]

        if all(s == "skipped_no_new_data" for s in statuses):
            logger.info(
                "⏭️ All resources skipped or failed — no data loaded.")
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


@task
def dbt_openlibrary_data(logger, openlibrary_books_asset: bool) -> subprocess.CompletedProcess:
    """Runs the dbt command after loading the data from Geo API."""

    if not openlibrary_books_asset:
        logger.warning(
            "\n⚠️  WARNING: DBT SKIPPED\n"
            "📉 No data was loaded from OpenLibrary API.\n"
            "🚫 Skipping dbt run.\n"
            "----------------------------------------"
        )

        return subprocess.CompletedProcess(
            args="dbt build --select source:fbi+ --profiles-dir .",
            returncode=0,
            stdout="DBT run skipped due to no new data.",
            stderr="")

    iscloudrun = write_profiles_yml(logger=logger)

    logger.info(f"DBT Project Directory: {DBT_DIR}")

    start = time.time()
    try:
        start = time.time()
        if iscloudrun:
            deps_result = subprocess.run(
                "dbt deps",
                shell=True,
                cwd=DBT_DIR,
                capture_output=True,
                text=True,
                check=True
            )

        result = subprocess.run(
            "dbt build --select source:openlibrary+",
            shell=True,
            cwd=DBT_DIR,
            capture_output=True,
            text=True,
            check=True
        )

        duration = round(time.time() - start, 2)
        logger.info(f"dbt build completed in {duration}s")
        return result if result else deps_result
    except subprocess.CalledProcessError as e:
        logger.error(f"dbt build failed:\n{e.stdout}\n{e.stderr}")
        return result if result else deps_result


@flow(name="openlibrary_prefect_flow", on_completion=[flow_summary], on_failure=[flow_summary])
def openlibrary_prefect_flow():
    logger = get_run_logger()

    # Run the OpenLibrary books task
    openlibrary_books_task_result = openlibrary_books_task(logger)

    # Run the dbt task if data was loaded
    return dbt_openlibrary_data(logger, openlibrary_books_task_result)


if __name__ == "__main__":
    openlibrary_prefect_flow()
