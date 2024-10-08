from __future__ import annotations

import logging

log = logging.getLogger(__name__)

from dynaconf import Dynaconf

CELERY_SETTINGS = Dynaconf(
    environments=True,
    env="celery",
    envvar_prefix="CELERY",
    settings_files=["celery/settings.toml", "celery/.secrets.toml"],
)
