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

dotenv.load_dotenv()

def analyzer(name: str, _input: dict):
    if os.getenv("DISABLE_ANALYTICS") == 1:
        return
    else:
        Posthog(
            project_api_key="phc_qLInS8phhqhE7IrHTMxfbm5yBiTSLz30mOQmsrgLaCD",
            host="https://app.posthog.com",
        ).capture(str(int(time.time())), name, _input)

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    "handlers": {
        "console_info": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "console_error": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
    },
    "root": {"level": "INFO", "handlers": ["console_info", "console_error"]},
}

logging_config["root"]["level"] = "INFO" if not getenv("LOG_LEVEL") else getenv("LOG_LEVEL")
logging.config.dictConfig(logging_config)
