from battery_testbench_sim.messages.bms_status import (
    decode_bms_status,
    encode_bms_status,
)


def test_encode_decode_roundtrip():
    data = {
        "pack_voltage": 400.0,
        "pack_current": -50.0,
        "soc": 80,
        "state": 1,
        "fault_level": 0,
    }

    encoded = encode_bms_status(data)
    decoded = decode_bms_status(encoded)

    assert abs(decoded["pack_voltage"] - data["pack_voltage"]) < 0.1
    assert abs(decoded["pack_current"] - data["pack_current"]) < 0.1
    assert decoded["soc"] == data["soc"]
    assert decoded["state"] == data["state"]
    assert decoded["fault_level"] == data["fault_level"]