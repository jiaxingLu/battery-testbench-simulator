from battery_testbench_sim.can_bus import CanBus
from battery_testbench_sim.config import load_config
from battery_testbench_sim.faults.fault_injector import FaultInjector
from battery_testbench_sim.logging_setup import setup_logging
from battery_testbench_sim.nodes.fake_bms import FakeBMS
from battery_testbench_sim.nodes.fake_vcu import FakeVCU
from battery_testbench_sim.nodes.verifier import Verifier
from battery_testbench_sim.providers.static_provider import StaticBMSDataProvider
from battery_testbench_sim.runtime.supervisor import Supervisor


def main():
    setup_logging()

    bms_config = load_config("configs/bms_default.yaml")
    can_config = load_config("configs/can_virtual.yaml")

    bms_cfg = bms_config["bms"]
    fault_cfg = bms_config.get("fault", {})
    can_cfg = can_config["can"]
    msg_cfg = can_config["messages"]

    provider = StaticBMSDataProvider(
        pack_voltage=bms_cfg["pack_voltage"],
        pack_current=bms_cfg["pack_current"],
        soc=bms_cfg["soc"],
        state=bms_cfg["state"],
        fault_level=bms_cfg["fault_level"],
    )

    bms = FakeBMS(
        data_provider=provider,
        cycle_time_s=bms_cfg["cycle_time_s"],
    )

    verifier = Verifier()
    vcu = FakeVCU()
    fault_injector = FaultInjector(fault_cfg)

    bus_tx = CanBus(
        interface=can_cfg["interface"],
        channel=can_cfg["channel"],
    )
    bus_rx = CanBus(
        interface=can_cfg["interface"],
        channel=can_cfg["channel"],
    )

    supervisor = Supervisor(
        bms=bms,
        verifier=verifier,
        bus_tx=bus_tx,
        bus_rx=bus_rx,
        fault_injector=fault_injector,
        bms_status_id=int(msg_cfg["bms_status_id"]),
        vcu=vcu,
    )

    supervisor.run()


if __name__ == "__main__":
    main()