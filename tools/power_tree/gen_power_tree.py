#!/usr/bin/env python3
"""Generate design-context/power-tree.md: power tree plus per-rail and per-tap consumption.

Structure (rails, regulators, fuses, switches, shunts, rail voltages) is read live from the KiCad
schematic through the kicad-happy `kicad` skill's analyze_schematic.py. What a schematic cannot
say (off-board loads, datasheet currents, efficiencies) comes from power_model.json, and every ref
in that file is checked against the schematic so a stale model fails loudly.

    python3 tools/power_tree/gen_power_tree.py            # writes design-context/power-tree.md
    python3 tools/power_tree/gen_power_tree.py --check    # exit 1 if the committed file is out of date

The skill needs Python 3.10+; this script itself runs on 3.9+. Override the skill location with
KICAD_HAPPY_SKILL=/path/to/skills/kicad.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SCH = os.path.join(ROOT, 'tool-power-supply-v1', 'tool-power-supply-v1.kicad_sch')
OUT = os.path.join(ROOT, 'design-context', 'power-tree.md')
MODEL = os.path.join(HERE, 'power_model.json')
SKILL = os.environ.get('KICAD_HAPPY_SKILL', os.path.expanduser('~/.claude/skills/kicad'))


def find_python():
    for name in (sys.executable, 'python3.13', 'python3.12', 'python3.11', 'python3.10', '/opt/homebrew/bin/python3.13', '/opt/homebrew/bin/python3.12', 'python3'):
        exe = shutil.which(name) or (name if os.path.exists(name) else None)
        if not exe:
            continue
        r = subprocess.run([exe, '-c', 'import sys;print(sys.version_info>=(3,10))'], capture_output=True, text=True)
        if r.stdout.strip() == 'True':
            return exe
    sys.exit('need Python 3.10+ for the kicad-happy analyzer')


def analyze():
    script = os.path.join(SKILL, 'scripts', 'analyze_schematic.py')
    if not os.path.exists(script):
        sys.exit(f'kicad-happy skill not found at {SKILL} (set KICAD_HAPPY_SKILL)')
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'a.json')
        r = subprocess.run([find_python(), script, SCH, '--output', out], capture_output=True, text=True)
        if not os.path.exists(out):
            sys.exit('analyzer failed:\n' + r.stdout[-800:] + r.stderr[-800:])
        return json.load(open(out))


def fmt_a(x):
    return f'{x:.3f}' if x < 0.1 else f'{x:.2f}'


def parse_ohms(v):
    m = re.match(r'\s*([0-9.]+)\s*([kKmM]?)', v or '')
    if not m:
        return None
    x = float(m.group(1)); u = m.group(2).lower()
    return x * (1e3 if u == 'k' else 1e6 if u == 'm' else 1)


def ilim_limits(an, comp, tps_ref):
    """TPS2553 current-limit window (A) from the resistor on its ILIM pin, per the datasheet equations."""
    for n in an['nets'].values():
        pins = n['pins']
        if any(p['component'] == tps_ref and p['pin_name'] == 'ILIM' for p in pins):
            for p in pins:
                c = comp.get(p['component'])
                if c and p['component'] != tps_ref and p['component'].startswith('R'):
                    r = parse_ohms(c['value'])
                    if r:
                        k = r / 1e3
                        return p['component'], c['value'], 25230.0 / k ** 1.016 / 1000.0, 22980.0 / k ** 0.94 / 1000.0
    sys.exit(f'{tps_ref}: no ILIM resistor found in the schematic')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    model = json.load(open(MODEL))
    an = analyze()
    comp = {c['reference']: c for c in an['components']}
    problems = []

    def val(ref, expect=None):
        c = comp.get(ref)
        if c is None:
            problems.append(f'{ref}: not in the schematic')
            return '?'
        if expect and expect.lower() not in (c['value'] or '').lower():
            problems.append(f'{ref}: value {c["value"]!r} does not contain {expect!r}')
        return c['value']

    ac = model['ac']
    val(ac['input']['ref'], ac['input']['expect']); val(ac['module']['ref'], ac['module']['expect'])
    mod_fuse = val(ac['module_fuse']['ref'], ac['module_fuse']['expect'])
    fur = ac['furnace']
    fur_fuse = val(fur['fuse']['ref'], fur['fuse']['expect']); val(fur['sensor']['ref'], fur['sensor']['expect']); val(fur['output']['ref'], fur['output']['expect'])
    rails = {r['id']: r for r in model['rails']}
    for r in model['rails']:
        for k in ('regulator', 'monitor'):
            if k in r:
                val(r[k]['ref'], r[k].get('expect'))
        for s in r.get('series', []) + r.get('extra', []):
            val(s['ref'], s.get('expect'))
    loads = model['loads']
    for l in loads:
        if 'connector' in l:
            val(l['connector']['ref'], l['connector']['expect'])
        for c in l.get('chain', []):
            val(c['ref'], c['expect'])
        for ref in l.get('refs', []):
            val(ref)
    # rail nets must exist in the schematic (any hierarchy prefix)
    nets = set(an['nets'])
    for rid in rails:
        if not any(n == rid or n.endswith('/' + rid) for n in nets):
            problems.append(f'rail net {rid} not found in the schematic')
    if problems:
        sys.exit('power_model.json is out of sync with the schematic:\n  ' + '\n  '.join(problems))

    # ---------- current limits and headroom
    min_head = model.get('min_headroom', 0.2)
    for l in loads:
        if l['kind'] != 'tap':
            continue
        if 'ilim_of' in l:
            l['ilim_ref'], l['ilim_val'], l['limit_min_A'], l['limit_max_A'] = ilim_limits(an, comp, l['ilim_of'])
            l['limit_note'] = f'TPS2553 ILIM {l["ilim_ref"]} {l["ilim_val"]}: {l["limit_min_A"]:.2f}-{l["limit_max_A"]:.2f} A'
        else:
            l['limit_min_A'] = l['limit_max_A'] = l['limit_A']
        l['headroom'] = l['limit_min_A'] / l['peak_A'] - 1.0
        l['max_peak_A'] = l['limit_min_A'] / (1.0 + min_head)

    # ---------- numbers
    def level_of(sc, l):
        lv = sc['overrides'].get(l['id'])
        if lv is None:
            lv = sc['kind_levels'].get(l['kind'], sc['default'])
        return lv

    def cur(l, lv):
        if lv == 'limit':
            return l.get('limit_max_A', l['peak_A'])
        return {'off': 0.0, 'nominal': l['nominal_A'], 'peak': l['peak_A']}[lv]

    def rail_loads(sc):
        out = {}
        for rid in rails:
            out[rid] = sum(cur(l, level_of(sc, l)) for l in loads if l['rail'] == rid)
        return out

    def solve(sc):
        """Return per-rail output current and the resulting current drawn from the parent."""
        direct = rail_loads(sc)
        i = dict(direct)
        # 3V3_MCU is made from the 5 V rail by the Pico's converter
        reg = rails['3V3_MCU']['regulator']
        i['5V_RAIL'] += i['3V3_MCU'] * 3.3 / 5.0 / reg['eff']
        for rid in ('5V_RAIL', '3V3_RAIL'):
            r = rails[rid]
            i['12V_BUS'] += i[rid] * r['v'] / 12.0 / r['regulator']['eff']
        return direct, i

    md = []
    A = md.append
    sch_bytes = open(SCH, 'rb').read()
    # the sub-sheets are part of the design too
    h = hashlib.sha256(sch_bytes)
    for n in ('mains', 'bus12v', 'rails', 'mcu'):
        p = os.path.join(os.path.dirname(SCH), n + '.kicad_sch')
        if os.path.exists(p):
            h.update(open(p, 'rb').read())
    try:
        commit = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(['git', '-C', ROOT, 'status', '--porcelain', '--', 'tool-power-supply-v1'], capture_output=True, text=True).stdout.strip())
    except Exception:
        commit, dirty = '?', False

    A('# Power tree and power consumption')
    A('')
    A('> Generated by `tools/power_tree/gen_power_tree.py` from the KiCad schematic (via the kicad-happy `kicad` skill) and `tools/power_tree/power_model.json`. '
      'Do not edit by hand; regenerate with `python3 tools/power_tree/gen_power_tree.py`.')
    A('')
    A(f'- Schematic fingerprint: `{h.hexdigest()[:12]}` (git `{commit}`{", uncommitted schematic changes" if dirty else ""}); analyzer: kicad-happy `analyze_schematic.py`, schema {an.get("schema_version", "?")}')
    A('- The schematic supplies structure and part values. Currents for off-board loads are inputs from `power_model.json`, each with its source; entries marked ASSUMPTION or UNVERIFIED are not from a datasheet in this repo.')
    A('')

    # ---------- tree
    A('## Power tree')
    A('')
    A('```')
    A(f'{ac["voltage_V"]} VAC in ({val(ac["input"]["ref"])}, {ac["input"]["ref"]})')
    A(f'|-- {fur["fuse"]["ref"]} {fur_fuse} -> {fur["sensor"]["ref"]} current sense -> AC out ({fur["output"]["ref"]}) -> external SSR -> furnace (<= {fur["max_W"]} W, {fur["max_W"] / ac["voltage_V"]:.1f} A)')
    m = ac['module']
    A(f'`-- {ac["module_fuse"]["ref"]} {mod_fuse} -> {m["ref"]} {val(m["ref"])}  [{m["cont_A"]} A continuous / {m["peak_A"]} A for {m["peak_s"]} s, {m["eff"] * 100:.0f}% efficient]')
    A('    `-- 12V_MOD')
    r12 = rails['12V_BUS']
    ser = ', '.join(f'{s["ref"]} {val(s["ref"])}' for s in r12['series'])
    ext = ', '.join(f'{s["ref"]} {s.get("note", val(s["ref"]))}' for s in r12.get('extra', []))
    A(f'        `-- {ser}, monitor {r12["monitor"]["ref"]} INA226 @{r12["monitor"]["addr"]}')
    A(f'            12V_BUS (12 V; {ext})')

    def tap_line(l, prefix):
        chain = ' -> '.join(f'{c["ref"]} {val(c["ref"])}' for c in l.get('chain', []))
        return f'{prefix}{chain} -> {l["connector"]["ref"]} {l["name"]}   nominal {fmt_a(l["nominal_A"])} A / peak {fmt_a(l["peak_A"])} A (limit {fmt_a(l["limit_min_A"])} A min: {l["limit_note"]})'

    branches = [l for l in loads if l['kind'] == 'tap' and l['rail'] == '12V_BUS']
    sub = [('5V_RAIL', rails['5V_RAIL']), ('3V3_RAIL', rails['3V3_RAIL'])]
    items = [('tap', l) for l in branches] + [('reg', s) for s in sub]
    for idx, (kind, it) in enumerate(items):
        last = idx == len(items) - 1
        b = '`-- ' if last else '|-- '
        cont = '    ' if last else '|   '
        base = '            '
        if kind == 'tap':
            A(tap_line(it, base + b))
        else:
            rid, r = it
            reg = r['regulator']
            A(f'{base}{b}{reg["ref"]} {val(reg["ref"])} -> {rid} ({r["v"]:g} V, {reg["cap_A"]:g} A, {reg["eff"] * 100:.0f}% assumed), {r["series"][0]["ref"]} {val(r["series"][0]["ref"])}, monitor {r["monitor"]["ref"]} INA226 @{r["monitor"]["addr"]}')
            taps = [l for l in loads if l['kind'] == 'tap' and l['rail'] == rid]
            for j, l in enumerate(taps):
                A(tap_line(l, base + cont + ('`-- ' if j == len(taps) - 1 and rid != '5V_RAIL' else '|-- ')))
            if rid == '5V_RAIL':
                p = rails['3V3_MCU']
                A(f'{base}{cont}`-- {p["series"][0]["ref"]} {val(p["series"][0]["ref"])} -> VSYS -> {p["regulator"]["ref"]} {val(p["regulator"]["ref"])} -> 3V3(OUT) 3V3_MCU (limit {p["regulator"]["cap_A"]:g} A)')
    A('```')
    A('')

    # ---------- taps
    A('## Consumption per tap')
    A('')
    A(f'Headroom is the minimum guaranteed limit over the peak demand, and must be at least {min_head * 100:.0f}% (`min_headroom` in `power_model.json`). For TPS2553 taps the limit window comes from the ILIM resistor in the schematic. Peak demand is what the tap is expected to draw; the limit is what protects it, so the limit has to sit above the peak.')
    A('')
    A(f'| Tap | Rail | Path | Nominal (A) | Peak demand (A) | Limit min-max (A) | Headroom | Max peak for {min_head * 100:.0f}% (A) | Nominal (W) | Peak (W) | Check |')
    A('|---|---|---|---|---|---|---|---|---|---|---|')
    failed = []
    for l in [x for x in loads if x['kind'] == 'tap']:
        v = rails[l['rail']]['v']
        path = ' > '.join(c['ref'] for c in l.get('chain', [])) + f' > {l["connector"]["ref"]}'
        ok = l['headroom'] >= min_head - 1e-9
        if not ok:
            failed.append(l['name'])
        lim = fmt_a(l['limit_min_A']) if l['limit_min_A'] == l['limit_max_A'] else f'{fmt_a(l["limit_min_A"])}-{fmt_a(l["limit_max_A"])}'
        A(f'| {l["name"]} | {l["rail"]} | {path} | {fmt_a(l["nominal_A"])} | {fmt_a(l["peak_A"])} | {lim} ({l["limit_note"]}) | {l["headroom"] * 100:.0f}% | {fmt_a(l["max_peak_A"])} | {l["nominal_A"] * v:.2f} | {l["peak_A"] * v:.2f} | {"ok" if ok else "BELOW " + format(min_head * 100, ".0f") + "%"} |')
    A('')
    A('Sources:')
    for l in [x for x in loads if x['kind'] == 'tap']:
        A(f'- {l["name"]}: {l["source"]}')
    A('')

    # ---------- onboard
    A('## On-board overhead (not tied to a tap)')
    A('')
    A('| Load | Rail | Nominal (mA) | Peak (mA) |')
    A('|---|---|---|---|')
    for l in [x for x in loads if x['kind'] == 'onboard']:
        A(f'| {l["name"]} ({", ".join(l["refs"])}) | {l["rail"]} | {l["nominal_A"] * 1000:.1f} | {l["peak_A"] * 1000:.1f} |')
    A('')
    A('Sources:')
    for l in [x for x in loads if x['kind'] == 'onboard']:
        A(f'- {l["name"]}: {l["source"]}')
    A('')

    # ---------- per rail per scenario
    A('## Consumption per rail')
    A('')
    A('Output current of each rail (taps plus on-board loads), and the 12 V module output current that results after regulator losses. The 5 V rail includes what the Pico draws through VSYS and the 3V3(OUT) loads reflected through the Pico converter.')
    A('')
    scs = model['scenarios']
    head = '| Rail | Capacity | ' + ' | '.join(s['name'] for s in scs) + ' |'
    A(head); A('|' + '---|' * (2 + len(scs)))
    solved = {s['id']: solve(s) for s in scs}
    caps = {'12V_BUS': f'{m["cont_A"]} A cont. / {m["peak_A"]} A peak (module)'}
    for rid in ('5V_RAIL', '3V3_RAIL', '3V3_MCU'):
        caps[rid] = f'{rails[rid]["regulator"]["cap_A"]:g} A ({rails[rid]["regulator"]["ref"]})'
    for rid in ('12V_BUS', '5V_RAIL', '3V3_RAIL', '3V3_MCU'):
        cells = []
        for s in scs:
            d, i = solved[s['id']]
            amps = i[rid]
            cells.append(f'{fmt_a(amps)} A ({amps * rails[rid]["v"]:.1f} W)')
        A(f'| {rid} ({rails[rid]["v"]:g} V) | {caps[rid]} | ' + ' | '.join(cells) + ' |')
    A('')

    # ---------- shunt drop at the INA226 input
    fs_mv = model.get('ina226_fs_mV', 81.92)
    A('## Shunt voltage drop (INA226 input)')
    A('')
    A(f'dV = I x R for the current through each rail shunt. The INA226 shunt input range is +-{fs_mv} mV (2.5 uV per bit), so a shunt is usable up to {fs_mv} mV / R. The same numbers are written on the schematic next to each shunt.')
    A('')
    A('| Shunt | R | Rail | ' + ' | '.join(s['name'] for s in scs) + ' | At the rail limit | INA226 full scale |')
    A('|' + '---|' * (3 + len(scs) + 2))
    for rid in ('12V_BUS', '5V_RAIL', '3V3_RAIL'):
        for s_ in rails[rid].get('series', []):
            if not s_.get('shunt'):
                continue
            rv = comp[s_['ref']]['value']
            mm = re.match(r'([0-9.]+)m', rv)
            ohm = float(mm.group(1)) / 1000.0
            cells = []
            for s in scs:
                d, i = solved[s['id']]
                cells.append(f'{i[rid]:.3g} A: {i[rid] * ohm * 1000:.1f} mV')
            lim = m['cont_A'] if rid == '12V_BUS' else rails[rid]['regulator']['cap_A']
            limtxt = f'{lim:g} A: {lim * ohm * 1000:.1f} mV, {lim * lim * ohm:.2f} W'
            if rid == '12V_BUS':
                limtxt += f' ({m["peak_A"]} A for 10 s: {m["peak_A"] * ohm * 1000:.1f} mV)'
            A(f'| {s_["ref"]} | {rv} ({ohm * 1000:g} mOhm) | {rid} | ' + ' | '.join(cells) + f' | {limtxt} | {fs_mv / 1000 / ohm:.1f} A |')
    A('')

    A('## Module budget')
    A('')
    A('| Scenario | 12 V output | Module continuous limit | Module peak limit | AC input power | AC input current | Module fuse '
      + f'{ac["module_fuse"]["ref"]} {mod_fuse} |')
    A('|---|---|---|---|---|---|---|')
    verdicts = []
    for s in scs:
        d, i = solved[s['id']]
        a = i['12V_BUS']
        pw = a * 12.0
        pin = pw / m['eff']
        iac = pin / ac['voltage_V']
        cont = a / m['cont_A'] * 100
        peak = a / m['peak_A'] * 100
        status = 'OK' if a <= m['cont_A'] else ('exceeds continuous, within 10 s peak' if a <= m['peak_A'] else 'EXCEEDS PEAK')
        verdicts.append((s, status))
        A(f'| {s["name"]} | {fmt_a(a)} A / {pw:.1f} W | {cont:.0f}% of {m["cont_A"]} A | {peak:.0f}% of {m["peak_A"]} A, {status} | {pin:.1f} W | {iac:.2f} A | {iac / 3.0 * 100:.0f}% of 3 A |')
    A('')
    A('AC input current is real power divided by 120 V and ignores power factor, so it is optimistic; the 3 A time-lag fuse is meant to ride through the module inrush, not to be run near its rating.')
    A('')
    A('## Furnace branch (separate from the module)')
    A('')
    ia = fur['max_W'] / ac['voltage_V']
    A(f'- Heater limit {fur["max_W"]} W at {ac["voltage_V"]} VAC is {ia:.1f} A; fuse {fur["fuse"]["ref"]} {fur_fuse} is loaded to {ia / 10 * 100:.0f}% of its rating. Source: {fur["source"]}.')
    A(f'- This current never touches the DC rails; {fur["sensor"]["ref"]} (ACS712-20A) measures it and the SSR is external.')
    A('')

    # ---------- kicad-happy crosscheck
    A('## kicad-happy cross-check')
    A('')
    A('What the analyzer detected on its own, for comparison with the model above.')
    A('')
    regs = [f for f in an['findings'] if f.get('detector') == 'detect_power_regulators']
    A('| Regulator | Topology | Input rail | Output rail | Output caps |')
    A('|---|---|---|---|---|')
    for f in regs:
        caps_s = ', '.join(f'{c["ref"]} {c["value"]}' for c in f.get('output_capacitors', []))
        out_rail = f['output_rail']
        note = ' (net between inductor and shunt, unnamed in the schematic)' if out_rail.startswith('__unnamed') else ''
        A(f'| {f["ref"]} {f["value"]} | {f["topology"]} | {f["input_rail"]} | {out_rail}{note} | {caps_s} |')
    A('')
    pb = an.get('power_budget', {}).get('rails', {})
    A('The analyzer\'s own power budget only counts on-board IC quiescent estimates (a flat 5 to 10 mA per IC). It cannot see off-board tap loads, so it is shown here for reference and is not used above:')
    A('')
    A('| Rail | ICs counted | Estimated load (mA) |')
    A('|---|---|---|')
    for rid, d in pb.items():
        ics = ', '.join(x['ref'] for x in d.get('ics', [])) or '-'
        A(f'| {rid} | {ics} | {d.get("estimated_load_mA", 0)} |')
    A('')
    A('Known analyzer artifacts on this design (not design errors):')
    A('')
    rs = [f for f in an['findings'] if f.get('rule_id') == 'RS-001']
    vm = [f for f in an['findings'] if f.get('rule_id') == 'VM-001']
    rs_nets = sorted({n.split('/')[-1] for f in rs for n in f['nets']})
    A(f'- RS-001 "no declared source" on {", ".join(rs_nets) or "no nets"}: the analyzer found no power-output pin or PWR_FLAG driving it, so it cannot trace the rail back to the {ac["module"]["ref"]} module.')
    vm_nets = sorted({n for f in vm for n in f['nets']})
    A(f'- {len(vm)} VM-001 "voltage domain crossing" errors on {", ".join("`" + n + "`" for n in vm_nets) or "no nets"}. These look like artifacts: the analyzer takes a net\'s voltage from its name (so `EN.5V_A` and `SENSE.12V_A` read as 5 V and 12 V although they are 3.3 V logic), and from the rail an INA226 is attached to (its Vbus and Vin pins sit on the monitored rail while its logic runs from 3V3(OUT)). Renaming the bus members (for example `EN.TAP5A`) would remove the first kind.')
    A('')
    open_path = OUT
    text = '\n'.join(md) + '\n'
    if args.check:
        old = open(open_path).read() if os.path.exists(open_path) else ''
        strip = lambda t: re.sub(r'- Schematic fingerprint:.*\n', '', t)
        if strip(old) != strip(text):
            print('power-tree.md is out of date; run tools/power_tree/gen_power_tree.py')
            sys.exit(1)
        print('power-tree.md is up to date')
        return
    open(open_path, 'w').write(text)
    print('wrote', os.path.relpath(open_path, ROOT))
    for s, st in verdicts:
        print(f'  {s["id"]}: {st}')
    for n in failed:
        print(f'  headroom below {min_head * 100:.0f}%: {n}')


if __name__ == '__main__':
    main()
