from .node import Node
from .dag import DAG
from .llm import LLM
from .utils.status import Status
from .utils.constants import CONFIG_PATH

import logging.config
import json
from os.path import exists 

def safe_load_log_config(json_filepath: str) -> None:
    if not exists(json_filepath):
        raise FileNotFoundError(f"Logging configuration file not found: {json_filepath}")

    with open(json_filepath, 'r') as f:
        config = json.load(f)
        logging.config.dictConfig(config)

safe_load_log_config(CONFIG_PATH)