import logging

log = logging.getLogger(__name__)

from cyclopts import App

app = App()


@app.command
def foo(loops: int):
    for i in range(loops):
        print(f"Looping! {i}")


@app.default
def default_action():
    print("Hello world! This runs when no command is specified")


if __name__ == "__main__":
    app()
