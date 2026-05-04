class PulseBMSDataProvider:
    def __init__(
        self,
        soc: int,
        pre_rest_cycles: int,
        pulse_current: float,
        pulse_cycles: int,
        post_rest_cycles: int,
        pack_voltage: float,
        state: int,
        fault_level: int,
    ):
        if pre_rest_cycles < 0:
            raise ValueError("pre_rest_cycles must be non-negative.")

        if pulse_cycles <= 0:
            raise ValueError("pulse_cycles must be positive.")

        if post_rest_cycles < 0:
            raise ValueError("post_rest_cycles must be non-negative.")

        self.soc = soc
        self.pre_rest_cycles = pre_rest_cycles
        self.pulse_current = pulse_current
        self.pulse_cycles = pulse_cycles
        self.post_rest_cycles = post_rest_cycles
        self.pack_voltage = pack_voltage
        self.state = state
        self.fault_level = fault_level

        self.total_cycles = (
            self.pre_rest_cycles
            + self.pulse_cycles
            + self.post_rest_cycles
        )

        self.cycle_count = 0

    def get_status_data(self) -> dict:
        if self.cycle_count >= self.total_cycles:
            raise StopIteration("Scenario completed.")

        if self.cycle_count < self.pre_rest_cycles:
            current = 0.0
        elif self.cycle_count < self.pre_rest_cycles + self.pulse_cycles:
            current = self.pulse_current
        else:
            current = 0.0

        self.cycle_count += 1

        return {
            "pack_voltage": self.pack_voltage,
            "pack_current": current,
            "soc": self.soc,
            "state": self.state,
            "fault_level": self.fault_level,
        }