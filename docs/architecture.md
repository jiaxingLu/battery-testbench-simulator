# Architecture Overview

## System Structure

The system follows a layered architecture:

```text
+---------------------------+
|       Runtime Layer       |
|     Supervisor loop       |
+---------------------------+
              |
              v
+---------------------------+
|         Node Layer        |
|    FakeBMS / Verifier     |
+---------------------------+
              |
              v
+---------------------------+
|   Infrastructure Layer    |
|  CAN / Logging / Config   |
+---------------------------+
```

## Data Flow

```text
FakeBMS
   ↓ status data dict
FaultInjector
   ↓ modified data
Encoder: bms_status
   ↓ bytes
CAN Bus: virtual
   ↓ received CAN frame
Verifier
   ↓ decode + structured log
```

## Components

### FakeBMS

Generates battery status data.

### FaultInjector

Applies configured faults based on cycle count.

### CanBus

Wraps the `python-can` interface.

### Verifier

Decodes CAN frames and logs structured BMS status information.

### Supervisor

Controls the runtime loop and data flow between components.

## Design Principles

- Config-driven behavior via YAML
- Separation of concerns between nodes, runtime, and infrastructure
- Testable components using `pytest`
- Deterministic CAN encoding
- No floating-point values transmitted on the CAN payload