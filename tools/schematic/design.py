import sys,os,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from engine import *

FP_R='Resistor_SMD:R_0603_1608Metric'
FP_C='Capacitor_SMD:C_0603_1608Metric'
LCSC={'10k':'C25804','4.7k':'C23162','33k':'C4216','1.5k':'C22843','680':'C23228','1k':'C21190'}
def R(v,a,b,fp=FP_R,**kw):
    p={'LCSC':LCSC.get(v,''),'Manufacturer':'Uni-Royal','MPN':{'10k':'0603WAF1002T5E','4.7k':'0603WAF4701T5E','33k':'0603WAF3302T5E','1.5k':'0603WAF1501T5E','680':'0603WAF6800T5E','1k':'0603WAF1001T5E'}.get(v,'')}
    p.update(kw.pop('props',{}))
    return Comp('Device:R',v+(' (1%)'),{'1':a,'2':b},fp,prefix='R',props=p,**kw)
def C100(a,b): return Comp('Device:C','100nF 50V X7R',{'1':a,'2':b},FP_C,prefix='C',props={'LCSC':'C14663','MPN':'CC0603KRX7R9BB104','Manufacturer':'Yageo'})
def LED(a_net,k_net,color='yellow',lcsc='C89811',mpn='NCD0603Y2'):
    return Comp('Device:LED',f'LED {color}',{'1':k_net,'2':a_net},'LED_SMD:LED_0603_1608Metric',prefix='D',props={'LCSC':lcsc,'MPN':mpn})
def term(a,b,val='Screw terminal 5.08mm',lcsc='C2915639'):
    return Comp('Connector:Screw_Terminal_01x02','DB128V-5.08-2P-GN-S',{'1':a,'2':b},'TerminalBlock_CUI:TerminalBlock_CUI_TB007-508-02_1x02_P5.08mm_Horizontal',prefix='J',props={'LCSC':lcsc,'MPN':'DB128V-5.08-2P-GN-S','Manufacturer':'DORABO'})
def virtual_fuse(a,b,val,pn):
    return Comp('Device:Fuse',val,{'1':a,'2':b},'',prefix='F',on_board=False,props={'MPN':pn,'_bom':'yes','Note':'Consumable in clips/holder; not a PCB footprint'})
def ina226(a1,a0,sda,scl,vs,alert,vbus,vinm,vinp):
    return Comp('Sensor_Energy:INA226','INA226AIDGSR',{'1':a1,'2':a0,'3':alert,'4':sda,'5':scl,'6':vs,'7':'GND','8':vbus,'9':vinm,'10':vinp},'Package_SO:MSOP-10_3x3mm_P0.5mm',prefix='U',props={'LCSC':'C49851','MPN':'INA226AIDGSR','Manufacturer':'TI'})
def flag(net): return Comp('power:PWR_FLAG','PWR_FLAG',{'1':net},'',prefix='#FLG',on_board=False)

def _project_root_uuid():
    # KiCad keeps the root sheet uuid in the .kicad_pro; the schematic header must match it
    # or KiCad reports 'An error was found when loading the schematic that has been automatically fixed'.
    import json
    pro=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tool-power-supply-v1','tool-power-supply-v1.kicad_pro')
    try:
        return json.load(open(pro))['sheets'][0][0]
    except Exception:
        return U()
root_uuid=_project_root_uuid()
sheets={}
def _project_sheet_uuids():
    import json
    pro=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','tool-power-supply-v1','tool-power-supply-v1.kicad_pro')
    try: return {n:u for u,n in json.load(open(pro))['sheets']}
    except Exception: return {}
_SU=_project_sheet_uuids()
def mk(name,title):
    s=Sheet(name,title,root_uuid,_SU.get(name) or U()); sheets[name]=s; return s

# ---------------- MAINS ----------------
m=mk('mains','Mains zone: AC in/out, fuses, module, current sense')
m.section('AC input and AC output (barrier strips)',[
  Comp('HF_Connectors:HB9500-9.5-3P','AC IN (L, N, PE)',{'1':'L_IN','2':'N_IN','3':'PE'},'TerminalBlock_Ningbo-Kagnex:TerminalBlock_Ningbo-Kagnex_HB9500M_1x03_P9.5mm',prefix='J',props={'LCSC':'C162697','MPN':'HB9500M-9.5-03P-13-00A','Manufacturer':'Kangnex','Note':'HF symbol is the HB9500; stock HB9500M footprint used'}),
  Comp('HF_Connectors:HB9500-9.5-3P','AC OUT (L, N, PE)',{'1':'L_OUT','2':'N_IN','3':'PE'},'TerminalBlock_Ningbo-Kagnex:TerminalBlock_Ningbo-Kagnex_HB9500M_1x03_P9.5mm',prefix='J',props={'LCSC':'C162697','MPN':'HB9500M-9.5-03P-13-00A','Manufacturer':'Kangnex'}),
])
FUSE_3AG='HF_Passives:Fuse_3AG_6.3x32mm'   # every 6.3 x 32 mm cartridge fuse carries this symbol + the two-clip footprint
def fuse_3ag(a,b,val,pn):
    return Comp(FUSE_3AG,val,{'1':a,'2':b},'HF_Footprints:Fuse_3AG_6.3x32mm_Clips_Littelfuse_102_122_P34.21mm',prefix='F',
                props={'MPN':pn,'Clip MPN':'01020074Z x2 (Digikey F4187-ND)','Note':'Fuse is a consumable pulled from the clips; the footprint is the two clip positions'})
m.section('Fuses: 3AG cartridge in PC-pin clips (module branch 3 A, furnace branch 10 A)',[
  fuse_3ag('L_IN','L_MOD','3A Slo-Blo 3AG','0313003.HXP (Digikey F2545-ND; 4A 0313004.HXP swap-in)'),
  fuse_3ag('L_IN','L_FURN','10A ceramic fast-blow 3AG 250VAC','0314010.HXP (Digikey F3222-ND)'),
])
m.section('Surge protection and mains-present indicator',[
  Comp('Device:Varistor','14D241K MOV',{'1':'L_MOD','2':'N_IN'},'Varistor:RV_Disc_D16.5mm_W6.7mm_P7.5mm',prefix='RV',props={'LCSC':'C49072887','MPN':'14D241K','Note':'Verify disc size against datasheet'}),
  R('33k','L_IN','MLED1',props={'Note':'Mains LED dropper 4 x 33k in series'}),R('33k','MLED1','MLED2'),R('33k','MLED2','MLED3'),R('33k','MLED3','MLED_A'),
  LED('MLED_A','N_IN',color='red',lcsc='C2286',mpn='KT-0603R'),
  Comp('Diode:1N4148W','1N4148W (LED antiparallel)',{'1':'MLED_A','2':'N_IN'},None,prefix='D',props={'LCSC':'C81598','MPN':'1N4148W'}),
])
m.section('AC/DC module and furnace current sensor',[
  Comp('HF_Misc:IRM-90-12','IRM-90-12',{'AC_L':'L_MOD','AC_N':'N_IN','+VO':'12V_MOD','-VO':'GND'},None,prefix='U',props={'LCSC':'C6577385','MPN':'IRM-90-12','Manufacturer':'Mean Well'}),
  Comp('Sensor_Current:ACS712xLCTR-20A','ACS712ELCTR-20A-T',{'1':'L_FURN','2':'L_FURN','3':'L_OUT','4':'L_OUT','5':'GND','6':'ACS_FILT','7':'ACS_OUT','8':'5V_RAIL'},None,prefix='U',props={'LCSC':'C10681','MPN':'ACS712ELCTR-20A-T','Manufacturer':'Allegro','Note':'Pins 1-4 are on the mains side, 5-8 on the DC side (4 mm creepage across the package)'}),
  C100('ACS_FILT','GND'),C100('5V_RAIL','GND'),
])
m.section('Chassis and star-ground solder jumpers (default open)',[
  Comp('Mechanical:MountingHole_Pad','M3 hole',{'1':'CHASSIS'},'MountingHole:MountingHole_3.2mm_M3_Pad',prefix='H') for _ in range(4)
]+[
  Comp('Jumper:SolderJumper_2_Open','PE tie (PE-GND)',{'1':'PE','2':'GND'},'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm',prefix='SJ'),
  Comp('Jumper:SolderJumper_2_Open','CHASSIS-PE',{'1':'CHASSIS','2':'PE'},'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm',prefix='SJ'),
  Comp('Jumper:SolderJumper_2_Open','CHASSIS-GND',{'1':'CHASSIS','2':'GND'},'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm',prefix='SJ'),
])

# ---------------- 12 V BUS ----------------
b=mk('bus12v','12 V bus, branch switches, fan')
b.section('12 V rail monitor (INA226 #1, address 0x40)',[
  Comp('Device:R','5mR 2512 (shunt)',{'1':'12V_MOD','2':'12V_BUS'},'Resistor_SMD:R_2512_6332Metric',prefix='R',props={'LCSC':'C393074','MPN':'RLP25FEGMR005','Manufacturer':'TA-I'}),
  ina226('GND','GND','I2C_SDA','I2C_SCL','3V3_MCU','INA_ALERT','12V_BUS','12V_BUS','12V_MOD'),
  C100('3V3_MCU','GND'),
])
b.section('Bus protection, bulk capacitance and rail LED',[
  Comp('Device:D_Zener','SMCJ15A TVS',{'1':'12V_BUS','2':'GND'},'Diode_SMD:D_SMC',prefix='D',props={'LCSC':'C42371550','MPN':'SMCJ15A','Note':'Unidirectional TVS drawn as a zener-style symbol'}),
  Comp('Device:C_Polarized','100uF 35V',{'1':'12V_BUS','2':'GND'},'Capacitor_SMD:CP_Elec_6.3x7.7',prefix='C',props={'LCSC':'C2836437','MPN':'RVE100UF35V67RV0072'}),
  R('4.7k','12V_BUS','LED12_A'),LED('LED12_A','GND'),
  flag('12V_BUS'),
])
def branch(tag,rating,fuse_pn,out_part):
    f=f'{tag}_FUSED';g=f'{tag}_GATE';o=f'{tag}_OUT';en=f'EN_{tag}';sn=f'SENSE_{tag}'
    comps=[
     virtual_fuse('12V_BUS',f,f'{rating} ATO blade fuse',fuse_pn),
     Comp('HF_Passives:3557-20','Keystone 3557 blade holder '+tag,{'1':'12V_BUS','2':'12V_BUS','3':f,'4':f},'HF_Footprints:355720',prefix='XH',props={'MPN':'3557-20 (3557-2)','Manufacturer':'Keystone','Note':'pads 1+2 one terminal, 3+4 the other'}),
     Comp('Transistor_FET:FDS9435A','AO4407C P-FET',{'1':f,'2':f,'3':f,'4':g,'5':o,'6':o,'7':o,'8':o},'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',prefix='Q',props={'LCSC':'C469397','MPN':'AO4407C','Manufacturer':'AOS','Note':'Stock SO-8 P-FET symbol used for the AO4407C; same S-S-S-G-D-D-D-D pin order'}),
     R('10k',f,g,props={'Note':'P-FET gate pull-up to source (keeps switch off)'}),
     Comp('Transistor_FET:2N7002','2N7002',{'1':en,'2':'GND','3':g},None,prefix='Q',props={'LCSC':'C8545','MPN':'2N7002'}),
     R('10k',en,'3V3_BUCK',props={'Note':'Default ON: pulled up to the 3.3 V buck rail; Pico pulls low to switch off'}),
     R('33k',o,sn),R('10k',sn,'GND'),
    ]
    comps.append(out_part(o))
    return comps
def tap_term(o): return term(o,'GND')
def esc_conn(o): return Comp('Connector_Generic:Conn_01x02','XT60PW-F (ESC power)',{'1':o,'2':'GND'},'Connector_AMASS:AMASS_XT60PW-F_1x02_P7.20mm_Horizontal',prefix='J',props={'LCSC':'C428722','MPN':'XT60PW-F','Manufacturer':'AMASS'})
b.section('12 V tap A (3 A blade fuse, P-FET switch, presence sense)',branch('12V_A','3A','0ATO003.V (Digikey F5040-ND)',tap_term))
b.section('12 V tap B (3 A blade fuse, P-FET switch, presence sense)',branch('12V_B','3A','0ATO003.V (Digikey F5040-ND)',tap_term))
b.section('ESC branch (7.5 A blade fuse, P-FET switch, presence sense)',branch('ESC','7.5A','0ATO07.5V (Digikey F11167-ND)',esc_conn))
b.section('Cooling fan header (4-pin PWM) with its own PTC',[
  Comp('Device:Polyfuse','PTC 500mA hold 33V',{'1':'12V_BUS','2':'FAN_12V'},'Fuse:Fuse_1206_3216Metric',prefix='F',props={'LCSC':'C70077','MPN':'nSMD050-33V','Manufacturer':'TECHFUSE'}),
  Comp('Connector_Generic:Conn_01x04','Fan (1 GND, 2 +12V, 3 TACH, 4 PWM)',{'1':'GND','2':'FAN_12V','3':'FAN_TACH','4':'FAN_PWM'},'Connector_Molex:Molex_KK-254_AE-6410-04A_1x04_P2.54mm_Vertical',prefix='J',props={'MPN':'47053-1000','Manufacturer':'Molex','Mouser':'538-47053-1000'}),
  R('10k','FAN_TACH','3V3_MCU'),
])

# ---------------- RAILS ----------------
r=mk('rails','5 V and 3.3 V rails, taps, monitors')
def buck(name,u,fbnet,swnet,bstnet,outnet,ind_val):
    return [
     Comp('Regulator_Switching:'+u,u+'-7',{'1':outnet,'2':'12V_BUS','3':'12V_BUS','4':'GND','5':swnet,'6':bstnet},None,prefix='U',props={'LCSC':{'AP63205WU':'C2071056','AP63203WU':'C780769'}[u],'MPN':u+'-7','Manufacturer':'Diodes Inc'}),
     Comp('Device:C','10uF 50V',{'1':'12V_BUS','2':'GND'},'Capacitor_SMD:C_1206_3216Metric',prefix='C',props={'LCSC':'C13585','MPN':'CL31A106KBHNNNE','Manufacturer':'Samsung'}),
     Comp('Device:L',ind_val,{'1':swnet,'2':outnet},'Inductor_SMD:L_Sumida_CDMC6D28_7.25x6.5mm',prefix='L',props={'LCSC':'C207840','MPN':'SLO0630H4R7MTT','Manufacturer':'Sunltech','Note':'Footprint is the closest stock land pattern; verify against the SLO0630H datasheet'}),
     Comp('Device:C','100nF 50V',{'1':bstnet,'2':swnet},FP_C,prefix='C',props={'LCSC':'C14663'}),
     Comp('Device:C','22uF 25V',{'1':outnet,'2':'GND'},'Capacitor_SMD:C_0805_2012Metric',prefix='C',props={'LCSC':'C45783','MPN':'CL21A226MAQNNNE','Manufacturer':'Samsung'}),
     Comp('Device:C','22uF 25V',{'1':outnet,'2':'GND'},'Capacitor_SMD:C_0805_2012Metric',prefix='C',props={'LCSC':'C45783','MPN':'CL21A226MAQNNNE','Manufacturer':'Samsung'}),
    ]
def tps(tag,rail,fault,out):
    return Comp('HF_ICs:TPS2553DBVR','TPS2553DBVR',{'1':rail,'2':'GND','3':f'EN_{tag}','4':fault,'5':f'ILIM_{tag}','6':out},None,prefix='U',props={'LCSC':'C55266','MPN':'TPS2553DBVR','Manufacturer':'TI'})
def tap(tag,rail,fault,out,sense_div):
    comps=[tps(tag,rail,fault,out),
      R('33k',f'ILIM_{tag}','GND',props={'Note':'ILIM 33k: about 0.72-0.86 A limit'}),
      C100(rail,'GND'),
      R('10k',f'EN_{tag}','3V3_BUCK',props={'Note':'Default ON: pulled up to the 3.3 V buck rail; Pico pulls low to switch off'}),
      term(out,'GND')]
    comps+=sense_div
    return comps
r.section('5 V buck (AP63205, 2 A)',buck('5V','AP63205WU','5V_BUCK','SW_5V','BST_5V','5V_BUCK','4.7uH'))
r.section('5 V monitor (INA226 #2, 0x41) and rail LED',[
  Comp('Device:R','33mR 1206 (shunt)',{'1':'5V_BUCK','2':'5V_RAIL'},'Resistor_SMD:R_1206_3216Metric',prefix='R',props={'LCSC':'C912764','MPN':'RLS12FTCR033','Manufacturer':'TA-I'}),
  ina226('GND','3V3_MCU','I2C_SDA','I2C_SCL','3V3_MCU','INA_ALERT','5V_RAIL','5V_RAIL','5V_BUCK'),
  C100('3V3_MCU','GND'),
  R('1.5k','5V_RAIL','LED5_A'),LED('LED5_A','GND'),flag('5V_RAIL'),
])
r.section('5 V taps A and B (TPS2553, enable control, presence sense)',
  tap('5V_A','5V_RAIL','FAULT_5V','5V_A_OUT',[R('4.7k','5V_A_OUT','SENSE_5V_A'),R('10k','SENSE_5V_A','GND')])+
  tap('5V_B','5V_RAIL','FAULT_5V','5V_B_OUT',[R('4.7k','5V_B_OUT','SENSE_5V_B'),R('10k','SENSE_5V_B','GND')]))
r.section('3.3 V buck (AP63203, 2 A)',buck('3V3','AP63203WU','3V3_BUCK','SW_3V3','BST_3V3','3V3_BUCK','4.7uH'))
r.section('3.3 V monitor (INA226 #3, 0x42) and rail LED',[
  Comp('Device:R','33mR 1206 (shunt)',{'1':'3V3_BUCK','2':'3V3_RAIL'},'Resistor_SMD:R_1206_3216Metric',prefix='R',props={'LCSC':'C912764','MPN':'RLS12FTCR033','Manufacturer':'TA-I'}),
  ina226('GND','I2C_SDA','I2C_SDA','I2C_SCL','3V3_MCU','INA_ALERT','3V3_RAIL','3V3_RAIL','3V3_BUCK'),
  C100('3V3_MCU','GND'),
  R('680','3V3_RAIL','LED3_A'),LED('LED3_A','GND'),flag('3V3_BUCK'),flag('3V3_RAIL'),
])
r.section('3.3 V taps A and B (TPS2553, enable control; tap net is the sense input)',
  tap('3V3_A','3V3_RAIL','FAULT_3V3','3V3_A_OUT',[R('10k','3V3_A_OUT','GND',props={'Note':'Sense pulldown: tap net goes straight to a Pico GPIO'})])+
  tap('3V3_B','3V3_RAIL','FAULT_3V3','3V3_B_OUT',[R('10k','3V3_B_OUT','GND',props={'Note':'Sense pulldown: tap net goes straight to a Pico GPIO'})]))

# ---------------- MCU ----------------
u=mk('mcu','Raspberry Pi Pico 2, analog inputs, SSR drive')
pico={'1':'SENSE_5V_A','2':'SENSE_5V_B','3':'GND','4':'3V3_A_OUT','5':'3V3_B_OUT','6':'I2C_SDA','7':'I2C_SCL','8':'GND','9':'EN_5V_A','10':'EN_5V_B','11':'EN_3V3_A','12':'EN_3V3_B','13':'GND','14':'FAULT_5V','15':'FAULT_3V3','16':'EN_12V_A','17':'EN_12V_B','18':'GND','19':'EN_ESC','20':'SENSE_12V_A',
 '21':'FAN_PWM','22':'NC','23':'GND','24':'SSR_CTRL','25':'FAN_TACH','26':'INA_ALERT','27':'SENSE_12V_B','28':'GND','29':'SENSE_ESC','30':'NC','31':'ADC_ACS','32':'ADC_NTC_MOD','33':'GND','34':'ADC_NTC_SSR','35':'NC','36':'3V3_MCU','37':'NC','38':'GND','39':'VSYS','40':'NC'}
u.section('Pico 2 (plugged into 2 x 1x20 sockets; pin map in design-context/pin-map.md)',[
  Comp('MCU_Module:RaspberryPi_Pico','Raspberry Pi Pico 2',pico,'Module:RaspberryPi_Pico_Common_THT',prefix='U',props={'LCSC':'C41407547','MPN':'SC1631 (Pico 2)','Note':'Hand-plugged. Sockets: 2 x LXWCONN 254PM-1x20P-V (C53202183). GP17 spare'}),
  Comp('Diode:SS14','SS14 (5V to VSYS)',{'1':'VSYS','2':'5V_RAIL'},None,prefix='D',props={'LCSC':'C2480','MPN':'SS14'}),
  flag('VSYS'),
])
u.section('I2C pull-ups and analog inputs',[
  R('4.7k','I2C_SDA','3V3_MCU'),R('4.7k','I2C_SCL','3V3_MCU'),
  R('4.7k','ACS_OUT','ADC_ACS',props={'Note':'ACS712 divider top (ratio 0.68)'}),R('10k','ADC_ACS','GND'),
  R('10k','3V3_MCU','ADC_NTC_MOD'),
  Comp('Device:Thermistor_NTC','NTC 10k (module)',{'1':'ADC_NTC_MOD','2':'GND'},FP_R,prefix='TH',props={'LCSC':'C13564','MPN':'NCP18XH103F03RB','Manufacturer':'Murata'}),
  R('10k','3V3_MCU','ADC_NTC_SSR'),
  term('ADC_NTC_SSR','GND'),
])
u.section('SSR drive: 2N7002 on the 5 V rail (default) or direct GPIO via solder jumpers',[
  term('SSR_POS','SSR_NEG'),
  Comp('Jumper:SolderJumper_3_Bridged12','SJ SSR+ (1-2 = 5V, 2-3 = GPIO)',{'1':'5V_RAIL','2':'SSR_POS','3':'SSR_CTRL'},'Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm',prefix='SJ'),
  Comp('Jumper:SolderJumper_3_Bridged12','SJ SSR- (1-2 = MOSFET, 2-3 = GND)',{'1':'SSR_DRAIN','2':'SSR_NEG','3':'GND'},'Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm',prefix='SJ'),
  Comp('Transistor_FET:2N7002','2N7002 (SSR drive)',{'1':'SSR_GATE','2':'GND','3':'SSR_DRAIN'},None,prefix='Q',props={'LCSC':'C8545','MPN':'2N7002'}),
  R('1k','SSR_CTRL','SSR_GATE'),R('4.7k','SSR_GATE','GND',props={'Note':'Keeps the SSR off while the Pico boots'}),
])

ORDER=['mains','bus12v','rails','mcu']
