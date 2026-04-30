from battery_testbench_sim.messages.bms_status import decode_bms_status


class Verifier:
    def decode_status_frame(self, frame: bytes) -> dict:
        return decode_bms_status(frame)

    def print_status(self, frame: bytes) -> None:
        decoded = self.decode_status_frame(frame)
        print(
            "BMS_Status_1 | "
            f"U={decoded['pack_voltage']:.1f} V | "
            f"I={decoded['pack_current']:.1f} A | "
            f"SOC={decoded['soc']} % | "
            f"state={decoded['state']} | "
            f"fault={decoded['fault_level']}"
        )