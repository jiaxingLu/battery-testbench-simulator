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