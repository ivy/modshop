"""An entry's inputs, extracted to a scratch folder for the duration of its steps.

Only the entry's own `inputs` are staged; what its steps declare through `inputs()` is key
material that the steps reach by path (a repair script, an installer), not something to unpack.
The folder is made fresh for the entry and removed after it, so nothing outside the checkpoints
carries state between runs.
"""

from __future__ import annotations

import re
import shutil
from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from pathlib import Path

from modshop.core.extract import Extractor
from modshop.core.inputs import InputResolver
from modshop.core.recipe import Entry


@dataclass(frozen=True, slots=True)
class Stage:
    path: Path


type StageFactory = Callable[[Entry], AbstractContextManager[Stage]]


def stage_dir(root: Path, entry: Entry) -> Path:
    return root / re.sub(r"[^\w.-]", "_", entry.name)


@contextmanager
def staged(root: Path, resolver: InputResolver, extractor: Extractor, entry: Entry) -> Generator[Stage]:
    out = stage_dir(root, entry)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    try:
        for spec in entry.inputs:
            for item in resolver.resolve(spec, entry.name).staged():
                extractor.place(item, out)
        yield Stage(out)
    finally:
        shutil.rmtree(out, ignore_errors=True)


def stage_factory(root: Path, resolver: InputResolver, extractor: Extractor) -> StageFactory:
    def make(entry: Entry) -> AbstractContextManager[Stage]:
        return staged(root, resolver, extractor, entry)

    return make
