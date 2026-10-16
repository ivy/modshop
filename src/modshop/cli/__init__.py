"""The command line: `modshop kotor <command>`."""

import typer

app = typer.Typer(no_args_is_help=True, add_completion=False)
kotor = typer.Typer(no_args_is_help=True, help="Knights of the Old Republic.")
app.add_typer(kotor, name="kotor")
