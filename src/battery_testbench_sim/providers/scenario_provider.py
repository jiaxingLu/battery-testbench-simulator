from math import ceil
from typing import Optional


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
        rest_cycles_after_end: Optional[int] = None,
    ):
        if soc_step_per_cycle <= 0:
            raise ValueError("soc_step_per_cycle must be positive.")

        if rest_cycles_after_end is not None and rest_cycles_after_end < 0:
            raise ValueError("rest_cycles_after_end must be non-negative.")

        self.start_soc = start_soc
        self.end_soc = end_soc
        self.soc_step_per_cycle = soc_step_per_cycle
        self.pack_voltage_start = pack_voltage_start
        self.pack_voltage_end = pack_voltage_end
        self.pack_current = pack_current
        self.state = state
        self.fault_level = fault_level
        self.rest_cycles_after_end = rest_cycles_after_end

        self.discharge_cycles = max(
            0,
            ceil((self.start_soc - self.end_soc) / self.soc_step_per_cycle),
        )

        if self.rest_cycles_after_end is None:
            self.total_cycles = None
        else:
            self.total_cycles = self.discharge_cycles + self.rest_cycles_after_end

        self.cycle_count = 0

    def get_status_data(self) -> dict:
        if self.total_cycles is not None and self.cycle_count >= self.total_cycles:
            raise StopIteration("Scenario completed.")

        if self.cycle_count < self.discharge_cycles:
            soc = self.start_soc - self.cycle_count * self.soc_step_per_cycle
            current = self.pack_current
        else:
            soc = self.end_soc
            current = 0.0

        self.cycle_count += 1

        return {
            "pack_voltage": self.pack_voltage_end,
            "pack_current": current,
            "soc": soc,
            "state": self.state,
            "fault_level": self.fault_level,
        }