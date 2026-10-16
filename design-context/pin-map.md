# Pico 2 pin map (revised 2026-10-14)

Source: `datasheets/RP-008299-DS-3-pico-2-datasheet.pdf` (26 usable GPIO: GP0-22 digital, GP26-28 digital or ADC; GP23/24/25/29 are internal). The pin numbers use the standard Pico pinout (the datasheet's Figure 2 is an image; confirm against the KiCad symbol). Logic is 3.3 V only.

Requirement (user, 2026-10-14): self-test and remotely power-cycle every tap except the AC. The user decided on direct GPIOs for now (an I2C expander such as the PCA9535C, LCSC C2652292, is the fallback if more IO is needed), so 25 of the 26 GPIO are used.

## GPIO assignment
| Pico pin | GPIO | Function | Connects to | Notes |
|---|---|---|---|---|
| 1 | GP0 | SENSE 5 V tap A | tap output via 4.7 k / 10 k divider | reads high when the tap output is present |
| 2 | GP1 | SENSE 5 V tap B | same | |
| 4 | GP2 | SENSE 3.3 V tap A | tap output direct, 10 k pulldown | |
| 5 | GP3 | SENSE 3.3 V tap B | same | |
| 6 | GP4 | I2C0 SDA | 3x INA226, 4.7 k pull-up to 3V3 | default Pico I2C0 pins |
| 7 | GP5 | I2C0 SCL | 3x INA226, 4.7 k pull-up to 3V3 | |
| 9 | GP6 | EN 5 V tap A | TPS2553 #1 EN | 10 k pull-up to the AP63203 3.3 V rail, so taps default ON; Pico pulls low to switch off |
| 10 | GP7 | EN 5 V tap B | TPS2553 #2 EN | same |
| 11 | GP8 | EN 3.3 V tap A | TPS2553 #3 EN | same |
| 12 | GP9 | EN 3.3 V tap B | TPS2553 #4 EN | same |
| 14 | GP10 | FAULT 5 V taps | TPS2553 #1 and #2 FAULT, wire-ORed | open-drain, active low, RP2350 internal pull-up |
| 15 | GP11 | FAULT 3.3 V taps | TPS2553 #3 and #4 FAULT, wire-ORed | same |
| 16 | GP12 | EN 12 V tap A | 2N7002 gate of the P-FET switch | 10 k pull-up to the AP63203 rail (default ON); Pico pulls low to switch off |
| 17 | GP13 | EN 12 V tap B | same | |
| 19 | GP14 | EN ESC branch | same | |
| 20 | GP15 | SENSE 12 V tap A | tap output via 33 k / 10 k divider | |
| 21 | GP16 | FAN PWM (25 kHz) | fan header pin 4 | PWM slice 0 ch A; drive open-drain style |
| 22 | GP17 | spare | | PWM slice 0 ch B, keep free (the one spare) |
| 24 | GP18 | SSR control | 2N7002 gate through 1 k (default; SSR on 5 V). SJ1/SJ2 can switch to direct GPIO drive | plain GPIO output, 4.7 k pulldown |
| 25 | GP19 | FAN TACH | fan header pin 3 | 10 k pull-up to 3V3 |
| 26 | GP20 | INA226 ALERT (optional) | 3x ALERT wire-ORed | open-drain, optional |
| 27 | GP21 | SENSE 12 V tap B | tap output via 33 k / 10 k divider | |
| 29 | GP22 | SENSE ESC branch | ESC output via 33 k / 10 k divider | |
| 31 | GP26 / ADC0 | ACS712 output | 4.7 k / 10 k divider | must stay below 3.3 V + 0.3 V |
| 32 | GP27 / ADC1 | NTC module | 10 k pull-up to 3V3(OUT), NTC to AGND | |
| 34 | GP28 / ADC2 | NTC SSR heat sink | via the 2P screw terminal | same divider |

25 of 26 GPIO used; 1 spare (GP17). UART debug is not on a header; use USB and SWD.

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
