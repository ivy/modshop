"""The key: everything that can change an entry's result, hashed.

Parent key and parent tree hash (so a change anywhere earlier propagates), the entry's canonical
form, the digests of its inputs, a fingerprint of the code that runs steps, and a fingerprint of
the environment the patcher runs in.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tomllib
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, NewType, cast

from modshop.core.hashing import sha256_file, sha256_text
from modshop.core.inputs import HashCache, InputResolver, InputRow
from modshop.core.recipe import Entry
from modshop.core.tree import TreeHash

Key = NewType("Key", str)
KEY_LEN = 16
VANILLA = Key("vanilla")


@dataclass(frozen=True, slots=True)
class KeyMaterial:
    parent: Key
    parent_tree: TreeHash
    entry: str
    inputs: tuple[InputRow, ...]
    code: str
    env: str

    def key(self) -> Key:
        material = {
            "parent": self.parent,
            "tree": self.parent_tree,
            "entry": self.entry,
            "inputs": [asdict(r) for r in self.inputs],
            "code": self.code,
            "env": self.env,
        }
        return Key(sha256_text(json.dumps(material, sort_keys=True))[:KEY_LEN])


def canonical_entry(entry: Entry) -> str:
    """The entry as JSON, every field of every step, sorted keys. The whole form enters the key,
    defaults included, so two steps of different kinds can never dump alike."""
    body = {
        "mod": entry.name,
        "inputs": list(entry.inputs),
        "steps": [step.canonical() for step in entry.steps],
    }
    return json.dumps(body, sort_keys=True)


class Keyer:
    def __init__(self, resolver: InputResolver, cache: HashCache, code: str, env: str) -> None:
        self.resolver, self.cache, self.code, self.env = resolver, cache, code, env

    def input_rows(self, entry: Entry, *, full: bool = False) -> tuple[InputRow, ...]:
        rows: list[InputRow] = []
        for spec in entry.all_inputs():
            rows.extend(self.resolver.resolve(spec, entry.name).rows(self.cache, full=full))
        return tuple(rows)

    def material(self, parent: Key, parent_tree: TreeHash, entry: Entry) -> KeyMaterial:
        return KeyMaterial(
            parent, parent_tree, canonical_entry(entry), self.input_rows(entry), self.code, self.env
        )

    def key_of(self, parent: Key, parent_tree: TreeHash, entry: Entry) -> Key:
        return self.material(parent, parent_tree, entry).key()


# ---- the code fingerprint ----------------------------------------------------------------------


def _strip_docstrings(tree: ast.Module) -> ast.Module:
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            body = node.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                node.body = body[1:] or [ast.Pass()]
    return tree


def _is_type_checking_block(node: ast.stmt) -> bool:
    return isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"


def _imports(tree: ast.Module, package: str) -> set[str]:
    """Module names imported anywhere in the tree that belong to `package`, TYPE_CHECKING blocks
    excluded (those imports are for the type checker, not for what runs)."""
    found: set[str] = set()

    def within(name: str) -> bool:
        return name == package or name.startswith(package + ".")

    def visit(nodes: Iterable[ast.stmt]) -> None:
        for node in nodes:
            if _is_type_checking_block(node):
                visit(cast(ast.If, node).orelse)
                continue
            if isinstance(node, ast.Import):
                found.update(a.name for a in node.names if within(a.name))
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0 and within(node.module):
                found.add(node.module)
                found.update(f"{node.module}.{a.name}" for a in node.names)
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    visit([child])
                else:
                    body = getattr(child, "body", None)
                    if isinstance(body, list):
                        visit(cast(list[ast.stmt], body))

    visit(tree.body)
    return found


def _module_file(name: str) -> Path | None:
    try:
        spec = importlib.util.find_spec(name)
    except ModuleNotFoundError:
        return None
    if spec is None or spec.origin is None or not spec.origin.endswith(".py"):
        return None
    return Path(spec.origin)


def code_closure(root: str, package: str = "modshop") -> list[str]:
    """Every module of `package` reachable from `root` by a static walk of import statements."""
    seen: set[str] = set()
    todo = [root]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        file = _module_file(name)
        if file is None:
            continue  # a name that is an attribute, not a module
        seen.add(name)
        tree = ast.parse(file.read_text(), filename=str(file))
        todo.extend(sorted(_imports(tree, package) - seen))
    return sorted(seen)


def code_fingerprint(root: str, package: str = "modshop") -> str:
    parts: list[str] = []
    for name in code_closure(root, package):
        file = _module_file(name)
        assert file is not None
        tree = _strip_docstrings(ast.parse(file.read_text(), filename=str(file)))
        parts.append(f"{name}\n{ast.dump(tree)}\n")
    return sha256_text("".join(parts))


# ---- the environment fingerprint ----------------------------------------------------------------


def lock_closure(lock: Path, root: str = "holopatcher") -> list[dict[str, object]]:
    """The packages reachable from `root` through `dependencies` in uv.lock, markers ignored:
    name, version, source and distribution hashes, sorted by name."""
    data: dict[str, Any] = tomllib.loads(lock.read_text())
    packages: list[dict[str, Any]] = [
        p for p in data.get("package", []) if isinstance(p, dict) and "name" in p
    ]
    by_name: dict[str, dict[str, Any]] = {str(p["name"]): p for p in packages}
    out: list[dict[str, object]] = []
    seen: set[str] = set()
    todo = [root]
    while todo:
        name = todo.pop()
        if name in seen or name not in by_name:
            continue
        seen.add(name)
        p = by_name[name]
        deps: list[dict[str, Any]] = [
            d for d in p.get("dependencies", []) if isinstance(d, dict) and "name" in d
        ]
        todo.extend(str(d["name"]) for d in deps)
        dists: list[dict[str, Any]] = [
            w for w in [p.get("sdist"), *p.get("wheels", [])] if isinstance(w, dict)
        ]
        hashes = sorted(str(w.get("hash", "")) for w in dists)
        out.append({"name": name, "version": p.get("version"), "source": p.get("source"), "hashes": hashes})
    return sorted(out, key=lambda p: str(p["name"]))


def env_fingerprint(lock: Path, sevenzip_version: str, python_version: str = sys.version) -> str:
    material = {"lock": lock_closure(lock), "python": python_version, "7zz": sevenzip_version}
    return sha256_text(json.dumps(material, sort_keys=True, default=str))


def override_env_fingerprint(package_dirs: Iterable[Path], python_version: str, sevenzip_version: str) -> str:
    """For a patcher from another environment: every .py under the given package directories,
    as that interpreter resolves them, so an editable checkout's edit changes the key."""
    files: list[str] = []
    for d in package_dirs:
        files.extend(f"{p.relative_to(d).as_posix()} {sha256_file(p)}" for p in sorted(d.rglob("*.py")))
    material = {"files": files, "python": python_version, "7zz": sevenzip_version}
    return sha256_text(json.dumps(material, sort_keys=True))
