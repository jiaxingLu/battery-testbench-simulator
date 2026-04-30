# Battery Testbench Simulator

Industrial-grade battery testbench simulator for fake BMS/VCU development, CAN message validation, fault injection, and test automation.

## Current Features

- `BMS_Status_1` CAN message encode/decode
- Fake BMS node
- Verifier node
- Config-driven runtime via YAML
- Configurable fault injection
- Structured logging
- Pytest-based validation

## Run

```bash
PYTHONPATH=src python3 -m battery_testbench_sim.main
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

## Fault Injection

Fault injection can override selected BMS status fields after a configured cycle count.

## Architecture


See:

```text
docs/architecture.md
```

The system is structured into:

- Node layer: `FakeBMS`, `Verifier`
- Runtime layer: `Supervisor`
- Infrastructure: CAN, logging, config