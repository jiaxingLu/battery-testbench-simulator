import argparse

from battery_testbench_sim.can_bus import CanBus
from battery_testbench_sim.config import load_config
from battery_testbench_sim.faults.fault_injector import FaultInjector
from battery_testbench_sim.infrastructure.csv_logger import CSVLogger
from battery_testbench_sim.infrastructure.logging_setup import setup_logging
from battery_testbench_sim.nodes.fake_bms import FakeBMS
from battery_testbench_sim.nodes.fake_vcu import FakeVCU
from battery_testbench_sim.nodes.verifier import Verifier
from battery_testbench_sim.providers.scenario_provider import ScenarioBMSDataProvider
from battery_testbench_sim.providers.pulse_provider import PulseBMSDataProvider
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
    parser.add_argument(
        "--no-sleep",
        action="store_true",
        help="Run the scenario without wall-clock sleep between cycles.",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Maximum number of runtime cycles to execute before stopping.",
    )
    parser.add_argument(
        "--output-dir",
        default="logs",
        help="Directory for runtime log and CSV output files.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    log_file = setup_logging(output_dir=args.output_dir)
    csv_file = log_file.with_name(log_file.stem + "_bms_status.csv")
    raw_trace_file = log_file.with_name(log_file.stem + "_raw_trace.csv")

    bms_config = load_config(args.bms_config)
    can_config = load_config(args.can_config)
    scenario_config = load_config(args.scenario)

    bms_cfg = bms_config["bms"]
    can_cfg = can_config["can"]
    msg_cfg = can_config["messages"]

    scenario_cfg = scenario_config.get("scenario", {})
    fault_cfg = scenario_config.get("fault", {})

    scenario_type = scenario_cfg.get("type", "discharge")

    if scenario_type == "discharge":
        provider = ScenarioBMSDataProvider(
            start_soc=bms_cfg["soc"],
            end_soc=scenario_cfg.get("end_soc", 0),
            soc_step_per_cycle=scenario_cfg.get("soc_step_per_cycle", 1),
            pack_voltage_start=bms_cfg["pack_voltage"],
            pack_voltage_end=scenario_cfg.get("pack_voltage_end", 280.0),
            pack_current=bms_cfg["pack_current"],
            state=bms_cfg["state"],
            fault_level=bms_cfg["fault_level"],
            rest_cycles_after_end=scenario_cfg.get("rest_cycles_after_end"),
        )
    elif scenario_type == "pulse":
        provider = PulseBMSDataProvider(
            soc=scenario_cfg.get("soc", bms_cfg["soc"]),
            pre_rest_cycles=scenario_cfg.get("pre_rest_cycles", 0),
            pulse_current=scenario_cfg.get("pulse_current", bms_cfg["pack_current"]),
            pulse_cycles=scenario_cfg.get("pulse_cycles", 1),
            post_rest_cycles=scenario_cfg.get("post_rest_cycles", 0),
            pack_voltage=scenario_cfg.get("pack_voltage", bms_cfg["pack_voltage"]),
            state=bms_cfg["state"],
            fault_level=bms_cfg["fault_level"],
        )
    else:
        raise ValueError(f"Unsupported scenario type: {scenario_type}")

    bms = FakeBMS(
        data_provider=provider,
        cycle_time_s=bms_cfg["cycle_time_s"],
    )

    csv_logger = CSVLogger(
        file_path=csv_file,
        fieldnames=[
            "timestamp",
            "signal",
            "pack_voltage",
            "pack_current",
            "soc",
            "state",
            "fault",
        ],
    )

    verifier = Verifier(csv_logger=csv_logger)
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
        raw_trace_file_path=raw_trace_file,
        sleep_enabled=not args.no_sleep,
        max_cycles=args.max_cycles,
    )

    supervisor.run()


if __name__ == "__main__":
    main()