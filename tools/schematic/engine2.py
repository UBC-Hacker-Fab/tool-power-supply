"""Schematic engine v2: placed symbols, orthogonal wires, junctions, power symbols,
local/hierarchical labels, buses and root-sheet generation."""
import math,re,copy
from sexp import *
from libs import *
from engine import Comp,fmt,U,rot_vec,lib_symbol_entry,PROJECT

G=1.27
def sn(v): return round(round(v/G)*G,4)

POWER={ # net -> (lib symbol, value shown)
 'GND':('power:GND','GND'),
 '12V_BUS':('power:+12V','12V_BUS'),
 '5V_RAIL':('power:+5V','5V_RAIL'),
 '3V3_MCU':('power:+3V3','3V3_MCU'),
 '3V3_BUCK':('power:+3V3','3V3_BUCK'),
 '3V3_RAIL':('power:+3V3','3V3_RAIL'),
}

class Sch:
    def __init__(s,name,title,uuid,root_uuid,parts,paper='A3'):
        s.name=name; s.title=title; s.uuid=uuid; s.root=root_uuid; s.paper=paper
        s.parts=parts            # ref -> Comp
        s.placed=set()
        s.wires=[]               # ((x1,y1),(x2,y2))
        s.buses=[]
        s.items=[]               # raw sexp items (labels, texts, bus entries, power symbols...)
        s.pwr=[]                 # power symbols placed: (lib,value,x,y,rot,ref)
        s.libs=set(); s.hlabels=[]  # (name,shape,x,y,angle)
        s.pinpts={}              # point -> count of pins/symbol pins at point
        s.pwr_n=0
    # ---------- placement
    def at(s,ref,x,y,rot=0,mirror=False,fld=None):
        c=s.parts[ref]; c.fld=fld; c.x=sn(x); c.y=sn(y); c.rot=rot; c.mirror=mirror; s.placed.add(ref)
        if mirror: assert rot==0
        for p in c.pins:
            X,Y=rot_vec(p['x'],p['y'],rot)
            if mirror: X=-X
            pt=(round(c.x+X,3),round(c.y-Y,3))
            s.pinpts[pt]=s.pinpts.get(pt,0)+1
        return c
    def P(s,ref,num):
        c=s.parts[ref]
        for p in c.pins:
            if p['number']==str(num):
                X,Y=rot_vec(p['x'],p['y'],c.rot)
                if getattr(c,'mirror',False): X=-X
                return (round(c.x+X,3),round(c.y-Y,3))
        raise KeyError((ref,num))
    def pt(s,a):
        if isinstance(a,str):
            ref,num=a.split('.'); return s.P(ref,num)
        return (round(sn(a[0]),3),round(sn(a[1]),3))
    # ---------- wires
    def wire(s,*pts,mode='h'):
        p=[s.pt(a) for a in pts]
        for a,b in zip(p,p[1:]):
            if a==b: continue
            if a[0]==b[0] or a[1]==b[1]: s.wires.append((a,b))
            else:
                c=(b[0],a[1]) if mode=='h' else (a[0],b[1])
                s.wires.append((a,c)); s.wires.append((c,b))
        return p[-1]
    def bus(s,*pts):
        p=[s.pt(a) for a in pts]
        for a,b in zip(p,p[1:]): s.buses.append((a,b))
    def entry(s,x,y,dx=2.54,dy=2.54):
        s.items.append(['bus_entry',['at',fmt(x),fmt(y)],['size',fmt(dx),fmt(dy)],['stroke',['width','0'],['type','default']],['uuid',Q(U())]])
    # ---------- net symbols
    def power(s,net,x,y,rot=None,hide_ref=True,hide_value=False):
        lib,val=POWER[net]
        if rot is None: rot=0 if net=='GND' else 0
        s.libs.add((lib.split(':')[0],lib.split(':')[1]))
        s.pwr_n+=1; ref=f'#PWR{s.name[:2].upper()}{s.pwr_n:03d}'
        s.pwr.append((lib,val,sn(x),sn(y),rot,ref,hide_value))
        s.pinpts[(round(sn(x),3),round(sn(y),3))]=s.pinpts.get((round(sn(x),3),round(sn(y),3)),0)+1
    def tap(s,pin,net,d=None,L=2.54,v=None,straight=False):
        """wire from a pin to a power symbol. d: direction of the stub ('u','d','l','r').
        Horizontal stubs end in a short vertical rise (v='u'/'d') so the symbol is always upright."""
        x,y=s.pt(pin)
        return s._tap_at(x,y,net,d,L,v,straight)
    def _tap_at(s,x,y,net,d,L,v,straight=False):
        if d is None: d='d' if net=='GND' else 'u'
        if straight and d in ('l','r'):
            dx=-1 if d=='l' else 1
            ex,ey=x+dx*L,y
            s.wires.append(((round(x,3),round(y,3)),(round(ex,3),round(ey,3))))
            rot={'GND':{'r':90,'l':270}[d]}.get(net) if net=='GND' else {'r':270,'l':90}[d]
            s.power(net,ex,ey,rot,hide_value=True)
            return (ex,ey)
        if d in ('u','d'):
            dy=-1 if d=='u' else 1
            ex,ey=x,y+dy*L
            s.wires.append(((round(x,3),round(y,3)),(round(ex,3),round(ey,3))))
            if net=='GND': rot={'d':0,'u':180}[d]
            else: rot={'u':0,'d':180}[d]
        else:
            dx=-1 if d=='l' else 1
            if v is None: v='d' if net=='GND' else 'u'
            mx=x+dx*L; vy=-1 if v=='u' else 1
            ex,ey=mx,y+vy*2.54
            s.wires.append(((round(x,3),round(y,3)),(round(mx,3),round(y,3))))
            s.wires.append(((round(mx,3),round(y,3)),(round(ex,3),round(ey,3))))
            if net=='GND': rot={'d':0,'u':180}[v]
            else: rot={'u':0,'d':180}[v]
        s.power(net,ex,ey,rot)
        return (ex,ey)
    def power_at(s,net,x,y,d=None,L=2.54,v=None,straight=False):
        return s._tap_at(round(x,3),round(y,3),net,d,L,v,straight)
    def label(s,name,x,y,angle=0,shape=None,glob=False):
        just='left' if angle in (0,90) else 'right'
        s.items.append(['label',Q(name),['at',fmt(x),fmt(y),str(angle)],['effects',['font',['size','1.27','1.27']],['justify',just,'bottom']],['uuid',Q(U())]])
    def lbl(s,pin,name,d='r',L=5.08):
        x,y=s.pt(pin)
        dx,dy={'u':(0,-1),'d':(0,1),'l':(-1,0),'r':(1,0)}[d]
        ex,ey=x+dx*L,y+dy*L
        s.wires.append(((x,y),(round(ex,3),round(ey,3))))
        s.label(name,ex,ey,{'r':0,'u':90,'l':180,'d':270}[d])
    def hlabel(s,name,shape,x,y,angle=0):
        s.hlabels.append((name,shape,round(x,3),round(y,3),angle))
        s.items.append(['hierarchical_label',Q(name),['shape',shape],['at',fmt(x),fmt(y),str(angle)],['effects',['font',['size','1.27','1.27']],['justify','left' if angle in (0,90) else 'right']],['uuid',Q(U())]])
    def hl(s,pin_or_pt,name,shape,d='l',L=7.62):
        x,y=s.pt(pin_or_pt)
        dx,dy={'u':(0,-1),'d':(0,1),'l':(-1,0),'r':(1,0)}[d]
        ex,ey=x+dx*L,y+dy*L
        s.wires.append(((x,y),(round(ex,3),round(ey,3))))
        # hierarchical label points away from the wire: angle indicates direction the label shape points
        s.hlabel(name,shape,ex,ey,{'l':180,'r':0,'u':90,'d':270}[d])
    def nc(s,pin):
        x,y=s.pt(pin); s.items.append(['no_connect',['at',fmt(x),fmt(y)],['uuid',Q(U())]])
    def text(s,t,x,y,size=1.27,bold=False):
        f=['font',['size',fmt(size),fmt(size)]]
        if bold: f.append(['bold','yes'])
        s.items.append(['text',Q(t),['exclude_from_sim','no'],['at',fmt(x),fmt(y),'0'],['effects',f,['justify','left','bottom']],['uuid',Q(U())]])
    # ---------- emit
    def junctions(s):
        segs=s.wires
        ends={}
        for a,b in segs:
            ends[a]=ends.get(a,0)+1; ends[b]=ends.get(b,0)+1
        cand=set(ends)|set(s.pinpts)
        out=[]
        for p in cand:
            n=ends.get(p,0)+s.pinpts.get(p,0)
            thru=0
            for a,b in segs:
                if p in (a,b): continue
                if a[0]==b[0]==p[0] and min(a[1],b[1])<p[1]<max(a[1],b[1]): thru+=1
                elif a[1]==b[1]==p[1] and min(a[0],b[0])<p[0]<max(a[0],b[0]): thru+=1
            if n+2*thru>=3 and (ends.get(p,0)>0 or thru>0): out.append(p)
        return out
    def emit(s,path,page=None):
        kids=[['version','20260306'],['generator',Q('eeschema')],['generator_version',Q('10.0')],['uuid',Q(s.uuid)],['paper',Q(s.paper)]]
        kids.append(['title_block',['title',Q(s.title)],['date',Q('2026-10-14')],['rev',Q('draft 2')],['company',Q('HackerFab power board')],['comment','1',Q('Hierarchical layout; generated by tools/schematic/build2.py')]])
        used=set(s.libs)
        for ref in s.placed:
            c=s.parts[ref]; used.add((c.nick,c.name))
        kids.append(['lib_symbols']+[lib_symbol_entry(n,m) for n,m in sorted(used)])
        body=[]
        for a,b in s.wires:
            body.append(['wire',['pts',['xy',fmt(a[0]),fmt(a[1])],['xy',fmt(b[0]),fmt(b[1])]],['stroke',['width','0'],['type','default']],['uuid',Q(U())]])
        for a,b in s.buses:
            body.append(['bus',['pts',['xy',fmt(a[0]),fmt(a[1])],['xy',fmt(b[0]),fmt(b[1])]],['stroke',['width','0'],['type','default']],['uuid',Q(U())]])
        for p in s.junctions():
            body.append(['junction',['at',fmt(p[0]),fmt(p[1])],['diameter','0'],['color','0','0','0','0'],['uuid',Q(U())]])
        body+=s.items
        for ref in sorted(s.placed,key=lambda r:(len(r),r)):
            body+=s.emit_comp(s.parts[ref],path)
        for lib,val,x,y,rot,ref,hv in s.pwr:
            body.append(s.emit_power(lib,val,x,y,rot,ref,path,hv))
        kids+=body
        kids.append(['sheet_instances',['path',Q('/'),['page',Q('1')]]])
        return ['kicad_sch']+kids
    def emit_comp(s,c,path):
        x,y=c.x,c.y
        def P(name,val,px,py,hide=False,just=None,ang=0):
            pr=['property',Q(name),Q(val),['at',fmt(px),fmt(py),str(((-c.rot)%360) if name in ('Reference','Value') else 0)],['effects',['font',['size','1.27','1.27']]]]
            if just and just!='center': pr[4].append(['justify']+just.split())
            if hide: pr[4].append(['hide','yes'])
            return pr
        # reference/value placement
        xs=[];ys=[]
        for p in c.pins:
            X,Y=rot_vec(p['x'],p['y'],c.rot)
            if getattr(c,'mirror',False): X=-X
            xs.append(X); ys.append(-Y)
        ang=(-c.rot)%360
        fld=getattr(c,'fld',None)
        two=len(set(zip(xs,ys)))==2 and c.nick in ('Device','Diode') or (len(c.pins)==2 and c.nick=='Device')
        if fld:
            rp=(x+fld[0],y+fld[1],fld[4] if len(fld)>4 else 'left'); vp=(x+fld[2],y+fld[3],fld[4] if len(fld)>4 else 'left')
        elif len(c.pins)==2 and c.nick in ('Device','Diode') and abs(xs[0]-xs[1])<0.01:
            rp=(x+3.2,y-1.2,'left'); vp=(x+3.2,y+1.6,'left')      # vertical two-pin part: text to the right
        elif len(c.pins)==2 and c.nick in ('Device','Diode'):
            rp=(x,y-3.4,'center'); vp=(x,y+4.4,'center')          # horizontal two-pin part: above and below
        else:
            cx=(max(xs)+min(xs))/2 if xs else 0
            top=min(ys) if ys else 0
            rp=(x+cx,y+top-5.2,'center'); vp=(x+cx,y+top-2.6,'center')
        inst=['symbol',['lib_id',Q(c.lib)],['at',fmt(x),fmt(y),str(c.rot)]]+([['mirror','y']] if getattr(c,'mirror',False) else [])+[['unit',str(c.unit)],['exclude_from_sim','no'],['in_bom','yes' if c.on_board or c.props.get('_bom','')=='yes' else 'no'],['on_board','yes' if c.on_board else 'no'],['dnp','yes' if c.dnp else 'no'],['uuid',Q(c.uuid)]]
        inst.append(P('Reference',c.ref,rp[0],rp[1],c.ref.startswith('#'),rp[2]))
        inst.append(P('Value',c.value,vp[0],vp[1],False,vp[2]))
        inst.append(P('Footprint',c.fp or prop(c.nick,c.name,'Footprint') or '',x,y,True))
        ds=prop(c.nick,c.name,'Datasheet') or ''
        inst.append(P('Datasheet',c.props.get('Datasheet',ds),x,y,True))
        inst.append(P('Description',c.desc or prop(c.nick,c.name,'Description') or '',x,y,True))
        for k,v in c.props.items():
            if k.startswith('_') or k=='Datasheet': continue
            inst.append(P(k,v,x,y,True))
        for p in c.pins: inst.append(['pin',Q(p['number']),['uuid',Q(U())]])
        inst.append(['instances',['project',Q(PROJECT),['path',Q(path),['reference',Q(c.ref)],['unit',str(c.unit)]]]])
        return [inst]
    def emit_power(s,lib,val,x,y,rot,ref,path,hv=False):
        return ['symbol',['lib_id',Q(lib)],['at',fmt(x),fmt(y),str(rot)],['unit','1'],['exclude_from_sim','no'],['in_bom','no'],['on_board','no'],['dnp','no'],['uuid',Q(U())],
          ['property',Q('Reference'),Q(ref),['at',fmt(x),fmt(y+3),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]],
          ['property',Q('Value'),Q(val),['at',fmt(x+1.5),fmt(y-2.6 if (lib!='power:GND') else y+3.4),'0'],['effects',['font',['size','1.27','1.27']],['justify','left']]+([['hide','yes']] if hv else [])],
          ['property',Q('Footprint'),Q(''),['at',fmt(x),fmt(y),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]],
          ['property',Q('Datasheet'),Q(''),['at',fmt(x),fmt(y),'0'],['effects',['font',['size','1.27','1.27']],['hide','yes']]],
          ['pin',Q('1'),['uuid',Q(U())]],
          ['instances',['project',Q(PROJECT),['path',Q(path),['reference',Q(ref)],['unit','1']]]]]
