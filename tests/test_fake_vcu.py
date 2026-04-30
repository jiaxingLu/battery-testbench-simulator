from battery_testbench_sim.nodes.fake_vcu import FakeVCU


def test_vcu_normal_state():
    vcu = FakeVCU()

    data = {"soc": 50, "state": 0}
    result = vcu.process_bms_status(data)

    assert result["state"] == 1


def test_vcu_protection_state():
    vcu = FakeVCU()

    data = {"soc": 5, "state": 0}
    result = vcu.process_bms_status(data)

    assert result["state"] == 2