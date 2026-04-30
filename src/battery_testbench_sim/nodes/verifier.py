import logging
from battery_testbench_sim.messages.bms_status import decode_bms_status


logger = logging.getLogger(__name__)


class Verifier:
    def decode_status_frame(self, frame: bytes) -> dict:
        return decode_bms_status(frame)

    def log_status(self, frame: bytes) -> None:
        d = self.decode_status_frame(frame)
        logger.info(
            "BMS_Status_1 | U=%.1f V | I=%.1f A | SOC=%d %% | state=%d | fault=%d",
            d["pack_voltage"],
            d["pack_current"],
            d["soc"],
            d["state"],
            d["fault_level"],
        )