#!/usr/bin/env python3
"""Download public mega.nz file links (new file/ID#KEY and old #!ID!KEY forms)."""
import sys,re,json,base64,struct,urllib.request,os
from Crypto.Cipher import AES
from Crypto.Util import Counter
def b64d(s): s=s.replace('-','+').replace('_','/'); return base64.b64decode(s+'='*(-len(s)%4))
def words(b): return struct.unpack('>%dI'%(len(b)//4), b)
def api(req):
    r=urllib.request.Request('https://g.api.mega.co.nz/cs?id=1',data=json.dumps([req]).encode(),headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
    return json.load(urllib.request.urlopen(r,timeout=60))[0]
def dl(url,dest='.'):
    m=re.search(r'mega\.nz/(?:file/([^#]+)#([^ ]+)|#!([^!]+)!([^ ]+))',url)
    fid=m.group(1) or m.group(3); key=m.group(2) or m.group(4)
    k=words(b64d(key)); fk=struct.pack('>4I',k[0]^k[4],k[1]^k[5],k[2]^k[6],k[3]^k[7]); iv=(k[4]<<32|k[5])<<64
    info=api({'a':'g','g':1,'p':fid}); 
    if isinstance(info,int): raise RuntimeError(f'mega error {info}')
    attrs=AES.new(fk,AES.MODE_CBC,b'\0'*16).decrypt(b64d(info['at'])).rstrip(b'\0')
    name=json.loads(attrs[4:].decode())['n']; size=info['s']
    p=os.path.join(dest,name)
    if os.path.exists(p) and os.path.getsize(p)==size: print('have',name,size); return p
    c=AES.new(fk,AES.MODE_CTR,counter=Counter.new(128,initial_value=iv))
    with urllib.request.urlopen(urllib.request.Request(info['g'],headers={'User-Agent':'Mozilla/5.0'}),timeout=600) as r, open(p,'wb') as f:
        while True:
            b=r.read(1<<20)
            if not b: break
            f.write(c.decrypt(b))
    print('got',name,size,os.path.getsize(p)); return p
if __name__=='__main__':
    for u in sys.argv[1:]: 
        try: dl(u)
        except Exception as e: print('FAILED',u,repr(e))
