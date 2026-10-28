# Symbols and footprints: what to download (2026-10-14)

Checked against `~/Documents/Github/hackerfab-kicadlibs` (the HF_* libraries) and the stock KiCad 10 libraries installed at `/Applications/KiCad/KiCad.app/Contents/SharedSupport`. The HF library today contains only: IRM-90-12 (symbol `HF_Misc:IRM-90-12`, footprint `HF_Footprints:CONV_IRM-90-12`) and unrelated ICs (ADS7042, ADS7052, INA351, STM32G071, TLV9061). `HF_Passives`, `HF_Connectors` and `HF_Discrete` are empty, so generic parts come from stock KiCad libraries.

## 1. Download these (not in the HF library, not in stock KiCad)
| Part | Where | CSE part ID | Notes |
|---|---|---|---|
| TI TPS2553DBVR (SOT-23-6) | CSE | **281440** | Symbol, footprint and 3D, model quality 3, 6 pins. Stock KiCad has only the TPS2051/TPS2065 family, which has a different pinout |
| Keystone 3557-2 blade fuse holder (x3) | CSE | **237823** (alt 3557-20: 362661, quality 4, same pads) | 4 pads, 13.47 mm x 3.4 mm, 1.6 mm drill. Tie pads 1+2 and 3+4 on the 3557-20 footprint now in the HF library (1+3 and 2+4 on the 3557-2 footprint) |
| Littelfuse 01020074Z fuse clip (x4) | not on CSE | | Stock has `Fuse:Fuseholder_Clip-6.3x32mm_Littelfuse_102071_Inline_P34.70x7.60mm_D2.00mm_Horizontal`; confirm it matches the 01020074Z datasheet before using it, otherwise download or draw it |

## 1b. Stock KiCad footprints that fit (checked 2026-10-14, no download)
| Part | Footprint | Evidence |
|---|---|---|
| Kangnex HB9500M-9.5-03P barrier strip (C162697) | `TerminalBlock_Ningbo-Kagnex:TerminalBlock_Ningbo-Kagnex_HB9500M_1x03_P9.5mm` | KiCad has a footprint for exactly this series (HB9500M, 3 pins, 9.5 mm pitch, 2.0 mm drill, 3.3 x 6.6 mm pads, 30 x 16 mm). The datasheet shows 9.5 mm pitch, 1.5 x 0.7 mm pins and 16 mm depth. Re-check the pad positions against the datasheet since this is a mains part |
| Sunltech SLO0630H4R7MTT inductor (C207840), 7.1 x 6.6 mm | `Inductor_SMD:L_Sumida_CDMC6D28_7.25x6.5mm` | Sunltech's recommended land pattern is G 7.5 mm overall, H 3.6 mm gap, I 3.0 mm wide, which works out to pads about 1.95 x 3.0 mm at +/-2.78 mm. The Sumida footprint has 2.0 x 3.4 mm pads at +/-2.85 mm (3.7 mm gap, 7.7 mm overall), within about 0.2 mm. Avoid `L_Bourns_SRP7028A_7.3x6.6mm` (pads 2.95 x 3.5 mm, only 2.5 mm gap) and `L_7.3x7.3_H3.5` (pads 1.5 x 2.2 mm, too small). There is no generic 7.1 x 6.6 footprint in KiCad |
| DORABO DB128V-5.08-2P-GN-S screw terminal (C2915639) | `TerminalBlock_CUI:TerminalBlock_CUI_TB007-508-02_1x02_P5.08mm_Horizontal` | DORABO's PCB layout shows 5.08 mm pitch and 1.60 mm holes (pins 0.8 x 1.0 mm). The CUI footprint has 5.08 mm pitch, 1.6 mm drill, 2.4 mm pads. The Phoenix MKDS-1,5-2-5.08 footprint has a 1.3 mm drill, which is too tight. There is no generic "through hole, 5.08 mm" footprint, so check the courtyard and silkscreen against the DB128V body (10.2 mm deep, 14 mm tall) |

## 2. Use the generic or stock KiCad parts (no download, just verify)
| Part | Symbol : footprint |
|---|---|
| Mean Well IRM-90-12 | HF library (already there) |
| AP63205WU, AP63203WU | `Regulator_Switching:AP63205WU` / `AP63203WU` : `Package_TO_SOT_SMD:TSOT-23-6` |
| INA226 | `Sensor_Energy:INA226` : `Package_SO:MSOP-10_3x3mm_P0.5mm` (INA226AIDGS is MSOP/VSSOP-10 without an exposed pad; do not use the HVSSOP-10-1EP footprint) |
| ACS712ELCTR-20A-T | `Sensor_Current:ACS712xLCTR-20A` : `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| 2N7002 | `Transistor_FET:2N7002` : `Package_TO_SOT_SMD:SOT-23` |
| AO4407C P-FET | no AO4407 symbol in stock; use a stock single SO-8 P-FET such as `Transistor_FET:FDS9435A` or `IRF7404` (same S-S-S-G-D-D-D-D pin order, which I believe but have not verified against the AO4407C datasheet), set Value and MPN to AO4407C, footprint `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| Raspberry Pi Pico 2 | `MCU_Module:RaspberryPi_Pico` : `Module:RaspberryPi_Pico_Common_THT` on 2 x 1x20 sockets (254PM-1x20P-V, 8.5 mm tall; sockets are BOM-only, they share the Pico's through holes). In the PCB the footprint's courtyard is edited to two socket strips and its Pico W antenna keep-out is removed so parts can sit under the module (2026-10-24) |
| SMCJ15A TVS | `Device:D_TVS` : `Diode_SMD:D_SMC` |
| SS14 | `Diode:SS14` : `Diode_SMD:D_SMA` |
| 1N4148W | `Diode:1N4148W` : `Diode_SMD:D_SOD-123` |
| NTC 10 k, 0603 | `Device:Thermistor_NTC` : `Resistor_SMD:R_0603_1608Metric` |
| PTC fan fuse, 1206 | `Device:Polyfuse` : `Fuse:Fuse_1206_3216Metric` |
| MOV 10D241K (C49072899, 2026-10-16; was 14D241K) | `Device:Varistor` : `Varistor:RV_Disc_D12mm_W5.4mm_P7.5mm` (courtyard 12.6 x 6.0 mm vs 17.1 x 7.3 for the old D16.5 footprint). 10D series sheets give 12.5 mm max diameter and 5.2 mm max thickness for the 241K; not checked against the LCSC part's own drawing |
| Mounting holes H1 to H4 (2026-10-22: schematic footprint is now `MountingHole:MountingHole_3.2mm_M3_Pad_Via`, floating; the PCB still has the M2 footprints; the rest of this row describes the old M2 state) | `MountingHole:MountingHole_2.2mm_M2_Pad` (2.2 mm hole, 4.4 mm pad, 5.0 x 5.0 mm courtyard; the M3 pad version was 7 x 7). The pad is wired to the chassis net (SJ1 pin A) |
| Shunts | `Device:R_Shunt` : `Resistor_SMD:R_2512_6332Metric` (5 mOhm), `R_1206_3216Metric` (33 mOhm) |
| Bulk cap 100 uF 35 V | `Device:C_Polarized` : `Capacitor_SMD:CP_Elec_6.3x7.7` |
| XT60PB-F (J6, since 2026-10-22; was XT60PW-F) | `HF_Connectors:XT60PB-F` : `HF_Footprints:XT60PBF` (pads 6.69 mm, 4.46 mm drills, 7.2 mm pitch, pad 1 square; ingested by the user from the Component Search Engine package). Not compared with the Amass drawing yet. |
| SN65HVD230DR (U14, 2026-10-22) | `Interface_CAN_LIN:SN65HVD230` : `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| TCA9534PWR (U12, 2026-10-24; replaced the PCA9535CPW) | `Interface_Expansion:TCA9534` : `Package_SO:TSSOP-16_4.4x5mm_P0.65mm` (stock KiCad symbol; the pinout matches the PWR package) |
| CAN termination jumper SJ4 | `Jumper:SolderJumper_2_Bridged` : `Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm` |
| Link connector J10 | `Connector:Screw_Terminal_01x04` : `TerminalBlock_CUI:TerminalBlock_CUI_TB007-508-04_1x04_P5.08mm_Horizontal` (DB128V-5.08-4P-GN-S) |
| Fan header, Molex 47053-1000 | `Connector_Generic:Conn_01x04` : `Connector_Molex:Molex_KK-254_AE-6410-04A_1x04_P2.54mm_Vertical` (same 2.54 mm pitch; check the 47053 drawing) |
| LEDs, R/C, 100 nF, 1N4148 | `Device:LED`, `Device:R_Small`, `Device:C_Small` with the 0603, 0805 and 1206 footprints in `LED_SMD`, `Resistor_SMD`, `Capacitor_SMD` |
| Inductor symbol | `Device:L` (footprint from section 1) |

## 3. Notes
- The pcbparts MCP tool `cse_get_kicad` returned the full KiCad symbol and footprint text for the Keystone 3557-2 and 3557-20 earlier in this project, so CSE through the MCP did work for those. If the website itself needs login for you, I can fetch the CSE files (TPS2553 and the two Keystone parts) through the MCP and stage them in a folder for the HF ingest script (`scripts/ingest.py` expects a CSE/SnapEDA zip, which I have not verified accepts a hand-built one).
- Generic parts need no library work, but every footprint above should still be checked against the datasheet before ordering boards.

## 4. Library check after the user added parts (2026-10-14)
`hackerfab-kicadlibs` now has (uncommitted): symbol `HF_ICs:TPS2553DBVR` with footprint `SOT95P280X145-6N`; `HF_Passives:3557-20` with footprint `355720`; `HF_Passives:01020074Z` with footprint `01020074Z`; `HF_Connectors:HB9500-9.5-3P` with footprint `HB9500953P`. `scripts/validate.py` reports 0 errors and 5 warnings (existing parts only).
- **3557-20:** the footprint pad numbering puts pads 1+2 on one side and 3+4 on the other, so tie 1+2 and 3+4 (this corrects the earlier 1+3 / 2+4 note, which belonged to the 3557-2 footprint).
- **01020074Z:** the footprint has 2 pads 7.62 mm apart (1.98 mm drill), so each clip appears to have two PC pins; a fuse needs two clips at about the fuse-length spacing (6.3 x 32 mm, stock Littelfuse 102071 uses 34.7 mm). Confirm in layout.
- **HB9500953P:** this is the HB9500 (no "M") 3-pin footprint, with 2.85 mm round pads and 1.9 mm drill. Our BOM part is the HB9500M (C162697, with cover plate), which has a matching stock footprint (`TerminalBlock_Ningbo-Kagnex_HB9500M_1x03_P9.5mm`, 3.3 x 6.6 mm pads, 2.0 mm drill). Both share the 9.5 mm pitch; use the HB9500M footprint for the HB9500M part and check the pins (1.5 x 0.7 mm) fit the drill.

## 5. 3AG fuse with its clips (2026-10-14)
Custom HF library parts `HF_Passives:Fuse_3AG_6.3x32mm` and footprint `Fuse_3AG_6.3x32mm_Clips_Littelfuse_102_122_P34.21mm` replace the clip-by-clip approach in section 4. Pad positions (origin at the fuse centre): clip 1 at x = -17.105 and -9.485 mm, clip 2 at +9.485 and +17.105 mm, 2.97 mm pads, 1.98 mm drills. These are from the Littelfuse 102/122 datasheet (7.62 mm pin spacing, A = 1.347 in) and match the KiCad stock `Fuseholder_Clip-6.3x32mm_Littelfuse_102_122_Inline_P34.21x7.62mm_D1.98mm_Horizontal` pads; the stock footprint was not used because the HF one carries the 01020074Z 3D models and the symbol default. The earlier suggestion to use the stock 102071 footprint (34.70 x 7.60 mm) is superseded: 102071 is a different clip.

## 6. Blade fuse with its holder (2026-10-15)
Custom HF library parts `HF_Passives:Fuse_Blade_Keystone_3557` and footprint `Fuse_Blade_Keystone_3557-20_P13.47mm` (the vendor 355720 footprint with pads renumbered 1,1 / 2,2 and `duplicate_pad_numbers_are_jumpers`, same 3D model). F4, F5 and F6 use it, so the Keystone holder is no longer a schematic symbol. Hand-made like the 3AG fuse (`sources/Fuse_Blade_Keystone_3557.json`), uncommitted in `hackerfab-kicadlibs`.
