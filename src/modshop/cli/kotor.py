"""`modshop kotor <command>`."""

from __future__ import annotations

import json
import logging
import shutil
import sys
import time
from pathlib import Path
from typing import Annotated

import typer

from modshop.cli.common import exits_cleanly, paths_for, store_for
from modshop.core.chain import Builder, Link, not_reproducible, resolve
from modshop.core.checkpoint import Store
from modshop.core.clone import Cloner
from modshop.core.config import Local, Paths
from modshop.core.errors import Preflight
from modshop.core.inputs import HashCache, InputResolver
from modshop.core.key import VANILLA, Key, Keyer, canonical_entry
from modshop.core.lock import held
from modshop.core.recipe import Recipe
from modshop.core.stage import stage_factory
from modshop.core.tree import Manifest
from modshop.core.worktree import WorkTree
from modshop.kotor import base as base_mod
from modshop.kotor import kmrp
from modshop.kotor.recipe import recipe as load_recipe
from modshop.kotor.runner import runner
from modshop.kotor.toolchain import Toolchain

app = typer.Typer(no_args_is_help=True, help="Knights of the Old Republic.")
base = typer.Typer(no_args_is_help=True, help="The vanilla game.")
recipe_app = typer.Typer(no_args_is_help=True, help="The ordered entries.")
app.add_typer(base, name="base")
app.add_typer(recipe_app, name="recipe")

DataOpt = Annotated[
    Path | None, typer.Option("--data", help="The data root (default: KOTOR_DATA, then games/kotor/data).")
]
log = logging.getLogger("modshop")


# ---- wiring ---------------------------------------------------------------------------------------


class Session:
    """The objects a command needs, built once from the paths."""

    def __init__(self, paths: Paths) -> None:
        self.paths = paths
        self.cloner = Cloner()
        self.store = store_for(paths, self.cloner)
        self.recipe: Recipe = load_recipe(paths.game_dir)
        self.resolver = InputResolver(paths)
        self.cache = HashCache(paths.hashcache, paths.archives)
        self.toolchain = Toolchain.resolve(paths)
        self.keyer = Keyer(self.resolver, self.cache, self.toolchain.code, self.toolchain.env)

    def local(self) -> Local | None:
        return Local.load(self.paths.local_toml) if self.paths.local_toml.exists() else None

    def work(self, name: str = "work") -> WorkTree:
        return WorkTree(self.paths.games / name, self.paths.games / f"{name}.json")

    def builder(self, store: Store | None = None, work: WorkTree | None = None) -> Builder:
        local = self.local()
        run = runner(self.paths, self.toolchain.patcher, local)
        stages = stage_factory(self.paths.stage, self.resolver, self.toolchain.extractor)
        return Builder(
            self.recipe, store or self.store, work or self.work(), self.keyer, stages, run, self.cloner
        )

    def preflight(self) -> None:
        for d in (self.paths.ckpt, self.paths.stage, self.paths.logs, self.paths.tags):
            d.mkdir(parents=True, exist_ok=True)
        if self.store.get(VANILLA) is None:
            raise Preflight(
                f"no vanilla manifest under {self.paths.vanilla}; run `base fetch` then `base index`"
            )
        self.cloner.probe(self.paths.ckpt)
        self.store.clear_partial()
        kmrp.remove_stale_container()

    def logging_to_file(self) -> None:
        self.paths.logs.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(self.paths.logs / "build.log")
        handler.setFormatter(logging.Formatter("%(message)s"))
        log.addHandler(handler)

    def links(self) -> list[Link]:
        return resolve(self.recipe, self.store, self.keyer)

    def default_key(self) -> Key:
        if not self.paths.build_link.is_symlink():
            raise Preflight("no build yet; name a checkpoint")
        return Key(self.paths.build_link.readlink().parent.name)


def console_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)


def set_build_link(paths: Paths, store: Store, key: Key) -> None:
    link = paths.build_link
    if link.is_symlink():
        link.unlink()
    elif link.exists():
        raise Preflight(f"{link} is a directory, not the symlink the build writes; move it aside")
    link.symlink_to(store.tree(key))


# ---- commands -------------------------------------------------------------------------------------


@base.command("index")
@exits_cleanly
def base_index(
    data: DataOpt = None,
    update: Annotated[
        bool, typer.Option("--update", help="Rewrite base.json's tree hash from the tree.")
    ] = False,
) -> None:
    """Normalise the vanilla tree, write its manifest, and check its hash against base.json."""
    paths = paths_for("kotor", data)
    c = base_mod.index(store_for(paths), paths.game_dir / "build" / "base.json", update=update)
    print(f"vanilla: {c.files} files, tree {c.tree}")


@app.command()
@exits_cleanly
def build(
    until: Annotated[
        list[str] | None, typer.Option("--until", help="Stop after this entry (repeatable).")
    ] = None,
    data: DataOpt = None,
) -> None:
    """Build the chain, or resume it; nothing happens for entries whose checkpoint exists."""
    console_logging()
    s = Session(paths_for("kotor", data))
    s.preflight()
    with held(s.paths.lock):
        s.logging_to_file()
        log.info("--- build %s", time.strftime("%Y-%m-%dT%H:%M:%S%z"))
        result = s.builder().build(until=tuple(until or ()))
        s.cache.save()
        set_build_link(s.paths, s.store, result.end.key)
        assert result.end.checkpoint is not None
        log.info(
            "ALL DONE: %d rebuilt; build -> ckpt/%s/tree (tree %s)",
            result.rebuilt, result.end.key, result.end.checkpoint.tree[:12],
        )  # fmt: skip


@app.command()
@exits_cleanly
def status(data: DataOpt = None) -> None:
    """Which entries have checkpoints, without building."""
    s = Session(paths_for("kotor", data))
    links = s.links()
    s.cache.save()
    for link in links:
        tree = link.checkpoint.tree[:12] if link.checkpoint else " " * 12
        print(f"{'ok  ' if link.checkpoint else 'MISS'} {link.key} {tree} {link.entry.name}")
    if links and links[-1].checkpoint is None:
        print(f"  (and {len(s.recipe.active()) - len(links)} more after it)")
    elif len(links) == len(s.recipe.active()):
        print("up to date")


@app.command()
@exits_cleanly
def verify(
    key: Annotated[
        str | None, typer.Argument(help="A checkpoint key (default: the chain end of the last build).")
    ] = None,
    inputs: Annotated[
        bool, typer.Option("--inputs", help="Rehash every archive instead; report cache entries that lie.")
    ] = False,
    data: DataOpt = None,
) -> None:
    """Rehash a checkpoint's tree in full and compare it with its manifest."""
    s = Session(paths_for("kotor", data))
    if inputs:
        n = sum(len(s.keyer.input_rows(e, full=True)) for e in s.recipe.active())
        s.cache.save()
        for p in s.cache.lies:
            print(f"!! hash cache lied for {p}")
        print(f"{n} input files rehashed, {len(s.cache.lies)} cache entries were wrong")
        raise typer.Exit(1 if s.cache.lies else 0)
    k = Key(key) if key else s.default_key()
    if s.store.get(k) is None:
        raise Preflight(f"no checkpoint {k} under {s.store.ckpt}")
    diff = s.store.manifest(k).diff(Manifest.of_tree(s.store.tree(k)))
    for p in diff.paths():
        print(p)
    if diff:
        print(f"{k}: {len(diff.paths())} paths differ from the manifest")
        raise typer.Exit(1)
    print(f"{k}: matches its manifest ({len(s.store.manifest(k))} files)")


@app.command()
@exits_cleanly
def checkout(key: str, dest: Path, data: DataOpt = None) -> None:
    """A reflink copy of a checkpoint's tree at DEST, for a bisect or an experiment."""
    s = Session(paths_for("kotor", data))
    if dest.exists():
        raise Preflight(f"{dest} exists")
    if s.store.get(Key(key)) is None:
        raise Preflight(f"no checkpoint {key}")
    s.cloner.copy_tree(s.store.tree(Key(key)), dest)
    print(f"{key} -> {dest}")


@app.command()
@exits_cleanly
def tag(name: str, key: Annotated[str | None, typer.Argument()] = None, data: DataOpt = None) -> None:
    """Name a checkpoint (default: the chain end of the last build); gc keeps it."""
    s = Session(paths_for("kotor", data))
    k = Key(key) if key else s.default_key()
    if s.store.get(k) is None:
        raise Preflight(f"no checkpoint {k}")
    s.paths.tags.mkdir(parents=True, exist_ok=True)
    (s.paths.tags / name).write_text(k + "\n")
    print(f"{name} = {k}")


@app.command()
@exits_cleanly
def gc(
    keep: Annotated[
        int, typer.Option("--keep", help="How many non-chain, untagged checkpoints to keep.")
    ] = 5,
    data: DataOpt = None,
) -> None:
    """Remove checkpoints that are not in the chain, not tagged, and not among the newest N others."""
    s = Session(paths_for("kotor", data))
    live = {link.key for link in s.links() if link.checkpoint}
    if s.paths.tags.exists():
        live |= {Key(p.read_text().strip()) for p in s.paths.tags.iterdir()}
    rest = sorted(
        (k for k in s.store.stored_keys() if k not in live),
        key=lambda k: s.store.dir(k).stat().st_mtime,
        reverse=True,
    )
    before = shutil.disk_usage(s.store.ckpt).free
    for k in rest[keep:]:
        c = s.store.get(k)
        print(f"rm {k} {c.mod if c else '?'}")
        s.store.remove(k)
    freed = (shutil.disk_usage(s.store.ckpt).free - before) / 2**30
    print(
        f"kept {len(live)} in chain or tagged, {min(keep, len(rest))} recent others; df freed {freed:.1f} GiB"
    )


@app.command()
@exits_cleanly
def prove(data: DataOpt = None) -> None:
    """Build the chain again, uncached, into a scratch store, and compare it entry by entry."""
    console_logging()
    s = Session(paths_for("kotor", data))
    s.preflight()
    with held(s.paths.lock):
        s.logging_to_file()
        scratch = Store(s.paths.games / "ckpt-prove", s.paths.vanilla, s.cloner)
        scratch.ckpt.mkdir(exist_ok=True)
        for d in scratch.ckpt.iterdir():
            shutil.rmtree(d)
        scratch_work = s.work("work-prove")
        scratch_work.discard()
        log.info("--- prove %s", time.strftime("%Y-%m-%dT%H:%M:%S%z"))
        result = s.builder().prove(scratch, scratch_work)
        if not result.reproducible:
            for p in result.differing_paths[:50]:
                log.info("    %s", p)
            raise not_reproducible(result)
        log.info(
            "REPRODUCIBLE: %d entries rebuilt to the same tree hashes; ckpt-prove/ can be removed",
            result.entries,
        )


@app.command()
@exits_cleanly
def compare(
    legacy: Annotated[
        Path, typer.Argument(help="Another data root's game/ directory holding ckpt/, vanilla/ and tags/.")
    ],
    key: Annotated[str | None, typer.Argument(help="Its chain end (default: its known-good tag).")] = None,
    data: DataOpt = None,
) -> None:
    """The lineage of a checkpoint in another store against this store's chain, paired by position."""
    s = Session(paths_for("kotor", data))
    other = Store(legacy / "ckpt", legacy / "vanilla", s.cloner)
    k = Key(key) if key else Key((legacy / "tags" / "known-good").read_text().strip())
    theirs = other.lineage(k)
    ours = [link for link in s.links() if link.checkpoint]
    mine = [s.store.get(VANILLA), *(link.checkpoint for link in ours)]
    bad = 0
    for i, (a, b) in enumerate(zip(theirs, mine, strict=False)):
        assert b is not None
        same = a.mod == b.mod and a.tree == b.tree
        bad += 0 if same else 1
        mark = "==" if same else "!!"
        print(
            f"{mark} {i:3d} {a.mod:50s} {a.tree[:12]} {b.tree[:12]}{'' if a.mod == b.mod else '  (' + b.mod + ')'}"
        )
    if len(theirs) != len(mine):
        print(f"!! lengths differ: legacy {len(theirs)}, here {len(mine)}")
        bad += 1
    print("SAME" if bad == 0 else f"{bad} differences")
    raise typer.Exit(1 if bad else 0)


@recipe_app.command("write")
@exits_cleanly
def recipe_write(data: DataOpt = None) -> None:
    """Write recipe.json: every entry's canonical form, the text that enters the key."""
    paths = paths_for("kotor", data)
    out = paths.game_dir / "build" / "recipe.json"
    out.write_text(recipe_json(load_recipe(paths.game_dir)))
    print(f"{out}: {len(load_recipe(paths.game_dir).entries)} entries")


@recipe_app.command("show")
@exits_cleanly
def recipe_show(entry: Annotated[str | None, typer.Argument()] = None, data: DataOpt = None) -> None:
    """Print an entry's canonical form (or every entry's name and skip reason)."""
    r = load_recipe(paths_for("kotor", data).game_dir)
    for e in r.entries:
        if entry is None:
            print(f"{e.name}{'  [skip: ' + e.skip + ']' if e.skip else ''}")
        elif e.name == entry:
            print(json.dumps(json.loads(canonical_entry(e)), indent=1))


def recipe_json(r: Recipe) -> str:
    rows = [{**json.loads(canonical_entry(e)), **({"skip": e.skip} if e.skip else {})} for e in r.entries]
    return json.dumps(rows, indent=1) + "\n"


@app.command()
@exits_cleanly
def deploy(
    key: Annotated[
        str | None, typer.Argument(help="A checkpoint key (default: the chain end of the last build).")
    ] = None,
    check: Annotated[bool, typer.Option("--check", help="Only report what differs on the handheld.")] = False,
    data: DataOpt = None,
) -> None:
    """Put a checkpoint on the handheld by content, into a copy swapped in by rename."""
    from modshop.core.deploy import Deployer
    from modshop.kotor.target import handheld_target

    s = Session(paths_for("kotor", data))
    local = s.local()
    if local is None:
        raise Preflight(f"{s.paths.local_toml} is missing; copy local.example.toml beside it and fill it in")
    k = Key(key) if key else s.default_key()
    c = s.store.get(k)
    if c is None:
        raise Preflight(f"no checkpoint {k}")
    target = handheld_target(local.handheld)
    d = Deployer(target)
    print(
        f"{'checking' if check else 'deploying'} {k} ({c.mod}, tree {c.tree[:12]}) against {local.handheld.ssh}:{target.game_dir}"
    )
    print("outside the comparison:", " ".join(target.exclude))
    if check:
        drift = d.drift(s.store.tree(k))
        for line in drift.lines:
            print(line)
        print(f"{len(drift.lines)} paths differ" if drift else "no drift")
        raise typer.Exit(1 if drift else 0)
    result = d.deploy(s.store.tree(k))
    if result.updated == 0:
        print("nothing to deploy")
    else:
        print(f"{result.updated} paths updated; previous folder kept as {result.previous}")


archives_app = typer.Typer(no_args_is_help=True, help="The mod archives.")
app.add_typer(archives_app, name="archives")


@base.command("fetch")
@exits_cleanly
def base_fetch(
    account: Annotated[str, typer.Argument(help="Your Steam account name.")], data: DataOpt = None
) -> None:
    """Download the vanilla game by depot manifest id into the vanilla tree (interactive the first time)."""
    paths = paths_for("kotor", data)
    b = base_mod.Base.load(paths.game_dir / "build" / "base.json")
    n = base_mod.fetch(b, paths.vanilla, account)
    print(f"vanilla tree at {paths.vanilla / 'tree'} ({n} files); now: modshop kotor base index")


@archives_app.command("fetch")
@exits_cleanly
def archives_fetch(
    nexus_key_file: Annotated[Path, typer.Argument(help="A file holding your Nexus API key.")],
    data: DataOpt = None,
) -> None:
    """Fetch every mod of the Full Build into the archives, in the build's order."""
    from modshop.kotor.archives import fetch_build

    console_logging()
    paths = paths_for("kotor", data)
    fetch_build(paths.game_dir / "build" / "k1full.json", paths.archives, nexus_key_file.read_text().strip())


@archives_app.command("mega")
@exits_cleanly
def archives_mega(
    urls: Annotated[list[str], typer.Argument(help="Public mega.nz file links.")], data: DataOpt = None
) -> None:
    """Fetch public mega.nz links into the archives' mega/ folder."""
    from modshop.kotor.archives import fetch_mega

    console_logging()
    dest = paths_for("kotor", data).archives / "mega"
    dest.mkdir(parents=True, exist_ok=True)
    for u in urls:
        try:
            fetch_mega(u, dest)
        except Exception as e:
            log.error("FAILED %s %r", u, e)


kmrp_app = typer.Typer(no_args_is_help=True, help="KMRP's controller module, built from source.")
app.add_typer(kmrp_app, name="kmrp")
re_app = typer.Typer(no_args_is_help=True, help="Reverse engineering the running game.")
app.add_typer(re_app, name="re")

KMRP_CLONE = Path.home() / "src" / "github.com" / "RayesDiyab" / "KMRP-KOTOR-Modern-Restoration-Patch"
XWIN_SDK = Path.home() / ".cache" / "xwin" / "sdk"


@kmrp_app.command("build")
@exits_cleanly
def kmrp_build(
    clone: Annotated[
        Path, typer.Option("--clone", help="The KMRP clone, at the commit to build.")
    ] = KMRP_CLONE,
    xwin: Annotated[
        Path, typer.Option("--xwin", help="Microsoft's CRT and SDK, as xwin splat laid them out.")
    ] = XWIN_SDK,
    data: DataOpt = None,
) -> None:
    """Build, check and package the controller module into data/kmrp-build/ for the kmrp-controller entry."""
    from modshop.kotor.kmrp_build import build as build_module

    paths = paths_for("kotor", data)
    print(f"building {clone} ...")
    b = build_module(clone.resolve(), paths.data / "kmrp-build", paths.repo, xwin)
    print(f"{b.label} ({b.commit[:12]}): {b.hooks} hooks -> {paths.data / 'kmrp-build'}")
    if b.previous:
        print(f"the outputs it replaced are in {b.previous}")
    print("next: modshop kotor build, then deploy")


@re_app.command("dump")
@exits_cleanly
def re_dump(data: DataOpt = None) -> None:
    """The running game's decrypted image, with KPM's hooks undone, as a PE under data/re/."""
    from modshop.kotor.re import dump

    s_paths = paths_for("kotor", data)
    local = Local.load(s_paths.local_toml)
    d = dump(local.handheld, s_paths.data / "re")
    print(f"{d.exe}: {d.hooks.restored} hook sites restored, {d.missing_pages} unreadable pages")
    if d.redirects:
        print(f"{len(d.redirects)} redirect candidates left in .text, listed in {d.record}")
