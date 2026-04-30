from battery_testbench_sim.messages.bms_status import decode_bms_status
from battery_testbench_sim.nodes.fake_bms import FakeBMS


def test_fake_bms_builds_valid_status_frame():
    bms = FakeBMS(
        pack_voltage=410.5,
        pack_current=-12.3,
        soc=75,
        state=1,
        fault_level=0,
    )

    frame = bms.build_status_frame()
    decoded = decode_bms_status(frame)

    assert len(frame) == 8
    assert decoded["pack_voltage"] == 410.5
    assert decoded["pack_current"] == -12.3
    assert decoded["soc"] == 75
    assert decoded["state"] == 1
    assert decoded["fault_level"] == 0