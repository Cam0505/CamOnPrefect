import os
import re
from datetime import datetime
import subprocess
from prefect import get_run_logger
from prefect.states import Completed, Failed
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




def parse_dbt_output_metadata(proc: subprocess.CompletedProcess, command: str = "dbt run") -> dict:
    """Parse metadata from a dbt subprocess run."""
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    returncode = proc.returncode
    success = returncode == 0

    # Extract number of models/tests run and their status
    model_count = 0
    test_count = 0
    warnings = 0
    errors = 0
    skip_count = 0
    time_taken = None

    # Parse counts from stdout
    model_match = re.search(r"(\d+)\s+model[s]?\s+run", stdout)
    test_match = re.search(r"(\d+)\s+test[s]?\s+passed", stdout)
    warning_match = re.search(r"(\d+)\s+warning[s]?", stdout)
    error_match = re.search(r"(\d+)\s+error[s]?", stdout)
    skip_match = re.search(r"(\d+)\s+model[s]?\s+skipped", stdout)
    time_match = re.search(r"Completed in\s+([\d.]+)s", stdout)

    if model_match:
        model_count = int(model_match.group(1))
    if test_match:
        test_count = int(test_match.group(1))
    if warning_match:
        warnings = int(warning_match.group(1))
    if error_match:
        errors = int(error_match.group(1))
    if skip_match:
        skip_count = int(skip_match.group(1))
    if time_match:
        time_taken = float(time_match.group(1))

    return {
        "command": command,
        "success": success,
        "returncode": returncode,
        "models_run": model_count,
        "tests_passed": test_count,
        "warnings": warnings,
        "errors": errors,
        "models_skipped": skip_count,
        "time_seconds": time_taken,
        "stdout_snippet": stdout.strip()[-500:],  # Last 500 chars for preview
        "stderr": stderr.strip(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


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
        if result is not None:
            logger.info(f"📦 Flow returned result of type: {type(result).__name__}")
            if isinstance(result, dict):
                logger.info(f"📘 Result preview (first 3 keys): {dict(list(result.items())[:3])}")
            elif isinstance(result, list):
                logger.info(f"📘 Result preview (first 3 items): {result[:3]}")
            elif isinstance(result, str):
                logger.info(f"📘 Result preview (string, first 100 chars): {result[:100]}")
            else:
                logger.info(f"📘 Result: {str(result)[:100]}")
    except Exception as e:
        logger.warning(f"⚠️ Could not extract flow result: {e}")

    logger.info("=== End Flow Summary ===")