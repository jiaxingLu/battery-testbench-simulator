# Project Status

## Current Stable Baseline

Current validated baseline:

```text
c827f44 docs: document latest CSV analysis shortcuts
```

Tagged observability baseline:

```text
v0.1-observability
```

The project currently implements a virtual battery testbench simulator with separated observability layers for runtime events, CAN communication, and physical model traces.

## Architecture Summary

The current data path is:

```text
ScenarioProvider
  ↓
SOC / current trajectory
  ↓
OCV model
  ↓
RCModel
  ↓
pack_voltage_raw = ocv_raw - v_rc_raw
  ↓
raw_trace.csv
  ↓
FakeVCU
  ↓
BMS_Status_1 encode
  ↓
virtual CAN
  ↓
BMS_Status_1 decode
  ↓
Verifier
  ↓
bms_status.csv
```

## Observability Layers

| Layer | File pattern | Purpose |
|---|---|---|
| System event layer | `run_*.log` | Runtime events, warnings, VCU transitions, scenario completion |
| Physical model layer | `*_raw_trace.csv` | OCV, RC polarization, raw pack voltage before CAN quantization |
| CAN communication layer | `*_bms_status.csv` | CAN-decoded BMS status observed by verifier |

The physical layer and communication layer are intentionally separated.

`*_raw_trace.csv` is used for RC / tau analysis.

`*_bms_status.csv` is used for CAN / verifier audit and is not suitable for RC time-constant fitting because voltage is quantized to 0.1 V.

## Verified Commands

Run tests:

```bash
python3 -m pytest
```

Expected current result:

```text
19 passed
```

Run default discharge scenario:

```bash
PYTHONPATH=src python3 -m battery_testbench_sim.main \
  --scenario configs/scenario_discharge.yaml
```

Expected behavior:

```text
Scenario completed
```

Plot latest raw physical trace:

```bash
python3 scripts/plot_bms_csv.py --latest-raw
```

Expected detection:

```text
detected_type = raw_trace
```

Plot latest CAN-decoded BMS status:

```bash
python3 scripts/plot_bms_csv.py --latest-bms
```

Expected detection:

```text
detected_type = bms_status
```

Fit RC tau from latest raw trace:

```bash
python3 scripts/fit_tau.py --latest-raw
```

Expected result:

```text
tau ≈ 9.74786 s
```

Verify CAN-decoded voltage is not observable for tau fitting:

```bash
python3 scripts/fit_tau.py --latest-bms
```

Expected behavior:

```text
Verdict: tau is NOT observable from this CSV.
```

Run default discharge scenario without wall-clock sleep:

```bash
PYTHONPATH=src python3 -m battery_testbench_sim.main \
  --scenario configs/scenario_discharge.yaml \
  --no-sleep
```

Expected behavior:

```text
Scenario completed
```

`--no-sleep` keeps simulated time based on `cycle_time_s` while skipping wall-clock waiting.

## Current Test Coverage

Current tests cover:

- `BMS_Status_1` encode/decode
- virtual CAN send/receive
- Fake BMS behavior
- Fake VCU state transition behavior
- fault injection
- scenario SOC stepping and clamping
- finite rest scenario completion
- verifier decoding
- raw trace tau fitting
- CAN quantization rejection for tau fitting
- CSV type detection for plotting
- supervisor sleep enable/disable behavior

## Recent Checkpoints

```text
c827f44 docs: document latest CSV analysis shortcuts
dd7dde7 feat: add latest CSV shortcuts to analysis scripts
95697f0 test: cover CSV plot type detection
6a5dfeb test: cover tau fitting observability layers
2eb1d27 test: cover finite rest scenario completion
48d6bba docs: document logging and observability layers
52b6636 feat: plot raw trace and CAN status CSVs separately
2eea67f fix: separate raw RC trace for tau fitting
001290a fix: correct RC relaxation model
```

## Current Engineering Meaning

The project has reached a stable observability baseline:

```text
runtime log     → system event audit
bms_status.csv  → CAN communication audit
raw_trace.csv   → physical RC model audit
```

This avoids mixing communication-layer quantized values with physical-layer model values.

## Next Recommended Phase

Next phase:

```text
Phase 4 — Runtime / CLI polish
```

Recommended next tasks:

1. Add an explicit `--max-cycles` runtime guard for bounded manual experiments.
2. Add a small integration test for scenario execution producing both CSV layers.
3. Add optional output directory configuration for logs.
4. Consider a `scripts/run_latest_analysis.sh` helper for one-command scenario + plot + tau audit.

Do not expand model complexity before runtime and integration behavior are locked.