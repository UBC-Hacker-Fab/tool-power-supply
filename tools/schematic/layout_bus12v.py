from lay import *

def branch(S,X,Y,tag,F,XH,Q,Rpu,Qn,Ren,R9,R10,J,bxE,bxS,esc=False):
    P=S.P
    S.text(f'{tag}: fuse, P-FET switch, presence sense',X,Y-7.62,1.5,True)
    S.at(F,X+30.48,Y,90)
    S.tap(f'{F}.1','12V_BUS','l',10.16)
    S.at(XH,X+19.05,Y+12.7)
    S.wire(f'{XH}.2',(X+19.05,Y)); S.wire(f'{XH}.3',(X+39.37,Y))
    S.at(Q,X+55.88,Y+7.62,180)
    S.wire(f'{F}.2',(X+53.34,Y),f'{Q}.1')              # FUSED row to the source pins
    xs=X+88.9
    S.wire((X+53.34,Y),(xs,Y))
    S.at(Rpu,xs,Y+3.81); S.wire((xs,Y),f'{Rpu}.1')
    S.wire(f'{Q}.4',f'{Rpu}.2')                        # gate node
    S.at(Qn,xs-2.54,Y+25.4)                            # D top at (xs, Y+20.32)
    S.wire(f'{Rpu}.2',f'{Qn}.3')
    S.tap(f'{Qn}.2','GND')
    S.at(Ren,xs-15.24,Y+21.59,180)                     # bottom pin at E=(xs-15.24, Y+25.4)
    S.tap(f'{Ren}.2','3V3_BUCK','u')
    S.wire(f'{Qn}.1',f'{Ren}.1')                       # EN node
    # output side
    S.at(J,X+43.18,Y+12.7,0,mirror=True)
    S.wire(f'{Q}.5',f'{J}.1')
    S.tap(f'{J}.2','GND')
    S.at(R9,X+53.34,Y+16.51); S.wire(f'{Q}.5',f'{R9}.1')
    S.at(R10,X+53.34,Y+24.13); S.wire(f'{R9}.2',f'{R10}.1'); S.tap(f'{R10}.2','GND')
    # EN -> bus
    ex=P(Ren,1)
    S.wire(ex,(ex[0],Y+38.1),(bxE-2.54,Y+38.1))
    S.entry(bxE-2.54,Y+38.1,2.54,2.54)
    S.label(f'EN.{tag}',bxE-12.7,Y+38.1,0)
    # SENSE -> bus
    sx,sy=P(R9,2)
    S.wire((sx,sy),(sx+5.08,sy),(sx+5.08,Y+43.18),(bxS-2.54,Y+43.18))
    S.entry(bxS-2.54,Y+43.18,2.54,2.54)
    S.label(f'SENSE.{tag}',bxS-12.7,Y+43.18,0)

def bus12v(S):
    P=S.P
    # ---------------- 12 V rail monitor ----------------
    S.text('12 V rail monitor (INA226 #1, address 0x40)',20.32,25.4,1.5,True)
    S.at('R5',50.8,50.8,90)
    S.hl('R5.1','12V_MOD','input','l',10.16)
    S.tap('R5.2','12V_BUS','u')
    S.text('5 mohm shunt: Kelvin-connect INA pins at the pads',50.8,45.72)
    S.at('U3',88.9,83.82)
    S.wire('U3.10',(46.99,P('U3',10)[1]),'R5.1')
    vb=P('U3',8); vm=P('U3',9)
    S.wire('U3.8',(vb[0]-2.54,vb[1]),(vb[0]-2.54,vm[1]),'U3.9')     # Vbus and Vin- bracket (12V_BUS); Vin+ wire crosses it
    S.power_at('12V_BUS',vb[0]-2.54,vb[1],'u')
    a0=P('U3',2); a1=P('U3',1)
    S.wire('U3.2',(101.6,a0[1]),(101.6,a1[1]),'U3.1')
    S.power_at('GND',101.6,a0[1],'r')
    S.tap('U3.6','3V3_MCU','u'); S.tap('U3.7','GND')
    decap(S,'C3',68.58,63.5,'3V3_MCU')
    # I2C bus
    bx=124.46
    for pin,mem in (('U3.4','I2C.SDA'),('U3.5','I2C.SCL'),('U3.3','I2C.ALERT')):
        x,y=P(pin.split('.')[0],pin.split('.')[1])
        S.wire((x,y),(bx-2.54,y)); S.entry(bx-2.54,y,2.54,2.54)
    S.label('I2C.SDA',109.22,P('U3',4)[1],0); S.label('I2C.SCL',109.22,P('U3',5)[1],0); S.label('I2C.ALERT',109.22,P('U3',3)[1],0)
    S.bus((bx,P('U3',4)[1]+2.54),(bx,P('U3',3)[1]+7.62))
    S.hlabel('I2C{SDA SCL ALERT}','bidirectional',bx,P('U3',3)[1]+7.62,270)
    # ---------------- bus protection ----------------
    S.text('Bus protection, bulk capacitance, rail LED',20.32,121.92,1.5,True)
    S.at('D3',38.1,142.24,270); S.tap('D3.1','12V_BUS'); S.tap('D3.2','GND')
    S.at('C4',63.5,142.24); S.tap('C4.1','12V_BUS'); S.tap('C4.2','GND')
    S.wire('C4.1',(71.12,P('C4',1)[1])); S.at('#FLG01',71.12,P('C4',1)[1])
    S.at('R6',88.9,139.7); S.tap('R6.1','12V_BUS')
    S.at('D4',88.9,147.32,90); S.wire('R6.2','D4.2'); S.tap('D4.1','GND')
    S.text('TVS SMCJ15A',27.94,134.62); S.text('100 uF',58.42,134.62); S.text('LED',96.52,143.51)
    # ---------------- fan ----------------
    S.text('Cooling fan header (4-pin PWM) with its own PTC',20.32,190.5,1.5,True)
    S.at('F6',111.76,205.74,270); S.tap('F6.1','12V_BUS','r')
    S.at('J6',91.44,205.74,0,mirror=True)
    S.wire('F6.2','J6.2'); S.tap('J6.1','GND','r',2.54,'u')
    S.wire('J6.3',(101.6,P('J6',3)[1]))
    S.at('R19',105.41,P('J6',3)[1],90); S.tap('R19.2','3V3_MCU','r')
    # bus FAN{PWM TACH}
    yb=218.44
    S.wire((101.6,P('J6',3)[1]),(101.6,215.9)); S.entry(101.6,215.9,2.54,2.54)
    S.wire('J6.4',(99.06,P('J6',4)[1]),(99.06,215.9)); S.entry(99.06,215.9,2.54,2.54)
    S.label('FAN.TACH',101.6,212.09,0); S.label('FAN.PWM',99.06,213.36,180)
    S.bus((101.6,yb),(111.76,yb)); S.hlabel('FAN{PWM TACH}','bidirectional',111.76,yb,0)
    # ---------------- three branches ----------------
    X=139.7
    bxE=X+114.3; bxS=X+121.92
    branch(S,X,38.1,'12V_A','F3','XH1','Q1','R7','Q2','R8','R9','R10','J3',bxE,bxS)
    branch(S,X,93.98,'12V_B','F4','XH2','Q3','R11','Q4','R12','R13','R14','J4',bxE,bxS)
    branch(S,X,149.86,'ESC','F5','XH3','Q5','R15','Q6','R16','R17','R18','J5',bxE,bxS)
    ye=149.86
    S.bus((bxE,38.1+40.64),(bxE,ye+48.26)); S.hlabel('EN{12V_A 12V_B ESC 5V_A 5V_B 3V3_A 3V3_B}','bidirectional',bxE,ye+48.26,270)
    S.bus((bxS,38.1+45.72),(bxS,ye+48.26)); S.hlabel('SENSE{12V_A 12V_B ESC 5V_A 5V_B 3V3_A 3V3_B}','bidirectional',bxS,ye+48.26,270)
