class ScenarioBMSDataProvider:
    def __init__(
        self,
        start_soc: int,
        end_soc: int,
        soc_step_per_cycle: int,
        pack_voltage_start: float,
        pack_voltage_end: float,
        pack_current: float,
        state: int,
        fault_level: int,
    ):
        self.start_soc = start_soc
        self.end_soc = end_soc
        self.soc_step_per_cycle = soc_step_per_cycle
        self.pack_voltage_start = pack_voltage_start
        self.pack_voltage_end = pack_voltage_end
        self.pack_current = pack_current
        self.state = state
        self.fault_level = fault_level

        self.cycle_count = 0

    def get_status_data(self) -> dict:
        soc = max(
            self.end_soc,
            self.start_soc - self.cycle_count * self.soc_step_per_cycle,
        )

        soc_span = self.start_soc - self.end_soc
        if soc_span == 0:
            progress = 1.0
        else:
            progress = (self.start_soc - soc) / soc_span

        voltage = (
            self.pack_voltage_start
            + progress * (self.pack_voltage_end - self.pack_voltage_start)
        )

        self.cycle_count += 1

        return {
            "pack_voltage": voltage,
            "pack_current": self.pack_current,
            "soc": soc,
            "state": self.state,
            "fault_level": self.fault_level,
        }