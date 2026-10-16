"""Layout helpers shared by the sheet layouts."""
G=1.27

def decap(S,ref,x,y,top,bottom='GND',dtop='u',dbot='d'):
    """standalone decoupling capacitor with its own supply symbols (vertical)"""
    S.at(ref,x,y)
    S.tap(f'{ref}.1',top,dtop); S.tap(f'{ref}.2',bottom,dbot)

def bus_v(S,x,y0,y1,name):
    """vertical bus line with a label"""
    S.bus((x,y0),(x,y1))
    S.items.append(['label',name_q(name),['at',fmt_(x),fmt_(y0),'90'],['effects',['font',['size','1.27','1.27']],['justify','left','bottom']],['uuid',uq()]])

def name_q(n):
    from sexp import Q
    return Q(n)
def uq():
    from sexp import Q
    from engine import U
    return Q(U())
def fmt_(v):
    from engine import fmt
    return fmt(v)

def member_to_vbus(S,start,bx,member,mode='h'):
    """wire from `start` (pin or point) horizontally to a vertical bus at x=bx and add the bus entry.
    The wire carries the member label. Returns the y of the wire."""
    sx,sy=S.pt(start)
    ex=bx-2.54
    S.wire((sx,sy),(ex,sy))
    S.entry(ex,sy,2.54,2.54)
    S.label(member,min(ex-10.16,sx+ (ex-sx)/2) if ex-sx>12.7 else sx+1.27, sy,0)
    return sy
