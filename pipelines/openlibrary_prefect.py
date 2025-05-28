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

BASE_URL = "https://openlibrary.org/search.json"

# Define your search terms and topics
SEARCH_TOPICS: dict[str, list[str]] = {
    "Python": ["Python", "python_books"],
    "Apache Airflow": ["Apache Airflow", "apache_airflow_books"],
    "Data Engineering": ["Data Engineering", "data_engineering_books"],
    "Data Warehousing": ["Data Warehousing", "data_warehousing_books"],
    "SQL": ["SQL", "sql_books"]
}

def create_resource(term: str, topic: str, resource_name: str, current_table_count: int, logger):

    @dlt.resource(name=resource_name, write_disposition="merge", primary_key="key")
    def resource_func() -> Iterator[Dict]:
        state = dlt.current.source_state().setdefault(resource_name, {
            "count": 0,
            "last_run_status": None
        })

        try: 
            response = requests.get(BASE_URL, params={"q": term, "limit": 100})
            data = response.json()
        except Exception as e:
            logger.error(f"❌ Fetch failed for '{term}': {e}")
            state["last_run_status"] = "failed"
            return

        # Prepare filtered rows first
        filtered_rows = []
        for book in data["docs"]:
            subject_list = book.get("subject", [])
            subject_str = " ".join(
                subject_list).lower() if subject_list else ""
            title = book.get("title", "").lower()

            if topic.lower() in title or topic.lower() in subject_str:
                filtered_rows.append({
                    "search_term": term,
                    "topic_filter": topic,
                    "title": book.get("title"),
                    "author_name": ", ".join(book.get("author_name", [])),
                    "publish_year": book.get("first_publish_year"),
                    "isbn": ", ".join(book.get("isbn", [])) if book.get("isbn") else None,
                    "edition_count": book.get("edition_count"),
                    "key": book.get("key"),
                    "subject_raw": subject_list,
                    "subject_str": subject_str
                })

        filtered_count = len(filtered_rows)
        previous_count = state["count"]

        if current_table_count < previous_count:
            logger.info(
                f"⚠️ Detected fewer rows in DuckDB table '{resource_name}' ({current_table_count}) "
                f"than previous filtered count ({previous_count}). Forcing reload."
            )
        elif filtered_count == previous_count:
            logger.info(
                f"🔁 SKIPPED LOAD for {term}:\n"
                f"📅 Previous filtered count: {previous_count}\n"
                f"📦 Current filtered count: {filtered_count}\n"
                f"⏳ No new data. Skipping..."
            )
            state["last_run_status"] = "skipped_no_new_data"
            return

        logger.info(
            f"✅ New filtered data for '{term}': {previous_count} ➝ {filtered_count}"
        )
        state["count"] = filtered_count
        state["last_run_status"] = "success"

        try:
            yield from filtered_rows
        except Exception as e:
            logger.error(f"❌ Failed to yield data for {term}: {e}")
            state["last_run_status"] = "failed"

    return resource_func


@dlt.source
def openlibrary_dim_source(logger, current_counts: Dict[str, int]):
    for term, (topic, resource_name) in SEARCH_TOPICS.items():
        yield create_resource(term, topic, resource_name, current_counts.get(resource_name, 0), logger)


@task
def openlibrary_books_task(logger) -> bool:

    logger.info("Starting DLT pipeline...")
    pipeline = dlt.pipeline(
        pipeline_name="openlibrary_incremental",
        destination=os.environ.get("DLT_DESTINATION") or os.getenv("DLT_DESTINATION"),
        pipelines_dir=str(DLT_PIPELINE_DIR),
        dataset_name="openlibrary_data"
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

    source = openlibrary_dim_source(logger, row_counts_dict)

    try:
        load_info = pipeline.run(source)

        statuses = [source.state.get(resource, {}).get(
            "last_run_status") for (junk, resource) in SEARCH_TOPICS.values()]

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