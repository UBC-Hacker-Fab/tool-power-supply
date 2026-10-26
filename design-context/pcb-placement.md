# PCB placement

## Status (2026-10-24; first placed 2026-10-16)
Board outline decided by the user: **90 x 160 mm** (portrait, 14,400 mm2), after the earlier 120 x 80 mm limit proved too small for this BOM (see below). A first-pass, single-sided (F.Cu) placement of all 120 parts is in the project PCB (scripts and method in `tools/pcb_placement/README.md`; copy of the result in `placement_90x160.kicad_pcb`). **Re-placed on 2026-10-16** after the user's layout review: four **M2** holes in the four board corners (centres 3.2 mm from both edges, pad copper 1.0 mm from the edge), the MOV changed to the 10D241K (12.6 x 6.0 mm courtyard instead of 17.1 x 7.3), and the 3.2 mm mains clearance built into the annealer. Nets unchanged, 120 parts. No tracks, zones or slots yet.

**Updated 2026-10-24 (after the 2026-10-21 design review; details in `design-decisions.md`, 'Control link, I/O expander, connector and mounting changes').** The user ran Update PCB from Schematic and re-annotated; the layout was then updated by a targeted script that keeps every hand edit (the hand-moved R1 to R4, D1, D2, RV1 and SJ3, the deleted SJ1 and SJ2, the whole mains stack) and moves only what the new parts and holes force. Nothing was re-annealed. **Current designators:** U12 TCA9534PWR, U13 the Pico (was U12), U14 SN65HVD230, J10 the 4-pin link connector (was J13 in the first schematic edit), J9 now 5 V tap B, J6 the vertical XT60PB-F, SJ4 the CAN termination jumper, SJ5 and SJ6 the SSR jumpers, R40 (Rs) and R41 (120 ohm).

What moved (board coordinates, mm): **H1 to H4** to 3.72 mm from both edges (M3 pad copper 0.51 mm from the edge, board rule 0.5 mm; at 3.5 mm it was 0.3 mm). **J1, F1, F2** down 1.25 mm so the J1 courtyard clears H1 (J1 now y 7.3 to 24.4; F2 ends at y 45.7, 0.3 mm above the module). The 3.2 mm rule was applied to the live pads, not to J1's plastic housing (see design-decisions.md; full courtyard clearance would need J1 and the stack about 3 mm lower). **Pico U13** down 1.27 mm (now y 7.3 to 61.2) to clear H2, which pushed U7, R38, TH1, R46 and C14 down 0.8 to 1.1 mm. **J4, J5** right 1.25 and 1.0 mm to clear H3. **Right-hand terminal column** (rot 90, wire entry right): J12 y 61.7 to 73.5, J11, J7, J8 each 1.18 mm lower, **J10** (new, 4P) y 110.5 to 132.5 where the old tap-A terminal was, **J9** moved down to y 132.8 to 144.7. **J6 XT60PB-F** (vertical) at x 67.3 to 77.3, y 142.0 to 159.7, between F6 and H4. **U12 + C19** in the free pocket at x 54 to 62, y 101 to 107 (central between the tap sense points; module edge 0.8 mm away). **CAN block** beside J10 at x 68 to 77.4, y 112 to 122.5: U14 with its CANH/CANL pins facing J10, C20 on its VCC side, R40 above, R41 and SJ4 below. Routing note: at J10 the CANH pad (pin 2) is below the CANL pad (pin 4) while U14's CANH pin is above CANL, so the pair crosses once (two vias) or the CAN block moves; the pad order follows the pin order the user chose.

**Parts under the Pico (2026-10-24, later; user committed to header sockets).** The Pico plugs into two 1x20 sockets (254PM-1x20P-V, 8.5 mm insulation height), so the pocket between the socket bodies (x 69.9 to 84.1, y 14 to 59.6, about 770 mm2, at least 8 mm headroom) now holds 34 logic-level SMD parts on the top side, no double-sided assembly: **U12 TCA9534 + C19** (U12 at (76.9, 45.1), rot 90), **the six sense-divider pairs** R8/R9, R10/R11, R12/R13, R32/R33, R34/R35, R36/R37 (vertical pairs along the bottom of the pocket, refs hidden on silk), **the 7 EN pull-ups** R14, R15, R16, R24 to R27 (one column on the left), **I2C pull-ups** R38, R39, **NTC / ACS712 dividers** TH1, R46, R47, R44, R45, **bypass** C13, C14, **SSR drive** Q7, R42, R43 and **D7 SS14** (VSYS). These came out of the right strip. The Pico footprint was edited in the PCB only: its single courtyard became two socket-strip courtyards (x 65.4 to 69.6 and 84.4 to 88.6) and the Pico W 'Antenna Copper Keep Out' rule area and comment text were removed (the 'USB Cable' rule area stays). The edited footprint differs from the library copy (DRC `lib_footprint_mismatch` warning, expected); do not 'Update footprint from library' on U13 without redoing this. The parts must stay under 7 mm tall (sockets are 8.5 mm, and the Pico's male-header body adds about 2.5 mm). The Pico's underside test pads (TP1 to TP7, datasheet section 3.1, in the USB end) are 8 mm above the parts, so nothing can short them.

**Hand edits found and kept (PCB differed from my 2026-10-24 install):** U2 moved left to x 49.6, C1/C2 to (55.1, 26.9) and (55.1, 29.2), J2 down 1.25 mm, the R1 to R4 / D1 / D2 / RV1 group down 1.25 to 6.2 mm, SJ3 to x 62.35. K1 and K4 were re-derived from those positions (see below).

Checks: no courtyard overlaps, all parts inside the outline. DRC against the baseline: the courtyard overlaps (J1/H1, J4/H3) and the 20 hole-pad copper-to-edge errors are gone; what is left is the same 20 INA226 pad gaps (0.15 mm vs 0.2 mm), silkscreen warnings, 304 unconnected items (no routing), and one mains-to-reachable error (R1 pad 1 to J2 pad 3, 2.91 mm) that is a **stale net class**: the PE class in `tool-power-supply-v1.kicad_pro` still lists `Net-(SJ1-A)` and `Net-(SJ1-B)`, but since SJ1 and SJ2 were deleted the PE net is called `Net-(SJ3-A)`, so J1 and J2's PE pads are treated as reachable (3.2 mm) instead of PE (1.6 mm). Change the PE pattern in Board Setup, Net Classes, to `Net-(SJ3-A)` (not edited here: the project manager has the file open).

Checks on the placement: no courtyard overlaps, every part inside the outline, 289 unconnected items (expected, no routing). **DRC** (with the new mains rules in `tool-power-supply-v1.kicad_dru`) shows only the 20 INA226 MSOP-10 pad gaps (0.15 mm vs the 0.2 mm default rule; JLC minimum 0.127 mm); no violation of the 3.2 mm mains-to-anything, 1.6 mm L-to-N or mains-to-PE rules. The mains parts (J1, J2, F1, F2, RV1, the LED dropper R1 to R4, D1, D2, the ACS712 pins 1 to 4 and the module's AC pins) are kept 3.2 mm (courtyard to courtyard) from every other part. The ACS712's own pad rows are exempt (3.0 mm apart in air, 4 mm creepage per the datasheet).

## Floor plan (board coordinates, mm, origin top-left; x right, y down)
To make room for the corner holes, the top block (J1, J2, F1, F2, Pico) and the right terminals moved down about 5.4 mm, the bottom row moved right, F6 stands upright and the XT60 moved left; the module did not move.

| Zone | Where | What |
|---|---|---|
| Corner holes | (3.72, 3.72), (86.28, 3.72), (3.72, 156.28), (86.28, 156.28) | H1 to H4, floating M3 (pad 6.4 mm, courtyard radius 3.45 mm, washer-clear radius 4.25 mm). |
| Mains band | x 0 to 66, y 5.5 to 46 | J1 (AC in, y 7.3 to 24.4) and J2 (AC out, y 6 to 23) with wire entry up; F1 (furnace 10 A) at y 29.75 and F2 at y 40.65, horizontal; U2 ACS712 at (49.6, 28.6) (hand-moved), RV1 at (47.6, 43.1); the LED dropper R1 to R4, D1, D2 in the pockets between. |
| Module | x 0.7 to 53.3, y 46 to 133.6 | U1 IRM-90-12 stood upright: AC pins at the top (x 41, 48; y 51.6), DC pins at the bottom left (x 6.8, 12.3; y 127.6). |
| Pico | x 65.4 to 88.6, y 7.3 to 61.2 | U13 (was U12) vertical, USB on the top edge, on two 1x20 sockets; the 15 x 51 mm pocket between the sockets holds the logic parts listed above (34 SMD parts). |
| Right edge | x 78 to 90, y 61.7 to 144.7 | J12 (SSR), J11 (NTC), J7, J8 (3.3 V taps), J10 (link, 4P, y 110.5 to 132.5), J9 (5 V tap B), wire entry facing right. |
| Right strip | x 54 to 78, y 46 to 140 | Both bucks, the 5 V and 3.3 V INA226s, the four TPS2553 taps and the CAN block (x 68 to 77.4, y 112 to 122.5) beside J10. |
| 12 V band | y 134 to 160 | J4, J5 (12 V taps) from x 6 on the bottom left edge, bus parts (R5, U3, D3 TVS, C3 bulk) by the module DC pins, blade fuses F4 and F5 stacked at x 31.5 to 53.5, F6 upright at x 56 to 65, J6 vertical XT60PB-F at x 67.3 to 77.3, y 142 to 159.7 (5.7 mm from the H4 courtyard). |

## Why 120 x 80 mm did not work
Courtyard areas (mm): U1 87.6 x 52.6 = 4,606 (matches the vendor's 87 x 52 x 29.5 mm), Pico 1,250, J1 and J2 1,064, F1 and F2 792, eight DB128V 1,072, XT60 307, blade holders 594, MOV, fan header and bulk cap 271. Through-hole and large parts total about 9,950 mm2 against a 9,600 mm2 board before any spacing. Everything including SMD is about 11,200 mm2, which is 78 % of the 90 x 160 board.
Levers if the board ever has to shrink: 5 x 20 mm fuse clips (about 380 mm2), 7.62 mm pitch mains blocks (about 560), castellated RP2350 module instead of the Pico (about 800), furnace AC chain off-board (about 930), a smaller AC/DC module. **Status 2026-10-24:** moving the logic parts under the Pico (about 225 mm2 of SMD courtyards, no double-sided assembly needed) emptied most of the right strip, but the board height is still set by through-hole blocks: the right terminal column (J12 to J9, 83 mm) and the bottom band (F4 and F5 stacked, J4/J5, F6, J6 at y 134 to 160). Getting to about 150 to 155 mm needs the high-current block (Q1 to Q3, F4 to F6, J4 to J6) re-arranged into the freed strip; not done, waiting for the user's go-ahead.

## Design guides in `design-guides/`
- `slyt734.pdf` (TI, linear vs switch-mode): background only. Switch-node loops and transformer edges are what radiate and conduct, which is why the IRM module and the two 1.1 MHz bucks matter for EMI.
- `slyy063a.pdf` (TI, reinforced isolation): creepage depends on working voltage, pollution degree and CTI (IEC 60664-1). FR-4 is material group IIIa (CTI 175 to 399 V), so use the IIIa creepage columns.
- `ssztd13.pdf`, `ssztaq1.pdf` (TI, limited power source): LPS limits (IEC 60950-1 clause 2.5, now PS2 in IEC 62368-1) lower the fire-enclosure requirements for downstream parts. Whether the IRM-90-12 output (80 W continuous, 88 W peak) qualifies is not established; the tap fuses and the PTC limit each branch regardless.
None of the four contain placement rules for this board; layout rules come from IEC 62368-1 / 60664-1, IPC-2221 and the datasheets.
- `1923421193536807.pdf` (IEC 60664-1:2007, added 2026-10-16): the creepage and clearance tables (F.1, F.2, F.3a, F.4) and clauses 5.1.6 and 5.2.4 are the source for the proposed 3.2 mm / 1.6 mm rules.

## Assumptions to verify
- Terminal wire-entry side (DB128V: the side with the thin lip and the pin-1 triangle, +y in the footprint; no 3D model) and the XT60PW-F orientation (body toward the bottom edge). Check against the datasheets before routing.
- J1 pin 1 (L) is at the right end of the strip and the fuses' input clips are at the left, so the L tail is a 20 to 25 mm mains trace along the gap under J1.
- Mains to low-voltage spacing: J2 and RV1 are 4 to 9 mm from the Pico's pins; U2 straddles the barrier (pins 1 to 4 mains side, 5 to 8 low-voltage side, facing the Pico). Confirm creepage once the traces exist. The proposed rule from IEC 60664-1 (see design-decisions.md, 'Clearance and standards approach') is 3.2 mm mains-to-reachable and 1.6 mm L-to-N; the earlier 6.4 mm figure was unsourced and is withdrawn. At 4 to 9 mm the Pico pins already clear 3.2 mm, so slots are likely only needed where parts are closer.
- The placement is a search result: decoupling caps are tied to their ICs but not tuned, and the bucks, INA226s and tap ICs are packed tightly in the right strip.

## Open items
- Fix the stale PE net class pattern (above); check the XT60PBF footprint against the Amass drawing; decide whether the housing-clearance relaxation at H1 stands (design-decisions.md).
- F2 fuse style (5 x 20 clips vs soldered radial vs keep 3AG): pending the user's choice, see design-decisions.md.
- Whether bottom-side SMDs or a castellated RP2350 module are worth doing: only if the board needs to shrink; estimates in the 2026-10-16 conversation (about 7% and 6% of the board).
- `tools/pcb_placement/fixed.json`, `ties.json` and `zones.json` use the 2026-10-15 designators and are now stale (the schematic was re-annotated on 2026-10-24); do not rerun the annealer over the hand-edited PCB without asking. The 2026-10-24 targeted scripts are in `tools/pcb_placement/update_2026_10_24/`.
- Routing, wide pours for the roughly 8.3 A furnace path, tuned decoupling placement; confirm the 3.2 mm / 1.6 mm creepage numbers; check the 10D241K drawing against the footprint; confirm the J1 pin order (L tail length) and the DB128V / XT60 orientations.


## Layout review before routing (2026-10-25, of the user's hand-finished layout)
Read-only check of the PCB (md5 7970e963...). 125 parts, all on F.Cu, none off-board, no courtyard overlaps, outline 90 x 160. DRC: 192 violations, of which only one is new and real.

**Fix before routing**
- RV1 pad 2 (neutral) to U2 pad 5 (GND) is 3.198 mm against the 3.2 mm mains-to-reachable rule (2 um short). Move RV1 or U2 about 0.2 mm.
- Net classes in the project are stale: the PE class still lists `Net-(SJ1-A)` and `Net-(SJ1-B)` (SJ1 was deleted); the PE net is `Net-(SJ3-A)`. Until fixed, PE copper is checked as 'reachable' (3.2 mm to L / N) instead of 1.6 mm.
- 21 INA226 pad-gap clearance errors (0.15 mm package gap against the 0.2 mm default) at U3, U6, U7; add a rule that allows 0.15 mm inside those courtyards.
- U13 reference text is clipped by the board edge (silk only).

**Routing risks (not errors)**
- No routing under the module body (K2, both layers): everything between the left and right halves passes through the 7 mm between the module bottom (y 134.4) and the fuses, which is already occupied by Q1 / Q2 and their gate parts, or through the strip x 54 to 56 beside the module. Expect about 12 nets (12V_BUS, 3 I2C, 3V3_MCU, 3 gate drives, sense lines) to use B.Cu under Q1 / Q2 and between the F4 / F5 pads.
- Q1 feeds F4 (lower row) but sits above F5 (upper row), so `Net-(F4-Pad2)` has to cross the F5 area and the 12V_BUS corridor at x 38.7. Needs B.Cu or a swap; decide before routing.
- ESC branch (7.5 A): the free corridors around F6 / J6 are 2.3 to 2.7 mm wide on each side (F4 edge to F6 pads, F6 pads to J6), and the Q3 to J6+ path squeezes past J6's GND pad. IPC-2221 external 1 oz gives about 3.2 mm for 7.5 A at 20 C rise, so both layers (or 2 oz) are needed there.
- U3 (12 V INA226 at the bottom-left) is 130 to 180 mm from the Pico: I2C SDA / SCL about 150 mm, ALERT 130 mm, 3V3_MCU 184 mm. With 4.7 k pull-ups the rise time is too slow for 400 kHz; run I2C at 100 kHz.
- 22 nets leave the Pico pocket, almost all through its 14 mm bottom opening (both layers) and the gaps between socket pins. The three 12 V sense nets (J4, J5, J6 +) run about 100 to 115 mm up to the divider tops R8 / R10 / R12 in the pocket; moving those three 33 k resistors next to the taps would make the long runs 3 V signals instead of 12 V (optional).
- The footprint's 'USB Cable' area (x 71 to 83, above the Pico) overlaps the H2 washer by about 1 mm; a wide cable overmold can touch an M3 screw head at H2.

## Copper pour keep-outs (drawn 2026-10-24 on User.Drawings, group "pour keepouts")
Hatched dashed outlines plus a legend at the right of the board (x 94 to 140, y 2 to 22). They are plan only (no rule areas), so the pours still have to be created.

| Id | Where (board mm) | Rule | Why |
|---|---|---|---|
| K1 mains zone | polygon x 0 to 62.3, y 0 to 46 (rev B: top block to y 26.4, notched to x 51.3 at y 26.4 to 31.5, x 54.1 to y 48.6 beside the module) | no GND or LV pour on either layer; only Mains / PE class copper | mains pad copper (J1, J2, F1, F2, R1 to R4, D1, D2, RV1, U2 pins 1 to 4, extents from the placed pads) plus 3.2 mm; keeps a GND fill from creeping between L / N pads |
| K2 module body | x 0.7 to 53.3, y 46 to 133.6, with a window x 0.7 to 19, y 120 to 133.6 | no pour on either layer except +Vo / -Vo in the window; traces only from the AC pins | isolation barrier and common-mode coupling under the IRM-90-12; nothing is placed under the body, so a plane there references nothing |
| K3 holes | circles r 4.25 around H1 to H4 | no pour on either layer | the holes are floating and an M3 washer has 7 mm OD (r 3.5) |
| K4 ACS712 | x 45.4 to 53.8, y 25.4 to 31.8 (U2 courtyard +0.5 mm, follows the hand-moved U2) | pads only | no copper between the pad rows (3.0 mm in air, 4 mm creepage comes from the package) |
| K5 inductors | L1 and L2 courtyards | no F.Cu pour; B.Cu stays solid GND | keeps the SW node copper small |
| K6 Pico pocket | dashed outline x 69.9 to 84.1, y 14 to 59.6 (not hatched) | no pour restriction; parts at most 7 mm tall | marks the area under the Pico that holds SMD parts |

Outside the keep-outs: GND on B.Cu stitched to an F.Cu GND pour (vias about every 10 mm and at each bypass cap), wide F.Cu pour for 12V_BUS and the ESC path (about 8.3 A for the furnace is on the AC side, the ESC branch is 7.5 A), Pico AGND joined to GND at the Pico only. The Pico 2 has no antenna, so the Pico W antenna keep-out was removed from the footprint (2026-10-24).
