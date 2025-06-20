import dlt
import os
from dotenv import load_dotenv
from dlt.sources.helpers import requests
from dlt.pipeline.exceptions import PipelineNeverRan
from dlt.destinations.exceptions import DatabaseUndefinedRelation
from sgp4.api import Satrec, jday
from datetime import datetime
from math import sqrt
from prefect import flow, task, get_run_logger
from helper_functions import dbt_run_task, flow_summary
from path_config import get_project_root, set_dlt_env_vars

# Load environment variables and set DLT config
paths = get_project_root()
set_dlt_env_vars(paths)

DLT_PIPELINE_DIR = paths["DLT_PIPELINE_DIR"]
ENV_FILE = paths["ENV_FILE"]
DBT_DIR = paths["DBT_DIR"]

load_dotenv(dotenv_path=ENV_FILE)


@dlt.source
def satellite_source(logger, prev_positions: dict):
    @dlt.resource(write_disposition="replace", name="satellite_positions")
    def satellite_resource():
        state = dlt.current.source_state().setdefault("satellite_positions", {
            "satellite_status": {},
            "satellite_position": {}
        })
        try:
            url = "https://celestrak.org/NORAD/elements/gp.php?INTDES=2023-013&FORMAT=TLE"
            response = requests.get(url)
            lines = response.text.strip().splitlines()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch TLE data: {e}")
            return []

        logger.info(f"Fetched {len(lines)//3} satellites TLE data.")

        did_yield = False
        for i in range(0, len(lines), 3):  # Name, line1, line2
            name, line1, line2 = lines[i:i+3]
            satrec = Satrec.twoline2rv(line1, line2)
            sat_id = int(line1[2:7])  # Extract NORAD ID from line1

            dt = datetime.utcnow()
            jd, fr = jday(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second + dt.microsecond * 1e-6)
            e, pos, _ = satrec.sgp4(jd, fr)

            if e != 0:
                # pos may not be valid if SGP4 failed, so set to None or 0
                x, y, z = (0.0, 0.0, 0.0)
                state["satellite_status"][sat_id] = "failed"
                state["satellite_position"][sat_id] = {
                    "x_km": x,
                    "y_km": y,
                    "z_km": z,
                    "timestamp": dt.isoformat()
                }
                logger.error(f"SGP4 failed for satellite {name.strip()} with error code {e}.")
                continue  # skip if SGP4 failed

            x, y, z = pos

            prev_state = state["satellite_position"].get(sat_id)

            if prev_state and all(
                abs(prev_state[k] - curr) < 1e-6 for k, curr in zip(["x_km", "y_km", "z_km"], [x, y, z])
            ):
                logger.info(f"No change for satellite {sat_id}, skipping.")
                state["satellite_status"][sat_id] = "skipped"
                continue

            # Compute distance from last known position in dataset (not state)
            prev_data = prev_positions.get(sat_id)
            if prev_data:
                dx, dy, dz = x - prev_data["x_km"], y - prev_data["y_km"], z - prev_data["z_km"]
                distance = sqrt(dx**2 + dy**2 + dz**2)
                state["satellite_status"][sat_id] = "success"
            else:
                distance = None
                state["satellite_status"][sat_id] = 'firstrun'
                state["satellite_position"][sat_id] = {
                    "x_km": x,
                    "y_km": y,
                    "z_km": z,
                    "timestamp": dt.isoformat()
                }

            yield {
                "satellite_id": sat_id,
                "satellite_name": name.strip(),
                "timestamp": dt.isoformat(),
                "tle_line1": line1,
                "tle_line2": line2,
                "x_km": x,
                "y_km": y,
                "z_km": z,
                "distance_km": distance,
            }
            did_yield = True
        if not did_yield:
            logger.info("🟡 No new or changed satellite data found — skipping load.")
            return

    return satellite_resource


@task(name="satellite-flow")
def satellite_task(logger):
    logger = get_run_logger()
    logger.info("Starting satellite data pipeline...")

    pipeline = dlt.pipeline(
        pipeline_name="satellite_pipeline",
        destination=os.getenv("DLT_DESTINATION"),
        dataset_name="satellite_data",
        pipelines_dir=str(DLT_PIPELINE_DIR),
        dev_mode=False
    )
    prev_positions = {}
    try:
        prev_df = pipeline.dataset()["satellite_positions"].df()
        if prev_df is not None:
            prev_positions = (
                prev_df.sort_values("timestamp")
                .groupby("satellite_id")
                .last()[["x_km", "y_km", "z_km"]]
                .to_dict("index")
            )
    except PipelineNeverRan:
        logger.warning(
            "⚠️ No previous runs found for this pipeline. Assuming first run.")
    except DatabaseUndefinedRelation:
        logger.warning(
            "⚠️ Table Doesn't Exist. Assuming truncation.")

    try:
        source = satellite_source(logger, prev_positions)
        load_info = pipeline.run(source)
        current_state = source.state.get("satellite_positions", {})
        statuses = list(current_state.get("satellite_status", {}).values())

        if statuses is None or not statuses:
            logger.info("No satellites found in the current state.")
            return False
        elif all(s == "skipped" for s in statuses):
            logger.info(
                "\n\n ⏭️ All Satellites skipped — no data loaded.")
            return False
        elif all(s == "failed" for s in statuses):
            logger.error(
                "\n\n 💥 All satellites failed to load — check API or network.")
            return False

        loaded_count = sum(1 for s in statuses if s in {"success", "firstrun"})
        logger.info(f"\n\n ✅ Number of satellites loaded: {loaded_count}")

        logger.info(f"Pipeline Load Info: {load_info}")
        return True

    except Exception as e:
        logger.error(f"❌ Pipeline run failed: {e}")
        return False


@flow(name="satellite_flow", on_completion=[flow_summary], on_failure=[flow_summary])
def satellite_flow():
    logger = get_run_logger()
    success = satellite_task(logger)

    return dbt_run_task(logger, dbt_trigger=success, select_target="source:satellite+")


if __name__ == "__main__":
    satellite_flow()