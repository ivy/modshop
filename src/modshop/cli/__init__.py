"""The command line: `modshop kotor <command>`. Commands parse, build objects, call one method, print."""

from __future__ import annotations

import typer

from modshop.cli import kotor as kotor_commands

app = typer.Typer(no_args_is_help=True, add_completion=False)
app.add_typer(kotor_commands.app, name="kotor")
