import glob,os,re
from sexp import *
STOCK='/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
HF='/Users/anushmutyala/Documents/Github/hackerfab-kicadlibs/symbols'
_cache={}
def load_lib(nick):
    if nick in _cache: return _cache[nick]
    path=(f'{HF}/{nick}.kicad_sym' if nick.startswith('HF_') else f'{STOCK}/{nick}.kicad_sym')
    t=open(path,errors='ignore').read()
    root=parse(t)[0]
    syms={}
    for c in root:
        if isinstance(c,list) and c and c[0]=='symbol': syms[c[1]]=c
    _cache[nick]=syms
    return syms
def flatten(nick,name):
    syms=load_lib(nick)
    s=syms[name]
    ext=find1(s,'extends')
    if not ext: return s
    parent=flatten(nick,ext[1])
    # new symbol = parent contents with child's properties overriding
    child_props={p[1]:p for p in find(s,'property')}
    out=[ 'symbol', Q(name) ]
    seen=set()
    for c in parent[2:]:
        if isinstance(c,list) and c and c[0]=='property':
            out.append(child_props.get(c[1],c)); seen.add(c[1])
        elif isinstance(c,list) and c and c[0]=='symbol':
            # rename sub-symbols parentname_u_s -> name_u_s
            pn=parent[1]
            sub=list(c); sub[1]=Q(re.sub('^'+re.escape(pn),name,c[1])); out.append(sub)
        else: out.append(c)
    for k,p in child_props.items():
        if k not in seen: out.append(p)
    return out
def pins(nick,name):
    s=flatten(nick,name)
    res=[]
    for sub in find(s,'symbol'):
        m=re.search(r'_(\d+)_(\d+)$',sub[1])
        u,st=int(m.group(1)),int(m.group(2))
        for p in find(sub,'pin'):
            at=find1(p,'at'); nm=find1(p,'name'); num=find1(p,'number')
            res.append(dict(unit=u,style=st,etype=p[1],x=float(at[1]),y=float(at[2]),a=float(at[3]),name=str(nm[1]),number=str(num[1]),length=float(find1(p,'length')[1]),hide=any(isinstance(z,list) and z[0]=='hide' for z in p) or ('hide' in p)))
    return res
def prop(nick,name,key):
    s=flatten(nick,name)
    for p in find(s,'property'):
        if p[1]==key: return str(p[2])
    return None
