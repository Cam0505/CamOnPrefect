# camonprefect/path_config.py
from pathlib import Path
import os
import sys

def get_project_root():
    """Resolves the correct root path across all environments.
    Returns:
        Path: Absolute path to project root
    Raises:
        FileNotFoundError: If no valid root is found
    """
    # Check these locations in order
    search_paths = [
        Path("/workspaces/CamOnPrefect"),  # Devcontainer
        Path(__file__).parent.parent,      # Fallback (local dev)
        Path.cwd()                         # Current directory
    ]

    for path in search_paths:
        try:
            if (path / "dbt").exists() and (path / "pipelines").exists():
                return path.resolve()  # Return absolute path
        except (PermissionError, OSError) as e:
            print(f"Warning: Couldn't access {path} - {str(e)}", file=sys.stderr)

    # Diagnostic information for debugging
    cwd = Path.cwd()
    raise FileNotFoundError(
        "Project root not found! Checked:\n"
        f"- Possible roots: {[str(p) for p in search_paths]}\n"
        f"- Current directory: {str(cwd)}\n"
        f"- Contents: {[f.name for f in cwd.iterdir() if f.is_dir()]}\n"
        "Required structure: must contain 'dbt/' and 'pipelines/' subdirectories"
    )

# Standardized paths
PROJECT_ROOT = get_project_root()
DBT_DIR = PROJECT_ROOT / "dbt"
PIPELINES_DIR = PROJECT_ROOT / "pipelines"
CREDENTIALS = PIPELINES_DIR / "credentials.json"
ENV_FILE = PROJECT_ROOT / ".env"  # For local development
REQUEST_CACHE_DIR = PROJECT_ROOT / "request_cache"
DLT_PIPELINE_DIR = PIPELINES_DIR / ".dlt"

# Environment variable for containers
os.environ["PROJECT_ROOT"] = str(PROJECT_ROOT)