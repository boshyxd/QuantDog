import logging
import os
import subprocess
import sys
from functools import cache
from pathlib import Path

import structlog
from pydantic_settings import BaseSettings

logging.getLogger("scapy").setLevel(logging.CRITICAL)
logger = structlog.stdlib.get_logger("quantdog.client")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


class Settings(BaseSettings):
    pqc_port: int = 11777


@cache
def get_settings():
    return Settings()


settings = get_settings()


def check_sudo():
    if os.geteuid() == 0:
        return

    logger.info(
        "Switching to root access. You may need to type in your password."
    )
    logger.debug("Arguments: %s", sys.argv)
    subprocess.call(
        ["sudo", PROJECT_ROOT / ".venv" / "bin" / "python", *sys.argv]
    )
    sys.exit(0)
