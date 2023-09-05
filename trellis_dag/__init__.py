from posthog import Posthog
import os
import time
import dotenv

import logging.config
import json
from os.path import exists
from os import getenv

from .node import Node
from .dag import DAG
from .llm import LLM
from .utils.status import Status
from .utils.constants import CONFIG_PATH

dotenv.load_dotenv()


def safe_load_log_config(json_filepath: str) -> None:
    if not exists(json_filepath):
        raise FileNotFoundError(
            f"Logging configuration file not found: {json_filepath}"
        )

    with open(json_filepath, "r") as f:
        config = json.load(f)
        config["root"]["level"] = (
            "DEBUG" if not getenv("LOG_LEVEL") else getenv("LOG_LEVEL")
        )
        logging.config.dictConfig(config)


def analyzer(name: str, _input: dict):
    if os.getenv("DISABLE_ANALYTICS") == 1:
        return
    else:
        Posthog(
            project_api_key="phc_qLInS8phhqhE7IrHTMxfbm5yBiTSLz30mOQmsrgLaCD",
            host="https://app.posthog.com",
        ).capture(str(int(time.time())), name, _input)


safe_load_log_config(CONFIG_PATH)
