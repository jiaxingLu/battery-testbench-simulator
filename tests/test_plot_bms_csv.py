import pandas as pd

from scripts.plot_bms_csv import detect_csv_type


def test_detects_raw_trace_csv_type():
    df = pd.DataFrame(
        {
            "cycle": [0, 1],
            "time_s": [0.0, 0.5],
            "soc": [30, 29],
            "pack_current": [-5.0, -5.0],
            "ocv_raw": [300.0, 299.8],
            "v_rc_raw": [0.1, 0.12],
            "pack_voltage_raw": [299.9, 299.68],
            "state": [1, 1],
            "fault_level": [0, 0],
        }
    )

    assert detect_csv_type(df) == "raw_trace"


def test_detects_bms_status_csv_type():
    df = pd.DataFrame(
        {
            "timestamp": ["2026-05-03 17:00:00", "2026-05-03 17:00:01"],
            "signal": ["BMS_Status_1", "BMS_Status_1"],
            "pack_voltage": [299.9, 299.8],
            "pack_current": [-5.0, -5.0],
            "soc": [30, 29],
            "state": [1, 1],
            "fault": [0, 0],
        }
    )

    assert detect_csv_type(df) == "bms_status"


def test_detects_unknown_csv_type():
    df = pd.DataFrame(
        {
            "foo": [1, 2],
            "bar": [3, 4],
        }
    )

    assert detect_csv_type(df) == "unknown"


def test_raw_trace_takes_precedence_if_columns_overlap():
    df = pd.DataFrame(
        {
            "timestamp": ["2026-05-03 17:00:00"],
            "signal": ["BMS_Status_1"],
            "pack_voltage": [299.9],
            "pack_current": [-5.0],
            "soc": [30],
            "state": [1],
            "fault": [0],
            "ocv_raw": [300.0],
            "v_rc_raw": [0.1],
            "pack_voltage_raw": [299.9],
            "fault_level": [0],
        }
    )

    assert detect_csv_type(df) == "raw_trace"