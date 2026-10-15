#!/usr/bin/env python3
"""Download the archives of the KOTOR 1 Full Build into this directory.
DeadlyStream: guest session; multi-file pages use the picks below.
Nexus: premium API, file ids below. Each archive lands under <NN-slug>/.
"""
import sys,re,html,json,os,time,urllib.request,http.cookiejar,pathlib
here=pathlib.Path(__file__).parent
archives=pathlib.Path(os.environ.get('KOTOR_DATA', str(here.parent/'data')))/'archives'
archives.mkdir(parents=True, exist_ok=True)
mods=json.load(open(here/'k1full.json')); ds=json.load(open(here/'dsfiles.json'))
key=open(sys.argv[1]).read().strip()
DS_PICKS={'1258':['85513','85516'],'2514':['85520'],'980':['85214'],'1909':['53226'],'1213':['46015'],
 '2516':['83986','83987'],'2277':['70859'],'2430':['78365'],'2382':['84585'],'1133':['85268'],'2031':['84597'],
 '1929':['54734'],'1125':['86160'],'723':['53694'],'1925':['85281'],'2522':['72769'],'2739':['84640'],
 '1199':['71059'],'2659':['75302']}
NX_PICKS={'1367':[2204],'1365':[2217],'1364':[2213],'1368':[2223],'1370':[2225],'1366':[2221],'1360':[2211],
 '1282':[1968,1973,1974,1975,1976,1977,1978],'1369':[2302],'1632':[2606,2608],'1209':[1588],'1192':[1546],
 '90':[145],'1666':[2722],'1710':[2900],'1711':[3008],'66':[77],'1384':[1933]}
cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)); op.addheaders=[('User-Agent','Mozilla/5.0')]
def save(resp,dest,fallback):
    cd=resp.headers.get('Content-Disposition','')
    m=re.search(r"filename\*=UTF-8''([^;]+)",cd) or re.search(r'filename="?([^";]+)"?',cd)
    name=urllib.request.unquote(m.group(1)) if m else fallback
    if not m: name=os.path.basename(urllib.request.unquote(resp.geturl().split('?')[0])) or fallback
    name=os.path.basename(name.replace('\\','/'))
    p=dest/name
    if p.exists() and p.stat().st_size>0: print('  have',name); return
    tmp=p.with_suffix(p.suffix+'.part')
    with open(tmp,'wb') as f:
        while True:
            b=resp.read(1<<20)
            if not b: break
            f.write(b)
    tmp.rename(p); print('  got',name,p.stat().st_size)
n=0
for m in mods:
    if m['section']!='Mod List': continue
    n+=1; slug=re.sub(r'[^a-z0-9]+','-',m['title'].lower()).strip('-'); dest=archives/f'{n:03d}-{slug}'; dest.mkdir(exist_ok=True)
    print(f'[{n}] {m["title"]}',flush=True)
    for l in m.get('links',[]):
        dm=re.match(r'https?://deadlystream\.com/files/file/(\d+)-[^/?#]+',l)
        nm=re.match(r'https://www\.nexusmods\.com/kotor/mods/(\d+)',l)
        try:
            if dm:
                fid=dm.group(1); base=dm.group(0)+'/'
                if fid in DS_PICKS:
                    page=op.open(base+'?do=download',timeout=120).read().decode('utf-8','replace')
                    for r in DS_PICKS[fid]:
                        hm=re.search(r'''href=["']([^"']*r=%s[^"']*)["']'''%r,page)
                        if not hm: print('  MISSING r=',r); continue
                        save(op.open(html.unescape(hm.group(1)),timeout=600),dest,f'ds{fid}-{r}.bin')
                else:
                    resp=op.open(base+'?do=download',timeout=600)
                    if 'text/html' in resp.headers.get('Content-Type',''):
                        page=resp.read().decode('utf-8','replace')
                        hm=re.search(r'''href=["']([^"']*do=download[^"']*csrfKey=[^"']*)["']''',page)
                        if not hm: print('  no download link on',base); continue
                        resp=op.open(html.unescape(hm.group(1)),timeout=600)
                    save(resp,dest,f'ds{fid}.bin')
            elif nm:
                mid=nm.group(1)
                if mid not in NX_PICKS: print('  no nexus pick for',mid); continue
                for fid in NX_PICKS[mid]:
                    req=urllib.request.Request(f'https://api.nexusmods.com/v1/games/kotor/mods/{mid}/files/{fid}/download_link.json',headers={'apikey':key,'accept':'application/json'})
                    links=json.load(urllib.request.urlopen(req,timeout=60))
                    url=links[0]['URI'].replace(' ','%20')
                    save(op.open(url,timeout=1200),dest,f'nexus{mid}-{fid}.bin')
            else:
                print('  other host:',l)
        except Exception as e:
            print('  ERROR',l,e,flush=True)
        time.sleep(0.5)
print('DONE')
