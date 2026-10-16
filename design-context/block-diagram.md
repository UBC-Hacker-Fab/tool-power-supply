# Rev 1 block diagram (2026-10-14)

An SVG render is in `block-diagram.svg` (Graphviz source: `block-diagram.dot`, regenerate with `dot -Tsvg block-diagram.dot -o block-diagram.svg`).

Mermaid source (renders on GitHub and in most Markdown viewers). Built from `design-decisions.md`, `bom.md` and `pin-map.md`. Dashed lines are signals, solid lines are power.

```mermaid
flowchart LR
  subgraph MAINS["Mains zone (120 VAC, L / N / PE)"]
    ACIN["AC in\n3P barrier strip"]
    MOV["MOV 14D241K\nL-N"]
    LED_M["Mains LED\n4x 33k + 1N4148W + red LED"]
    F3["3 A Slo-Blo 3AG\nmodule branch"]
    F10["10 A fast-blow 3AG\nfurnace branch"]
    ACS["ACS712-20A\nfurnace current"]
    ACOUT["AC out\n3P barrier strip"]
    IRM["Mean Well IRM-90-12\n12 V / 6.7 A"]
  end

  SSR["Fotek SSR-60 DA\noff-board, own heat sink"]
  FURN["Tube furnace\n<= ~1000 W"]

  ACIN --> MOV
  ACIN -.-> LED_M
  ACIN --> F3 --> IRM
  ACIN --> F10 --> ACS --> ACOUT --> SSR --> FURN

  subgraph BUS["12 V bus"]
    SH12["Shunt 5 mOhm\nINA226 #1 (0x40)"]
    TVS["TVS SMCJ15A\n+ 100 uF bulk cap"]
  end
  IRM --> SH12 --> TVS

  subgraph T12["12 V branches (fuse, then P-FET switch)"]
    B1["3 A blade fuse\nAO4407C"] --> OUT12A["12 V tap A"]
    B2["3 A blade fuse\nAO4407C"] --> OUT12B["12 V tap B"]
    B3["7.5 A blade fuse\nAO4407C"] --> XT60["XT60 female\nESC power (EMAX ESC)"]
    PTC["PTC 500 mA"] --> FAN["Fan header\n4-pin PWM (Noctua NF-A8)"]
  end
  TVS --> B1
  TVS --> B2
  TVS --> B3
  TVS --> PTC

  subgraph R5["5 V rail"]
    BK5["AP63205 buck\n+ INA226 #2 (0x41)"] --> TP1["TPS2553 x2"] --> OUT5["5 V taps A, B"]
  end
  subgraph R33["3.3 V rail"]
    BK33["AP63203 buck\n+ INA226 #3 (0x42)"] --> TP2["TPS2553 x2"] --> OUT33["3.3 V taps A, B"]
  end
  TVS --> BK5
  TVS --> BK33

  subgraph MCU["Raspberry Pi Pico 2"]
    PICO["RP2350\nI2C, 25 GPIO, 3 ADC"]
    SSRSEL["SSR drive\n2N7002 on 5 V (default)\nor direct GPIO (solder jumpers)"]
  end
  BK5 --> SS14["SS14"] --> PICO

  PICO -.->|"I2C"| SH12
  PICO -.->|"I2C"| BK5
  PICO -.->|"I2C"| BK33
  PICO -.->|"EN x4, FAULT x2"| TP1
  PICO -.->|"EN x4, FAULT x2"| TP2
  PICO -.->|"EN x3 via 2N7002"| T12
  PICO -.->|"SENSE x7\n(downstream of switches)"| OUT12A
  PICO -.-> SSRSEL -.-> SSR
  PICO -.->|"PWM, tach"| FAN
  ACS -.->|"ADC0 via divider"| PICO
  NTC1["NTC at the module"] -.->|"ADC1"| PICO
  NTC2["NTC on the SSR heat sink"] -.->|"ADC2"| PICO

  STAR(("Star ground\nsolder jumpers:\nPE, DC GND, ESC,\nlogic, chassis"))
  ACIN -.->|"PE"| STAR
  IRM -.-> STAR
```

## Reading notes
- The IRM-90-12 isolates mains (4 kVAC), so everything right of it is SELV. The ACS712 and the mains LED straddle the barrier and need creepage care in layout.
- No diode between the module and the bus (dropped for rev 1): the ESC runs with Brake OFF and a ramped throttle from its separate controller.
- The AC passthrough (AC in to AC out) is not switched or power-cycled. The SSR switches the heater lead off-board.
- All seven DC taps (5 V x2, 3.3 V x2, 12 V x2, ESC) are switchable (default ON through pull-ups) and each has a downstream presence sense for self-test; per-tap current comes from the per-rail INA226 delta.
