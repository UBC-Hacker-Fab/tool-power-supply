# PCB placement

## Status (2026-10-16)
Board outline decided by the user: **90 x 160 mm** (portrait, 14,400 mm2), after the earlier 120 x 80 mm limit proved too small for this BOM (see below). A first-pass, single-sided (F.Cu) placement of all 120 parts is in the project PCB (scripts and method in `tools/pcb_placement/README.md`; copy of the result in `placement_90x160.kicad_pcb`). **Re-placed on 2026-10-16** after the user's layout review: four **M2** holes in the four board corners (centres 3.2 mm from both edges, pad copper 1.0 mm from the edge), the MOV changed to the 10D241K (12.6 x 6.0 mm courtyard instead of 17.1 x 7.3), and the 3.2 mm mains clearance built into the annealer. Nets unchanged, 120 parts. No tracks, zones or slots yet.

**Pending after the 2026-10-21 design review (not yet applied; details in `design-decisions.md`, 'Control link, I/O expander, connector and mounting changes'):** (1) M3 floating plated holes with ring vias (`MountingHole_3.2mm_M3_Pad_Via`, 6.4 mm pad, courtyard radius 3.45 mm) at (3.5, 3.5), (86.5, 3.5), (3.5, 156.5), (86.5, 156.5), which collide with J1 at the top left (hole courtyard reaches y 6.95, J1 starts at y 6.0) so the top block must move down about 4 mm or sideways; mains parts stay 3.2 mm from the hole courtyard; (2) a vertical female XT60 in place of the horizontal one (about 150 mm2 freed, bottom-right corner relaxes); (3) new parts: SN65HVD230 (SOIC-8), PCA9535C (TSSOP-24), 120 ohm termination with a solder jumper, a 4-pin CAN/5 V link connector near the Pico (replaces J9). Placement has to be rerun after the schematic and footprints change; fixed.json, ties.json and zones.json need the new refs.

Checks on the placement: no courtyard overlaps, every part inside the outline, 289 unconnected items (expected, no routing). **DRC** (with the new mains rules in `tool-power-supply-v1.kicad_dru`) shows only the 20 INA226 MSOP-10 pad gaps (0.15 mm vs the 0.2 mm default rule; JLC minimum 0.127 mm); no violation of the 3.2 mm mains-to-anything, 1.6 mm L-to-N or mains-to-PE rules. The mains parts (J1, J2, F1, F2, RV1, the LED dropper R1 to R4, D1, D2, the ACS712 pins 1 to 4 and the module's AC pins) are kept 3.2 mm (courtyard to courtyard) from every other part. The ACS712's own pad rows are exempt (3.0 mm apart in air, 4 mm creepage per the datasheet).

## Floor plan (board coordinates, mm, origin top-left; x right, y down)
To make room for the corner holes, the top block (J1, J2, F1, F2, Pico) and the right terminals moved down about 5.4 mm, the bottom row moved right, F6 stands upright and the XT60 moved left; the module did not move.

| Zone | Where | What |
|---|---|---|
| Corner holes | (3.2, 3.2), (86.8, 3.2), (3.2, 156.8), (86.8, 156.8) | H1 to H4, M2, 5.0 x 5.0 mm courtyards. |
| Mains band | x 0 to 66, y 5.5 to 46 | J1 (AC in) and J2 (AC out) at y 6 to 23 with wire entry up (6 mm of free board above them); F1 (furnace 10 A) at y 28.5 and F2 at y 39.4, horizontal; U2 ACS712 at (55.5, 28.6), RV1 at (53, 40.9); the LED dropper R1 to R4, D1, D2 in the pockets between. |
| Module | x 0.7 to 53.3, y 46 to 133.6 | U1 IRM-90-12 stood upright: AC pins at the top (x 41, 48; y 51.6), DC pins at the bottom left (x 6.8, 12.3; y 127.6). |
| Pico | x 65.4 to 88.6, y 6 to 60 | U12 vertical, USB on the top edge. |
| Right edge | x 78 to 90, y 60.5 to 133.5 | J12 (SSR), J11 (NTC), J7 to J10 (3.3 V and 5 V taps), wire entry facing right, centres at y 66.4 + 12.2 n. |
| Right strip | x 54 to 78, y 46 to 140 | Both bucks, the 5 V and 3.3 V INA226s, the four TPS2553 taps, SSR drive, I2C pull-ups, the Pico's support parts. |
| 12 V band | y 134 to 160 | J4, J5 (12 V taps) from x 6 on the bottom left edge, bus parts (R5, U3, D3 TVS, C3 bulk) by the module DC pins, blade fuses F4 and F5 stacked at x 31.5 to 53.5, F6 upright at x 56 to 65, J6 XT60 at x 66.5 to 83.1 (kept 1.7 mm clear of the H4 hole so a plugged-in XT60 does not cover the screw). |

## Why 120 x 80 mm did not work
Courtyard areas (mm): U1 87.6 x 52.6 = 4,606 (matches the vendor's 87 x 52 x 29.5 mm), Pico 1,250, J1 and J2 1,064, F1 and F2 792, eight DB128V 1,072, XT60 307, blade holders 594, MOV, fan header and bulk cap 271. Through-hole and large parts total about 9,950 mm2 against a 9,600 mm2 board before any spacing. Everything including SMD is about 11,200 mm2, which is 78 % of the 90 x 160 board.
Levers if the board ever has to shrink: 5 x 20 mm fuse clips (about 380 mm2), 7.62 mm pitch mains blocks (about 560), castellated RP2350 module instead of the Pico (about 800), furnace AC chain off-board (about 930), a smaller AC/DC module.

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
- 2026-10-21 changes above: schematic edits (blocked while KiCad has the project open), footprint swaps, link connector choice, then a placement rerun.
- F2 fuse style (5 x 20 clips vs soldered radial vs keep 3AG): pending the user's choice, see design-decisions.md.
- Whether bottom-side SMDs or a castellated RP2350 module are worth doing: only if the board needs to shrink; estimates in the 2026-10-16 conversation (about 7% and 6% of the board).
- The F4 to F6 flag is fixed in the schematic. If the schematic gets re-annotated or the footprints change, rerun `tools/pcb_placement` (update the refs in `fixed.json`, `ties.json` and `zones.json`).
- Routing, wide pours for the roughly 8.3 A furnace path, tuned decoupling placement; confirm the 3.2 mm / 1.6 mm creepage numbers; check the 10D241K drawing against the footprint; confirm the J1 pin order (L tail length) and the DB128V / XT60 orientations.
