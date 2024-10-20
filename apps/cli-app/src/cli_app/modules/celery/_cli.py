from cyclopts import App

from scripts import start_celery_worker, start_celery_beat

celery_cli_app = App(
    name="celery",
    help="Celery functions like starting a worker/beat schedule.",
    group="automation",
)

VALID_CELERY_SERVICES = ["worker", "beat"]


def validate_service(value: str):

    if value is None:
        print(
            f"No Celery service detected. Valid service options: {VALID_CELERY_SERVICES}"
        )
    value = value.lower()

    if value not in VALID_CELERY_SERVICES:
        raise ValueError(
            f"Invalid Celery service: {value}. Must be one of {VALID_CELERY_SERVICES}"
        )

    return value


@celery_cli_app.command(name="start", group="manage")
def start_service(service: str):
    """Start a Celery service (worker, beat, etc)."""
    service = validate_service(value=service)

    print(f"Starting service: {service}")

    match service:
        case "worker":

            try:
                start_celery_worker.run()
            except Exception as exc:
                msg = f"({type(exc)}) Error starting Celery worker. Details: {exc}"
                print(f"[ERROR] {msg}")

                exit(1)

        case "beat":
            try:
                start_celery_beat.run()
            except Exception as exc:
                msg = f"({type(exc)}) Error starting Celery beat. Details: {exc}"
                print(f"[ERROR] {msg}")

                exit(1)

        case _:
            if service is None:
                raise NotImplementedError(f"Unknown service: {service}")
