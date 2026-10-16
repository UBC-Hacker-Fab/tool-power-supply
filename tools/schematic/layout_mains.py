def mains(S):
    P=S.P
    # ---------------- AC input ----------------
    S.text('AC input / output (mains zone)',25.4,22.86,2.54,True)
    S.at('J1',50.8,58.42,0,mirror=True)                 # pins on the right: 1 L, 2 N, 3 PE
    xL=76.2; yF=58.42; yM=104.14; yN=172.72; yPE=185.42
    S.wire('J1.1',(xL,yF))                             # L_IN node
    S.wire('J1.2',(63.5,P('J1',2)[1]),(63.5,yN))       # N rail down
    S.wire((63.5,yN),(312.42,yN))                      # N rail across
    S.wire('J1.3',(58.42,P('J1',3)[1]),(58.42,yPE))    # PE rail down
    S.wire((58.42,yPE),(317.5,yPE))                   # PE rail across
    S.text('N',66.04,yN-1.27); S.text('PE',60.96,yPE-1.27); S.text('L',55.88,yF-1.27)
    # ---------------- furnace branch (10 A) ----------------
    S.text('Furnace branch: 10 A fast-blow 3AG, then current sensor',88.9,45.72,1.5,True)
    S.at('F2',127,yF,90)
    S.wire((xL,yF),'F2.1')
    S.wire('F2.2',(165.1,yF))
    S.text('F2: 3AG in 2 clips',112.0,yF-6.0)
    S.wire((165.1,yF),'U2.1') if False else None
    S.at('U2',254,63.5,fld=(-12.7,-10.5,-12.7,-8,'left'))
    S.wire((165.1,yF),'U2.1')                          # L_FURN to IP+
    pl=P('U2',3)
    S.wire('U2.3',(236.22,pl[1]),(236.22,83.82),(P('J2',1) if False else (320.04,83.82)))
    S.at('J2',320.04,83.82)
    S.wire('J2.1',(236.22,83.82))
    S.wire('J2.2',(312.42,P('J2',2)[1]),(312.42,yN))
    S.wire('J2.3',(317.5,P('J2',3)[1]),(317.5,yPE))
    S.text('L_OUT',280,82.55)
    S.tap('U2.5','GND'); S.tap('U2.8','5V_RAIL')
    S.hl('U2.7','ACS_OUT','output','r',10.16)
    S.at('C1',269.24,P('U2',6)[1]+3.81); S.wire('U2.6','C1.1'); S.tap('C1.2','GND')
    S.at('C2',284.48,49.53); S.tap('C2.1','5V_RAIL'); S.tap('C2.2','GND')
    S.text('FILTER 100 nF (about 940 Hz)',266.7,77.47)
    # ---------------- module branch (3 A) ----------------
    S.text('Module branch: 3 A time-lag 3AG, surge protection, IRM-90-12',88.9,91.44,1.5,True)
    S.wire((xL,yF),(xL,yM))
    S.at('F1',127,yM,90)
    S.wire((xL,yM),'F1.1')
    S.text('F1: 3AG in 2 clips',112.0,yM-6.0)
    S.at('U1',203.2,106.68,fld=(-12.7,-9.5,-12.7,-7,'left'))
    S.wire('F1.2','U1.AC_L')
    S.wire('U1.AC_N',(180.34,P('U1','AC_N')[1]),(180.34,yN))
    S.tap('U1.-VO','GND')
    S.hl('U1.+VO','12V_MOD','output','r',10.16)
    S.at('RV1',170.18,139.7); S.wire('RV1.1',(170.18,yM)); S.wire('RV1.2',(170.18,yN))
    S.text('MOV',160.02,139.7)
    # ---------------- mains-present LED ----------------
    S.text('Mains-present LED (4 x 33k dropper)',88.9,150.0,1.27,False) if False else None
    S.at('R1',xL,118.11); S.at('R2',xL,128.27); S.at('R3',xL,138.43); S.at('R4',xL,148.59)
    S.wire((xL,yM),'R1.1')
    S.wire('R1.2','R2.1'); S.wire('R2.2','R3.1'); S.wire('R3.2','R4.1')
    S.at('D1',xL,160.02,90)
    S.wire('R4.2','D1.2')
    S.at('D2',88.9,160.02,270)
    S.wire('D2.1',(xL,P('D2',1)[1]))                   # cathode of D2 joins MLED_A at D1 anode
    S.wire('D1.1',(xL,yN)); S.wire('D2.2',(88.9,yN))
    S.text('Mains-present LED',78.74,112.0)
    # ---------------- chassis and star ground ----------------
    S.text('Chassis and star-ground solder jumpers (default open)',63.5,198.12,1.5,True)
    for i,h in enumerate(['H1','H2','H3','H4']):
        x=63.5+12.7*i; S.at(h,x,203.2); S.wire(f'{h}.1',(x,210.82))
    S.wire((63.5,210.82),(134.62,210.82))
    S.at('SJ2',139.7,210.82); S.wire('SJ2.1',(134.62,210.82)); S.wire('SJ2.2',(144.78,210.82),(144.78,yPE))
    S.at('SJ3',139.7,223.52); S.wire((134.62,210.82),(134.62,223.52),'SJ3.1'); S.tap('SJ3.2','GND')
    S.at('SJ1',170.18,236.22); S.wire((165.1,yPE),(165.1,236.22),'SJ1.1'); S.tap('SJ1.2','GND')
    S.text('CHASSIS',66.04,209.55); S.text('PE tie',172.72,233.68)
