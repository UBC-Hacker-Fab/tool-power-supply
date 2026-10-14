from lay import *

BX_I=172.72                                   # I2C bus (both INA226 on this sheet)
BX_S=270.51; BX_F=284.48; BX_E=298.45            # vertical buses on the right: SENSE, FAULT, EN

def buck(S,x,y,U,Cin,L,Cbst,Cout1,Cout2,out_sym=None,flag=None):
    """AP63205 / AP63203 buck converter block. Returns the end of the output line."""
    P=S.P
    S.at(U,x,y)
    en=P(U,2); inn=P(U,3)
    S.wire(f'{U}.2',(en[0]-2.54,en[1]),(en[0]-2.54,inn[1]),f'{U}.3')     # EN tied to IN
    S.power_at('12V_BUS',en[0]-2.54,inn[1],'u')
    decap(S,Cin,x-27.94,y,'12V_BUS')
    S.tap(f'{U}.4','GND')
    sw=P(U,5); bst=P(U,6); fb=P(U,1)
    S.at(Cbst,sw[0]+6.35,bst[1],90)                           # boost cap between BST (left) and SW (right)
    S.wire(f'{U}.6',f'{Cbst}.1')
    c2=P(Cbst,2); S.wire(f'{Cbst}.2',(c2[0],sw[1]))
    S.at(L,sw[0]+17.78,sw[1],90)
    S.wire(f'{U}.5',f'{L}.1')                                  # SW to the inductor (passes over the boost cap tap)
    ol=P(L,2); xo=ol[0]
    xend=xo+27.94
    S.wire(f'{L}.2',(xend,ol[1]))                              # output line
    S.wire(f'{U}.1',(fb[0]+2.54,fb[1]),(xo+7.62,fb[1]),(xo+7.62,ol[1]))   # FB sense wire joins the output
    for i,c in enumerate((Cout1,Cout2)):
        cx=xo+12.7+7.62*i
        S.at(c,cx,ol[1]+3.81); S.wire((cx,ol[1]),f'{c}.1'); S.tap(f'{c}.2','GND')
    if out_sym: S.power_at(out_sym,xo+5.08,ol[1],'u')
    if flag:
        S.wire((xo+3.81*0+20.32,ol[1]),(xo+20.32,ol[1]-5.08)); S.at(flag,xo+20.32,ol[1]-5.08)
    return (xend,ol[1])

def monitor(S,xv,yo,R,U,Cvs,Rled,Dled,rail,a0,flag):
    """Shunt in the output line, INA226 below it, rail LED, flag on the rail."""
    P=S.P
    S.at(R,xv+7.62,yo,90)
    S.wire((xv,yo),f'{R}.1')
    S.tap(f'{R}.2',rail,'u')
    rp=P(R,2); S.wire(f'{R}.2',(rp[0]+5.08,rp[1])); S.at(flag,rp[0]+5.08,rp[1])
    uy=yo+30.48
    S.at(U,xv+17.78,uy)
    vp=P(U,10); vb=P(U,8); vm=P(U,9)
    S.wire((xv,yo),(xv,vp[1]),f'{U}.10')                       # Vin+ from the buck output
    S.wire(f'{U}.8',(vb[0]-2.54,vb[1]),(vb[0]-2.54,vm[1]),f'{U}.9')
    S.power_at(rail,vb[0]-2.54,vb[1],'u')
    S.tap(f'{U}.1','GND','r',2.54,straight=True)
    if a0=='3V3_MCU': S.tap(f'{U}.2','3V3_MCU','r',5.08,straight=True)
    else:
        a=P(U,2); sd=P(U,4)
        S.wire(f'{U}.2',(a[0]+2.54,a[1]),(a[0]+2.54,sd[1]))      # A0 strapped to SDA
    S.tap(f'{U}.6','3V3_MCU','u'); S.tap(f'{U}.7','GND')
    decap(S,Cvs,P(U,6)[0]+12.7,P(U,6)[1]-3.81,'3V3_MCU')
    # I2C entries
    for pin,mem in ((4,'I2C.SDA'),(5,'I2C.SCL'),(3,'I2C.ALERT')):
        x,y=P(U,pin)
        S.wire((x,y),(BX_I-2.54,y)); S.entry(BX_I-2.54,y,2.54,2.54); S.label(mem,BX_I-12.7,y,0)
    # LED
    lx=xv-12.7
    S.at(Rled,lx,uy-7.62); S.tap(f'{Rled}.1',rail)
    S.at(Dled,lx,uy+3.81,90); S.wire(f'{Rled}.2',f'{Dled}.2'); S.tap(f'{Dled}.1','GND')
    return uy

def channel(S,TX,TY,U,Rilim,Cin,Ren,J,Rs_top,Rs_bot,rail,tag,sense_kind):
    P=S.P
    S.at(U,TX,TY)
    S.tap(f'{U}.1',rail,'u')
    g=P(U,2); S.wire(f'{U}.2',(g[0]-3.81,g[1])); S.power_at('GND',g[0]-3.81,g[1],'d')
    decap(S,Cin,TX-15.24,TY-3.81,rail)
    e=P(U,3)
    S.wire(f'{U}.3',(e[0],TY+10.16))
    S.at(Ren,TX-6.35,TY+10.16,270)
    S.wire((e[0],TY+10.16),f'{Ren}.1')
    S.tap(f'{Ren}.2','3V3_BUCK','l',2.54,'u')
    yen=TY+22.86
    S.wire((e[0],TY+10.16),(e[0],yen),(BX_E-2.54,yen))
    S.entry(BX_E-2.54,yen,2.54,2.54); S.label(f'EN.{tag}',BX_E-12.7,yen,0)
    o=P(U,6); il=P(U,5); fl=P(U,4)
    yo=TY-7.62
    xj=TX+58.42
    S.at(J,xj+5.08,yo)
    S.wire(f'{U}.6',(o[0]+2.54,o[1]),(o[0]+2.54,yo),f'{J}.1')
    S.tap(f'{J}.2','GND','l',2.54,'d')
    S.at(Rilim,il[0]+8.89,il[1],90)
    S.wire(f'{U}.5',f'{Rilim}.1'); S.tap(f'{Rilim}.2','GND','d')
    xc=TX+48.26
    if sense_kind=='divider':
        S.at(Rs_top,xc,yo+3.81); S.wire((xc,yo),f'{Rs_top}.1')
        S.at(Rs_bot,xc,yo+11.43); S.wire(f'{Rs_top}.2',f'{Rs_bot}.1'); S.tap(f'{Rs_bot}.2','GND')
        sn_=P(Rs_top,2)
        S.wire(sn_,(xc+5.08,sn_[1]),(xc+5.08,TY+12.7))
    else:
        S.at(Rs_bot,xc,yo+3.81); S.wire((xc,yo),f'{Rs_bot}.1'); S.tap(f'{Rs_bot}.2','GND')
        S.wire((xc+5.08,yo),(xc+5.08,TY+12.7))
    ys=TY+12.7
    S.wire((xc+5.08,ys),(BX_S-2.54,ys)); S.entry(BX_S-2.54,ys,2.54,2.54); S.label(f'SENSE.{tag}',BX_S-12.7,ys,0)
    yf=TY+17.78
    S.wire(f'{U}.4',(fl[0]+2.54,fl[1]),(fl[0]+2.54,yf),(BX_F-2.54,yf))
    S.entry(BX_F-2.54,yf,2.54,2.54); S.label(f'FAULT.{tag.split("_")[0]}',BX_F-12.7,yf,0)

def rails(S):
    P=S.P
    # =============== 5 V ===============
    S.text('5 V buck (AP63205, 2 A)',20.32,25.4,1.5,True)
    out5=buck(S,63.5,60.96,'U4','C5','L1','C6','C7','C8')
    S.text('5 V monitor (INA226 #2, address 0x41) and rail LED',20.32,92.71,1.5,True)
    monitor(S,out5[0],out5[1],'R20','U5','C9','R21','D5','5V_RAIL','3V3_MCU','#FLG02')
    S.text('5 V taps A and B (TPS2553, enable pull-up, presence sense)',190.5,25.4,1.5,True)
    channel(S,203.2,48.26,'U6','R22','C10','R23','J7','R24','R25','5V_RAIL','5V_A','divider')
    channel(S,203.2,99.06,'U7','R26','C11','R27','J8','R28','R29','5V_RAIL','5V_B','divider')
    # =============== 3.3 V ===============
    S.text('3.3 V buck (AP63203, 2 A)',20.32,152.4,1.5,True)
    out3=buck(S,63.5,187.96,'U8','C12','L2','C13','C14','C15',out_sym='3V3_BUCK',flag='#FLG03')
    S.text('3.3 V monitor (INA226 #3, address 0x42) and rail LED',20.32,222.25,1.5,True)
    monitor(S,out3[0],out3[1],'R30','U9','C16','R31','D6','3V3_RAIL','SDA','#FLG04')
    S.text('3.3 V taps A and B (TPS2553, enable pull-up; the tap net is the presence sense)',190.5,152.4,1.5,True)
    channel(S,203.2,175.26,'U10','R32','C17','R33','J9',None,'R34','3V3_RAIL','3V3_A','pulldown')
    channel(S,203.2,226.06,'U11','R35','C18','R36','J10',None,'R37','3V3_RAIL','3V3_B','pulldown')
    # buses
    u5=P('U5',4); u9=P('U9',3)
    S.bus((BX_I,u5[1]+2.54),(BX_I,P('U9',3)[1]+2.54)); S.hlabel('I2C{SDA SCL ALERT}','bidirectional',BX_I,P('U9',3)[1]+2.54,270) if False else None
    S.bus((BX_I,P('U9',3)[1]+2.54),(BX_I,P('U9',3)[1]+7.62)); S.hlabel('I2C{SDA SCL ALERT}','bidirectional',BX_I,P('U9',3)[1]+7.62,270)
    ys_end=226.06+12.7+2.54+10.16; yf_end=226.06+17.78+2.54+5.08; ye_end=226.06+22.86+2.54+2.54
    jS,jF,jE=ys_end+5.08,yf_end+12.7,ye_end+20.32       # staggered jogs so the long bus names run left along free space
    S.bus((BX_S,48.26-7.62+12.7+2.54),(BX_S,jS)); S.bus((BX_S,jS),(BX_S-7.62,jS)); S.hlabel('SENSE{12V_A 12V_B ESC 5V_A 5V_B 3V3_A 3V3_B}','bidirectional',BX_S-7.62,jS,180)
    S.bus((BX_F,48.26+17.78+2.54),(BX_F,jF)); S.bus((BX_F,jF),(BX_F-7.62,jF)); S.hlabel('FAULT{5V 3V3}','bidirectional',BX_F-7.62,jF,180)
    S.bus((BX_E,48.26+22.86+2.54),(BX_E,jE)); S.bus((BX_E,jE),(BX_E-7.62,jE)); S.hlabel('EN{12V_A 12V_B ESC 5V_A 5V_B 3V3_A 3V3_B}','bidirectional',BX_E-7.62,jE,180)
