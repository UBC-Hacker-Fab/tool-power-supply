# Schematic generator (first draft, 2026-10-14)

Generates the KiCad 10 schematic in `tool-power-supply-v1/` (root + 4 sub-sheets: mains, bus12v, rails, mcu) from the component and net tables in `design.py`.

```sh
python3 tools/schematic/build.py            # writes tool-power-supply-v1/*.kicad_sch
python3 tools/schematic/build.py /tmp/out   # write somewhere else
```

- Needs Python 3.9+, KiCad 10 installed at `/Applications/KiCad/KiCad.app` (stock symbol libraries) and the `hackerfab-kicadlibs` repo at `~/Documents/Github/hackerfab-kicadlibs` (HF_* symbols). Paths are hard-coded in `libs.py`.
- Every pin is connected with a short wire and a global label (or a GND symbol), so nets are defined by name in `design.py`. All sheets share one global net namespace.
- **Re-running overwrites any manual edits to the schematic.** Treat this as a one-time bootstrap: once you start editing in KiCad, stop using the generator.
- Check a run with `kicad-cli sch erc --severity-all` and `kicad-cli sch export netlist`.
- Design context: `design-context/` (design-decisions.md, bom.md, pin-map.md, block-diagram.md).

## Status

The first generated draft was opened and saved in KiCad on 2026-10-14, so the files in `tool-power-supply-v1/` are now KiCad-native. KiCad's first load reported "An error was found ... automatically fixed" because the generated root schematic had a uuid that did not match the root sheet uuid stored in `tool-power-supply-v1.kicad_pro` (`sheets`). The generator now reads the root and sub-sheet uuids from that file, so a regenerated schematic matches the project. Still: do not regenerate over a schematic you have edited in KiCad.
