import logging
import time
from datetime import datetime
from pathlib import Path

from battery_testbench_sim.infrastructure.csv_logger import CSVLogger
from battery_testbench_sim.messages.bms_status import encode_bms_status
from battery_testbench_sim.models.ocv import ocv_from_soc
from battery_testbench_sim.models.rc_model import RCModel


logger = logging.getLogger(__name__)


class Supervisor:
    def __init__(
        self,
        bms,
        verifier,
        bus_tx,
        bus_rx,
        fault_injector,
        bms_status_id,
        vcu=None,
        raw_trace_enabled=True,
        raw_trace_dir="logs",
    ):
        self.bms = bms
        self.verifier = verifier
        self.bus_tx = bus_tx
        self.bus_rx = bus_rx
        self.fault_injector = fault_injector
        self.bms_status_id = bms_status_id
        self.vcu = vcu

        self.rc_model = RCModel(R=0.05, C=200.0)
        self.cycle_count = 0

        self.raw_trace_logger = None
        if raw_trace_enabled:
            stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            raw_trace_path = Path(raw_trace_dir) / f"run_{stamp}_raw_trace.csv"

            self.raw_trace_logger = CSVLogger(
                raw_trace_path,
                fieldnames=[
                    "cycle",
                    "time_s",
                    "soc",
                    "pack_current",
                    "ocv_raw",
                    "v_rc_raw",
                    "pack_voltage_raw",
                    "state",
                    "fault_level",
                ],
            )

            logger.info("Raw trace logging enabled: %s", raw_trace_path)

    def _recompute_voltage(self, soc: int) -> float:
        cell_v = ocv_from_soc(soc)

        v_min = 280.0
        v_max = 300.0

        return v_min + (v_max - v_min) * (cell_v - 3.0) / (4.2 - 3.0)

    def _write_raw_trace(self, data: dict, ocv: float, v_rc: float) -> None:
        if self.raw_trace_logger is None:
            return

        self.raw_trace_logger.write_row(
            {
                "cycle": self.cycle_count,
                "time_s": self.cycle_count * self.bms.cycle_time_s,
                "soc": data["soc"],
                "pack_current": data["pack_current"],
                "ocv_raw": ocv,
                "v_rc_raw": v_rc,
                "pack_voltage_raw": data["pack_voltage"],
                "state": data.get("state"),
                "fault_level": data.get("fault_level"),
            }
        )

    def run(self):
        try:
            while True:
                data = self.bms.get_status_data()
                data = self.fault_injector.apply(data, self.cycle_count)

                ocv = self._recompute_voltage(data["soc"])

                v_rc = self.rc_model.step(
                    current=data["pack_current"],
                    dt=self.bms.cycle_time_s,
                )

                data["pack_voltage"] = ocv - v_rc

                if self.vcu is not None:
                    data = self.vcu.process_bms_status(data)

                # Raw physical trace before CAN quantization.
                self._write_raw_trace(data=data, ocv=ocv, v_rc=v_rc)

                frame = encode_bms_status(data)

                self.bus_tx.send(
                    arbitration_id=self.bms_status_id,
                    data=frame,
                )

                msg = self.bus_rx.recv(timeout_s=1.0)

                if msg is None:
                    logger.warning("No CAN message received.")
                elif msg.arbitration_id == self.bms_status_id:
                    self.verifier.log_status(bytes(msg.data))
                else:
                    logger.warning("Unexpected CAN ID: 0x%X", msg.arbitration_id)

                self.cycle_count += 1
                time.sleep(self.bms.cycle_time_s)

        except StopIteration:
            logger.info("Scenario completed.")
        except KeyboardInterrupt:
            logger.info("System stopped by user.")
        finally:
            if self.raw_trace_logger is not None:
                self.raw_trace_logger.close()

            self.bus_tx.shutdown()
            self.bus_rx.shutdown()