class StaticBMSDataProvider:
    def __init__(
        self,
        pack_voltage: float,
        pack_current: float,
        soc: int,
        state: int,
        fault_level: int,
    ):
        self.data = {
            "pack_voltage": pack_voltage,
            "pack_current": pack_current,
            "soc": soc,
            "state": state,
            "fault_level": fault_level,
        }

    def get_status_data(self) -> dict:
        return dict(self.data)