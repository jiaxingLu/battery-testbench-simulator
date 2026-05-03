# Battery Testbench Simulator

Industrial-grade battery testbench simulator for fake BMS/VCU development, CAN message validation, fault injection, physical trace inspection, and test automation.

## Current Features

- `BMS_Status_1` CAN message encode/decode
- Fake BMS node
- Fake VCU node
- Verifier node
- Config-driven runtime via YAML
- Configurable fault injection
- Structured runtime logging
- CSV logging for CAN-decoded BMS status
- Raw physical trace logging before CAN quantization
- CSV plotting utility for communication and physical trace data
- RC relaxation time fitting from raw RC state
- Pytest-based validation

## Run

Run the default scenario:

```bash
PYTHONPATH=src python3 -m battery_testbench_sim.main
```

Run an explicit scenario:

```bash
PYTHONPATH=src python3 -m battery_testbench_sim.main \
  --scenario configs/scenario_discharge.yaml
```

## Test

```bash
python3 -m pytest
```

## Configuration

The simulator loads BMS parameters from:

```text
configs/bms_default.yaml
```

Scenario behavior can be configured through files such as:

```text
configs/scenario_discharge.yaml
configs/scenario_soc_drop_fault.yaml
```

## Fault Injection

Fault injection can override selected BMS status fields after a configured cycle count.

## Output Files and Observability Layers

Each simulator run can generate three output layers under `logs/`.

| File pattern | Layer | Purpose |
|---|---|---|
| `run_*.log` | System event layer | Runtime events, VCU state transitions, warnings, scenario completion |
| `*_bms_status.csv` | CAN / communication layer | CAN-decoded BMS status used for verifier and message-level audit |
| `*_raw_trace.csv` | Physical model layer | Raw internal model values before CAN quantization, used for RC and tau analysis |

The CAN-decoded BMS status CSV is intentionally not used for RC time-constant fitting.

The BMS status message encodes pack voltage with 0.1 V resolution. Small voltage relaxation signals can therefore be quantized into only one or two voltage levels. In that case, the RC time constant is not observable from `*_bms_status.csv`.

For physical RC analysis, use `*_raw_trace.csv`, which contains:

```text
cycle
time_s
soc
pack_current
ocv_raw
v_rc_raw
pack_voltage_raw
state
fault_level
```

The current RC model uses:

```text
R = 0.05
C = 200.0
tau = R * C = 10 s
```

Because the RC model is updated in discrete time, fitting the decay of `v_rc_raw` gives the equivalent discrete-time decay constant. With the current time step, this is approximately:

```text
tau ≈ 9.75 s
```

This is expected.

## Typical Analysis Workflow

Run the default discharge scenario:

```bash
PYTHONPATH=src python3 -m battery_testbench_sim.main \
  --scenario configs/scenario_discharge.yaml
```

Plot the latest raw physical trace:

```bash
raw_csv=$(ls -t logs/*_raw_trace.csv | head -n 1)
python3 scripts/plot_bms_csv.py "$raw_csv"
```

Plot the latest CAN-decoded BMS status:

```bash
can_csv=$(ls -t logs/*_bms_status.csv | head -n 1)
python3 scripts/plot_bms_csv.py "$can_csv"
```

Fit the RC relaxation time from the raw trace:

```bash
raw_csv=$(ls -t logs/*_raw_trace.csv | head -n 1)
python3 scripts/fit_tau.py "$raw_csv"
```

Do not use `*_bms_status.csv` for tau fitting. The fitting script should reject it as not observable when the voltage recovery is dominated by CAN quantization.

## Architecture

See:

```text
docs/architecture.md
```

The system is structured into:

- Provider layer: `StaticBMSDataProvider`, `ScenarioBMSDataProvider`
- Model layer: OCV model, RC polarization model
- Node layer: `FakeBMS`, `FakeVCU`, `Verifier`
- Runtime layer: `Supervisor`
- Infrastructure layer: virtual CAN, CSV logging, structured logging, config loading