# Pico 2 pin map (revised 2026-10-26)

Source: `datasheets/RP-008299-DS-3-pico-2-datasheet.pdf` (26 usable GPIO: GP0-22 digital, GP26-28 digital or ADC; GP23/24/25/29 are internal). The pin numbers use the standard Pico pinout (the datasheet's Figure 2 is an image; confirm against the KiCad symbol). Logic is 3.3 V only.

Requirement (user, 2026-10-14): self-test and remotely power-cycle every tap except the AC. EN / FAULT use direct GPIOs; the sense inputs went to an I2C expander on 2026-10-22.

## History
- 2026-10-14: first assignment, 25 of 26 GPIO used, SENSE inputs on GP0-3, GP15, GP21, GP22.
- 2026-10-22 (decided 2026-10-21): CAN link and I/O expander (details in `design-decisions.md`, 'Control link, I/O expander, connector and mounting changes'). The 7 SENSE inputs moved to a TCA9534PWR (U12) on the I2C bus (address 0x20, P0 to P6 = 12V_A, 12V_B, ESC, 5V_A, 5V_B, 3V3_A, 3V3_B); GP0 = CAN_TX and GP1 = CAN_RX (can2040 PIO, SN65HVD230 U14).
- **2026-10-26: re-pinned for routing** (user asked for the pin order that makes routing easiest; a targeted edit of `mcu.kicad_sch`, no regeneration, done twice while the lane plan was worked out). The Pico's left socket exits both sides: the nets for the parts south-east of the socket (U14, U8 to U11, Q6) leave eastwards as one B.Cu bundle and peel off one by one, so their pin order north to south has to be the order in which they peel (CAN_TX, CAN_RX, EN 5 V A, FAULT 5 V, EN 5 V B, EN 3.3 V A, FAULT 3.3 V, EN ESC, EN 3.3 V B); the nets for the parts south-west (I2C to U12 / U6 / U7 / U3, EN 12 V A and B to Q4 / Q5) leave westwards in a second bundle whose order has to be SDA, SCL, ALERT, EN 12 V A, EN 12 V B, and the two fan nets (PWM, then TACH, so that PWM peels off into J3 first) run as a pair between the two bundles. The two groups can be interleaved freely on the pins. The seven EN pull-ups (R14 to R16, R24 to R27) sit beside their pins in the PCB. Net names did not change, so nothing in the other sheets changed; only the 14 U13 pad nets did. ERC is identical to before the change.

## GPIO assignment (current)
Left socket (x 68.11 on the board; pin y = 11.94 + 2.54 per pin step, GND pins skipped):

| Pico pin | GPIO | Function | Connects to | Notes |
|---|---|---|---|---|
| 1 | GP0 | CAN_TX | SN65HVD230 U14 pin 1 (D) | can2040 PIO (any pin pair works); east bundle |
| 2 | GP1 | CAN_RX | U14 pin 4 (R) | east bundle |
| 4 | GP2 | EN 5 V tap A | TPS2553 U8 EN | 10 k pull-up R24 to the 3V3_RAIL, so taps default ON; Pico pulls low to switch off; east bundle |
| 5 | GP3 | FAULT 5 V | U8 and U9 FAULT, wire-ORed | open-drain, active low, RP2350 internal pull-up; east bundle |
| 6 | GP4 | I2C0 SDA | U12, U6, U7, U3 | I2C0 SDA (Pico 2 datasheet Figure 2); 4.7 k pull-up R39 to 3V3_MCU; west bundle |
| 7 | GP5 | I2C0 SCL | same | I2C0 SCL; R38; west bundle |
| 9 | GP6 | INA226 ALERT | 3x ALERT wire-ORed | open-drain, optional; west bundle |
| 10 | GP7 | EN 12 V tap A | 2N7002 gate Q4 | pull-up R14 (default ON); west bundle |
| 11 | GP8 | EN 12 V tap B | 2N7002 gate Q5 | pull-up R15; west bundle |
| 12 | GP9 | EN 5 V tap B | U9 EN | pull-up R25; east bundle |
| 14 | GP10 | EN 3.3 V tap A | U10 EN | pull-up R26; east bundle |
| 15 | GP11 | FAULT 3.3 V | U10 and U11 FAULT, wire-ORed | same as the 5 V one; east bundle |
| 16 | GP12 | EN ESC branch | 2N7002 gate Q6 | pull-up R16 (default ON); east bundle |
| 17 | GP13 | FAN PWM (25 kHz) | fan header pin 4 | PWM slice 6 ch B; a different slice from the tach, so both run at once; drive open-drain style; fan pair (own lanes down the middle) |
| 19 | GP14 | EN 3.3 V tap B | U11 EN | pull-up R27; east bundle |
| 20 | GP15 | FAN TACH | fan header pin 3 (J3) | odd GPIO = PWM channel B, the only one that can count pulses (slice 7 input mode); 10 k pull-up R6 to 3V3_MCU; fan pair |

Right socket (x 85.89):

| Pico pin | GPIO | Function | Connects to | Notes |
|---|---|---|---|---|
| 21, 22, 25, 26, 27, 29 | GP16, GP17, GP19, GP20, GP21, GP22 | spare | no-connect flags | six spare GPIO, all on the right socket |
| 24 | GP18 | SSR control | 2N7002 Q7 gate through R42 (default; SSR on 5 V). SJ5 / SJ6 can switch to direct GPIO drive | plain GPIO output, 4.7 k pulldown |
| 31 | GP26 / ADC0 | ACS712 output | R44 / R45 divider | must stay below 3.3 V + 0.3 V |
| 32 | GP27 / ADC1 | NTC module (TH1) | R46 pull-up, TH1 to AGND | |
| 34 | GP28 / ADC2 | NTC SSR heat sink | via J11, R47 pull-up | same divider |

20 of 26 GPIO used, 6 spare (GP16, GP17, GP19, GP20, GP21, GP22). GP23, GP24, GP25 and GP29 are used inside the Pico 2 (SMPS mode, VBUS sense, LED, VSYS/3) and are not on the header. UART debug is not on a header; use USB and SWD.

**Datasheet cross-check (`datasheets/RP-008299-DS-3-pico-2-datasheet.pdf`, Figure 2):** GP4 / GP5 are I2C0 SDA / SCL; GP26 / GP27 / GP28 are ADC0 / 1 / 2; everything else used is a plain GPIO / PIO / PWM pin (the board datasheet does not list the PWM slice map; slice = GPIO / 2 mod 8, channel A on even and B on odd GPIO, from the RP2350 datasheet, which I have not re-read). GP2 / GP3 would have been I2C1 SDA / SCL; nothing is on I2C1.

## Sense circuits (self-test)
- Taken downstream of the tap's fuse and switch, so a blown fuse, failed switch or shorted tap reads as not present.
- **12 V taps and ESC:** 33 k (top, C4216) and 10 k (bottom, C25804) give a ratio of 0.23: 12 V reads 2.78 V and 11.5 V reads 2.67 V, above the RP2350 VIH of 0.7 x 3.3 V = 2.31 V. During a TVS-clamp event (24.4 V) the pin would see 5.7 V; the 7.7 k source impedance limits injected current to about 0.3 mA through the pad protection diode. This depends on the RP2350's input limits, which I have not verified.
- **5 V taps:** 4.7 k and 10 k (ratio 0.68): 5 V reads 3.4 V, which is inside the IOVDD + 0.3 V limit. Same values as the ACS712 divider.
- **3.3 V taps:** connected directly with a 10 k pulldown so the line reads low when the tap is off.
- Per-tap current: toggle the tap and read the change in the per-rail INA226.

## 12 V branch switch (x3: 12 V taps A and B, ESC)
Fuse, then P-FET AO4407C (LCSC C469397) high side, then the output. The P-FET gate has a 10 k pull-up to +12 V (keeps it off) and a 2N7002 pulling it low; the 2N7002 gate has a 10 k pull-up to the AP63203 rail (default ON) and the Pico GPIO pulls it low to switch off. About 0.3 W of loss at 5 A in the ESC branch. Check the gate clamp against the 25 V Vgs limit during a TVS-clamp event.

## Power and other pins
- **VSYS (39):** fed from the 5 V rail through the SS14 Schottky (datasheet Figure 8 power OR-ing). VBUS (40) is left to USB.
- **3V3(OUT) (36):** Pico's own 3.3 V, keep the load under 300 mA. Use it for the INA226 VS pins, the I2C pull-ups, the NTC divider tops and the tach pull-up. It is separate from the AP63203 3.3 V tap rail.
- **ADC_VREF (35), AGND (33):** ADC reference is the Pico's own filtered 3.3 V (201 ohm into 2.2 uF), so the ADC accuracy is limited; return the ACS712 and NTC divider bottoms to AGND, which ties to digital GND at the Pico.
- **3V3_EN (37), RUN (30):** leave open (RUN has an internal pull-up).

## INA226 addresses (Table 6-2 of `datasheets/ina226.pdf`)
| Rail | A1 | A0 | Address |
|---|---|---|---|
| 12 V | GND | GND | 0x40 |
| 5 V | GND | VS | 0x41 |
| 3.3 V | GND | SDA | 0x42 |

## Notes
- ADC-capable GPIO26-29 have a reverse diode to the 3V3 rail, so inputs must not exceed IOVDD plus about 0.3 V and leak into the rail if the RP2350 is unpowered. The ACS712 divider tops out at 3.06 V even at 20 A, which is safe.
- The SSR pulldown is 4.7 k rather than 10 k out of caution about RP2350 pull-down behavior on floating inputs (I recall an erratum on this and have not verified it; check the RP2350 datasheet).
