"""The one mutable tree: a reflink copy of a checkpoint, with a record of which.

`work.json` names the checkpoint the tree equals, or says `dirty` while an entry's steps run,
so a tree left by a build killed by any means is restored from its parent on the next run rather
than reused.
"""

from __future__ import annotations

import json
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from modshop.core.clone import Cloner
from modshop.core.key import Key


@dataclass(frozen=True, slots=True)
class WorkTree:
    path: Path
    record: Path

    def key(self) -> Key | None:
        """The checkpoint the tree equals, or None if there is no tree, no record, or it is dirty."""
        if not (self.record.exists() and self.path.exists()):
            return None
        d = json.loads(self.record.read_text())
        return None if d.get("dirty") else Key(d["key"])

    def set_key(self, key: Key) -> None:
        self.record.write_text(json.dumps({"key": key}))

    def set_dirty(self) -> None:
        self.record.write_text(json.dumps({"dirty": True}))

    def discard(self) -> None:
        self.record.unlink(missing_ok=True)
        if self.path.exists():
            shutil.rmtree(self.path)

    def restore(self, tree: Path, key: Key, cloner: Cloner) -> int:
        """Make the tree a copy of checkpoint `key` unless it already is. Returns a clock reading
        taken after the copy and a sync, for Manifest.of_tree's ctime test."""
        if self.key() != key:
            self.discard()
            cloner.copy_tree(tree, self.path)
            self.set_key(key)
        os.sync()
        return time.time_ns()
