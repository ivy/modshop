"""The step kinds, one frozen model each."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from modshop.kotor.context import StepContext


class StepModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    def inputs(self) -> tuple[str, ...]:
        return ()

    def canonical(self) -> dict[str, object]:
        return self.model_dump(mode="json")

    def apply(self, ctx: StepContext) -> None:
        raise NotImplementedError


class Copy(StepModel):
    do: Literal["copy"] = "copy"
    src: str = "."
    pattern: str = "*"
    exclude: tuple[str, ...] = ()
    recursive: bool = False
    dest: str | None = None

    def apply(self, ctx: StepContext) -> None:
        raise NotImplementedError
