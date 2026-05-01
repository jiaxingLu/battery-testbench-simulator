import argparse

from battery_testbench_sim.infrastructure.logging_setup import setup_logging
from battery_testbench_sim.can_bus import CanBus
from battery_testbench_sim.config import load_config
from battery_testbench_sim.faults.fault_injector import FaultInjector
from battery_testbench_sim.nodes.fake_bms import FakeBMS
from battery_testbench_sim.nodes.fake_vcu import FakeVCU
from battery_testbench_sim.nodes.verifier import Verifier
from battery_testbench_sim.providers.scenario_provider import ScenarioBMSDataProvider
from battery_testbench_sim.runtime.supervisor import Supervisor


def parse_args():
    parser = argparse.ArgumentParser(
        description="Battery testbench simulator runtime"
    )
    parser.add_argument(
        "--bms-config",
        default="configs/bms_default.yaml",
        help="Path to BMS base configuration YAML",
    )
    parser.add_argument(
        "--can-config",
        default="configs/can_virtual.yaml",
        help="Path to CAN configuration YAML",
    )
    parser.add_argument(
        "--scenario",
        default="configs/scenario_discharge.yaml",
        help="Path to scenario configuration YAML",
    )
    return parser.parse_args()


def main():
    setup_logging()
    args = parse_args()

    bms_config = load_config(args.bms_config)
    can_config = load_config(args.can_config)
    scenario_config = load_config(args.scenario)

    bms_cfg = bms_config["bms"]
    can_cfg = can_config["can"]
    msg_cfg = can_config["messages"]

    scenario_cfg = scenario_config.get("scenario", {})
    fault_cfg = scenario_config.get("fault", {})

    provider = ScenarioBMSDataProvider(
        start_soc=bms_cfg["soc"],
        end_soc=scenario_cfg.get("end_soc", 5),
        soc_step_per_cycle=scenario_cfg.get("soc_step_per_cycle", 1),
        pack_voltage_start=bms_cfg["pack_voltage"],
        pack_voltage_end=scenario_cfg.get("pack_voltage_end", 280.0),
        pack_current=bms_cfg["pack_current"],
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