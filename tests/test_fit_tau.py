import numpy as np
import pandas as pd
import pytest

from scripts.fit_tau import fit_tau


def test_fit_tau_from_raw_v_rc_trace(tmp_path, monkeypatch):
    """
    RCModel uses an explicit discrete-time update.

    For nominal tau = 10 s and dt = 0.5 s:
        decay factor = 1 - dt / tau = 0.95

    If this discrete decay is fitted with a continuous exponential,
    the expected equivalent tau is:

        tau_eff = -dt / ln(0.95) ≈ 9.74786 s
    """
    import matplotlib.pyplot as plt

    monkeypatch.setattr(plt, "show", lambda: None)

    dt = 0.5
    nominal_tau = 10.0
    decay_factor = 1.0 - dt / nominal_tau
    expected_tau = -dt / np.log(decay_factor)

    n_discharge = 5
    n_rest = 40
    amplitude = 0.2

    time_s = np.arange(n_discharge + n_rest) * dt
    current = [-5.0] * n_discharge + [0.0] * n_rest

    v_rc_discharge = [amplitude] * n_discharge
    v_rc_rest = [amplitude * decay_factor**k for k in range(n_rest)]

    df = pd.DataFrame(
        {
            "cycle": np.arange(n_discharge + n_rest),
            "time_s": time_s,
            "soc": [10] * n_discharge + [0] * n_rest,
            "pack_current": current,
            "ocv_raw": [280.0] * (n_discharge + n_rest),
            "v_rc_raw": v_rc_discharge + v_rc_rest,
            "pack_voltage_raw": [
                280.0 - v for v in (v_rc_discharge + v_rc_rest)
            ],
            "state": [1] * n_discharge + [2] * n_rest,
            "fault_level": [0] * (n_discharge + n_rest),
        }
    )

    csv_path = tmp_path / "raw_trace.csv"
    df.to_csv(csv_path, index=False)

    result = fit_tau(str(csv_path))

    assert result == 0
    assert expected_tau == pytest.approx(9.74786, rel=1e-5)


def test_fit_tau_rejects_quantized_bms_status_csv(tmp_path):
    """
    CAN-decoded BMS status voltage has only 0.1 V resolution here.

    The relaxation segment contains only two unique voltage levels:
        279.8 V -> 279.9 V

    This is not enough to observe an RC time constant.
    """
    n_discharge = 5
    n_rest = 20

    timestamps = pd.date_range(
        "2026-05-03 17:00:00",
        periods=n_discharge + n_rest,
        freq="500ms",
    )

    df = pd.DataFrame(
        {
            "timestamp": timestamps.astype(str),
            "signal": ["BMS_Status_1"] * (n_discharge + n_rest),
            "pack_voltage": [279.8] * n_discharge
            + [279.8] * 10
            + [279.9] * 10,
            "pack_current": [-5.0] * n_discharge + [0.0] * n_rest,
            "soc": [1] * n_discharge + [0] * n_rest,
            "state": [2] * (n_discharge + n_rest),
            "fault": [0] * (n_discharge + n_rest),
        }
    )

    csv_path = tmp_path / "bms_status.csv"
    df.to_csv(csv_path, index=False)

    result = fit_tau(str(csv_path))

    assert result == 2