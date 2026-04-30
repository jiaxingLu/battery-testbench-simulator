from battery_testbench_sim.can_bus import CanBus


def test_virtual_can_send_receive():
    tx = CanBus(interface="virtual", channel="testbench_test")
    rx = CanBus(interface="virtual", channel="testbench_test")

    payload = bytes.fromhex("a00fceff50010000")

    tx.send(arbitration_id=0x180, data=payload)
    msg = rx.recv(timeout_s=1.0)

    tx.shutdown()
    rx.shutdown()

    assert msg is not None
    assert msg.arbitration_id == 0x180
    assert bytes(msg.data) == payload