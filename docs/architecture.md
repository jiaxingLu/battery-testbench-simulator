# Architecture Overview

## System Structure

The system follows a layered architecture:

```text
+------------------------------------------------+
|                 Runtime Layer                  |
|              Supervisor loop                   |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
|                 Provider Layer                 |
|  StaticBMSDataProvider / ScenarioBMSDataProvider |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
|                  Model Layer                   |
|          OCV model / RC polarization model     |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
|                   Node Layer                   |
|             FakeBMS / FakeVCU / Verifier       |
+------------------------------------------------+
                       |
                       v
+------------------------------------------------+
|              Infrastructure Layer              |
|          Virtual CAN / CSV / Logging / Config  |
+------------------------------------------------+
```

## Runtime Data Flow

```text
ScenarioProvider
   ↓ SOC / current trajectory
OCV model
   ↓ ocv_raw
RCModel
   ↓ v_rc_raw
pack_voltage_raw = ocv_raw - v_rc_raw
   ↓
raw_trace.csv
   ↓
FakeVCU
   ↓ state / fault processing
Encoder: BMS_Status_1
   ↓ CAN payload bytes
Virtual CAN bus
   ↓ received CAN frame
Verifier
   ↓ decode + structured log
bms_status.csv
```

## Data and Observability Layers

The simulator separates physical model observability from CAN communication observability.

| Output file | Layer | Purpose |
|---|---|---|
| `run_*.log` | System event layer | Runtime events, warnings, VCU transitions, scenario completion |
| `*_raw_trace.csv` | Physical model layer | Internal model variables before CAN quantization |
| `*_bms_status.csv` | CAN / communication layer | CAN-decoded BMS status observed by the verifier |

### Physical Model Layer

`*_raw_trace.csv` records internal model variables before CAN encoding:

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

This layer is used for:

- RC model sanity checks
- polarization trace inspection
- relaxation-time fitting from `v_rc_raw`
- physical model debugging

The physical voltage relation is:

```text
pack_voltage_raw = ocv_raw - v_rc_raw
```

For discharge:

```text
pack_current < 0
v_rc_raw > 0
pack_voltage_raw < ocv_raw
```

### CAN Communication Layer

`*_bms_status.csv` records the decoded CAN message observed by the verifier:

```text
timestamp
signal
pack_voltage
pack_current
soc
state
fault
```

This layer is used for:

- CAN encode/decode validation
- verifier logging
- message-level signal audit
- VCU state and fault observation

This layer is not suitable for RC time-constant fitting. In the current `BMS_Status_1` message format, pack voltage is encoded at 0.1 V resolution. Small relaxation signals can therefore be quantized into one or two voltage levels, making the RC time constant unobservable from the CAN-decoded CSV.

### System Event Layer

`run_*.log` records runtime events such as:

```text
Logging initialized
Raw trace logging enabled
VCU state transition
Scenario completed
System stopped by user
```

This layer is used for runtime and scenario-level audit.

## Components

### ScenarioBMSDataProvider

Generates deterministic scenario data such as SOC and current trajectories.

For discharge scenarios, the provider can hold the terminal SOC for a configurable number of rest cycles using:

```text
rest_cycles_after_end
```

When this value is configured, the scenario can terminate naturally with `Scenario completed`.

### FakeBMS

Provides BMS status data to the runtime loop.

### OCV Model

Maps SOC to a pack-level open-circuit voltage estimate.

### RCModel

Models a first-order polarization voltage state.

The current model uses:

```text
R = 0.05
C = 200.0
tau = R * C = 10 s
```

The raw RC state is logged as:

```text
v_rc_raw
```

Because the RC model is updated in discrete time, fitting `v_rc_raw` gives an equivalent discrete-time decay constant of approximately:

```text
tau ≈ 9.75 s
```

for the current time step.

### FakeVCU

Processes BMS status data and can update system state based on SOC thresholds.

Example:

```text
SOC < 10 %  →  state = 2
```

### FaultInjector

Applies configured faults based on cycle count.

### Encoder / Decoder

`BMS_Status_1` is encoded into a deterministic CAN payload and decoded by the verifier.

No floating-point values are transmitted directly on the CAN payload. Physical values are scaled into integer raw values before transmission.

### CanBus

Wraps the `python-can` virtual bus interface.

### Verifier

Decodes CAN frames and logs structured BMS status information.

### Supervisor

Controls the runtime loop and data flow between components.

The supervisor also writes raw physical traces before CAN quantization.

## Design Principles

- Config-driven behavior via YAML
- Separation of physical model observability and CAN communication observability
- Separation of concerns between providers, models, nodes, runtime, and infrastructure
- Testable components using `pytest`
- Deterministic CAN encoding
- No floating-point values transmitted on the CAN payload