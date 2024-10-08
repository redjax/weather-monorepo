import logging

log = logging.getLogger(__name__)

from cli_app import app as cli_app

if __name__ == "__main__":
    cli_app()
