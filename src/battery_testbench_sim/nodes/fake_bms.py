import time
from battery_testbench_sim.messages.bms_status import encode_bms_status


class FakeBMS:
    def __init__(
        self,
        pack_voltage: float = 400.0,
        pack_current: float = 0.0,
        soc: int = 80,
        state: int = 1,
        fault_level: int = 0,
        cycle_time_s: float = 0.1,
    ):
        self.pack_voltage = pack_voltage
        self.pack_current = pack_current
        self.soc = soc
        self.state = state
        self.fault_level = fault_level
        self.cycle_time_s = cycle_time_s

    def get_status_data(self) -> dict:
        return {
            "pack_voltage": self.pack_voltage,
            "pack_current": self.pack_current,
            "soc": self.soc,
            "state": self.state,
            "fault_level": self.fault_level,
        }

    def build_status_frame(self) -> bytes:
        return encode_bms_status(self.get_status_data())

    def run_once(self) -> bytes:
        frame = self.build_status_frame()
        return frame

    def run_forever(self):
        try:
            while True:
                frame = self.run_once()
                print(frame.hex())
                time.sleep(self.cycle_time_s)
        except KeyboardInterrupt:
            print("\nFakeBMS stopped by user.")