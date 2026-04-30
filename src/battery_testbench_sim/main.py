from battery_testbench_sim.nodes.fake_bms import FakeBMS


def main():
    bms = FakeBMS(
        pack_voltage=400.0,
        pack_current=-5.0,
        soc=80,
        state=1,
        fault_level=0,
        cycle_time_s=0.5,  # 先慢一点，方便观察
    )

    bms.run_forever()


if __name__ == "__main__":
    main()