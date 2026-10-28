# Rev 1 BOM (draft v2, 2026-10-14)

Derived from `design-decisions.md` (the sourcing table there has stock, notes and alternatives) and `pin-map.md`. Quantities are first-pass and get finalized against the schematic. "JLC" = placed by JLC PCBA, "Hand" = hand-soldered (through-hole or plug-in). Library type: B = basic, P = preferred, E = extended (per-unique-part JLC fee, only if JLC places it).

v2 changes (2026-10-14): added 12 V branch switches, tap sense circuits and EN pull-ups; swapped the extended green LED for the no-fee yellow LED; swapped the extended 51 k 1206 mains-LED resistors for four basic 33 k 0603; dropped the series Schottky and the inrush NTC footprint.

## Mains and AC/DC
| Qty | Part | PN | Lib | Asm | Notes |
|---|---|---|---|---|---|
| 1 | Mean Well IRM-90-12 | LCSC C6577385 | E | Hand | 12 V / 6.7 A |
| 2 | Barrier strip 3P 9.5 mm (Kangnex HB9500M-9.5-03P-13-00A) | LCSC C162697 | E | Hand | AC in, AC out |
| 1 | MOV 10D241K | LCSC C49072899 | E | Hand | L-N after the fuse; 10 mm disc, 150 VAC, 2.5 kA, 35 J (was the 14D241K) |
| 4 | Fuse clip, Littelfuse 01020074Z | Digikey F4187-ND | - | Hand | 2 per 3AG fuse. Not a schematic symbol: the clips are the pads of the F1 and F2 footprint (`Fuse_3AG_6.3x32mm_Clips_Littelfuse_102_122_P34.21mm`) |
| 1 | 3 A Slo-Blo 3AG, 0313003.HXP | Digikey F2545-ND | - | Hand | Module branch. Keep spares; 4 A 0313004.HXP (F2546-ND) is the swap-in if it trips |
| 1 | 10 A ceramic fast-blow 3AG, 0314010.HXP | Digikey F3222-ND | - | Hand | Furnace branch |
| 0-1 | X2 100 nF 275 VAC | LCSC C2901341 | E | Hand | Optional, IRM has its own filter |

## 12 V bus, branch switches and protection
| Qty | Part | PN | Lib | Asm | Notes |
|---|---|---|---|---|---|
| 1 | TVS SMCJ15A | LCSC C42371550 | P | JLC | |
| 1 | Bulk cap 100 uF 35 V (KNSCHA RVE100UF35V67RV0072) | LCSC C2836437 | E | JLC | |
| 3 | Blade fuse holder Keystone 3557-2 | Mouser 534-3557-2 / Digikey 36-3557-2-ND | - | Hand | Not a schematic symbol: it is the footprint of F4, F5 and F6 (`Fuse_Blade_Keystone_3557-20_P13.47mm`, pads renumbered 1,1 / 2,2). Old note on the vendor footprint, tie pads: 1+2 and 3+4 for the added 3557-20 footprint (HF library), 1+3 and 2+4 for the 3557-2 footprint. Same body, same pad geometry |
| 2 | ATO blade fuse 3 A (0ATO003.V) | Digikey F5040-ND | - | Hand | 12 V taps |
| 1 | ATO blade fuse 7.5 A (0ATO07.5V) | Digikey F11167-ND | - | Hand | ESC |
| 1 | XT60PB-F (vertical female) | LCSC C19268038 | E | Hand | ESC power (J6; was the horizontal XT60PW-F C428722 until 2026-10-22) |
| 3 | P-FET AO4407C (30 V, 14 A, 11.5 mOhm) | LCSC C469397 | E | JLC | High-side switch for 12 V tap A, tap B and the ESC branch |
| 3 | 2N7002 | LCSC C8545 | B | JLC | Gate drivers for the three P-FETs (a fourth 2N7002 drives the SSR, below) |

## 5 V / 3.3 V rails and taps
| Qty | Part | PN | Lib | Asm | Notes |
|---|---|---|---|---|---|
| 1 | AP63205WU-7 | LCSC C2071056 | E | JLC | 5 V buck |
| 1 | AP63203WU-7 | LCSC C780769 | E | JLC | 3.3 V buck |
| 2 | Inductor 4.7 uH (SLO0630H4R7MTT) | LCSC C207840 | E | JLC | |
| 2 | 10 uF 50 V 1206 | LCSC C13585 | B | JLC | Buck Cin |
| 4 | 22 uF 25 V 0805 | LCSC C45783 | B | JLC | Buck Cout, 2 per buck |
| 4 | TPS2553DBVR | LCSC C55266 | E | JLC | One per tap, ILIM 33 k |

## Telemetry and sensing
| Qty | Part | PN | Lib | Asm | Notes |
|---|---|---|---|---|---|
| 3 | INA226AIDGSR | LCSC C49851 | E | JLC | 12 V, 5 V, 3.3 V rails |
| 1 | Shunt 5 mOhm 2512 (RLP25FEGMR005) | LCSC C393074 | E | JLC | 12 V rail, CAL 1024 |
| 2 | Shunt 33 mOhm 1206 (RLS12FTCR033) | LCSC C912764 | E | JLC | 5 V and 3.3 V rails, CAL 1552 |
| 1 | ACS712ELCTR-20A-T | LCSC C10681 | E | JLC | Furnace L leg. Divider 4.7 k / 10 k, FILTER cap 100 nF |
| 2 | NTC 10 k 0603 (NCP18XH103F03RB) | LCSC C13564 | E | JLC | Next to the IRM-90-12, and on the SSR heat sink (off-board via screw terminal) |

## MCU, indicators, SSR drive
| Qty | Part | PN | Lib | Asm | Notes |
|---|---|---|---|---|---|
| 1 | Raspberry Pi Pico 2 | LCSC C41407547 | E | Hand | Plug in |
| 2 | 1x20 female socket (254PM-1x20P-V) | LCSC C53202183 | E | Hand | 8.5 mm tall; SMD parts sit under the Pico between the sockets (decided 2026-10-24) |
| 2 | 1x20 male pin header, 2.54 mm | TBD (or buy the Pico 2 H) | E | Hand | The Pico 2 ships without headers; **not yet sourced** |
| 3 | Yellow LED 0603 (NCD0603Y2) | LCSC C89811 | P | JLC | 12 V, 5 V, 3.3 V rails (replaces the extended green LED) |
| 1 | Red LED 0603 (KT-0603R) | LCSC C2286 | B | JLC | Mains present |
| 4 | 33 k 0603 | LCSC C4216 | B | JLC | Mains LED dropper in series (about 132 k); counted again under the 33 k line below |
| 1 | 1N4148W | LCSC C81598 | B | JLC | Mains LED antiparallel |
| 1 | SS14 | LCSC C2480 | B | JLC | Pico VSYS Schottky |
| 1 | 2N7002 | LCSC C8545 | B | JLC | SSR low-side drive, SSR input on the 5 V rail |
| 1 | 1 k 0603 | LCSC C21190 | B | JLC | SSR gate resistor |
| 2 | Solder jumpers (3-pad) | - | - | - | SSR drive select; default = MOSFET/5 V, move both for direct 3.3 V drive |

## Passives and connectors
| Qty | Part | PN | Lib | Asm | Notes |
|---|---|---|---|---|---|
| ~16 | 100 nF 50 V 0603 | LCSC C14663 | B | JLC | Boots (2), TPS2553 IN (4; OUT needs none), INA226 (3), ACS712 FILTER (1) and VCC bypass (1), Pico/others |
| ~21 | 10 k 0603 | LCSC C25804 | B | JLC | NTC dividers (2), ACS712 divider bottom (1), tach pull-up (1), TPS2553 EN pull-ups (4), 12 V sense bottoms (3), 5 V sense bottoms (2), 3.3 V sense pulldowns (2), P-FET gate pull-ups (3), 2N7002 gate pull-ups (3) |
| 7 | 4.7 k 0603 | LCSC C23162 | B | JLC | I2C pull-ups (2), 12 V LED, ACS712 divider top, SSR GPIO pulldown, 5 V sense tops (2) |
| 11 | 33 k 0603 | LCSC C4216 | B | JLC | TPS2553 ILIM (4), 12 V sense tops (3), mains LED dropper (4) |
| 1 | 1.5 k 0603 | LCSC C22843 | B | JLC | 5 V LED |
| 1 | 680 ohm 0603 | LCSC C23228 | B | JLC | 3.3 V LED |
| 1 | 4-pin PC fan header, Molex 47053-1000 | Mouser 538-47053-1000 | - | Hand | Fan: GND, +12 V, tach, PWM. Fan: Noctua NF-A8 PWM (Amazon), off-board |
| 1 | PTC resettable fuse 500 mA hold, 33 V (TECHFUSE nSMD050-33V) | LCSC C70077 | E | JLC | Fan +12 V |
| 8 | 2P 5.08 mm screw terminal (DB128V-5.08-2P-GN-S) | LCSC C2915639 | E | Hand | 6 taps, SSR control, SSR heat-sink NTC |

## Not yet sourced
- M3 mounting hardware and standoffs (four floating M3 plated holes in the board corners from 2026-10-21; the schematic still has M2 until it is updated); solder-jumper star-ground pads (footprint only).
- SSR heat sink and its wiring (off-board). Dump-load parts (DNP footprint only).
- Gate clamp for the 12 V branch P-FETs (check Vgs against the 25 V limit during a TVS clamp).

## Counts
- **Unique extended parts JLC places (fee applies): 12**: AP63205, AP63203, inductor, TPS2553, INA226, 5 mOhm shunt, 33 mOhm shunt, ACS712, NTC, bulk cap, fan PTC, AO4407C.
- Extended LCSC parts that are hand-assembled (no JLC fee if you don't use JLC for them): IRM-90-12, barrier strip, MOV, XT60PB-F, screw terminal, Pico, sockets.
- Basic/preferred (no fee): TVS (P), yellow LED (P), 10 uF, 22 uF, 100 nF, 10 k, 4.7 k, 33 k, 1.5 k, 680, 1 k, red LED, 1N4148W, SS14, 2N7002.
- Digikey/Mouser hand parts: fan header, blade fuse holders, blade fuses, 3AG fuses, fuse clips.

## Additions and swaps in the schematic (2026-10-22) and the PCB (2026-10-24)
Current designators after the user re-annotated on 2026-10-24: U12 expander, U13 Pico, U14 transceiver, J10 link connector (5 V tap A), J9 is now 5 V tap B, SJ4 CAN termination jumper, SJ5 and SJ6 the SSR jumpers, R40 Rs, R41 120 ohm.
| Change | Part | LCSC | Library | Note |
|---|---|---|---|---|
| CAN transceiver U14 (new) | SN65HVD230DR | C12084 | preferred | SOIC-8, 3.3 V, 153k in stock, $0.57; datasheet in `datasheets/` |
| I/O expander U12 (new, for the 7 sense inputs; replaces the first choice, PCA9535CPW, C2652292) | TCA9534PWR | C783615 | extended | TSSOP-16, 11,514 in stock, $0.93 |
| CAN termination R41 + SJ4 (new) | 120 ohm 0603 (0603WAF1200T5E) + solder jumper | C22787 | basic | closed by default; R40 10 k (Rs) and C19, C20 100 nF are existing basic values |
| CAN / 5 V link connector J10 (new) | DB128V-5.08-4P-GN-S, pins 5 V, CANH, GND, CANL | C2915641 | extended | 102k in stock, $0.42; replaces the old 2P tap-A terminal (C2915639, one fewer 2P) |
| ESC connector J6 (swap) | XT60PB-F vertical female | C19268038 | extended | replaces XT60PW-F C428722; footprint `HF_Footprints:XT60PBF` (from the user's ingest), not yet compared with the Amass drawing |
| Mounting holes H1 to H4 (swap) | `MountingHole_3.2mm_M3_Pad_Via` | - | - | M3 hardware instead of M2, floating (schematic footprint changed 2026-10-22) |

## Optimization notes
- Done: green LED to yellow (-1 extended), mains-LED resistors to basic 33 k 0603 (-1 extended), expander not used (-1 extended; reversed 2026-10-21, the I/O expander is back for the sense inputs, as the 8-bit TCA9534PWR since 2026-10-24).
- Possible, user's call: use one 33 mOhm or one 5 mOhm shunt everywhere (-1 extended, costs resolution on one rail); drop the NTC part by using the Pico's on-die temperature (loses the module/SSR sensing); skip the optional X2 cap.
- Resistor values are all basic, so merging them (for example the LED resistors) saves only line items, not fees.
