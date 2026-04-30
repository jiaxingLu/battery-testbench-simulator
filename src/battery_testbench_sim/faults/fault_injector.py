class FaultInjector:
    def __init__(self, config: dict):
        self.enabled = bool(config.get("enabled", False))
        self.trigger_after_cycles = int(config.get("trigger_after_cycles", -1))
        self.fault_level = int(config.get("fault_level", 0))
        self.soc_override = config.get("soc_override", None)

    def apply(self, data: dict, cycle_count: int) -> dict:
        if not self.enabled:
            return data

        if cycle_count < self.trigger_after_cycles:
            return data

        modified = dict(data)
        modified["fault_level"] = self.fault_level

        if self.soc_override is not None:
            modified["soc"] = int(self.soc_override)

        return modified