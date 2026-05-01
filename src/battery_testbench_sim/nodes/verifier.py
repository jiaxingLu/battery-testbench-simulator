from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from battery_testbench_sim.infrastructure.csv_logger import CSVLogger
from battery_testbench_sim.messages.bms_status import decode_bms_status


logger = logging.getLogger(__name__)


class Verifier:
    def __init__(self, csv_logger: Optional[CSVLogger] = None) -> None:
        self.csv_logger = csv_logger

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

        if self.csv_logger is not None:
            self.csv_logger.write_row(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "signal": "BMS_Status_1",
                    "pack_voltage": d["pack_voltage"],
                    "pack_current": d["pack_current"],
                    "soc": d["soc"],
                    "state": d["state"],
                    "fault": d["fault_level"],
                }
            )