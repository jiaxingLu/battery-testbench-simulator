from battery_testbench_sim.nodes.fake_bms import FakeBMS
from battery_testbench_sim.nodes.verifier import Verifier


def test_verifier_decodes_fake_bms_frame():
    bms = FakeBMS(pack_voltage=399.9, pack_current=-7.5, soc=66)
    verifier = Verifier()

    frame = bms.build_status_frame()
    decoded = verifier.decode_status_frame(frame)

    assert decoded["pack_voltage"] == 399.9
    assert decoded["pack_current"] == -7.5
    assert decoded["soc"] == 66