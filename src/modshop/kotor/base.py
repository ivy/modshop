"""The vanilla game as a definition: Steam ids and the tree hash they must produce."""

from __future__ import annotations

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
