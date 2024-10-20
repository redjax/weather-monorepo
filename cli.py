import logging

log = logging.getLogger(__name__)

from cli_app import app as cli_app
from core.setup import setup_logging, LOGGING_SETTINGS

if __name__ == "__main__":
    setup_logging(level="DEBUG")
    cli_app()
