#!/usr/bin/env python3
"""Build the modded game as a chain of checkpoints.

Each entry of manifest.json is one mod: a few steps (copies, a HoloPatcher run,
a repair) applied to a game folder that every earlier entry has already changed.
The driver gives every entry a key that names everything that could change its
result: the previous entry's key and the hash of the tree it produced, the
entry itself, the hashes of the files it reads (its archive folder, or what
`inputs` lists), this file's syntax tree, the patcher's venv and patch series,
and the versions of Python and 7-Zip. A checkpoint named by that key is a
reflink copy of the game folder after the entry ran, with a manifest of every
file's hash. A build walks the chain and does nothing for entries whose
checkpoint exists; the first missing one is rebuilt from its parent's
checkpoint and so is every entry after it.

Commands:
  build.py                  build the whole chain (or resume it)
  build.py MOD [MOD...]     stop after the named entries (still builds what they need)
  build.py status           which entries have checkpoints, without building
  build.py base             normalise the vanilla tree and write its manifest
  build.py verify [KEY]     rehash a checkpoint in full and compare with its manifest
  build.py verify-inputs    rehash every archive the manifest uses, reporting any cached hash that lies
  build.py checkout KEY DIR reflink-copy a checkpoint's tree to DIR, for a bisect
  build.py tag NAME [KEY]   name a checkpoint (default: the chain's end); gc keeps it
  build.py gc [--keep N]    remove checkpoints not in the chain, not tagged, beyond the newest N
  build.py prove            build the whole chain again, uncached, and compare it with the cached chain

Environment: KOTOR_DATA (default ../data), HOLOPATCHER (default the venv's), KOTOR_MANIFEST (default manifest.json here).
"""
import ast, fcntl, fnmatch, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time, tomllib

HERE = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(os.environ.get('KOTOR_DATA', str(HERE.parent / 'data'))).resolve()
ARCHIVES = DATA / 'archives'
LOGS = DATA / 'logs'
GAMES = DATA / 'game'
VANILLA = GAMES / 'vanilla'          # vanilla/tree is the download; vanilla/manifest.txt its hashes
CKPT = GAMES / 'ckpt'
WORK = GAMES / 'work'                # the tree being built; work.json says which checkpoint it equals
STAGE = DATA / 'stage'
TAGS = GAMES / 'tags'
LOCAL = HERE.parent.parent.parent / 'local.toml'   # the handheld's name, paths and panel; gitignored
HP = os.environ.get('HOLOPATCHER', str(DATA / 'venv' / 'bin' / 'holopatcher'))
MTIME_NS = 946684801 * 10**9        # 2000-01-01T00:00:01Z: every file in a checkpoint carries this mtime
PATCHER_TIMEOUT = 1800
KEY_LEN = 16

GAME = WORK                          # the verbs below work on these two
OVR = WORK / 'Override'


def use_work(path):
    global WORK, GAME, OVR
    WORK = GAME = path; OVR = path / 'Override'
LOG = None


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    if LOG: LOG.write(s + '\n'); LOG.flush()


def sha256_file(p, h=None):
    h = h or hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.encode()).hexdigest()


# ---- tree manifests ---------------------------------------------------------
# One line per file: "F <sha256> <size> <path>", per symlink: "L <target> <path>".
# Sorted by path; the manifest's own sha256 is the tree hash.

def walk(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        d = pathlib.Path(dirpath)
        for n in list(dirnames):
            if (d / n).is_symlink():
                dirnames.remove(n); filenames.append(n)
        dirnames.sort()
        for n in filenames:
            out.append(d / n)
    return sorted(out, key=lambda p: str(p.relative_to(root)).encode())


def read_manifest(path):
    m = {}
    for line in open(path, encoding='utf-8'):
        kind, rest = line.rstrip('\n').split(' ', 1)
        if kind == 'F':
            digest, size, rel = rest.split(' ', 2); m[rel] = ('F', digest, int(size))
        else:
            target, rel = rest.split(' ', 1); m[rel] = ('L', target)
    return m


def write_manifest(path, m):
    with open(path, 'w', encoding='utf-8') as f:
        for rel in sorted(m, key=lambda r: r.encode()):
            e = m[rel]
            f.write(f'F {e[1]} {e[2]} {rel}\n' if e[0] == 'F' else f'L {e[1]} {rel}\n')
    return sha256_file(path)


def tree_manifest(root, prev=None, since_ns=None):
    """Hash every file under root. With prev (the parent checkpoint's manifest) and since_ns
    (a clock reading taken after the tree was restored from it), a file whose inode has not
    changed since (ctime older than since_ns, same size, same path in prev) keeps its parent
    hash: the kernel sets ctime on every write and no user can set it back."""
    m = {}
    for p in walk(root):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            m[rel] = ('L', os.readlink(p)); continue
        st = p.stat()
        old = prev.get(rel) if prev else None
        if old and since_ns and old[0] == 'F' and old[2] == st.st_size and st.st_ctime_ns < since_ns:
            m[rel] = old
        else:
            m[rel] = ('F', sha256_file(p), st.st_size)
    return m


def normalise_mtimes(root):
    """Give every file the fixed mtime, so no later comparison depends on an archive's clock."""
    n = 0
    for p in walk(root):
        if p.is_symlink(): continue
        if p.stat().st_mtime_ns != MTIME_NS:
            os.utime(p, ns=(MTIME_NS, MTIME_NS)); n += 1
    return n


def reflink_copy(src, dst):
    subprocess.run(['cp', '-a', '--reflink=always', str(src), str(dst)], check=True)


# ---- the key ------------------------------------------------------------------

# Functions whose code cannot change what an entry writes into the tree: the orchestration around
# the verbs (keys, checkpoints, manifests, commands). Everything else in this file, the verbs and the
# lookup and staging helpers they call, is part of every key, so a change to it rebuilds the chain.
ORCHESTRATION = {'log', 'sha256_file', 'sha256_str', 'walk', 'read_manifest', 'write_manifest', 'tree_manifest',
                 'normalise_mtimes', 'reflink_copy', 'code_hash', 'env_hash', 'hashcache', 'save_hashcache',
                 'inputs_hash', 'key_of', 'meta_of', 'tree_of', 'manifest_path', 'work_key', 'set_work_key',
                 'discard_work', 'restore_work', 'commit_checkpoint', 'use_work', 'load_manifest', 'chain',
                 'preflight', 'lock', 'main'}


def code_hash():
    tree = ast.parse((HERE / 'build.py').read_text())
    body = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and (n.name in ORCHESTRATION or n.name.startswith('cmd_')))]
    return sha256_str(ast.dump(ast.Module(body=body, type_ignores=[])))


_env_hash = None
def env_hash():
    global _env_hash
    if _env_hash: return _env_hash
    venv_py = pathlib.Path(HP).parent / 'python'
    freeze = subprocess.run([str(venv_py), '-m', 'pip', 'freeze'], capture_output=True, text=True, check=True).stdout
    sevenzip = subprocess.run(['7zz'], capture_output=True, text=True).stdout.splitlines()[1:2]
    patches = [sha256_file(p) for p in sorted((HERE.parent / 'patches' / 'pykotor').glob('*.patch'))]
    _env_hash = sha256_str(json.dumps({'python': sys.version, 'venv': freeze, '7zz': sevenzip, 'pykotor-patches': patches}))
    return _env_hash


_hashcache = None
def hashcache():
    """sha256 of archive files, keyed by path, size and mtime (ns). Archives are immutable downloads
    and 26 GB; `verify-inputs` rehashes them all and reports any cache entry that lies."""
    global _hashcache
    if _hashcache is None:
        f = ARCHIVES / '.hashcache.json'
        _hashcache = json.load(open(f)) if f.exists() else {}
    return _hashcache


def save_hashcache():
    if _hashcache is not None:
        tmp = ARCHIVES / '.hashcache.json.tmp'
        json.dump(_hashcache, open(tmp, 'w')); tmp.replace(ARCHIVES / '.hashcache.json')


_local = None
def local(dotted):
    """A value from local.toml by dotted key, e.g. handheld.display."""
    global _local
    if _local is None:
        if not LOCAL.exists(): sys.exit(f'{LOCAL} is missing; copy local.example.toml and fill it in')
        _local = tomllib.load(open(LOCAL, 'rb'))
    v = _local
    for k in dotted.split('.'): v = v[k]
    return v


def input_path(spec):
    """An input is a path under data/archives; with a leading './' one under this directory; with
    'data/' one under data/. 'local:<key>' names a value from local.toml and 'image:<name>' a podman
    image; both are key material only."""
    if spec.startswith('./'): return (HERE / spec[2:]).resolve()
    if spec.startswith('data/'): return DATA / spec[5:]
    return ARCHIVES / spec


def value_input(spec):
    if spec.startswith('local:'): return json.dumps(local(spec[6:]))
    if spec.startswith('image:'):
        r = subprocess.run(['podman', 'image', 'inspect', '--format', '{{.Id}}', spec[6:]], capture_output=True, text=True)
        if r.returncode != 0: raise FileNotFoundError(f'podman image {spec[6:]} is not built')
        return r.stdout.strip()
    return None


def inputs_of(entry):
    return entry['inputs'] if 'inputs' in entry else [entry['mod']]


def inputs_hash(entry, full=False):
    rows = []
    for spec in inputs_of(entry):
        v = value_input(spec)
        if v is not None:
            rows.append([spec, '', sha256_str(v)]); continue
        root = input_path(spec)
        if not root.exists(): raise FileNotFoundError(f'{entry["mod"]}: input {spec} ({root})')
        files = walk(root) if root.is_dir() else [root]
        for p in files:
            if p.is_symlink(): continue
            st = p.stat(); ck = f'{p}|{st.st_size}|{st.st_mtime_ns}'
            cache = hashcache()
            if full or ck not in cache:
                digest = sha256_file(p)
                if full and ck in cache and cache[ck] != digest:
                    log(f'!! hash cache lied for {p}')
                cache[ck] = digest
            rows.append([spec, p.relative_to(root).as_posix() if root.is_dir() else p.name, cache[ck]])
    save_hashcache()
    return rows


def key_of(parent_key, parent_tree, entry):
    material = {'parent': parent_key, 'tree': parent_tree, 'entry': entry,
                'inputs': inputs_hash(entry), 'code': code_hash(), 'env': env_hash()}
    return sha256_str(json.dumps(material, sort_keys=True))[:KEY_LEN]


# ---- checkpoints ----------------------------------------------------------------

def meta_of(key):
    d = VANILLA if key == 'vanilla' else CKPT / key
    return json.load(open(d / 'meta.json')) if (d / 'meta.json').exists() else None


def tree_of(key):
    return (VANILLA if key == 'vanilla' else CKPT / key) / 'tree'


def manifest_path(key):
    return (VANILLA if key == 'vanilla' else CKPT / key) / 'manifest.txt'


def work_key():
    f = GAMES / 'work.json'
    return json.load(open(f))['key'] if f.exists() and WORK.exists() else None


def set_work_key(key):
    f = GAMES / 'work.json'
    if key is None: f.unlink(missing_ok=True)
    else: json.dump({'key': key}, open(f, 'w'))


def discard_work():
    set_work_key(None)
    if WORK.exists(): shutil.rmtree(WORK)


def restore_work(key):
    """Make WORK a reflink copy of checkpoint `key` unless it already is; return a clock reading
    taken after the copy, for tree_manifest's ctime test."""
    if work_key() != key:
        discard_work()
        t = time.time()
        reflink_copy(tree_of(key), WORK)
        set_work_key(key)
        log(f'   restored {key} -> work in {time.time()-t:.1f}s')
    os.sync()
    return time.time_ns()


def commit_checkpoint(key, parent_key, entry, since_ns):
    """WORK, finished, becomes checkpoint `key`: mtimes normalised, manifest written, the tree built in
    ckpt/<key>.tmp and renamed; WORK stays equal to the new checkpoint.

    A checkpoint's tree hardlinks the parent checkpoint's files and holds reflink clones of only the
    files the entry changed. Nothing ever writes inside a checkpoint (WORK is a reflink copy, so its
    writes land on new inodes), which makes the hardlinks safe, and it keeps the filesystem's
    extent-ownership metadata small: a reflink clone of a whole tree per checkpoint adds a record for
    every file to XFS's per-allocation-group reserved pool, and a few hundred such clones exhaust it
    with ENOSPC while `df` still shows terabytes free."""
    t = time.time()
    normalise_mtimes(WORK)
    prev = read_manifest(manifest_path(parent_key))
    m = tree_manifest(WORK, prev, since_ns)
    changed = sorted(set(r for r in m if m[r] != prev.get(r)) | set(r for r in prev if r not in m), key=lambda r: r.encode())
    tmp = CKPT / f'{key}.tmp'
    if tmp.exists(): shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    tree_hash = write_manifest(tmp / 'manifest.txt', m)
    (tmp / 'changed.txt').write_text(''.join(f'{"-" if r not in m else "+" if r not in prev else "~"} {r}\n' for r in changed))
    subprocess.run(['cp', '-al', str(tree_of(parent_key)), str(tmp / 'tree')], check=True)
    for r in changed:
        dst = tmp / 'tree' / r
        if dst.is_symlink() or dst.exists(): dst.unlink()
        if r in m:
            dst.parent.mkdir(parents=True, exist_ok=True)
            src = WORK / r
            if src.is_symlink(): os.symlink(os.readlink(src), dst)
            else: subprocess.run(['cp', '-a', '--reflink=always', str(src), str(dst)], check=True)
    for d in sorted((d for d in tmp.joinpath('tree').rglob('*') if d.is_dir() and not d.is_symlink()), key=lambda d: -len(str(d))):
        if not any(d.iterdir()) and not (WORK / d.relative_to(tmp / 'tree')).exists(): d.rmdir()
    json.dump({'key': key, 'parent': parent_key, 'mod': entry['mod'], 'tree': tree_hash, 'files': len(m),
               'changed': len(changed), 'built_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'seconds': round(time.time() - t, 1)},
              open(tmp / 'meta.json', 'w'), indent=1)
    os.sync()
    tmp.rename(CKPT / key)
    set_work_key(key)
    log(f'   checkpoint {key}: {len(changed)} paths changed, tree {tree_hash[:12]}, {time.time()-t:.1f}s')
    return tree_hash


# ---- the stage -------------------------------------------------------------------

def extract(entry):
    """A fresh stage for the entry: each archive among its inputs unpacked into <stem>/, loose files
    and directories copied in. Removed again after the entry's steps."""
    out = STAGE / re.sub(r'[^\w.-]', '_', entry['mod'])
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    for spec in inputs_of(entry):
        if value_input(spec) is not None: continue
        src = input_path(spec)
        items = sorted(src.iterdir()) if src.is_dir() and not spec.startswith('./') else [src]
        for a in items:
            if a.is_file() and a.suffix.lower() in ('.zip', '.rar', '.7z'):
                sub = out / a.stem; sub.mkdir(exist_ok=True)
                r = subprocess.run(['7zz', 'x', '-y', '-bd', '-bso0', f'-o{sub}', str(a)], capture_output=True, text=True)
                if r.returncode != 0: raise RuntimeError(f'7zz failed on {a}: {r.stderr[-500:]}')
                # Windows zips with backslash names unpack as single files named "a\b\c"
                for f in list(sub.iterdir()):
                    if '\\' in f.name:
                        t = sub / f.name.replace('\\', '/'); t.parent.mkdir(parents=True, exist_ok=True); f.rename(t)
            elif a.is_file():
                shutil.copy2(a, out / a.name)
            elif a.is_dir():
                shutil.copytree(a, out / a.name, symlinks=True)
    return out


# ---- path lookup: case-insensitive, as the game is ---------------------------------

def ci_find(d, name):
    """Path of `name` inside dir `d`, matched case-insensitively (the exact spelling first), or None."""
    low = name.lower()
    hits = sorted((p for p in d.iterdir() if p.name.lower() == low), key=lambda p: (p.name != name, p.name))
    return hits[0] if hits else None


def _resolve(cur, parts):
    """All paths under cur matching the segment list (case-insensitive, * wildcards per segment)."""
    if not parts: return [cur]
    if not cur.is_dir(): return []
    part, rest = parts[0], parts[1:]
    if '*' in part:
        kids = sorted(p for p in cur.iterdir() if fnmatch.fnmatch(p.name.lower(), part.lower()) and '__macosx' not in p.name.lower())
    else:
        k = ci_find(cur, part); kids = [k] if k else []
    out = []
    for k in kids: out += _resolve(k, rest)
    return out


def ci_path(root, rel):
    """Resolve a slash path under root case-insensitively; a segment may hold * wildcards.
    Archives unpack as <stem>/<their own folders>, so if nothing matches, one or two extra
    wildcard levels are tried after the first segment before giving up; a path that does
    not exist is returned as given (callers that create files rely on that)."""
    root = pathlib.Path(root); parts = list(pathlib.PurePosixPath(rel.replace('\\', '/')).parts)
    if not parts or parts == ['.']: return root
    for extra in (0, 1, 2):
        trial = parts[:1] + ['*'] * extra + parts[1:] if parts[0] != '.' else ['*'] * extra + parts[1:]
        hits = _resolve(root, trial)
        if hits: return hits[0]
    return root.joinpath(*parts)


def put(src, dest_dir=None):
    """Copy a file into Override (or dest_dir), replacing any case-variant of it."""
    dest_dir = pathlib.Path(dest_dir) if dest_dir else OVR
    dest_dir.mkdir(parents=True, exist_ok=True)
    old = ci_find(dest_dir, src.name)
    if old and old.name != src.name: old.unlink()
    shutil.copy2(src, dest_dir / src.name)


SKIP_SUFFIXES = ('.jpg', '.png', '.txt', '.rtf', '.pdf', '.md', '.ds_store', '.url', '.htm', '.html', '.docx', '.exe', '.bat', '.ini')


def files_in(root, pattern='*', recursive=False):
    root = pathlib.Path(root)
    it = root.rglob('*') if recursive else root.iterdir()
    return sorted(p for p in it if p.is_file() and fnmatch.fnmatch(p.name.lower(), pattern.lower())
                  and not p.name.lower().endswith(SKIP_SUFFIXES) and '__macosx' not in str(p).lower())


# ---- step verbs ----------------------------------------------------------------------

def s_copy(st, src='.', pattern='*', exclude=(), recursive=False, dest=None):
    """Copy files from a staged folder into Override (or GAME/dest)."""
    root = ci_path(st, src)
    if not root.exists(): raise FileNotFoundError(f'copy: {root}')
    # a wrapper folder holding nothing but one folder is not the mod's content yet
    while not recursive and not files_in(root, pattern) and len([d for d in root.iterdir() if d.is_dir() and '__macosx' not in d.name.lower()]) == 1:
        root = [d for d in root.iterdir() if d.is_dir() and '__macosx' not in d.name.lower()][0]
    ex = [e.lower() for e in exclude]; n = 0
    for f in files_in(root, pattern, recursive):
        if any(fnmatch.fnmatch(f.name.lower(), e) for e in ex): continue
        put(f, GAME / dest if dest else None); n += 1
    log('   copied', n, 'from', root.relative_to(STAGE))
    if n == 0: raise RuntimeError('copied nothing')


def s_copy_files(st, src, names, dest=None, if_absent=False):
    """Copy named files from the stage into Override (or GAME/dest); with if_absent, only those the
    tree does not already have."""
    n = 0
    for name in names:
        d = GAME / dest if dest else OVR
        if if_absent and d.is_dir() and ci_find(d, name): continue
        put(ci_path(st, f'{src}/{name}'), d); n += 1
    log('   copied', n, 'named files from', src)


def s_delete(st, names):
    """Delete files from Override (case-insensitive); missing ones are reported, not fatal."""
    for n in names:
        p = ci_find(OVR, n)
        if p: p.unlink(); log('   deleted', n)
        else: log('   (absent)', n)


def s_rename_in_override(st, old, new):
    p = ci_find(OVR, old)
    if not p: raise FileNotFoundError(old)
    q = ci_find(OVR, new)
    if q: q.unlink()
    p.rename(OVR / new); log('   renamed', old, '->', new)


def s_stage_delete(st, src, names):
    for n in names:
        p = ci_path(st, f'{src}/{n}')
        if p.exists(): p.unlink()


def s_stage_copy_as(st, src, new):
    p = ci_path(st, src); shutil.copy2(p, p.parent / new)


def s_tlk(st, src):
    shutil.copy2(ci_path(st, src), GAME / 'dialog.tlk'); log('   dialog.tlk <-', src)


def s_symlink(st, link, target):
    """A name in the game folder pointing at another: `Modules` for the patcher, which opens module
    paths by exact name, and `override` for mods whose installer spells the folder in lower case."""
    p = GAME / link
    if p.is_symlink() and os.readlink(p) == target: return
    if p.exists() or p.is_symlink(): raise FileExistsError(p)
    p.symlink_to(target); log('   ', link, '->', target)


def s_script(st, path, args=()):
    """Run one of our scripts on the working tree. Arguments: `game` for the tree, `Override` for its
    Override, `stage` for this entry's stage, `archives/...` and `data/...` for paths there, anything
    else as given."""
    script = input_path(path)
    def arg(a):
        if a == 'game': return str(GAME)
        if a == 'Override': return str(OVR)
        if a == 'stage': return str(st)
        if a.startswith('archives/'): return str(ARCHIVES / a[9:])
        if a.startswith('data/'): return str(DATA / a[5:])
        return a
    argv = [sys.executable, '-I', str(script)] + [arg(a) for a in args]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=PATCHER_TIMEOUT)
    for l in (r.stdout + r.stderr).splitlines()[-6:]: log('    ', l[:200])
    if r.returncode != 0: raise RuntimeError(f'{script.name} failed (exit {r.returncode})')


def s_repair(st, name, args=()):
    s_script(st, f'./../repairs/{name}/make.py', args)


KMRP_STAMP = '2000-01-01T00:00:01'


def s_kmrp(st, installer, settings, image='modshop-wine'):
    """KMRP's Windows installer, in-place on the working tree, under Wine in a container with no
    network and nothing mounted but the tree and the installer. The tree is mounted at the path it
    will have on the handheld, since the installer records the executable's path for its Restore;
    the resolution is the handheld's panel; `settings` is what its Advanced Settings would hold
    (driverCompatibility, markerFixes, controllerSupport, highFpsFix, hdIcons). Afterwards the two
    timestamps its state file carries are fixed and the manifest row for that file recomputed, so
    the step's output depends on nothing but its inputs."""
    home, game_dir, display = local('handheld.home'), local('handheld.game_dir'), local('handheld.display')
    target = game_dir.replace('~', home, 1) if game_dir.startswith('~') else game_dir
    exe_win = 'Z:' + target.replace('/', '\\') + '\\swkotor.exe'
    with tempfile.TemporaryDirectory(dir=STAGE) as cfg:
        body = '{\r\n' + ',\r\n'.join(f'  "{k}": {"true" if v else "false"}' for k, v in settings.items()) + '\r\n}\r\n'
        (pathlib.Path(cfg) / 'settings.json').write_bytes(body.encode())
        cmd = ['podman', 'run', '--rm', '--network', 'none', '--security-opt', 'label=disable',
               '-v', f'{GAME}:{target}', '-v', f'{ARCHIVES / installer}:/in/{installer}:ro',
               '-v', f'{cfg}:/wine/drive_c/users/root/AppData/Local/KMRP',
               '-e', 'WINEDEBUG=-all', image, 'bash', '-c',
               f'xvfb-run -a wine "/in/{installer}" --in-place "{exe_win}" {display}; rc=$?; wineserver --wait; exit $rc']
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=PATCHER_TIMEOUT)
    for l in [x for x in (r.stdout + r.stderr).splitlines() if 'X connection' not in x][-6:]: log('    ', l[:200])
    if r.returncode != 0: raise RuntimeError(f'KMRP installer failed (exit {r.returncode})')
    state = GAME / 'kpm_install_state.json'
    text = re.sub(r'"(CreatedAt|UpdatedAt)": "[^"]*"', rf'"\1": "{KMRP_STAMP}"', state.read_text())
    state.write_text(text)
    digest = sha256_file(state).upper()
    man = GAME / 'KMRP_KPM.manifest'
    lines = man.read_bytes().split(b'\n')
    for i, l in enumerate(lines):
        if l.startswith(b'file\tkpm_install_state.json\t'):
            lines[i] = b'file\tkpm_install_state.json\t' + digest.encode() + (b'\r' if l.endswith(b'\r') else b'')
    man.write_bytes(b'\n'.join(lines))
    log(f'    KMRP installed at {display} for {target}')


def case_aliases(td):
    """pykotor opens module files by exact name: for every modules\\<name> a mod's ini files mention
    whose case differs from the file on disk, link that spelling to the real file for the run."""
    mods = GAME / 'modules'; created = []
    for ini in sorted(td.rglob('*.ini')):
        text = ini.read_text(encoding='utf-8', errors='replace')
        for name in sorted(set(re.findall(r'(?i)modules\\([^\\\r\n;=]+?\.(?:mod|rim|erf))\s*$', text, re.M))):
            name = name.strip(); real = ci_find(mods, name)
            if real and real.name != name and not (mods / name).exists():
                (mods / name).symlink_to(real.name); created.append((mods / name, real)); log('   alias', name, '->', real.name)
    return created


def drop_aliases(created):
    for link, real in created:
        if link.is_symlink(): link.unlink()
        elif link.exists():
            # the patcher replaced the link with a real file: keep it under the canonical name
            link.replace(real); log('   alias', link.name, 'became the file; moved to', real.name)


def collapse_case(d):
    """Keep one file per case-insensitive name in d, the most recently written. The game runs under
    Wine, where two names differing only in case are one file; HoloPatcher writes a file by the exact
    name its ini spells, beside an existing one of another spelling, where Windows would overwrite."""
    groups = {}
    for p in d.iterdir():
        if p.is_file(): groups.setdefault(p.name.lower(), []).append(p)
    for low, ps in groups.items():
        if len(ps) > 1:
            ps.sort(key=lambda p: p.stat().st_ctime_ns, reverse=True)
            for p in ps[1:]: p.unlink()
            log(f'   case collapse: kept {ps[0].name}, removed {", ".join(p.name for p in ps[1:])}')


def s_holopatcher(st, src='.', option=None, allow_errors=0):
    """Run HoloPatcher on a staged tslpatchdata (or its parent). option = namespace index."""
    td = ci_path(st, src)
    aliases = case_aliases(td)
    cmd = [HP, '--game-dir', str(GAME), '--tslpatchdata', str(td), '--install', '--console']
    if option is not None: cmd += ['--namespace-option-index', str(option)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=PATCHER_TIMEOUT)
    finally:
        drop_aliases(aliases)
    (LOGS / 'holopatcher').mkdir(exist_ok=True)
    n = len(list((LOGS / 'holopatcher').glob('hp-*.log'))) + 1
    (LOGS / 'holopatcher' / f'hp-{n:03d}-{td.parts[-3][:30] if len(td.parts) > 2 else td.name}.log').write_text(r.stdout + '\n--- stderr ---\n' + r.stderr)
    tail = [l for l in r.stdout.splitlines() if l.startswith('[Error]') or 'Install completed' in l or l.startswith('[Warning]')]
    for l in tail[-6:]: log('   ', l[:200])
    m = [re.search(r'Install completed: (\d+) errors', l) for l in tail]; m = [x for x in m if x]
    if not m or int(m[-1].group(1)) > allow_errors:
        raise RuntimeError(f'holopatcher failed on {td} (exit {r.returncode})')
    collapse_case(OVR)


def s_dedupe_tpc(st):
    """Remove every Override .tpc that has a same-named .tga or .dds (the game crashes when both exist)."""
    names = {p.name.lower(): p for p in OVR.iterdir()}
    n = 0
    for low, p in list(names.items()):
        if low.endswith('.tpc') and (low[:-4] + '.tga' in names or low[:-4] + '.dds' in names):
            p.unlink(); n += 1
    log('   removed', n, 'duplicate tpc files')


VERBS = {'dedupe_tpc': s_dedupe_tpc, 'copy': s_copy, 'copy_files': s_copy_files, 'delete': s_delete,
         'rename': s_rename_in_override, 'stage_delete': s_stage_delete, 'stage_copy_as': s_stage_copy_as,
         'tlk': s_tlk, 'holopatcher': s_holopatcher, 'symlink': s_symlink, 'repair': s_repair, 'script': s_script, 'kmrp': s_kmrp}


# ---- the chain -------------------------------------------------------------------------

MANIFEST = pathlib.Path(os.environ.get('KOTOR_MANIFEST', str(HERE / 'manifest.json')))


def load_manifest():
    return [e for e in json.load(open(MANIFEST)) if not e.get('skip')]


def chain(build=False, until=()):
    """Walk the manifest. With build=False, report; with build=True, build what is missing.
    Yields (entry, key, exists)."""
    parent, tree = 'vanilla', meta_of('vanilla')['tree']
    for entry in load_manifest():
        key = key_of(parent, tree, entry)
        exists = meta_of(key) is not None
        if build and not exists:
            log(f'== {entry["mod"]}  [{key}]')
            since = restore_work(parent)
            st = extract(entry)
            try:
                for step in entry['steps']:
                    step = dict(step); verb = step.pop('do'); log('  ', verb, step)
                    VERBS[verb](st, **step)
                tree = commit_checkpoint(key, parent, entry, since)
            except BaseException:
                log(f'!! {entry["mod"]} failed; the working tree is discarded and the next run restores {parent}')
                discard_work(); raise
            finally:
                shutil.rmtree(st, ignore_errors=True)
        else:
            tree = meta_of(key)['tree'] if exists else None
        yield entry, key, exists
        if not exists and not build: return
        parent = key
        if entry['mod'] in until: return


def preflight():
    for d in (CKPT, STAGE, LOGS, TAGS): d.mkdir(parents=True, exist_ok=True)
    if not meta_of('vanilla'): sys.exit(f'no vanilla manifest at {VANILLA}; run base.sh then `build.py base`')
    probe = CKPT / '.reflink-probe'
    try:
        if probe.exists(): shutil.rmtree(probe)
        probe.mkdir(); (probe / 'a').write_text('x')
        subprocess.run(['cp', '--reflink=always', str(probe / 'a'), str(probe / 'b')], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        sys.exit(f'{CKPT} is not on a reflink-capable filesystem')
    finally:
        shutil.rmtree(probe, ignore_errors=True)
    for t in CKPT.glob('*.tmp'): shutil.rmtree(t)
    if not pathlib.Path(HP).exists(): sys.exit(f'no patcher at {HP}; run setup-venv.sh')


def lock():
    f = open(GAMES / '.lock', 'w')
    try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: sys.exit('another build holds the lock')
    return f


def cmd_build(until):
    global LOG
    preflight(); _l = lock()
    LOG = open(LOGS / 'build.log', 'a')
    log(f'--- build {time.strftime("%Y-%m-%dT%H:%M:%S%z")}')
    last = None; built = 0
    for entry, key, exists in chain(build=True, until=until):
        last = key; built += 0 if exists else 1
    link = GAMES / 'build'
    if link.is_symlink(): link.unlink()
    elif link.exists(): sys.exit(f'{link} is a directory, not the symlink the build writes; move it aside')
    link.symlink_to(tree_of(last))
    log(f'ALL DONE: {built} rebuilt; build -> ckpt/{last}/tree (tree {meta_of(last)["tree"][:12]})')


def cmd_status():
    preflight()
    n = 0
    for entry, key, exists in chain():
        n += 1
        print(f'{"ok  " if exists else "MISS"} {key} {entry["mod"]}')
        if not exists: print('  (and everything after it)')
    if n == len(load_manifest()) and exists: print('up to date')


def cmd_base():
    t = VANILLA / 'tree'
    if not t.is_dir(): sys.exit(f'no vanilla tree at {t}; run base.sh first')
    n = normalise_mtimes(t)
    m = tree_manifest(t)
    h = write_manifest(VANILLA / 'manifest.txt', m)
    json.dump({'key': 'vanilla', 'parent': None, 'mod': 'vanilla', 'tree': h, 'files': len(m), 'built_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')},
              open(VANILLA / 'meta.json', 'w'), indent=1)
    print(f'vanilla: {len(m)} files, {n} mtimes normalised, tree {h}')


def cmd_verify(key=None):
    if key is None and (GAMES / 'build').is_symlink():
        key = pathlib.Path(os.readlink(GAMES / 'build')).parent.name
    if not key: sys.exit('verify: which checkpoint?')
    recorded = read_manifest(manifest_path(key))
    actual = tree_manifest(tree_of(key))
    bad = sorted(set(r for r in actual if actual[r] != recorded.get(r)) | set(r for r in recorded if r not in actual))
    for r in bad: print(r)
    print(f'{key}: {len(bad)} paths differ from the manifest' if bad else f'{key}: matches its manifest ({len(actual)} files)')
    sys.exit(1 if bad else 0)


def cmd_verify_inputs():
    global LOG; LOG = open(LOGS / 'build.log', 'a')
    n = 0
    for entry in load_manifest(): n += len(inputs_hash(entry, full=True))
    print(f'{n} input files rehashed')


def cmd_checkout(key, dest):
    dest = pathlib.Path(dest)
    if dest.exists(): sys.exit(f'{dest} exists')
    reflink_copy(tree_of(key), dest); print(f'{key} -> {dest}')


def cmd_tag(name, key=None):
    TAGS.mkdir(parents=True, exist_ok=True)
    key = key or [k for _, k, _ in chain()][-1]
    (TAGS / name).write_text(key + '\n'); print(f'{name} = {key}')


def cmd_prove():
    """Determinism: the chain built again from vanilla into its own checkpoint directory, with no
    cached checkpoint reused, must reach the same tree hash at every entry. The first entry whose
    hash differs is named, with the paths that differ."""
    global CKPT
    preflight(); _l = lock()
    cached = {k: meta_of(k) for _, k, ok in chain() if ok}
    if len(cached) != len(load_manifest()): sys.exit('the cached chain is incomplete; run a build first')
    CKPT = GAMES / 'ckpt-prove'; use_work(GAMES / 'work-prove')
    CKPT.mkdir(exist_ok=True)
    for t in list(CKPT.iterdir()): shutil.rmtree(t)
    discard_work()
    global LOG; LOG = open(LOGS / 'build.log', 'a')
    log(f'--- prove {time.strftime("%Y-%m-%dT%H:%M:%S%z")}')
    for entry, key, _ in chain(build=True):
        a, b = cached[key]['tree'], meta_of(key)['tree']
        if a != b:
            ma, mb = read_manifest(GAMES / 'ckpt' / key / 'manifest.txt'), read_manifest(CKPT / key / 'manifest.txt')
            diff = sorted(set(r for r in mb if mb[r] != ma.get(r)) | set(r for r in ma if r not in mb))
            for r in diff[:50]: log('   ', r)
            log(f'NOT REPRODUCIBLE: {entry["mod"]} ({key}) gives tree {b[:12]}, the cached chain had {a[:12]}; {len(diff)} paths differ')
            sys.exit(1)
    discard_work()
    log(f'REPRODUCIBLE: {len(cached)} entries rebuilt to the same tree hashes; ckpt-prove/ can be removed')


def cmd_gc(keep=5):
    preflight()
    live = {k for _, k, ok in chain() if ok}
    live |= {p.read_text().strip() for p in TAGS.iterdir()} if TAGS.exists() else set()
    rest = sorted((d for d in CKPT.iterdir() if d.is_dir() and d.name not in live), key=lambda d: d.stat().st_mtime, reverse=True)
    before = shutil.disk_usage(CKPT).free
    for d in rest[keep:]:
        print('rm', d.name, (meta_of(d.name) or {}).get('mod', '?')); shutil.rmtree(d)
    print(f'kept {len(live)} in chain or tagged, {min(keep, len(rest))} recent others; df freed {(shutil.disk_usage(CKPT).free - before) / 2**30:.1f} GiB')


def main(argv):
    if not argv: return cmd_build(())
    c, a = argv[0], argv[1:]
    if c == 'status': return cmd_status()
    if c == 'base': return cmd_base()
    if c == 'verify': return cmd_verify(*a)
    if c == 'verify-inputs': return cmd_verify_inputs()
    if c == 'checkout': return cmd_checkout(*a)
    if c == 'tag': return cmd_tag(*a)
    if c == 'gc': return cmd_gc(int(a[1]) if a[:1] == ['--keep'] else 5)
    if c == 'prove': return cmd_prove()
    return cmd_build(tuple(argv))


if __name__ == '__main__':
    main(sys.argv[1:])
