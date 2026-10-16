# PCB initial placement (2026-10-15)

First-pass placement and board outline, done by script with KiCad's `pcbnew` Python API (no tracks, zones or slots yet). The board is **200 x 120 mm**, 3 mm corner radius, origin at KiCad (60, 40) so it sits inside the A4 sheet. Everything is on F.Cu.

## Zones (board coordinates, mm, origin top-left)

| Zone | Where | What |
|---|---|---|
| Mains | x 0 to 50, full height | J1 (AC in) and J2 (AC out) on the left edge with the wire entry facing outward, F2 (furnace) and F1 (module) standing vertically between them, U2 ACS712 under F2, RV1 beside the module's AC pins, the LED dropper (R1 to R4, D1, D2) and the PE and chassis jumpers (SJ1 to SJ3) on the left. |
| Module | x 52 to 140, y 34 to 86 | U1 IRM-90-12, AC pins top left, DC pins right. |
| Bucks | x 52 to 140, y 4 to 24 | 5 V buck (U4, L1, U5, R20) left, 3.3 V buck (U8, L2, U9, R30) right. |
| 12 V branches | x 52 to 140, y 89 to 119 | Blade holders F3, F4, F7 across the top, P-FETs and gate parts below, outputs (J3, J4, XT60 J5) on the bottom edge. |
| 12 V bus | x 142 to 157, y 76 to 113 | R5 shunt, U3, C3, D3 TVS, C4 bulk, D4 LED. |
| Pico | x 158 to 182, y 2 to 56 | U12 vertical with USB on the top edge. |
| Pico support | right strip x 184 to 200, y 12 to 58 | J11 (NTC), J12 (SSR), Q7 drive, divider resistors, D7. |
| Logic taps | x 158 to 200, y 60 to 110 | Four rows (5 V A, 5 V B, 3.3 V A, 3.3 V B): TPS2553, its resistors, and the terminal on the right edge. |
| Corners | all four | M3 holes H1 to H4 (chassis net). |

## Checks run
- Courtyards: no overlaps, nothing within 0.5 mm of the board edge.
- DRC (errors only, default rules): 20 clearance hits, all between adjacent pads of the INA226 MSOP-10 (0.15 mm gap against the 0.2 mm default rule; JLC's minimum is 0.127 mm), so a rule-setting question, not a placement one. No tracks exist yet, so the 283 "unconnected" items are expected.
- 3D render checked for orientation: Pico USB at the top edge, barrier strips open to the left, terminal blocks and XT60 open to their nearest edge.

## Assumptions to verify
- **Terminal wire-entry side.** The CUI footprint has no 3D model, so I assumed the wire entry is the side with the thin front lip and the pin-1 triangle (+y in the footprint), and rotated every DB128V so that side faces the nearest board edge. The XT60PW-F is rotated 180 degrees so the body points at the bottom edge. Check both against the datasheets.
- **Fuse holders.** F3, F4 and F7 are placed horizontally, 22 x 9 mm courtyards. The IRM-90-12 footprint's courtyard (87.6 x 52.6 mm) is taken as-is; its pad positions put AC on the left and DC on the right.
- No creepage slots or isolation cutouts yet. The mains zone is about 10 mm from the nearest low-voltage part, but the module straddles the barrier and U2 (ACS712) has its low-voltage pins facing the rest of the board.
- Only a handful of passives are in their final positions (decoupling caps are next to their ICs but not optimised); this is a starting point for the manual pass.

## Schematic issue found while placing
F3, F4 and F7 were missing from the PCB because their schematic symbols still carry the "exclude from board" flag from when they were virtual fuses. They were added to the PCB by script with the correct symbol paths and nets. To clear the flag in the schematic, open each symbol's properties and untick "Exclude from board", then run Update PCB from Schematic and check that no duplicates appear.
