__version__ = "0.1.0" 

from .path_config import (
    DBT_DIR,
    ENV_FILE, 
    PROJECT_ROOT,
    get_project_root
)

__all__ = [
    'DBT_DIR',
    'ENV_FILE',
    'PROJECT_ROOT',
    'get_project_root'
]