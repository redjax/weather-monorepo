from __future__ import annotations

from contextlib import contextmanager
import importlib.util
import logging
import os
from pathlib import Path
import platform
import sys
import typing as t
import shutil

log = logging.getLogger(__name__)

import nox

## Set nox options
if importlib.util.find_spec("uv"):
    nox.options.default_venv_backend = "uv|virtualenv"
else:
    nox.options.default_venv_backend = "virtualenv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False
nox.options.error_on_missing_interpreters = False
# nox.options.report = True

## Instruct PDM to use nox's Python
os.environ.update({"UV_NO_CACH": "1"})

## Define versions to test
PY_VERSIONS: list[str] = ["3.12", "3.11"]
## Get tuple of Python ver ('maj', 'min', 'mic')
PY_VER_TUPLE: tuple[str, str, str] = platform.python_version_tuple()
## Dynamically set Python version
DEFAULT_PYTHON: str = f"{PY_VER_TUPLE[0]}.{PY_VER_TUPLE[1]}"


# this VENV_DIR constant specifies the name of the dir that the `dev`
# session will create, containing the virtualenv;
# the `resolve()` makes it portable
VENV_DIR = Path("./.venv").resolve()

## At minimum, these paths will be checked by your linters
#  Add new paths with nox_utils.append_lint_paths(extra_paths=["..."],)
DEFAULT_LINT_PATHS: list[str] = ["src", "tests", "scripts", "packages", "shared"]
## Set directory for requirements.txt file output
REQUIREMENTS_OUTPUT_DIR: Path = Path("./")

NOX_COMPOSE_FILE = (
    os.environ.get("NOX_COMPOSE_FILE") or "containers/dev.docker-compose.yml"
)

logging.basicConfig(
    level="DEBUG",
    format="%(name)s | [%(levelname)s] > %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

for _logger in []:
    logging.getLogger(_logger).setLevel("WARNING")


@contextmanager
def cd(newdir):
    """Context manager to change a directory before executing command."""
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def check_path_exists(p: t.Union[str, Path] = None) -> bool:
    """Check the existence of a path.

    Params:
        p (str | Path): The path to the directory/file to check.

    Returns:
        (True): If Path defined in `p` exists.
        (False): If Path defined in `p` does not exist.

    """
    p: Path = Path(f"{p}")
    if "~" in f"{p}":
        p = p.expanduser()

    _exists: bool = p.exists()

    if not _exists:
        log.error(FileNotFoundError(f"Could not find path '{p}'."))

    return _exists


def install_uv_project(session: nox.Session, external: bool = False) -> None:
    """Method to install uv and the current project in a nox session."""
    log.info("Installing uv in session")
    session.install("uv")
    log.info("Syncing uv project")
    session.run("uv", "sync", external=external)
    log.info("Installing project")
    session.run("uv", "pip", "install", ".", external=external)


def run_docker_cmd(session: nox.Session, compose_file: str, operation: str):
    if compose_file is None:
        raise ValueError("Missing a compose_file value.")

    if operation is None:
        raise ValueError("operation should not be None")

    if not check_path_exists(p=compose_file):
        raise FileNotFoundError(f"Could not find compose file: {compose_file}")

    valid_operations: list[str] = [
        "build",
        "build-no-cache",
        "up",
        "up-build",
        "up-recreate",
        "down",
    ]

    match operation:
        case "build":
            session.run(
                "docker",
                "compose",
                "-f",
                compose_file,
                "build",
                external=True,
            )
        case "build-no-cache":
            session.run(
                "docker",
                "compose",
                "-f",
                compose_file,
                "build",
                "--no-cache",
                external=True,
            )
        case "up":
            session.run(
                "docker",
                "compose",
                "-f",
                compose_file,
                "up",
                "-d",
                external=True,
            )
        case "up-build":
            session.run(
                "docker",
                "compose",
                "-f",
                compose_file,
                "up",
                "-d",
                "--build",
                external=True,
            )
        case "up-recreate":
            session.run(
                "docker",
                "compose",
                "-f",
                compose_file,
                "up",
                "-d",
                "--force-recreate",
                external=True,
            )
        case "down" | "stop":
            session.run(
                "docker",
                "compose",
                "-f",
                compose_file,
                "down",
                external=True,
            )
        case _:
            raise ValueError(
                f"Invalid Docker compose operation: {operation}. Must be one of {valid_operations}"
            )


##############
# Repository #
##############


@nox.session(python=[DEFAULT_PYTHON], name="dev-env")
def dev(session: nox.Session) -> None:
    """Sets up a python development environment for the project.

    This session will:
    - Create a python virtualenv for the session
    - Install the `virtualenv` cli tool into this environment
    - Use `virtualenv` to create a global project virtual environment
    - Invoke the python interpreter from the global project environment to install
      the project and all it's development dependencies.
    """
    install_uv_project(session)


@nox.session(python=[DEFAULT_PYTHON], name="ruff-lint", tags=["ruff", "clean", "lint"])
def run_linter(session: nox.Session, lint_paths: list[str] = DEFAULT_LINT_PATHS):
    """Nox session to run Ruff code linting."""
    if not check_path_exists(p="ruff.toml"):
        if not Path("pyproject.toml").exists():
            log.warning(
                """No ruff.toml file found. Make sure your pyproject.toml has a [tool.ruff] section!
                    
If your pyproject.toml does not have a [tool.ruff] section, ruff's defaults will be used.
Double check imports in __init__.py files, ruff removes unused imports by default.
"""
            )

    session.install("ruff")

    log.info("Linting code")
    for d in lint_paths:
        if not Path(d).exists():
            log.warning(f"Skipping lint path '{d}', could not find path")
            pass
        else:
            lint_path: Path = Path(d)
            log.info(f"Running ruff imports sort on '{d}'")
            session.run(
                "ruff",
                "check",
                lint_path,
                "--select",
                "I",
                "--fix",
            )

            log.info(f"Running ruff checks on '{d}' with --fix")
            session.run(
                "ruff",
                "check",
                lint_path,
                "--fix",
            )

    log.info("Linting noxfile.py")
    session.run(
        "ruff",
        "check",
        f"{Path('./noxfile.py')}",
        "--fix",
    )


@nox.session(python=[DEFAULT_PYTHON], name="uv-export")
@nox.parametrize("requirements_output_dir", REQUIREMENTS_OUTPUT_DIR)
def export_requirements(session: nox.Session, requirements_output_dir: Path):
    ## Ensure REQUIREMENTS_OUTPUT_DIR path exists
    if not requirements_output_dir.exists():
        try:
            requirements_output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"Unable to create requirements export directory: '{requirements_output_dir}'. Details: {exc}"
            )
            log.error(msg)

            requirements_output_dir: Path = Path("./")

    session.install(f"uv")

    log.info("Exporting production requirements")
    session.run(
        "uv",
        "pip",
        "compile",
        "pyproject.toml",
        "-o",
        str(REQUIREMENTS_OUTPUT_DIR / "requirements.txt"),
    )


@nox.session(name="fresh-clone-setup", tags=["init"])
def fresh_clone_setup(session: nox.Session):
    copy_files = [
        {"src": "./config/settings.toml", "dst": "./config/settings.local.toml"},
        {"src": "./config/db/settings.toml", "dst": "./config/db/settings.local.toml"},
        {
            "src": "./config/db/.secrets.example.toml",
            "dst": "./config/db/.secrets.toml",
        },
        {
            "src": "./config/apis/weatherapi/settings.toml",
            "dst": "./config/apis/weatherapi/settings.local.toml",
        },
        {
            "src": "./config/celery/settings.toml",
            "dst": "./config/celery/settings.local.toml",
        },
        {"src": "./containers/.env.example", "dst": "./containers/.env"},
        {
            "src": "./containers/.env.example",
            "dst": "./containers/.env",
        },
    ]

    log.info(f"Copying config files to locally editable versions")
    for _file in copy_files:
        if Path(_file["dst"]).exists():
            log.info(f"Path '{_file['dst']} already exists. Skipping copy.")
            continue

        log.info(f"Copying '{_file['src']}' to '{_file['dst']}")
        try:
            shutil.copy(src=_file["src"], dst=_file["dst"])
        except Exception as exc:
            msg = f"({type(exc)}) Error copying file '{_file['src']}' to location '{_file['dst']}'. Details: {exc}"
            log.error(msg)

            continue


@nox.session(python=[DEFAULT_PYTHON], name="install-repo")
def install_monorepo(session: nox.Session):
    install_uv_project(session)

    log.info("Locking dependencies")
    session.run("pdm", "lock", external=False)
    log.info("Installing monorepo with PDM")
    session.run("pdm", "install", external=False)


@nox.session(name="init-container-data", tags=["init", "docker"])
def init_container_data_dir(session: nox.Session):
    log.info("Initializing vols/ directory")

    root = Path("./containers")

    paths = [
        Path(f"{root}/vols/pgadmin"),
        Path(f"{root}/vols/postgres"),
        Path(f"{root}/vols/redis"),
    ]

    for p in paths:
        p = Path(f"{p}/data")

        if not p.exists():
            log.info(f"Creating directory: {p}/data")
            p.mkdir(parents=True, exist_ok=True)


@nox.session(name="init-db", tags=["db"])
def initialize_database(session: nox.Session):
    install_uv_project(session)

    script_path = Path("./scripts/db_init.py")

    if not script_path.exists():
        log.error(f"Could not find path: {script_path}")
    else:
        log.info("Running db_init.py script")
        session.run("python", script_path)


###################
# Celery Sessions #
###################


@nox.session(name="start-celery-worker", tags=["celery"])
def start_celery_worker(session: nox.Session):
    install_uv_project(session)

    log.info("Starting Celery worker")
    session.run("uv", "run", "./scripts/start_celery_worker.py")


@nox.session(name="start-celery-beat", tags=["celery"])
def start_celery_beat(session: nox.Session):
    install_uv_project(session)

    log.info("Starting Celery beat")
    session.run("uv", "run", "./scripts/start_celery_beat.py")


####################
# Alembic Sessions #
####################


@nox.session(python=[DEFAULT_PYTHON], name="alembic-init", tags=["alembic"])
def run_alembic_initialization(session: nox.Session):
    if Path("./migrations").exists():
        log.warning(
            "Migrations directory [./migrations] exists. Skipping alembic init."
        )
        return
    install_uv_project(session)

    log.info("Initializing Alembic database")
    session.run("uv", "run", "alembic", "init", "migrations")

    log.info(
        """
!! READ THIS !!

Alembic initialized at path ./migrations.

You must edit migrations/env.py to configure your project.

If you're using a "src" layout, add this to the top of your code:

import sys

sys.path.append("./src")

Import your SQLAlchemy models (look for the commented sections describing model imports),
set your SQLAlchemy Base.metadata, and set the database URI.

If you're using Dynaconf, i.e. in a `db.settings.DB_SETTINGS` object, you can set the
database URI like:

## Get database URI from config
#  !! You have to write this function !!
DB_URI = get_db_uri()
## Set alembic's SQLAlchemy URL
if DB_URI:
    config.set_main_option(
        "sqlalchemy.url", DB_URI.render_as_string(hide_password=False)
    )
else:
    raise Exception("DATABASE_URL not found in Dynaconf settings")
    
!! READ THIS !! 
"""
    )


@nox.session(name="alembic-migrate", tags=["alembic"])
def do_alembic_migration(session: nox.Session):
    install_uv_project(session)

    log.info("Doing alembic automigration")
    session.run(
        "uv",
        "run",
        "alembic",
        "revision",
        "--autogenerate",
        "-m",
        "autogenerated migration",
    )
    session.run("uv", "run", "alembic", "upgrade", "head")


##########
# Docker #
##########


@nox.session(name="init-container-data", tags=["init", "docker"])
def init_container_data_dir(session: nox.Session):
    log.info("Initializing vols/ directory")

    root = Path("./containers")

    paths = [
        Path(f"{root}/vols/pgadmin"),
        Path(f"{root}/vols/postgres"),
        Path(f"{root}/vols/mariadb"),
        Path(f"{root}/vols/redis"),
        Path(f"{root}/vols/rabbitmq"),
    ]

    for p in paths:
        p = Path(f"{p}/data")

        if not p.exists():
            log.info(f"Creating directory: {p}/data")
            p.mkdir(parents=True, exist_ok=True)

    for p in [
        Path(f"{root}/vols/postgres/pg_entrypoint"),
        Path(f"{root}/vols/postgres/pgsql_scripts"),
    ]:
        if not p.exists():
            log.info(f"Creating directory: {p}")
            p.mkdir(parents=True, exist_ok=True)


@nox.session(name="run-dev-containers", tags=["docker"])
def run_dev_containers(session: nox.Session):
    install_uv_project(session)

    script_path = Path("./scripts/start_dev_containers.py")

    if not script_path.exists():
        log.error(f"Could not find path: {script_path}")
    else:
        log.info("Running Docker dev containers")
        session.run("python", script_path)


@nox.session(name="compose-build", tags=["docker"])
def rebuild_dev_containers(session: nox.Session):
    log.info("Rebuilding Docker dev containers")
    run_docker_cmd(session, compose_file=NOX_COMPOSE_FILE, operation="build")


@nox.session(name="compose-build-nocache", tags=["docker"])
def rebuild_dev_containers_no_cache(session: nox.Session):
    log.info("Rebuilding Docker dev containers without cache")
    run_docker_cmd(
        session,
        compose_file=NOX_COMPOSE_FILE,
        operation="build-no-cache",
    )


@nox.session(name="compose-up", tags=["docker"])
def run_dev_containers(session: nox.Session):
    log.info("Bringing Docker dev stack up")
    run_docker_cmd(
        session,
        compose_file=NOX_COMPOSE_FILE,
        operation="up",
    )


@nox.session(name="compose-up-build", tags=["docker"])
def build_run_dev_containers(session: nox.Session):
    log.info("Rebuilding containers & bringing Docker dev stack up")
    run_docker_cmd(
        session,
        compose_file=NOX_COMPOSE_FILE,
        operation="up-build",
    )


@nox.session(name="compose-up-recreate", tags=["docker"])
def recreate_dev_containers(session: nox.Session):
    log.info("Bringing Docker dev stack up, restarting all containers")
    run_docker_cmd(
        session,
        compose_file=NOX_COMPOSE_FILE,
        operation="up-recreate",
    )


@nox.session(name="compose-down", tags=["docker"])
def rebuild_dev_containers(session: nox.Session):
    log.info("Stopping Docker dev containers")
    run_docker_cmd(session, compose_file=NOX_COMPOSE_FILE, operation="down")
