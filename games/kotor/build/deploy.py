#!/usr/bin/env python3
"""Deploy a checkpoint to the handheld, by content, into a copy that is swapped in by rename.

    deploy.py            deploy data/game/build (the chain's end)
    deploy.py KEY        deploy that checkpoint
    deploy.py --check    only report drift between the handheld's folder and the checkpoint

local.toml names the handheld ([handheld] ssh, game_dir). The game must not be running.

The handheld's live folder is reflink-copied to <game_dir>.next, rsync writes into that copy
comparing checksums, not timestamps, so a rebuilt file with identical content moves nothing;
then a dry run must find nothing left to do, the old folder becomes <game_dir>.prev (the
rollback) and the copy becomes live. The exclusions below are the one list of paths the
deploy never touches and the drift check never reports; they are printed on every run so
that what is outside the proof stays visible.
"""
import json, os, pathlib, subprocess, sys, tomllib

HERE = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(os.environ.get('KOTOR_DATA', str(HERE.parent / 'data'))).resolve()
LOCAL = HERE.parent.parent.parent / 'local.toml'

# Until KMRP's installer runs on the build host, everything it writes on the handheld lives
# outside the build, as do the player's saves and the logs the game and KMRP write.
EXCLUDE = ['/Saves/', '/swkotor.ini', '/swkotor.ini.*', '/binkw32.dll', '/binkw32Hooked.dll',
           '/configs/', '/patches/', '/dinput8.dll', '/K1DriverCompat.ini', '/k1-modern-driver-compatibility.asi',
           '/KMRP_*', '/KotorPatcher.dll', '/kpm_install_state.json', '/patch_config.toml*',
           '/kmrp-*', '*.log']


def sh(host, cmd, check=True, capture=False):
    return subprocess.run(['ssh', host, cmd], check=check, text=True, capture_output=capture)


def rsync(src, dest, dry):
    cmd = ['rsync', '--recursive', '--links', '--perms', '--times', '--checksum', '--delete', '--itemize-changes']
    if dry: cmd.append('--dry-run')
    for e in EXCLUDE: cmd += ['--exclude', e]
    cmd += [str(src) + '/', dest + '/']
    r = subprocess.run(cmd, text=True, capture_output=True)
    if r.returncode != 0: sys.exit(f'rsync failed:\n{r.stderr}')
    return [l for l in r.stdout.splitlines() if l and not l.startswith('.d')]


def main(argv):
    check = '--check' in argv; argv = [a for a in argv if a != '--check']
    cfg = tomllib.load(open(LOCAL, 'rb'))['handheld']
    host, game_dir = cfg['ssh'], cfg['game_dir']
    src = DATA / 'game' / 'ckpt' / argv[0] / 'tree' if argv else DATA / 'game' / 'build'
    if not src.is_dir(): sys.exit(f'no tree at {src}')
    key = src.resolve().parent.name
    meta = json.load(open(src.resolve().parent / 'meta.json'))
    print(f'deploying {key} ({meta["mod"]}, tree {meta["tree"][:12]}) to {host}:{game_dir}')
    print('outside the comparison:', ' '.join(EXCLUDE))

    if sh(host, 'pgrep -x swkotor.exe', check=False, capture=True).returncode == 0:
        sys.exit('the game is running on the handheld')
    live = sh(host, f'echo {game_dir}', capture=True).stdout.strip()
    drift = rsync(src, f'{host}:{live}', dry=True)
    if check:
        for l in drift: print(l)
        print(f'{len(drift)} paths differ' if drift else 'no drift')
        return sys.exit(1 if drift else 0)
    if not drift:
        print('nothing to deploy'); return
    for l in drift: print(l)

    nxt = f'{live}.next'
    sh(host, f'rm -rf "{nxt}" && cp -a --reflink=always "{live}" "{nxt}"')
    rsync(src, f'{host}:{nxt}', dry=False)
    left = rsync(src, f'{host}:{nxt}', dry=True)
    if left:
        for l in left: print(l)
        sys.exit(f'{len(left)} paths still differ after the sync; {nxt} left for inspection, live folder untouched')
    sh(host, f'rm -rf "{live}.prev" && mv "{live}" "{live}.prev" && mv "{nxt}" "{live}"')
    print(f'{len(drift)} paths updated; previous folder kept as {live}.prev')


if __name__ == '__main__':
    main(sys.argv[1:])
