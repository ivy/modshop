#!/usr/bin/env python3
"""Apply the KOTOR 1 Full Build manifest to a game directory.

Every step works case-insensitively inside Override (Wine resolves names that
way, and two files differing only in case would be a coin toss), and every
archive is unpacked once into STAGE/<mod>/ before its steps run.
"""
import sys,os,re,json,shutil,subprocess,pathlib,fnmatch
HERE=pathlib.Path(__file__).resolve().parent
DATA=pathlib.Path(os.environ.get('KOTOR_DATA', str(HERE.parent/'data'))).resolve()
ARCHIVES=DATA/'archives'   # one numbered folder per mod, as download.py left them
LOGS=DATA/'logs'
GAME=pathlib.Path(os.environ['KOTOR_GAME']).resolve()
STAGE=pathlib.Path(os.environ.get('KOTOR_STAGE', str(DATA/'stage'))).resolve()
HP=os.environ['HOLOPATCHER']
OVR=GAME/'Override'; OVR.mkdir(exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)
LOG=open(LOGS/'install.log','a')
def log(*a):
    s=' '.join(str(x) for x in a); print(s,flush=True); LOG.write(s+'\n'); LOG.flush()
def ci_find(d,name):
    """Path of `name` inside dir `d`, matched case-insensitively, or None."""
    low=name.lower()
    for p in d.iterdir():
        if p.name.lower()==low: return p
    return None
def _resolve(cur,parts):
    """All paths under cur matching the segment list (case-insensitive, * wildcards per segment)."""
    if not parts: return [cur]
    if not cur.is_dir(): return []
    part,rest=parts[0],parts[1:]
    if '*' in part:
        kids=sorted(p for p in cur.iterdir() if fnmatch.fnmatch(p.name.lower(),part.lower()) and '__macosx' not in p.name.lower())
    else:
        k=ci_find(cur,part); kids=[k] if k else []
    out=[]
    for k in kids: out+=_resolve(k,rest)
    return out
def ci_path(root,rel):
    """Resolve a slash path under root case-insensitively; a segment may hold * wildcards.
    Archives unpack as <stem>/<their own folders>, so if nothing matches, one or two extra
    wildcard levels are tried after the first segment before giving up; a path that does
    not exist is returned as given (callers that create files rely on that)."""
    if rel.startswith('/'): return pathlib.Path(rel)
    if rel.startswith('data/'): return DATA/rel[5:]      # another archive folder, e.g. data/archives/k1cp-fix
    root=pathlib.Path(root); parts=list(pathlib.PurePosixPath(rel.replace('\\','/')).parts)
    if not parts or parts==['.']: return root
    for extra in (0,1,2):
        trial=parts[:1]+['*']*extra+parts[1:] if parts[0]!='.' else ['*']*extra+parts[1:]
        hits=_resolve(root,trial)
        if hits: return hits[0]
    return root.joinpath(*parts)
def put(src,dest_dir=None):
    """Copy a file into Override (or dest_dir), replacing any case-variant of it."""
    dest_dir=pathlib.Path(dest_dir) if dest_dir else OVR
    dest_dir.mkdir(parents=True,exist_ok=True)
    old=ci_find(dest_dir,src.name)
    if old and old.name!=src.name: old.unlink()
    shutil.copy2(src,dest_dir/src.name)
def extract(mod):
    d=ARCHIVES/mod; out=STAGE/mod
    if out.exists(): return out
    out.mkdir(parents=True)
    for a in sorted(d.iterdir()):
        if a.suffix.lower() in ('.zip','.rar','.7z'):
            sub=out/a.stem; sub.mkdir()
            r=subprocess.run(['7zz','x','-y','-bd','-bso0',f'-o{sub}',str(a)],capture_output=True,text=True)
            if r.returncode!=0: raise RuntimeError(f'7zz failed on {a}: {r.stderr[-500:]}')
            # Windows zips with backslash names unpack as single files named "a\b\c"
            for f in list(sub.iterdir()):
                if '\\' in f.name:
                    t=sub/f.name.replace('\\','/'); t.parent.mkdir(parents=True,exist_ok=True); f.rename(t)
        elif a.is_file():
            shutil.copy2(a,out/a.name)
    return out
def files_in(root,pattern='*',recursive=False):
    root=pathlib.Path(root)
    it=root.rglob('*') if recursive else root.iterdir()
    return sorted(p for p in it if p.is_file() and fnmatch.fnmatch(p.name.lower(),pattern.lower()) and not p.name.lower().endswith(('.jpg','.png','.txt','.rtf','.pdf','.md','.ds_store','.url','.htm','.html','.docx','.exe','.bat','.ini')) and '__macosx' not in str(p).lower())
# ---- step verbs -------------------------------------------------------------
def s_copy(st,src='.',pattern='*',exclude=(),recursive=False,dest=None):
    """Copy files from a staged folder into Override."""
    root=ci_path(st,src)
    if not root.exists(): raise FileNotFoundError(f'copy: {root}')
    # a wrapper folder holding nothing but one folder is not the mod's content yet
    while not recursive and not files_in(root,pattern) and len([d for d in root.iterdir() if d.is_dir() and '__macosx' not in d.name.lower()])==1:
        root=[d for d in root.iterdir() if d.is_dir() and '__macosx' not in d.name.lower()][0]
    ex=[e.lower() for e in exclude]; n=0
    for f in files_in(root,pattern,recursive):
        if any(fnmatch.fnmatch(f.name.lower(),e) for e in ex): continue
        put(f, GAME/dest if dest else None); n+=1
    log('   copied',n,'from',root.relative_to(STAGE))
    if n==0: raise RuntimeError('copied nothing')
def s_copy_files(st,src,names,dest=None):
    for n in names: put(ci_path(st,f'{src}/{n}'), GAME/dest if dest else None)
    log('   copied',len(names),'named files from',src)
def s_delete(st,names):
    """Delete files from Override (case-insensitive); missing ones are reported, not fatal."""
    for n in names:
        p=ci_find(OVR,n)
        if p: p.unlink(); log('   deleted',n)
        else: log('   (absent)',n)
def s_rename_in_override(st,old,new):
    p=ci_find(OVR,old); 
    if not p: raise FileNotFoundError(old)
    q=ci_find(OVR,new); 
    if q: q.unlink()
    p.rename(OVR/new); log('   renamed',old,'->',new)
def s_stage_delete(st,src,names):
    for n in names:
        p=ci_path(st,f'{src}/{n}')
        if p.exists(): p.unlink()
def s_stage_copy_as(st,src,new):
    p=ci_path(st,src); shutil.copy2(p,p.parent/new)
def s_tlk(st,src):
    shutil.copy2(ci_path(st,src),GAME/'dialog.tlk'); log('   dialog.tlk <-',src)
def case_aliases(td):
    """pykotor opens module files by exact name: for every modules\\<name> a mod's ini files mention
    whose case differs from the file on disk, link that spelling to the real file for the run."""
    mods=GAME/'modules'; created=[]
    for ini in list(td.rglob('*.ini')):
        text=ini.read_text(encoding='utf-8',errors='replace')
        for name in set(re.findall(r'(?i)modules\\([^\\\r\n;=]+?\.(?:mod|rim|erf))\s*$',text,re.M)):
            name=name.strip(); real=ci_find(mods,name)
            if real and real.name!=name and not (mods/name).exists():
                (mods/name).symlink_to(real.name); created.append((mods/name,real)); log('   alias',name,'->',real.name)
    return created
def drop_aliases(created):
    for link,real in created:
        if link.is_symlink(): link.unlink()
        elif link.exists():
            # the patcher replaced the link with a real file: keep it under the canonical name
            link.replace(real); log('   alias',link.name,'became the file; moved to',real.name)
def s_holopatcher(st,src='.',option=None,allow_errors=0):
    """Run HoloPatcher on a staged tslpatchdata (or its parent). option = namespace index."""
    td=ci_path(st,src)
    aliases=case_aliases(td)
    cmd=[HP,'--game-dir',str(GAME),'--tslpatchdata',str(td),'--install','--console']
    if option is not None: cmd+=['--namespace-option-index',str(option)]
    r=subprocess.run(cmd,capture_output=True,text=True)
    drop_aliases(aliases)
    (LOGS/'holopatcher').mkdir(exist_ok=True)
    n=len(list((LOGS/'holopatcher').glob('hp-*.log')))+1
    (LOGS/'holopatcher'/f'hp-{n:03d}-{td.parts[-3][:30] if len(td.parts)>2 else td.name}.log').write_text(r.stdout+'\n--- stderr ---\n'+r.stderr)
    tail=[l for l in r.stdout.splitlines() if l.startswith('[Error]') or 'Install completed' in l or l.startswith('[Warning]')]
    for l in tail[-6:]: log('   ',l[:200])
    m=[re.search(r'Install completed: (\d+) errors',l) for l in tail]; m=[x for x in m if x]
    if not m or int(m[-1].group(1))>allow_errors:
        raise RuntimeError(f'holopatcher failed on {td} (exit {r.returncode})')
def s_dedupe_tpc(st):
    """Remove every Override .tpc that has a same-named .tga or .dds (the game crashes when both exist)."""
    names={p.name.lower():p for p in OVR.iterdir()}
    n=0
    for low,p in list(names.items()):
        if low.endswith('.tpc') and (low[:-4]+'.tga' in names or low[:-4]+'.dds' in names):
            p.unlink(); n+=1
    log('   removed',n,'duplicate tpc files')
VERBS={'dedupe_tpc':s_dedupe_tpc,'copy':s_copy,'copy_files':s_copy_files,'delete':s_delete,'rename':s_rename_in_override,'stage_delete':s_stage_delete,'stage_copy_as':s_stage_copy_as,'tlk':s_tlk,'holopatcher':s_holopatcher}
# ---- driver -----------------------------------------------------------------
def main():
    manifest=json.load(open(HERE/'manifest.json'))
    done=set(json.load(open(LOGS/'install.state.json'))) if (LOGS/'install.state.json').exists() else set()
    only=sys.argv[1:]
    for entry in manifest:
        mod=entry['mod']
        if only and mod not in only: continue
        if mod in done and not only: continue
        if entry.get('skip'): log(f'-- {mod}: SKIP ({entry["skip"]})'); done.add(mod); continue
        log(f'== {mod}')
        st=extract(entry.get('stage',mod))
        for step in entry['steps']:
            step=dict(step); verb=step.pop('do'); log('  ',verb,step)
            VERBS[verb](st,**step)
        done.add(mod); json.dump(sorted(done),open(LOGS/'install.state.json','w'))
    log('ALL DONE')
if __name__=='__main__': main()
