import logging

from battery_testbench_sim.can_bus import CanBus
from battery_testbench_sim.config import load_config
from battery_testbench_sim.faults.fault_injector import FaultInjector
from battery_testbench_sim.logging_setup import setup_logging
from battery_testbench_sim.nodes.fake_bms import FakeBMS
from battery_testbench_sim.nodes.verifier import Verifier
from battery_testbench_sim.runtime.supervisor import Supervisor


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    bms_config = load_config("configs/bms_default.yaml")

    bms_cfg = bms_config["bms"]
    fault_cfg = bms_config.get("fault", {})

    bms = FakeBMS(**bms_cfg)
    verifier = Verifier()
    fault_injector = FaultInjector(fault_cfg)

    bus_tx = CanBus(interface="virtual", channel="testbench_runtime")
    bus_rx = CanBus(interface="virtual", channel="testbench_runtime")

    supervisor = Supervisor(
        bms=bms,
        verifier=verifier,
        bus_tx=bus_tx,
        bus_rx=bus_rx,
        fault_injector=fault_injector,
        bms_status_id=0x180,
    )

    supervisor.run()


if __name__ == "__main__":
    main()