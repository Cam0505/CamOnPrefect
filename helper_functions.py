import os
import re
from prefect import get_run_logger
import json
from prefect.client.schemas.objects import State
from prefect.flows import Flow
from prefect.client import get_client
from prefect.client.schemas.objects import FlowRun
# from typing import Optional
from prefect.client.schemas.filters import FlowRunFilter, FlowRunFilterId
import inspect

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
    

def sanitize_filename(value: str) -> str:
    # Replace all non-word characters (anything other than letters, digits, underscore) with underscore
    no_whitespace = ''.join(value.split())
    ascii_only = no_whitespace.encode("ascii", errors="ignore").decode()
    return re.sub(r"[^\w\-_\.]", "_", ascii_only)



async def flow_summary(flow, flow_run, state):
    logger = get_run_logger()

    logger.info(f"Flow Name: {flow.name}")
    logger.info(f"Flow Run Start Time: {flow_run.start_time}")
    logger.info(f"Flow Run End Time: {flow_run.end_time}")
    logger.info(f"🔁 Flow Status: {state.name}")

    if state.is_failed():
        logger.error(f"❌ Flow failed with message: {state.message}")

    try:
        client = get_client()
        task_runs = await client.read_task_runs(
            flow_run_filter=FlowRunFilter(
                id=FlowRunFilterId(any_=[flow_run.id])
            )
        )
        for tr in task_runs:
            state_type = tr.state_type.name if tr.state_type else "UNKNOWN"
            duration = tr.total_run_time or "N/A"
            logger.info(f"✅ Task: {tr.name} | State: {state_type} | Duration: {duration}")
        logger.info(f"✅ Tasks executed in this run: {[tr.name for tr in task_runs]}")
    except Exception as e:
        logger.warning(f"⚠️ Could not fetch task run info: {e}")

    try:
        result = await state.result() if inspect.isawaitable(state.result()) else state.result()
        if result is not None and hasattr(result, "stdout"):
            logger.info("📄 Full stdout:")
            logger.info(result.stdout.strip())
        else:
            logger.info("📄 No stdout attribute found on result.")
    except Exception as e:
        logger.warning(f"⚠️ Could not extract flow result: {e}")

    logger.info("=== End Flow Summary ===")
    return result