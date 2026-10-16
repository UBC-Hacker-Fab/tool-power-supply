import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
sys.argv_saved=sys.argv
import io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x','/tmp/_ignore_build']
    import build as _b   # assigns refs and builds v1 (ignored output)
import design
from design import sheets,ORDER,root_uuid
from engine import PROJECT
from engine2 import *
import layout_mains,layout_bus12v,layout_rails,layout_mcu
OUT=None; SOLO=None; HL={}
args=[a for a in sys_argv] if False else sys.argv_saved[1:]
for a in args:
    if a.startswith('--solo='): SOLO=a.split('=',1)[1]
    elif a=='--force': pass
    else: OUT=a
OUT=OUT or os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tool-power-supply-v1')
os.makedirs(OUT,exist_ok=True)
# KiCad drops ~*.lck files next to the project while it has it open, and will overwrite our output on its next save.
_locks=[f for f in os.listdir(OUT) if f.startswith('~') and f.endswith('.lck')]
if _locks and '--force' not in sys.argv_saved:
    sys.exit('KiCad appears to have the project open (%s in %s). Close KiCad without saving, then rerun; pass --force to write anyway.'%(', '.join(_locks),os.path.abspath(OUT)))
LAYOUT={'mains':layout_mains.mains,'bus12v':layout_bus12v.bus12v,'rails':layout_rails.rails,'mcu':layout_mcu.mcu}
for n in ORDER:
    if n not in LAYOUT: continue
    if SOLO and n!=SOLO: continue
    sh=sheets[n]
    parts={c.ref:c for _,comps in sh.sections for c in comps}
    # reset placement state
    uuid=root_uuid if SOLO else sh.uuid
    S=Sch(n,sh.title,uuid,root_uuid,parts,paper='A3')
    LAYOUT[n](S)
    left=[r for r in parts if r not in S.placed]
    print(n,'placed',len(S.placed),'of',len(parts),'unplaced:',left)
    path=f'/{root_uuid}' if SOLO else f'/{root_uuid}/{sh.uuid}'
    fn=os.path.join(OUT,('tool-power-supply-v1' if SOLO else n)+'.kicad_sch')
    open(fn,'w').write(dump(S.emit(path))+'\n')
    print('wrote',fn)
    HL[n]=sorted(set((a,b) for a,b,*_ in S.hlabels))
    for a,b in HL[n]: print('   hl',a,b)

# ---------------- root sheet ----------------
def build_root():
    def pin(name,shape,x,y,ang):
        j='left' if ang in (0,90) else 'right'
        if ang==180: j='left'
        return ['pin',Q(name),shape,['at',fmt(x),fmt(y),str(ang)],['uuid',Q(U())],['effects',['font',['size','1.27','1.27']],['justify','right' if ang==0 else 'left']]]
    def sheet(n,x,y,w,h,pins,page):
        sh=sheets[n]
        k=['sheet',['at',fmt(x),fmt(y)],['size',fmt(w),fmt(h)],['exclude_from_sim','no'],['in_bom','yes'],['on_board','yes'],['dnp','no'],['fields_autoplaced','yes'],['stroke',['width','0.1524'],['type','solid']],['fill',['color','0','0','0','0']],['uuid',Q(sh.uuid)],
           ['property',Q('Sheetname'),Q(n),['at',fmt(x),fmt(y-1),'0'],['effects',['font',['size','1.27','1.27']],['justify','left','bottom']]],
           ['property',Q('Sheetfile'),Q(f'{n}.kicad_sch'),['at',fmt(x),fmt(y+h+1),'0'],['effects',['font',['size','1.27','1.27']],['justify','left','top']]]]
        k+=pins
        k.append(['instances',['project',Q(PROJECT),['path',Q('/'+root_uuid),['page',Q(str(page))]]]])
        return k
    items=[]; wires=[]; buses=[]; juncs=[]
    def W(*p): wires.append(p)
    def B(a,b): buses.append((a,b))
    def J(x,y): juncs.append((x,y))
    shapes={n:dict(HL[n]) for n in HL}
    # geometry
    MX,MY=25.4,30.48; BX,BY=25.4,91.44; RX,RY=25.4,152.4; CX,CY=190.5,88.9
    RE=88.9
    L=lambda n,d: [k for k in d]
    def stack(n,names,x,y0,ang):
        out=[];ys={}
        for i,nm in enumerate(names):
            yy=y0+i*5.08; out.append(pin(nm,shapes[n][nm],x,yy,ang)); ys[nm]=yy
        return out,ys
    busorder=['EN','SENSE','FAULT','I2C','FAN']
    def kind(nm): return nm.split('{')[0]
    # mains
    mp=[pin('12V_MOD','output',MX+10.16,MY+25.4,270),pin('ACS_OUT','output',MX+63.5,MY+5.08,0)]
    items.append(sheet('mains',MX,MY,63.5,25.4,mp,2))
    # bus12v
    names=sorted([k for k in shapes['bus12v'] if kind(k) in busorder],key=lambda k:busorder.index(kind(k)))
    bp,bys=stack('bus12v',names,RE,BY+5.08,0); bp.append(pin('12V_MOD','input',BX+10.16,BY,90))
    items.append(sheet('bus12v',BX,BY,63.5,38.1,bp,3))
    names=[k for k in sorted(shapes['rails'],key=lambda k:busorder.index(kind(k)))]
    rp,rys=stack('rails',names,RE,RY+5.08,0)
    items.append(sheet('rails',RX,RY,63.5,38.1,rp,4))
    names=[k for k in sorted(shapes['mcu'],key=lambda k:busorder.index(kind(k)) if kind(k) in busorder else -1)]
    cp,cys=stack('mcu',names,CX,CY+5.08,180)
    items.append(sheet('mcu',CX,CY,76.2,60.96,cp,5))
    W((MX+10.16,MY+25.4),(MX+10.16,BY))
    ay=cys['ACS_OUT']
    W((MX+63.5,MY+5.08),(172.72,MY+5.08),(172.72,ay),(CX,ay))
    tx={k:104.14+12.7*i for i,k in enumerate(busorder)}
    ends={k:[] for k in busorder}
    for d in (bys,rys):
        for nm,yy in d.items():
            k=kind(nm); B((RE,yy),(tx[k],yy)); ends[k].append(yy)
            d[nm]=(tx[k],yy)
    for nm,yy in cys.items():
        if kind(nm) not in busorder: continue
        k=kind(nm); B((tx[k],yy),(CX,yy)); ends[k].append(yy)
    for k in busorder:
        lo,hi=min(ends[k]),max(ends[k]); B((tx[k],lo),(tx[k],hi))
        for yy in set(ends[k]):
            if lo<yy<hi: J(tx[k],yy)
    body=[]
    for pts in wires:
        for a,b in zip(pts,pts[1:]):
            body.append(['wire',['pts',['xy',fmt(a[0]),fmt(a[1])],['xy',fmt(b[0]),fmt(b[1])]],['stroke',['width','0'],['type','default']],['uuid',Q(U())]])
    for a,b in buses:
        body.append(['bus',['pts',['xy',fmt(a[0]),fmt(a[1])],['xy',fmt(b[0]),fmt(b[1])]],['stroke',['width','0'],['type','default']],['uuid',Q(U())]])
    for x,y in juncs:
        body.append(['junction',['at',fmt(x),fmt(y)],['diameter','0'],['color','0','0','0','0'],['uuid',Q(U())]])
    notes=("Rev 1 power board. Sheets connect through sheet pins; control signals travel on the bus groups EN, SENSE, FAULT, I2C and FAN. "
           "Source of truth for decisions: design-context/design-decisions.md; BOM: design-context/bom.md; pin map: design-context/pin-map.md. Generated by tools/schematic/build2.py.")
    body.append(['text',Q(notes),['exclude_from_sim','no'],['at','25.4','20.32','0'],['effects',['font',['size','1.27','1.27']],['justify','left','top']],['uuid',Q(U())]])
    for lbl,x,y in (('12 V bus and branch switches',BX,BY+40.64),('5 V / 3.3 V rails and taps',RX,RY+40.64),('Pico 2, analog inputs, SSR drive',CX,CY+63.5),('Mains zone',MX,MY+27.94)):
        body.append(['text',Q(lbl),['exclude_from_sim','no'],['at',fmt(x),fmt(y),'0'],['effects',['font',['size','1.27','1.27']],['justify','left','top']],['uuid',Q(U())]])
    root=[['version','20260306'],['generator',Q('eeschema')],['generator_version',Q('10.0')],['uuid',Q(root_uuid)],['paper',Q('A3')],
          ['title_block',['title',Q('HackerFab tool power supply')],['date',Q('2026-10-14')],['rev',Q('draft 2')],['comment','1',Q('Hierarchical layout; generated by tools/schematic/build2.py')]],['lib_symbols']]
    root+=items+body+[['sheet_instances',['path',Q('/'),['page',Q('1')]]],['embedded_fonts','no']]
    return ['kicad_sch']+root

if not SOLO:
    open(os.path.join(OUT,'tool-power-supply-v1.kicad_sch'),'w').write(dump(build_root())+'\n')
    print('root written')
