import logging
import time

from battery_testbench_sim.config import load_config
from battery_testbench_sim.faults.fault_injector import FaultInjector
from battery_testbench_sim.logging_setup import setup_logging
from battery_testbench_sim.messages.bms_status import encode_bms_status
from battery_testbench_sim.nodes.fake_bms import FakeBMS
from battery_testbench_sim.nodes.verifier import Verifier


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    config = load_config("configs/bms_default.yaml")
    bms_cfg = config["bms"]
    fault_cfg = config.get("fault", {})

    bms = FakeBMS(
        pack_voltage=bms_cfg["pack_voltage"],
        pack_current=bms_cfg["pack_current"],
        soc=bms_cfg["soc"],
        state=bms_cfg["state"],
        fault_level=bms_cfg["fault_level"],
        cycle_time_s=bms_cfg["cycle_time_s"],
    )

    fault_injector = FaultInjector(fault_cfg)
    verifier = Verifier()

    cycle_count = 0

    try:
        while True:
            data = bms.get_status_data()
            data = fault_injector.apply(data, cycle_count)
            frame = encode_bms_status(data)

            verifier.log_status(frame)

            cycle_count += 1
            time.sleep(bms.cycle_time_s)

    except KeyboardInterrupt:
        logger.info("System stopped by user.")


if __name__ == "__main__":
    main()