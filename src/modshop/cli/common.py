"""What every command needs: the paths, the store, the error-to-exit mapping."""

from __future__ import annotations

import functools
import sys
from collections.abc import Callable
from pathlib import Path

import typer

from modshop.core.checkpoint import Store
from modshop.core.clone import Cloner
from modshop.core.config import Paths
from modshop.core.errors import ModshopError


def repo_root() -> Path:
    """The checkout: the first ancestor of the working directory holding `games/`, else the one
    this package is installed from."""
    for d in [Path.cwd(), *Path.cwd().parents]:
        if (d / "games").is_dir() and (d / "pyproject.toml").exists():
            return d
    return Path(__file__).resolve().parents[3]


def paths_for(game: str, data: Path | None) -> Paths:
    return Paths.resolve(repo_root() / "games" / game, data, env_var=f"{game.upper()}_DATA")


def store_for(paths: Paths, cloner: Cloner | None = None) -> Store:
    return Store(paths.ckpt, paths.vanilla, cloner or Cloner())


def exits_cleanly[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    """An expected failure prints its message and exits 1; anything else is a bug and shows."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return fn(*args, **kwargs)
        except ModshopError as e:
            print(f"error: {e}", file=sys.stderr)
            raise typer.Exit(1) from None

    return wrapper
