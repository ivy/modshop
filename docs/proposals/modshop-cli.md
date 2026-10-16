# Proposal: modshop as a Python application

Status: accepted on 2026-10-15, all five decisions as recommended; implementation in progress. The fork for decision 1 is [ivy/PyKotor](https://github.com/ivy/PyKotor), branch `modshop-patches`. [`kotor-build-pipeline.md`](kotor-build-pipeline.md) is the pipeline this document restructures; its goals and determinism rules stand unchanged.

## Summary

The KotOR pipeline under `games/kotor/build/` becomes one installable Python package, `modshop`, with the command `modshop kotor <command>`, a typed domain model, a test suite, and one environment managed by uv. Scope is the scripts that exist today: nothing new is built, and what the port adds is structure, tests, one environment, and a key that is harder to get wrong. The port is accepted when the rebuilt chain reaches the same tree hash at every entry as the chain built today, and when a real deploy of it leaves a clean drift check.

The decisions the plan rests on, each argued below:

1. **pykotor from a public fork commit** pinned in the lockfile, rather than patched after install ([The patcher's library](#the-patchers-library)). The fork exists.
2. **Code at `src/modshop/`** at the repository root; `games/kotor/` keeps documentation, data and evidence ([Package layout](#package-layout)).
3. **The recipe stays Python**, with its canonical JSON committed beside it as a generated, checked file ([Recipe](#the-recipe)).
4. **typer and pydantic** as the application's own dependencies, plus what the scripts already need ([Libraries](#libraries)).
5. **"Recipe"** as the name of the ordered entries; "manifest" keeps meaning a tree's file listing ([The domain](#the-domain)).

## Why

The pipeline works: 190 entries build in 25 minutes, a no-op rebuild takes a second, `prove` passes, deploys are by content. It is also ten scripts with no tests. The driver is 800 lines of module-level globals; its verbs run only against one global working tree; its key function hashes its own source file minus an allowlist of function names, which fails toward not rebuilding when a helper moves; the recipe generator lists the archive directory at import time; the deploy script carries a second copy of path resolution. A fix to a verb is verified by a full rebuild because nothing smaller can run one. The ideas under [`../../games/kotor/docs/ideas/`](../../games/kotor/docs/ideas/) (try an entry without committing, audit the patcher's claims, inspect resources) all need the verbs, the tree and the patcher as objects callable from somewhere other than the chain walk.

## Goals and non-goals

Goals:

- Every piece of behaviour is a typed object or function that runs against paths it is given, so it can be unit-tested on a ten-file synthetic game and reused by a command that is not "build the whole chain".
- The determinism properties hold by construction and are tested: nothing changed means nothing happens, one change rebuilds the tail and ships only the paths it altered, a clean build matches the cached one, and every input kind and every step field moves the key.
- One command, one environment, one lockfile, with the patcher's library pinned in the same lockfile as the tool.
- The data on disk keeps working: the vanilla tree, the checkpoint layout, the manifest format, `meta.json`'s fields, the tags and the archives are read as they are.

Non-goals:

- A second game. `core` never imports `kotor`, and that rule is enforced by a test, because it keeps the layers honest; no abstraction is drawn for a game that does not exist. The command group `kotor` is a namespace, so a later project gets its own group without moving anything, and that is the whole provision.
- Any new capability. The ideas are not built here. [Room left for later](#room-left-for-later) names where each would plug in so the port does not close them off.
- Performance beyond today's. The chain is bound by the patcher's 16 minutes; the port must not slow the no-op case or the hashing.
- Engines that are not installed by ordered, in-place mutation of one tree. The chain model fits that and nothing else, and says so.

## The domain

Terms, each a type, with what it owns on disk. One rename: the ordered list of mods is a **recipe**, because "manifest" already means a tree's file listing here, a Steam depot's content list, and KMRP's install record. The rename touches the game README, the pipeline proposal and four idea files, which the cutover phase updates.

| Term | What it is | On disk |
| --- | --- | --- |
| **Tree** | A game folder: a directory root and nothing more. | any directory |
| **Manifest** | The sorted listing of a tree: path to file digest and size, or symlink target. Its own SHA-256 is the **tree hash**. | `manifest.txt` |
| **ChangeSet** | The difference between two manifests: added, removed, changed paths. | `changed.txt` |
| **Base** | The vanilla game as a definition: app, depot and depot-manifest ids, and the tree hash they must produce. | `base.json` in the repo; `data/game/vanilla/` holds the download |
| **Input** | Something an entry reads, named by a stable spec string: an archive folder or one archive file under `data/archives/`, a file or folder in the repo, a path under `data/`, a value from `local.toml`, a container image. Each yields hash rows. | the spec strings in the recipe |
| **Step** | One operation on a tree given a stage. A frozen model per kind with `apply`, and `inputs()` naming what it reads besides the stage. | the recipe |
| **Entry** | A named unit of the build: explicit inputs, steps, or a skip reason. Checkpoint granularity. | the recipe |
| **Recipe** | The ordered entries, in Python, and their canonical JSON. | `recipe.py`, `recipe.json` |
| **KeyMaterial**, **Key** | Everything that can change an entry's result (parent key, parent tree hash, canonical entry, input hashes, code fingerprint, environment fingerprint) and the 16-hex-digit hash of it. | `meta.json` |
| **Checkpoint** | An immutable tree with its manifest, change set and metadata, named by key. The vanilla tree is the checkpoint with key `vanilla` and no parent. | `data/game/ckpt/<key>/`, `data/game/vanilla/` |
| **Store** | A directory of checkpoints; the only code that writes one. A `Store` is a parameter, not a global, so two can be open at once. | `data/game/ckpt/` |
| **WorkTree** | The one mutable tree, a reflink copy of a checkpoint, with a record of which, or a record that it is dirty. | `data/game/work/`, `work.json` |
| **Stage** | An entry's inputs extracted to a scratch folder for the duration of its steps. | `data/stage/<entry>/` |
| **Chain** | The recipe resolved against a store: for each entry its key and its checkpoint if one exists, up to the first that does not. | computed |
| **Tags** | Names for keys; what `gc` keeps besides the chain. | `data/game/tags/<name>` |
| **Target** | The handheld as a deploy destination: a transport, the game folder, the paths outside the comparison and the ones sent only when absent. | transport and folder from `local.toml`; the path lists in `kotor` |
| **Drift** | What differs between a tree and the target's folder, by path. | computed |

Three things the table leaves implicit:

- **A step declares what it reads.** The repair script, the KMRP installer with its Containerfile, image and `local.toml` values, the controller module: today each is listed by hand in the entry's `inputs` beside the step that uses it, and a forgotten one is exactly the hidden input the key exists to catch. In the model the step's `inputs()` returns them and the entry's key material is the union of its own inputs and its steps'. An entry's `inputs` is always explicit; the recipe's constructors supply the archive folder named like the entry, so there is no `None` that means one thing and empty tuple that means another.
- **Entry names are the identity** of an entry across recipe edits and across stores. They are the archive folder names (`170-jc-s-blaster-adjustment`) or chosen ones (`kmrp`), as today, and `meta.json` carries them in its `mod` field, which keeps its name.
- **The game-specific surface is small**: the step kinds, the step context, the path rules, the patcher runner, the KMRP container run, the base provider, the deploy exclusions, and the recipe. Manifests, keys, checkpoints, the work tree, the stage, the chain and the deploy mechanics never import from the game.

### Types

The shapes that matter, with the fields that will be written.

```python
# modshop/core/tree.py
@dataclass(frozen=True, slots=True)
class File:
    digest: str
    size: int

@dataclass(frozen=True, slots=True)
class Symlink:
    target: str

class Manifest(Mapping[str, File | Symlink]):
    """Sorted by path bytes; immutable; its canonical text hashes to the tree hash."""
    @classmethod
    def of_tree(cls, root: Path, *, prior: Manifest | None = None, since_ns: int | None = None) -> Manifest: ...
    @classmethod
    def read(cls, path: Path) -> Manifest: ...
    def write(self, path: Path) -> TreeHash: ...
    @property
    def tree_hash(self) -> TreeHash: ...
    def diff(self, other: Manifest) -> ChangeSet: ...

def normalise_mtimes(root: Path, mtime_ns: int) -> int: ...
```

```python
# modshop/core/recipe.py   (core knows what a step is for keying; running one is the game's business)
class Step(Protocol):
    @property
    def do(self) -> str: ...
    def inputs(self) -> tuple[str, ...]: ...
    def canonical(self) -> dict[str, object]: ...   # every field, including `do` and defaults

@dataclass(frozen=True)
class Entry:
    name: str
    inputs: tuple[str, ...]
    steps: tuple[Step, ...] = ()
    skip: str | None = None
    def all_inputs(self) -> tuple[str, ...]: ...    # own inputs plus each step's, deduplicated, ordered
    def canonical(self) -> str: ...                 # JSON, sorted keys, in full

@dataclass(frozen=True)
class Recipe:
    entries: tuple[Entry, ...]
    def active(self) -> tuple[Entry, ...]: ...

Runner = Callable[[Entry, WorkTree, Stage], None]   # what the game gives the Builder: run this entry's steps here
```

`core` never calls a step. It keys entries, which needs `do`, `inputs()` and `canonical()`, and it hands each entry to a `Runner` the game supplies; `kotor`'s runner builds the `StepContext`, narrows each step to `StepModel` (the one base every KotOR step kind extends, which is where `apply` is declared), and calls it. A step that is not a `StepModel` is a `RecipeError`. There is no type variable and no second-game abstraction, and the protocol has only read-only members so that a frozen pydantic model satisfies it under pyright strict. Phase 1 includes a thirty-line spike of exactly this seam, type-checked strict, before anything else is written against it. `Entry` is a dataclass holding step objects, not a pydantic model over a union: the recipe is constructed in Python, so there is no JSON to parse and nothing to discriminate. The steps themselves are pydantic models so that a wrong field fails at construction with its name.

```python
# modshop/core/key.py
@dataclass(frozen=True)
class KeyMaterial:
    parent: Key
    parent_tree: TreeHash
    entry: str                       # Entry.canonical()
    inputs: tuple[InputRow, ...]     # (spec, relative path, digest)
    code: str
    env: str
    def key(self) -> Key: ...

class Keyer:
    """Holds the two fingerprints and the input hash cache; keys entries against a parent."""
    def key_of(self, parent: Key, parent_tree: TreeHash, entry: Entry) -> Key: ...
```

```python
# modshop/core/checkpoint.py   (fields are meta.json's, names kept)
@dataclass(frozen=True)
class Checkpoint:
    key: Key                         # 16 hex digits, or the literal "vanilla"
    parent: Key | None
    mod: str                         # the entry name
    tree: TreeHash
    files: int
    built_at: str
    changed: int | None = None       # absent on the vanilla row
    seconds: float | None = None

class Store:
    def __init__(self, ckpt_dir: Path, vanilla_dir: Path) -> None: ...
    def get(self, key: Key) -> Checkpoint | None: ...
    def tree(self, key: Key) -> Path: ...
    def manifest(self, key: Key) -> Manifest: ...
    def commit(self, work: WorkTree, key: Key, parent: Key, entry: Entry, since_ns: int) -> Checkpoint: ...
    def lineage(self, key: Key) -> list[Checkpoint]: ...    # key, its parent, ... up to vanilla
    def remove(self, key: Key) -> None: ...
    def keys(self) -> list[Key]: ...
```

```python
# modshop/core/chain.py
@dataclass(frozen=True)
class Link:
    entry: Entry
    key: Key
    checkpoint: Checkpoint | None

def resolve(recipe: Recipe, store: Store, keyer: Keyer) -> list[Link]: ...

class Builder:
    def __init__(self, recipe: Recipe, store: Store, work: WorkTree, keyer: Keyer, stages: StageFactory, run: Runner) -> None: ...
    def build(self, until: Collection[str] = ()) -> BuildResult: ...
    def prove(self, scratch: Store, scratch_work: WorkTree) -> ProveResult: ...

StageFactory = Callable[[Entry], AbstractContextManager[Stage]]   # extracts the entry's inputs, removes them after

@dataclass(frozen=True)
class BuildResult:
    links: tuple[Link, ...]      # the chain as built; the last link is the chain end
    rebuilt: int

@dataclass(frozen=True)
class ProveResult:
    reproducible: bool
    first_difference: Link | None
    differing_paths: tuple[str, ...]
```

```python
# modshop/kotor/context.py
@dataclass(frozen=True)
class StepContext:
    game: GameTree          # the work tree with the game's path rules
    stage: Stage
    paths: Paths            # data root, archives, the game directory in the repo
    handheld: Handheld      # the three local.toml values the KMRP step needs, not the whole file
    patcher: Patcher
    log: logging.Logger
```

The context is a bundle, and bundles are where mud starts; it stays acceptable because it is frozen, built in one place by the runner, and holds nothing a step cannot name in its `inputs()`. A field added to it is a review question, not a convenience.

```python
# modshop/kotor/steps.py   (one frozen pydantic model per kind)
class StepModel(BaseModel, frozen=True):
    def inputs(self) -> tuple[str, ...]: return ()
    def canonical(self) -> dict[str, object]: return self.model_dump(mode="json")
    def apply(self, ctx: StepContext) -> None: raise NotImplementedError

class GameDir(BaseModel, frozen=True):   kind: Literal["game"] = "game"
class StageDir(BaseModel, frozen=True):  kind: Literal["stage"] = "stage"
class ArchivePath(BaseModel, frozen=True):
    kind: Literal["archive"] = "archive"
    rel: str
    @property
    def spec(self) -> str: return self.rel
ScriptArg = GameDir | OverrideDir | StageDir | ArchivePath | DataPath | Word   # each with its own `kind`, so no two dump alike

class Copy(StepModel):
    do: Literal["copy"] = "copy"
    src: str = "."
    pattern: str = "*"
    exclude: tuple[str, ...] = ()
    recursive: bool = False
    dest: str | None = None

class Script(StepModel):
    do: Literal["script"] = "script"
    path: str                                   # an input spec: "./..." or "data/..."
    args: tuple[ScriptArg, ...] = ()
    reads: tuple[str, ...] = ()                 # further input specs; repair() sets the whole repair folder, README included, as today
    def inputs(self) -> tuple[str, ...]: return (self.path, *self.reads, *(a.spec for a in self.args if a.spec))

class HoloPatcher(StepModel):
    do: Literal["holopatcher"] = "holopatcher"
    src: str = "*/tslpatchdata"
    option: int | None = None
    allow_errors: int = 0

class Kmrp(StepModel):
    do: Literal["kmrp"] = "kmrp"
    installer: str
    settings: KmrpSettings
    image: str = "modshop-wine"
    def inputs(self) -> tuple[str, ...]: ...   # the installer, the Containerfile, image:, the three local: values
```

```python
# modshop/kotor/patcher.py
class Patcher(Protocol):
    def install(self, game: Path, tslpatchdata: Path, *, option: int | None, log_to: Path) -> PatchReport: ...

@dataclass(frozen=True)
class PatchReport:
    errors: int
    log: Path
```

```python
# modshop/core/deploy.py
class Transport(Protocol):
    def run(self, cmd: str, *, check: bool = True) -> CompletedProcess[str]: ...
    def rsync_dest(self, path: str) -> str: ...
    def snapshot(self, src: str, dst: str) -> None: ...     # reflink copy on the target; plain copy in LocalTransport

@dataclass(frozen=True)
class Target:
    transport: Transport
    game_dir: str
    exclude: tuple[str, ...]
    first_time: tuple[str, ...]
    process: str                  # the game's process name; a deploy refuses while it runs

class Deployer:
    def drift(self, tree: Path) -> Drift: ...
    def deploy(self, tree: Path) -> DeployResult: ...
```

### The recipe

`recipe.py` builds the entries with typed constructors (`mod(170, repair("09-blaster-adjustment-orphan-rows", StageDir()), holopatcher(option=1))`). Entry names come from the committed `k1full.json` through the same slug rule the downloader uses to name archive folders, which moves to one function both import; the one archive file name the recipe needs (mod 157's, for repair 08) is written as a literal. The recipe therefore reads nothing under `data/`, `recipe.json` is the same on every machine, and the sync test runs on a clean clone. The archive folder for an entry is resolved at build time from its name, as every other input is. `modshop kotor recipe write` dumps every entry's canonical form to `recipe.json` beside it, which is committed: it is the reviewable, diffable artifact that `manifest.json` is today and the exact text that enters the key. A test fails when the two are out of sync. `--recipe PATH` points a command at another module, which is what `KOTOR_MANIFEST` does now.

### What stays the same on disk

The checkpoint layout, the manifest text, `meta.json` with its `mod` field, `work.json`, the tags and `base.json` are read and written as they are. Keys will differ after the port because the fingerprints and the canonical entry are computed differently, so the first build rebuilds the chain once; the old checkpoints stay readable, and the acceptance test reads them. Three changes: the archive hash cache moves from `archives/.hashcache.json` to `data/hashcache.json` and is keyed by path relative to the archives directory, since the archives can be reached by more than one path and are not the tool's to write into (the old file is left where it is); `work.json` can record `dirty` (below); and `base index` compares the vanilla tree's hash with `base.json` and refuses a mismatch unless told to update the record, which nothing does today.

## Package layout

One installable package at the repository root. Game directories keep what is not code.

```text
pyproject.toml
uv.lock
src/modshop/
  __main__.py
  cli/                 typer app: `modshop kotor <command>`; commands parse, call one object, print
  core/
    config.py          Paths; Local (typed local.toml), Handheld
    tree.py            File, Symlink, Manifest, ChangeSet, normalise_mtimes
    clone.py           Cloner (reflink and hardlink copies, the reflink probe); the plain-copy Cloner the tests use
    inputs.py          Input kinds, parsing, hashing with the cache
    key.py             KeyMaterial, Keyer, code and environment fingerprints
    checkpoint.py      Checkpoint, Store
    worktree.py        WorkTree, with the dirty record
    stage.py           Stage
    extract.py         Extractor (7zz, the backslash-name fix)
    recipe.py          Step, Entry, Recipe, Runner
    chain.py           Link, resolve, Builder
    deploy.py          Target, Transport, SshTransport, LocalTransport, Deployer, Drift
    errors.py          ModshopError and its kinds
  kotor/
    context.py         StepContext
    paths.py           case-insensitive lookup, GameTree
    steps.py           the step kinds, ScriptArg
    patcher.py         Patcher protocol, HoloPatcherCli, PatchReport (FakePatcher lives in tests)
    kmrp.py            the installer's container run and the state-file normalisation
    base.py            Base from base.json, the DepotDownloader run
    archives.py        download.py and megadl.py as functions; the slug rule the recipe shares
    runner.py          run_entry: builds the StepContext, applies the steps
    recipe.py          the K1 Full Build
tests/
  unit/                one module per core and kotor module
  integration/         the synthetic game, end to end
  real_fs/             the few tests that need the data filesystem; skipped when it is absent
  conftest.py          fixtures: synthetic vanilla, archives as zips, FakePatcher, the plain-copy Cloner
games/kotor/
  README.md docs/ repairs/ patches/ kmrp-build/ fixes/ data/
  base.json recipe.json k1full.json dsfiles.json nexusfiles.json cleanlist_k1.txt
```

The dependency rule: `core` imports nothing from `kotor`; `cli` imports both; only `kotor.patcher`'s subprocess runner knows the patcher's command line, and nothing in the package imports `pykotor`. A test walks each module's imports and asserts the first.

The repairs stay as they are: a folder with `make.py` and a README, run by the `Script` step with the tool's interpreter in isolated mode, which is what the conventions define a repair to be. Each gets a test with a fixture input, which none has today. `install-controller.py` under `kmrp-build/` likewise.

## Libraries

Chosen for being standard, documented and no larger than the job. Runtime dependencies, all of them:

| Package | Why |
| --- | --- |
| **typer** (brings click, rich, shellingham) | Commands are functions with typed parameters; groups are free. Rich arrives with it and is used for nothing but what typer uses it for; output is plain text. |
| **pydantic v2** | The step models, `local.toml` and `base.json`: a bad field fails at construction with its name, and the canonical JSON is one method call. Dataclasses would need hand-written validation for every step kind. `meta.json` and `work.json` are the tool's own output and are read into dataclasses with `json`. |
| **holopatcher** 1.5.3, with **pykotor** from the fork | The patcher. holopatcher requires `pykotor>=2.0.0`, so a git source for pykotor satisfies it. |
| **pycryptodome** | `megadl.py` imports it; the patcher's venv does not provide it. |
| **Pillow**, in an optional `repairs` group | Repair 07 imports it. That repair is not in the recipe; if it enters, its interpreter's packages must join the environment fingerprint, since a script's dependencies are not keyed today. |

Internal values (manifest rows, keys, checkpoints, links) are frozen dataclasses with slots: created in the thousands per build, never parsed from untrusted input.

Development: uv (from mise) for the environment and lockfile, pytest, ruff for lint and format, pyright strict. `mise run check` runs all three; hk runs them on commit, as the homestead repository does. The build host needs a Python with tkinter, because HoloPatcher imports it even on the console; that is a property of the interpreter mise installs, and the README keeps saying so.

### The patcher's library

Today `setup-venv.sh` installs HoloPatcher from PyPI and applies the six patches under `games/kotor/patches/pykotor/` to `site-packages` with `patch`. That cannot survive `uv sync`, which rebuilds the environment from the lockfile; worse, uv hardlinks installed files from its cache on Linux, so patching them in place would corrupt the cache for every other environment unless the link mode is set to copy. Two ways out:

1. **A fork commit in the lockfile.** Push the series branch of the PyKotor clone to a public fork and pin `pykotor` to that commit in `[tool.uv.sources]`, as the commit's source archive with `subdirectory = "Libraries/PyKotor"` rather than a git source, because uv clones a git source's submodules and the monorepo has twenty, several on repositories that no longer exist. The series under `patches/pykotor/` stays what the conventions say it is: the exported form of that branch, regenerated with `git format-patch` when the branch moves, with its README naming the base commit and the branch. Verified in phase 1: uv builds the `Libraries/PyKotor` subdirectory as a package with the `loggerplus` and `utility` modules the wheel ships, and the installed files match the fork head.
2. **Patch after sync.** Keep the series as the source of truth and apply it in a post-sync step with the copy link mode. Simpler to set up; fragile on every environment rebuild, and the environment fingerprint must then be computed from the installed files rather than the lockfile.

The first is the recommendation. It costs one public fork holding no game bytes, and the push is yours.

A patch in progress reaches a build the way it does today: `MODSHOP_PATCHER` names another `holopatcher` executable (today's `HOLOPATCHER`), the environment fingerprint is then taken from that environment's installed files ([The key](#the-key)), and the build says on its first line which patcher it runs.

The patcher runs as a subprocess, as today: the command line is its supported interface, a crash or hang in it must not take the build down, the timeout stays, and the log is the artifact. `HoloPatcherCli` runs it from the tool's environment; a `FakePatcher` serves the tests.

## The key

The same six things as today. Three are computed differently, each tested.

The **code fingerprint** is the hash of the syntax trees, docstrings stripped, of every `modshop` module reachable from `kotor.runner` by a static walk of `import` statements: `from` and plain imports at any depth, `TYPE_CHECKING` blocks excluded, `__init__.py` files required empty by a test so a package import brings in nothing by itself. Reachable today: the runner, the context, the steps, the path rules, the patcher runner, the KMRP run, the stage and the extractor, and through them `core.config`, `core.inputs` and `core.errors`. The closure is computed, not declared, so a helper moved to a new module cannot fall out of the key by omission, which is the failure mode of today's allowlist of orchestration names; and its member list is pinned in a golden test, so a module entering or leaving it is a visible change in review rather than a silent one. The cost is that an edit to `core.config` rebuilds the chain even when it touches nothing a step reads; the context's `Handheld` field keeps that surface small. Tests: a comment or docstring edit inside the closure leaves the fingerprint alone; a change to a step's body changes it; the chain walk, the store, the deploy and the command line are outside it, which is also the dependency rule tested from the other side, since a step that imported the store would key it.

The **environment fingerprint** is the hash of the patcher's closure in `uv.lock`: starting at the `holopatcher` package entry, every package reachable through `dependencies`, markers ignored so the walk is the same on every platform, each contributing its name, version, source (the git commit for pykotor) and distribution hashes; plus the version of the Python the tool runs and of 7-Zip. A typer or pytest bump does not rebuild the chain; a pykotor commit does. Preflight checks, through `importlib.metadata` and the `direct_url.json` a git install carries, that each package in that closure is installed at the locked version and commit, and refuses to build otherwise, so the fingerprint describes what will run. Under `MODSHOP_PATCHER` the fingerprint is instead the hash of every Python source file under the `pykotor` and `holopatcher` package directories as that environment's interpreter resolves them (`python -c 'import pykotor; print(pykotor.__path__)'`, then a walk), plus that environment's Python version. Resolving through the import system rather than through the distributions' `RECORD` files is what makes an editable install's uncommitted edit change the key, which is the case the override exists for.

The **canonical entry** is the entry dumped in full: sorted keys, every field of every step including its `do` and its defaults. Leaving defaults out would make `Copy(src="*")` and `HoloPatcher(src="*")` dump identically and let an edit from one to the other keep its key.

Two tests carry the completeness argument. A golden test pins a key material fixture to its key, so the function cannot change by accident; when it must, the commit says the chain rebuilds. A perturbation test on the synthetic game changes, one at a time, each input kind (an archive file, a repo file, a `data/` file, a `local:` value, an `image:` digest), each field of each step kind, one script argument kind swapped for another, a step's order, a parent's tree, and asserts that the key moves every time and stays put for a no-op edit. The cutover repeats the real-chain mutation run from the pipeline proposal (a changed display value rebuilds exactly the KMRP entries) before the old scripts are removed.

## Commands

`modshop kotor <command>`: a thin layer that builds objects from configuration, calls one method, prints, and maps the exception kind to an exit status.

| Today | New | Notes |
| --- | --- | --- |
| `build.py [MOD...]` | `build [--until ENTRY]...` | |
| `build.py status` | `status` | |
| `build.py base` | `base index` | the vanilla tree's manifest, checked against `base.json` |
| `base.sh ACCOUNT` | `base fetch ACCOUNT` | the DepotDownloader run |
| `build.py verify [KEY]` | `verify [KEY]` | default: the chain end of the last completed build, the `build` symlink, as today |
| `build.py verify-inputs` | `verify --inputs` | |
| `build.py checkout KEY DIR` | `checkout KEY DIR` | |
| `build.py tag NAME [KEY]` | `tag NAME [KEY]` | |
| `build.py gc --keep N` | `gc --keep N` | keeps the chain, every tagged key, and the N most recently written others, as today |
| `build.py prove` | `prove` | rebuilds the chain uncached into a scratch store and compares, as today |
| none | `compare DIR [KEY]` | cutover only: the lineage of KEY in the store under DIR (default: its `known-good` tag), vanilla included, against this store's chain from vanilla, paired by position; equal length, names and tree hashes required |
| `deploy.py [KEY]` | `deploy [KEY]` | default: the `build` symlink |
| `deploy.py --check` | `deploy --check [KEY]` | exit 1 on drift, as today |
| `manifest.py` | `recipe write`, `recipe show [ENTRY]` | |
| `download.py KEYFILE`, `megadl.py URL...` | `archives fetch KEYFILE`, `archives mega URL...` | the same code as functions; `download.py` runs at import today |
| `setup-venv.sh` | `uv sync` | |

That is the whole surface: every current command, `compare` for the port's own acceptance, and no new capability. Configuration: the data root from `--data`, then `KOTOR_DATA`, then `games/kotor/data`; `local.toml` from the repository root, parsed when a key or a deploy needs it (`status` on a complete chain keys the KMRP entry, so it needs the file and the container image too, as today); the patcher from `MODSHOP_PATCHER`, then the environment's. The unused `[build_host] data` key leaves `local.example.toml`.

`known-good` is a tag set by hand after the deployed build has been played, which is what happens today; the pipeline proposal says in two places that a passing deploy sets it, and phase 5 edits those two sentences to match. `compare` defaults to the legacy store's `known-good` because that is the chain that was played.

## Errors, logging, interruption

`ModshopError` is the base of every expected failure: `RecipeError` (entry and field), `InputMissing` (spec and path), `StepFailed` (entry, step index, cause, log path), `NotReproducible` (entry and differing paths), `Locked`, `Preflight` (no reflinks, no base, no patcher, environment out of sync). The command prints the message and exits 1; anything else is a bug and shows its traceback.

A build logs to `data/logs/build.log` through `logging`, one line per step, and the same to the console. Each patcher run keeps its own log under `data/logs/holopatcher/`, named by entry and step index, since one entry runs up to three.

One build at a time, by a file lock on the data directory. The work tree's record is set to `dirty` before an entry's first step and to the new key only by the commit, so a tree left by a build killed by any means (SIGKILL, out of memory, a reboot) is restored from its parent on the next run rather than reused; today the record changes only at commit, and a killed run would replay the entry's steps on a half-modified tree whose same-size files the ctime shortcut would then mis-hash. SIGTERM and SIGINT are handled like a failing step: the work tree is discarded and the run exits non-zero. A commit interrupted between writing `<key>.tmp` and the rename leaves the `.tmp`, which preflight removes, as today. The KMRP step's container outlives a killed client and would keep writing into the tree the next run discards, so the step runs it under a fixed name and preflight removes any container by that name before touching the work tree.

## Testing

**Unit**, one module per module. Those that carry the determinism argument: `Manifest.of_tree` with and without a prior manifest and a since time, on files touched and untouched; the manifest round trip with a path containing a space and a symlink; the key golden and perturbation tests; the fingerprint tests; input parsing for every kind, and the hash cache on a changed file; every path-rule case the current driver handles (exact, case variant, wildcard, the wrapper-folder descent, the backslash); every step on a small tree with a hand-made stage, including the case collapse after a patcher run; `Store.commit` with the plain-copy cloner, asserting hardlinks to the parent for unchanged paths and new inodes for changed ones; the deploy planner and the deploy itself against `LocalTransport`.

**Integration**, on a synthetic game: a vanilla of a dozen files with `Override`, `modules` and a `dialog.tlk`, archives made by the test as zips, a recipe of six entries using every step kind, and a `FakePatcher` that writes what it is told and returns a report. Scenarios: a build; a second build that does nothing and ends at the same key; a change to one archive that rebuilds that entry and the three after it and leaves the two before untouched; `prove` against the cached store; a step that raises mid-entry, leaving the work tree discarded and the next build resuming; a build killed with SIGKILL mid-entry whose next run restores the parent; a commit interrupted at each of its stages, after which the next run recovers; `gc` keeping tagged and in-chain checkpoints; `deploy` to a local directory, then a clean drift, then drift after a file is edited there, then the swap and the `.prev` rollback folder. These run on tmpfs with the plain-copy cloner.

**Real filesystem**, skipped when the data directory is absent: the reflink probe; and one test with the real cloner where the fake patcher truncates and rewrites an existing file in place, asserting the parent checkpoint's bytes are unchanged, which is the invariant the hardlink design rests on and which tmpfs cannot exercise. The allocation-group exhaustion is not testable and is documented instead.

**Acceptance**, at the cutover, recorded in this document: `compare` against the legacy store; the mutation run; a real deploy of the checkpoint before the chain end followed by the chain end, which exercises the write path and the swap twice; a clean `deploy --check`. The rollback itself is a rename of `.prev` by hand and is documented, not tested.

Coverage is not a target. The determinism properties, every path rule and the interruption cases are, because those are where the defects have been.

## Room left for later

The port builds none of the ideas, but a model that cannot grow toward them would be the ball of mud with types. These are the seams, each present for its own reasons, that the ideas most likely to be built would use. None costs anything now.

- **Try an entry without committing.** `Builder` runs steps against the `WorkTree` and `Store` it is given, and `Store.commit` is a separate call; a try is one entry into a second work tree with no commit.
- **Patcher audit.** `Patcher.install` returns a report that holds the log path; the audit adds parsed claims and a check between the patcher step and the commit, with the stage, the tree and the change set already in hand.
- **Inspect.** `GameTree` is the one place that knows the game's path rules; an inspect command is a reader over it and a `Store`, and would be the first code in the package to import pykotor.
- **Impact.** `resolve` is a pure function of recipe, store and keyer; printing its first miss is the command.
- **Pinned archives.** Input hashing goes through one cache object; a committed index replaces its trust in size and mtime at that one point.

The rule that keeps the next idea from re-forming the mud: a new capability is a new command over existing objects, or one new object with its own tests, never a branch inside a step.

## The plan

Each phase ends with the repository working and is one or a few commits. The old scripts and their data directory run untouched until phase 5. Until then the new tool works in a sibling data root, `games/kotor/data-next/`, whose `game/vanilla` is a reflink copy of the old one (same content, so the same tree hash) and whose `archives` and `kmrp-build` are symlinks to the old root's, since both are read-only inputs; its hash cache is the new one described above, so it neither writes the old tool's cache nor misses it for being reached by another path (the first run rehashes once). Neither tool's `gc` can then see the other's checkpoints, and `base index` rewrites only the sibling's vanilla manifest. Two chains on the filesystem is what `prove` already produces; the hardlink checkpoints are not the whole-tree clones that exhausted the metadata pool.

1. **Scaffold.** `pyproject.toml`, `uv.lock`, the empty package, ruff and pyright configuration, pytest, `mise.toml` with uv and the `check` and `test` tasks, hk hooks. Decision 1 is taken here because the lockfile needs it, and the subdirectory build of the fork is verified.
2. **Tree and key.** `core/tree.py`, `clone.py`, `inputs.py`, `key.py`, `config.py`, `checkpoint.py` (read side) with their tests. First commands: `base index` on the sibling root, and `verify` and `verify --inputs` pointed at the old root's checkpoints and archives with the new tool's own cache; they must agree with the current driver on every checkpoint's manifest and every archive hash.
3. **The chain.** `worktree.py`, `stage.py`, `extract.py`, `recipe.py`, `chain.py`, the commit side of the store; `kotor/context.py`, `runner.py`, `paths.py`, `steps.py`, `patcher.py`, `kmrp.py`, the slug rule in `archives.py` (the rest of that module comes in phase 6), `recipe.py` as a port of `manifest.py`, and `recipe.json`. The integration and real-filesystem suites. Commands: `build`, `status`, `checkout`, `tag`, `gc`, `prove`, `compare`, `recipe write`, `recipe show`.
4. **Deploy.** `core/deploy.py` with both transports and its tests; `deploy`, `deploy --check`.
5. **Cutover.** `compare` against the legacy store, then the mutation run, then the two real deploys and the drift check. Then `build.py`, `manifest.py`, `manifest.json`, `deploy.py` and `setup-venv.sh` are removed; the old root's `game/ckpt` is renamed `game/ckpt-legacy` and its `game/vanilla` is replaced by the sibling's; the sibling's `game/ckpt`, `game/work`, `game/tags` and `hashcache.json` move into the old root, its two symlinks are deleted, and a no-op `build` rewrites the absolute `build` symlink; the legacy store is kept until a `gc` after the port has been used for a while; the game README, the pipeline proposal (the two `known-good` sentences; its `gc --keep-last` for the real `--keep`; and its claim that a change in one entry leaves later keys unchanged, which the key's inclusion of the parent key contradicts) and the idea files are updated for the commands and the rename; `known-good` is re-pointed by hand. A differing entry in `compare` is a bug in the port, and the cutover waits.
6. **Base and archives.** `kotor/base.py` as a port of `base.sh`; `kotor/archives.py` holds `download.py` and `megadl.py` wrapped into functions with their data files read from the game directory, behaviour unchanged, tested only for the slug rule and the mega key parsing, since the rest is network code against accounts. The three scripts are removed.

Phases 2 through 4 can overlap; 5 waits for all of them; 6 is independent after 1.

## Alternatives considered for the whole

- **Leave the scripts, add tests.** The verbs cannot be called without the module globals, the key function hashes the file it lives in, and the tests would be the integration suite only. The refactor is the precondition for the tests.
- **A build system (make, ninja, doit) with entries as targets.** The chain is linear and every target depends on all previous ones; a DAG tool adds a model with nothing in it, the key is richer than a file hash, and the artifacts are trees. Rejected for the reasons the pipeline proposal rejected ostree and DVC.
- **Another language.** The step logic is path manipulation and subprocess orchestration, the patcher is Python, and the inspect idea will want pykotor in-process. The problem was never the language.
