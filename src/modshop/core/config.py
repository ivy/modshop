"""Where things are, and what local.toml says.

`Paths` is computed once from the data root and the game directory in the repository, and
passed to whatever needs it; nothing reads the environment after start-up. `Local` is the typed
form of local.toml, read only by the commands and keys that need it.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from pydantic import BaseModel, ConfigDict

from modshop.core.errors import Preflight


@dataclass(frozen=True, slots=True)
class Paths:
    data: Path
    game_dir: Path  # the game's directory in the repository (games/kotor): recipe data, repairs, fixes

    @property
    def archives(self) -> Path:
        return self.data / "archives"

    @property
    def logs(self) -> Path:
        return self.data / "logs"

    @property
    def stage(self) -> Path:
        return self.data / "stage"

    @property
    def games(self) -> Path:
        return self.data / "game"

    @property
    def vanilla(self) -> Path:
        return self.games / "vanilla"

    @property
    def ckpt(self) -> Path:
        return self.games / "ckpt"

    @property
    def work(self) -> Path:
        return self.games / "work"

    @property
    def work_record(self) -> Path:
        return self.games / "work.json"

    @property
    def tags(self) -> Path:
        return self.games / "tags"

    @property
    def build_link(self) -> Path:
        return self.games / "build"

    @property
    def lock(self) -> Path:
        return self.games / ".lock"

    @property
    def hashcache(self) -> Path:
        return self.data / "hashcache.json"

    @property
    def repo(self) -> Path:
        return self.game_dir.parent.parent

    @property
    def local_toml(self) -> Path:
        return self.repo / "local.toml"

    @classmethod
    def resolve(cls, game_dir: Path, data: Path | None = None, env_var: str = "KOTOR_DATA") -> Paths:
        """`data` from the argument, then the environment variable, then <game_dir>/data."""
        chosen = data or (Path(os.environ[env_var]) if os.environ.get(env_var) else game_dir / "data")
        return cls(chosen.resolve(), game_dir.resolve())


class Handheld(BaseModel):
    """The device that runs the game, as local.toml describes it."""

    model_config = ConfigDict(extra="allow", frozen=True)
    ssh: str
    home: str
    game_dir: str
    display: str

    @property
    def game_dir_absolute(self) -> str:
        return self.game_dir.replace("~", self.home, 1) if self.game_dir.startswith("~") else self.game_dir


class Local(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=True)
    handheld: Handheld

    @classmethod
    def load(cls, path: Path) -> Local:
        if not path.exists():
            raise Preflight(f"{path} is missing; copy local.example.toml beside it and fill it in")
        with path.open("rb") as f:
            return cls.model_validate(tomllib.load(f))

    def value(self, dotted: str) -> object:
        """A value by dotted key, e.g. `handheld.display`, including keys the model does not name."""
        node: object = self.model_dump()
        for part in dotted.split("."):
            if not isinstance(node, dict):
                raise KeyError(dotted)
            node = cast(dict[str, object], node)[part]
        return node
