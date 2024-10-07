from __future__ import annotations

from dynaconf import Dynaconf

## Database settings loaded with dynaconf
DB_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    env="database",
    envvar_prefix="DB",
    settings_files=["db/settings.toml", "db/.secrets.toml"],
)
