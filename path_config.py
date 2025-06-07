# camonprefect/path_config.py
from pathlib import Path
import os
import sys


def get_project_root():
    """Resolves the correct root path across all environments."""
    search_paths = [
        Path("/workspaces/CamOnPrefect"),  # Devcontainer
        Path(__file__).parent.parent,      # Local dev
        Path.cwd()                         # Fallback
    ]

    for path in search_paths:
        try:
            if (path / "dbt").exists() and (path / "pipelines").exists():
                project_root = path.resolve()
                break
        except (PermissionError, OSError) as e:
            print(
                f"Warning: Couldn't access {path} - {str(e)}", file=sys.stderr)
    else:

        cwd = Path.cwd()
        raise FileNotFoundError(
            "Project root not found! Checked:\n"
            f"- Possible roots: {[str(p) for p in search_paths]}\n"
            f"- Current directory: {str(cwd)}\n"
            f"- Contents: {[f.name for f in cwd.iterdir() if f.is_dir()]}\n"
            "Required structure: must contain 'dbt/' and 'pipelines/' subdirectories"
        )

    paths = {
        "PROJECT_ROOT": project_root,
        "DBT_DIR": project_root / "dbt",
        "DBT_TARGETS_DIR": project_root / "dbt" / "target",
        "DBT_RUN_RESULTS_DIR": project_root / "dbt" / "target" / "run_results.json",
        "PIPELINES_DIR": project_root / "pipelines",
        "CREDENTIALS": project_root / "pipelines" / "credentials.json",
        "ENV_FILE": project_root / ".env",
        "REQUEST_CACHE_DIR": project_root / "request_cache",
        "DLT_PIPELINE_DIR": project_root / "pipelines" / ".dlt"
    }
    return paths


def set_dlt_env_vars(paths):
    """Set DLT environment variables based on resolved paths."""
    os.environ["DLT_DATA_DIR"] = str(paths["DLT_PIPELINE_DIR"])
    os.environ["DLT_CONFIG_DIR"] = str(paths["DLT_PIPELINE_DIR"])
    os.environ["DLT_SECRETS_DIR"] = str(paths["DLT_PIPELINE_DIR"])
    os.environ["PROJECT_ROOT"] = str(paths["PROJECT_ROOT"])
