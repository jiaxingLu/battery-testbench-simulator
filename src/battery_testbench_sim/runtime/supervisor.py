import logging
import time

from battery_testbench_sim.messages.bms_status import encode_bms_status


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
    ):
        self.bms = bms
        self.verifier = verifier
        self.bus_tx = bus_tx
        self.bus_rx = bus_rx
        self.fault_injector = fault_injector
        self.bms_status_id = bms_status_id
        self.vcu = vcu

        self.cycle_count = 0

    def run(self):
        try:
            while True:
                data = self.bms.get_status_data()
                data = self.fault_injector.apply(data, self.cycle_count)

                if self.vcu is not None:
                    data = self.vcu.process_bms_status(data)

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

        except KeyboardInterrupt:
            logger.info("System stopped by user.")
        finally:
            self.bus_tx.shutdown()
            self.bus_rx.shutdown()