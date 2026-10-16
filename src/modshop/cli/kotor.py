"""`modshop kotor <command>`."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from modshop.cli.common import exits_cleanly, paths_for, store_for
from modshop.core.key import VANILLA, Key
from modshop.core.tree import Manifest
from modshop.kotor import base as base_mod

app = typer.Typer(no_args_is_help=True, help="Knights of the Old Republic.")
base = typer.Typer(no_args_is_help=True, help="The vanilla game.")
app.add_typer(base, name="base")

DataOpt = Annotated[
    Path | None, typer.Option("--data", help="The data root (default: KOTOR_DATA, then games/kotor/data).")
]


@base.command("index")
@exits_cleanly
def base_index(
    data: DataOpt = None,
    update: Annotated[
        bool, typer.Option("--update", help="Rewrite base.json's tree hash from the tree.")
    ] = False,
) -> None:
    """Normalise the vanilla tree, write its manifest, and check its hash against base.json."""
    paths = paths_for("kotor", data)
    c = base_mod.index(store_for(paths), paths.game_dir / "build" / "base.json", update=update)
    print(f"vanilla: {c.files} files, tree {c.tree}")


@app.command()
@exits_cleanly
def verify(
    key: Annotated[
        str | None, typer.Argument(help="A checkpoint key (default: the chain end of the last build).")
    ] = None,
    data: DataOpt = None,
) -> None:
    """Rehash a checkpoint's tree in full and compare it with its manifest."""
    paths = paths_for("kotor", data)
    store = store_for(paths)
    if key is None:
        if not paths.build_link.is_symlink():
            raise typer.BadParameter("no build yet; name a checkpoint")
        key = paths.build_link.readlink().parent.name
    k = Key(key)
    if store.get(k) is None and k != VANILLA:
        raise typer.BadParameter(f"no checkpoint {key} under {store.ckpt}")
    recorded = store.manifest(k)
    actual = Manifest.of_tree(store.tree(k))
    diff = recorded.diff(actual)
    for p in diff.paths():
        print(p)
    if diff:
        print(f"{key}: {len(diff.paths())} paths differ from the manifest")
        raise typer.Exit(1)
    print(f"{key}: matches its manifest ({len(actual)} files)")
