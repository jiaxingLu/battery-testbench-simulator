import struct


def encode_bms_status(data: dict) -> bytes:
    voltage_raw = int(data["pack_voltage"] * 10)
    current_raw = int(data["pack_current"] * 10)

    soc = int(data["soc"])
    state = int(data["state"])
    fault = int(data["fault_level"])

    return struct.pack(
        "<HhBBBB",
        voltage_raw,
        current_raw,
        soc,
        state,
        fault,
        0,
    )


def decode_bms_status(frame: bytes) -> dict:
    voltage_raw, current_raw, soc, state, fault, _ = struct.unpack(
        "<HhBBBB", frame
    )

    return {
        "pack_voltage": voltage_raw / 10.0,
        "pack_current": current_raw / 10.0,
        "soc": soc,
        "state": state,
        "fault_level": fault,
    }