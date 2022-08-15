import os
from ocrd_webapi.config import *

__all__ = [
    'SERVER_PATH',
    'WORKSPACES_DIR',
    'JOB_DIR',
    'WORKFLOWS_DIR',
    'DB_URL',
]

config = read_config()

SERVER_PATH: str = config[CONFIG_SERVER_PATH]
BASE_DIR: str = config[CONFIG_STORAGE_DIR]
DB_URL: str = config[CONFIG_DB_URL]
WORKSPACES_DIR: str = os.path.join(BASE_DIR, "workspaces")
JOB_DIR: str = os.path.join(BASE_DIR, "jobs")
WORKFLOWS_DIR: str = os.path.join(BASE_DIR, "workflows")
DEFAULT_NF_SCRIPT_NAME: str = "nextflow.nf"
