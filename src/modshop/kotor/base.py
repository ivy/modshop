"""The vanilla game as a definition: Steam ids and the tree hash they must produce.

`base fetch` downloads exactly that depot manifest with DepotDownloader (SteamRE's open-source
Steam client, installed by mise from the repository's mise.toml) into the vanilla tree. The
first run asks for the account's password and a Steam Guard code on the terminal; with
`-remember-password` the login state is kept under ~/.config/DepotDownloader, outside the
repository and the data root.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from modshop.core.checkpoint import Checkpoint, Store
from modshop.core.errors import Preflight
from modshop.core.key import VANILLA


class Base(BaseModel):
    model_config = ConfigDict(frozen=True, extra="allow")
    app: int
    depot: int
    manifest: str
    buildid: int | None = None
    tree: str | None = None
    files: int | None = None

    @classmethod
    def load(cls, path: Path) -> Base:
        return cls.model_validate_json(path.read_text())

    def with_tree(self, tree: str, files: int) -> Base:
        return self.model_copy(update={"tree": tree, "files": files})

    def dump(self) -> str:
        return self.model_dump_json(indent=1) + "\n"


def fetch(base: Base, vanilla: Path, account: str, downloader: str = "DepotDownloader") -> int:
    """Download the base's depot manifest into `<vanilla>/tree`, replacing any tree there.
    Returns the number of files. Interactive: Steam may ask for a password and a Guard code."""
    if shutil.which(downloader) is None:
        raise Preflight(f"{downloader} is not installed; run `mise install`")
    partial = vanilla / "tree.partial"
    if partial.exists():
        shutil.rmtree(partial)
    partial.mkdir(parents=True)
    cmd = [
        downloader, "-app", str(base.app), "-depot", str(base.depot), "-manifest", base.manifest,
        "-os", "windows", "-osarch", "32", "-username", account, "-remember-password",
        "-dir", str(partial), "-validate",
    ]  # fmt: skip
    subprocess.run(cmd, check=True)
    # DepotDownloader keeps its own bookkeeping beside the files; the tree is the game alone
    shutil.rmtree(partial / ".DepotDownloader", ignore_errors=True)
    tree = vanilla / "tree"
    if tree.exists():
        shutil.rmtree(tree)
    partial.rename(tree)
    (vanilla / "source.json").write_text(
        json.dumps({"app": base.app, "depot": base.depot, "manifest": base.manifest}) + "\n"
    )
    return sum(1 for p in tree.rglob("*") if p.is_file())


def index(store: Store, base_json: Path, *, update: bool = False) -> Checkpoint:
    """Normalise the vanilla tree and write its manifest, then compare its hash with base.json:
    a mismatch is refused unless the record is being updated, in which case base.json is rewritten."""
    if not store.tree(VANILLA).is_dir():
        raise Preflight(f"no vanilla tree at {store.tree(VANILLA)}; run `base fetch` first")
    c = store.index_vanilla()
    base = Base.load(base_json)
    if base.tree is None or update:
        base_json.write_text(base.with_tree(c.tree, c.files).dump())
    elif base.tree != c.tree:
        raise Preflight(
            f"the vanilla tree hashes to {c.tree[:12]} but base.json records {base.tree[:12]}; "
            "fetch the base again, or pass --update if the record is wrong"
        )
    return c
