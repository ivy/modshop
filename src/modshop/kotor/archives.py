"""The mod archives: how they are named, and the downloaders that fetch them."""

from __future__ import annotations

import re


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def folder_name(number: int, title: str) -> str:
    """The archive folder for the build's mod number `number`: `NNN-<slug>`."""
    return f"{number:03d}-{slug(title)}"
