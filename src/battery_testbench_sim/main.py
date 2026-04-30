import time
from battery_testbench_sim.nodes.fake_bms import FakeBMS
from battery_testbench_sim.nodes.verifier import Verifier


def main():
    bms = FakeBMS(
        pack_voltage=400.0,
        pack_current=-5.0,
        soc=80,
        state=1,
        fault_level=0,
        cycle_time_s=0.5,
    )
    verifier = Verifier()

    try:
        while True:
            frame = bms.run_once()
            verifier.print_status(frame)
            time.sleep(bms.cycle_time_s)
    except KeyboardInterrupt:
        print("\nSystem stopped.")


if __name__ == "__main__":
    main()