"""Running an entry's steps against the work tree: what the Builder is given for KotOR."""

from __future__ import annotations

import logging

from modshop.core.config import Local, Paths
from modshop.core.errors import ModshopError, RecipeError, StepFailed
from modshop.core.recipe import Entry, Runner
from modshop.core.stage import Stage
from modshop.core.worktree import WorkTree
from modshop.kotor.context import StepContext
from modshop.kotor.patcher import Patcher
from modshop.kotor.paths import GameTree
from modshop.kotor.steps import StepModel

log = logging.getLogger("modshop")


def runner(paths: Paths, patcher: Patcher, local: Local | None, timeout: int = 1800) -> Runner:
    def run(entry: Entry, work: WorkTree, stage: Stage) -> None:
        for index, step in enumerate(entry.steps):
            if not isinstance(step, StepModel):
                raise RecipeError(entry.name, f"step {index} is not a KotOR step: {type(step).__name__}")
            ctx = StepContext(
                game=GameTree(work.path),
                stage=stage,
                paths=paths,
                handheld=local.handheld if local else None,
                patcher=patcher,
                log=log,
                entry=entry.name,
                index=index,
                timeout=timeout,
                local=local,
            )
            log.info("   %s %s", step.do, step.model_dump(mode="json", exclude={"do"}))
            try:
                step.apply(ctx)
            except ModshopError:
                raise
            except Exception as e:
                raise StepFailed(entry.name, index, step.do, f"{type(e).__name__}: {e}") from e

    return run
