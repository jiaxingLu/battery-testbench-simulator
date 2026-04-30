import time

from battery_testbench_sim.messages.bms_status import encode_bms_status


class FakeBMS:
    def __init__(
        self,
        data_provider,
        cycle_time_s: float = 0.1,
    ):
        self.data_provider = data_provider
        self.cycle_time_s = cycle_time_s

    def get_status_data(self) -> dict:
        return self.data_provider.get_status_data()

    def build_status_frame(self) -> bytes:
        return encode_bms_status(self.get_status_data())

    def run_once(self) -> bytes:
        return self.build_status_frame()

    def run_forever(self):
        try:
            while True:
                frame = self.run_once()
                print(frame.hex())
                time.sleep(self.cycle_time_s)
        except KeyboardInterrupt:
            print("\nFakeBMS stopped by user.")