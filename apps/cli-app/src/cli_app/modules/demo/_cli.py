from cyclopts import App

demo_app = App(name="demo", help="Demo functionality. Remove this eventually!")


@demo_app.command
def bar(n: int):
    """Print the number, prepended with 'BAR: '."""
    print(f"BAR: {n}")


@demo_app.command
def baz(n: int):
    """Print the number, prepended with 'BAZ: '."""
    print(f"BAZ: {n}")
