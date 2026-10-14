from lay import *

EN_ALL ='EN{12V_A 12V_B ESC 5V_A 5V_B 3V3_A 3V3_B}'
SENSE_ALL='SENSE{12V_A 12V_B ESC 5V_A 5V_B 3V3_A 3V3_B}'
FAULT_ALL='FAULT{5V 3V3}'
I2C_ALL='I2C{SDA SCL ALERT}'
FAN_ALL='FAN{PWM TACH}'

def mcu(S):
    P=S.P
    D=33.02
    x0,y0=144.78+D,127.0
    S.at('U12',x0,y0)
    S.text('Raspberry Pi Pico 2 (plugged into 2 x 1x20 sockets; pin map in design-context/pin-map.md)',40.64+D,76.2,1.5,True)
    # ---------- supply pins ----------
    S.tap('U12.36','3V3_MCU','u')
    S.tap('U12.38','GND','d')                  # all GND pins are stacked at one point
    S.nc('U12.40'); S.nc('U12.30'); S.nc('U12.37'); S.nc('U12.35'); S.nc('U12.22')
    S.tap('U12.33','GND','r',2.54)
    # 5 V to VSYS through the Schottky
    vs=P('U12',39)
    S.at('D7',vs[0]-17.78,vs[1]-6.35,180)
    S.wire('D7.1',(vs[0],vs[1]-6.35),'U12.39')
    S.tap('D7.2','5V_RAIL','l',2.54,'u')
    S.wire((vs[0],vs[1]-6.35),(vs[0]+5.08,vs[1]-6.35)); S.at('#FLG05',vs[0]+5.08,vs[1]-6.35)
    # ---------- left side buses ----------
    bx=86.36+D
    rows={1:('SENSE','5V_A'),2:('SENSE','5V_B'),4:('SENSE','3V3_A'),5:('SENSE','3V3_B'),
          6:('I2C','SDA'),7:('I2C','SCL'),
          9:('EN','5V_A'),10:('EN','5V_B'),11:('EN','3V3_A'),12:('EN','3V3_B'),
          14:('FAULT','5V'),15:('FAULT','3V3'),
          16:('EN','12V_A'),17:('EN','12V_B'),19:('EN','ESC'),20:('SENSE','12V_A')}
    segs={}      # (kind,groupid) -> list of entry-end y
    groups=[('SENSE',[1,2,4,5],SENSE_ALL,5.08),('I2C',[6,7],I2C_ALL,None),('EN',[9,10,11,12],EN_ALL,5.08),
            ('FAULT',[14,15],FAULT_ALL,5.08),('EN',[16,17,19],EN_ALL,5.08),('SENSE',[20],SENSE_ALL,5.08)]
    ext={}
    for kind,pins,full,L in groups:
        ends=[]
        for pn in pins:
            x,y=P('U12',pn)
            S.wire((x,y),(bx+2.54,y)); S.entry(bx+2.54,y,-2.54,2.54)
            S.label(f'{rows[pn][0]}.{rows[pn][1]}',bx+7.62,y,0)
            ends.append(y+2.54)
        top=min(ends); bot=max(ends)
        if len(ends)==1: bot=top+2.54
        S.bus((bx,top),(bx,bot))
        # extension to the left and hierarchical label
        xl=bx-(L if L else 83.82)
        S.bus((bx,top),(xl,top))
        S.hlabel(full,'bidirectional',xl,top,180)
        ext[(kind,pins[0])]=(top,xl)
    # I2C pull-ups on the extended I2C bus (row = top end of the I2C segment)
    ytop,xl=ext[('I2C',6)]
    for ref,xe,mem in (('R38',50.8,'I2C.SDA'),('R39',40.64,'I2C.SCL')):
        S.entry(xe,ytop,2.54,-2.54)               # bus point (xe,ytop) up to wire end (xe+2.54,ytop-2.54)
        yw=ytop-2.54
        S.at(ref,xe+2.54,yw-2.54-3.81,180)         # bottom pin end at yw-2.54
        S.wire((xe+2.54,yw),f'{ref}.1')
        S.label(mem,xe+2.54,yw,90)
        S.tap(f'{ref}.2','3V3_MCU','u')
    # ---------- right side: buses ----------
    xa,xb,xc=205.74+D,218.44+D,231.14+D
    # SENSE 12V_B / ESC
    ends=[]
    for pn,mem in ((27,'12V_B'),(29,'ESC')):
        x,y=P('U12',pn); S.wire((x,y),(xa-2.54,y)); S.entry(xa-2.54,y,2.54,2.54); S.label(f'SENSE.{mem}',xa-12.7,y,0); ends.append(y+2.54)
    S.bus((xa,min(ends)),(xa,max(ends))); S.hlabel(SENSE_ALL,'bidirectional',xa,max(ends),0)
    # I2C ALERT
    x,y=P('U12',26); S.wire((x,y),(xb-2.54,y)); S.entry(xb-2.54,y,2.54,2.54); S.label('I2C.ALERT',xb-12.7,y,0)
    S.bus((xb,y+2.54),(xb,y+5.08)); S.hlabel(I2C_ALL,'bidirectional',xb,y+5.08,0)
    # FAN PWM / TACH
    ends=[]
    for pn,mem in ((21,'PWM'),(25,'TACH')):
        x,y=P('U12',pn); S.wire((x,y),(xc-2.54,y)); S.entry(xc-2.54,y,2.54,2.54); S.label(f'FAN.{mem}',xc-12.7,y,0); ends.append(y+2.54)
    S.bus((xc,min(ends)),(xc,max(ends))); S.hlabel(FAN_ALL,'bidirectional',xc,max(ends),0)
    # ---------- ADC lanes ----------
    # ACS712 (pin 31), NTC module (pin 32), NTC SSR heat sink (pin 34)
    lanes=[(31,'R40','R41',182.88+D,160.02),(32,'R42','TH1',177.8+D,182.88),(34,'R43','J11',172.72+D,205.74)]
    nx=205.74+D
    for pn,Rt,Rb,lx,ly in lanes:
        x,y=P('U12',pn)
        S.wire((x,y),(lx,y),(lx,ly),(nx,ly))
    # ACS712 divider: 4.7k from ACS_OUT, 10k to ground
    S.at('R40',nx+3.81,160.02,270,fld=(0,-3.2,0,4.2,'center')); S.hl('R40.1','ACS_OUT','input','r',10.16)
    S.at('R41',nx,163.83,fld=(3.2,-1.2,3.2,1.6,'left')); S.wire((nx,160.02),'R41.1'); S.tap('R41.2','GND')
    S.text('ACS712 output divider (ratio 0.68)',nx-5.08,153.67)
    # NTC on the module
    S.at('R42',nx+3.81,182.88,270,fld=(0,-3.2,0,4.2,'center'))
    S.wire('R42.1',(nx+10.16,182.88)); S.power_at('3V3_MCU',nx+10.16,182.88,'u')
    S.at('TH1',nx,186.69,fld=(3.2,-1.2,3.2,1.6,'left')); S.wire((nx,182.88),'TH1.1'); S.tap('TH1.2','GND')
    S.text('NTC on the module',nx-5.08,176.53)
    # NTC on the SSR heat sink (off-board through a terminal)
    S.at('R43',nx+3.81,205.74,270,fld=(0,-3.2,0,4.2,'center'))
    S.wire('R43.1',(nx+10.16,205.74)); S.power_at('3V3_MCU',nx+10.16,205.74,'u')
    S.at('J11',nx+5.08,210.82); S.wire((nx,205.74),(nx,210.82)); S.tap('J11.2','GND','l',2.54,'d')
    S.text('NTC on the SSR heat sink (off-board)',nx-5.08,199.39)
    # ---------- SSR drive ----------
    S.text('SSR drive: 2N7002 on the 5 V rail (default); solder jumpers select direct 3.3 V GPIO drive',177.8+D,40.64,1.5,True)
    cx=180.34+D
    sx,sy=P('U12',24)
    S.wire((sx,sy),(cx,sy),(cx,48.26))
    S.at('SJ4',200.66+D,48.26,0,mirror=True)
    S.wire((cx,48.26),'SJ4.3')
    S.tap('SJ4.1','5V_RAIL','r',2.54,'u')
    S.at('J12',254+D,54.61)
    S.wire('SJ4.2',(200.66+D,54.61),'J12.1')
    S.at('SJ5',203.2+D,64.77)
    S.at('Q7',195.58+D,76.2)
    S.wire('SJ5.1','Q7.3')
    S.tap('SJ5.3','GND','r',2.54,'d')
    S.wire('SJ5.2',(203.2+D,73.66),(243.84+D,73.66),(243.84+D,P('J12',2)[1]),'J12.2')
    S.tap('Q7.2','GND')
    S.at('R44',cx+3.81,76.2,90); S.wire((cx,48.26),(cx,76.2)) if False else None
    S.wire((cx,76.2),'R44.1')
    S.wire('R44.2','Q7.1')
    S.at('R45',190.5+D,80.01); S.wire((190.5+D,76.2),'R45.1'); S.tap('R45.2','GND')
