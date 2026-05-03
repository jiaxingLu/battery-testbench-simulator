#!/usr/bin/env python3

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CURRENT_NEG_THRESHOLD_A = -1e-6
CURRENT_ZERO_THRESHOLD_A = 1e-6

MIN_FIT_POINTS = 6
MIN_UNIQUE_VOLTAGE_LEVELS = 6
MIN_RECOVERY_AMPLITUDE_V = 0.02


def infer_time_s(df: pd.DataFrame) -> np.ndarray:
    """
    Prefer explicit simulation time if available.
    Fall back to timestamp.
    Fall back to sample index only if no usable time information exists.
    """
    if "time_s" in df.columns:
        t = df["time_s"].to_numpy(dtype=float)
        if np.nanmax(t) > np.nanmin(t):
            return t

    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        if ts.notna().all():
            t = (ts - ts.iloc[0]).dt.total_seconds().to_numpy(dtype=float)
            if np.nanmax(t) > np.nanmin(t):
                return t

    return np.arange(len(df), dtype=float)


def find_rest_start_index(df: pd.DataFrame, current_col: str) -> int:
    current = df[current_col].to_numpy(dtype=float)

    candidates = np.where(
        (current[:-1] < CURRENT_NEG_THRESHOLD_A)
        & (np.abs(current[1:]) <= CURRENT_ZERO_THRESHOLD_A)
    )[0]

    if len(candidates) == 0:
        raise RuntimeError("No discharge-to-rest transition found: I < 0 -> I ≈ 0.")

    return int(candidates[0] + 1)


def estimate_voltage_resolution(voltage: np.ndarray) -> float:
    levels = np.unique(np.round(voltage, 9))

    if len(levels) < 2:
        return np.inf

    diffs = np.diff(levels)
    diffs = diffs[diffs > 0]

    if len(diffs) == 0:
        return np.inf

    return float(np.min(diffs))


def fit_decay_from_positive_state(t: np.ndarray, state: np.ndarray):
    """
    Fit:
        state(t) = A * exp(-t / tau)

    Linearized:
        log(state) = log(A) - t / tau

    This is the cleanest method for raw_trace.csv because v_rc_raw is
    the actual RC state.
    """
    state = np.asarray(state, dtype=float)

    max_state = float(np.nanmax(state))
    threshold = max(1e-12, 0.02 * max_state)

    mask = state > threshold

    if mask.sum() < MIN_FIT_POINTS:
        raise RuntimeError(
            f"Not enough usable RC-state points: {mask.sum()} < {MIN_FIT_POINTS}."
        )

    t_fit = t[mask]
    y_fit = state[mask]

    log_y = np.log(y_fit)
    slope, intercept = np.polyfit(t_fit, log_y, 1)

    if slope >= 0:
        raise RuntimeError(
            f"Invalid RC-state fit slope: {slope:.6g}. "
            "State does not decay exponentially."
        )

    tau = -1.0 / slope
    amplitude = float(np.exp(intercept))

    return tau, amplitude, mask


def fit_decay_from_voltage_with_known_ocv(
    t: np.ndarray,
    voltage: np.ndarray,
    ocv: np.ndarray,
):
    """
    Fit terminal-voltage recovery using known OCV:
        v_rc(t) = ocv(t) - V(t)

    During rest, SOC should be fixed, so ocv(t) should be nearly constant.
    """
    v_rc = ocv - voltage

    if np.nanmin(v_rc) < -1e-9:
        raise RuntimeError(
            "Computed v_rc = ocv_raw - pack_voltage_raw contains negative values."
        )

    return fit_decay_from_positive_state(t, v_rc)


def fit_voltage_without_known_ocv(t: np.ndarray, voltage: np.ndarray):
    """
    Fallback for decoded voltage only.

    This is intentionally conservative. If voltage is quantized or the recovery
    amplitude is not observable, the function refuses to fit.
    """
    v_start = float(voltage[0])
    v_end = float(voltage[-1])
    delta_v = v_end - v_start

    n_unique_voltage = int(len(np.unique(voltage)))
    voltage_resolution = estimate_voltage_resolution(voltage)

    print(f"[V_start] {v_start:.9g} V")
    print(f"[V_end]   {v_end:.9g} V")
    print(f"[delta_V] {delta_v:.9g} V")
    print(f"[n_unique_V_recovery] {n_unique_voltage}")
    print(f"[estimated_voltage_resolution] {voltage_resolution:.9g} V")

    hard_unobservable = False

    if abs(delta_v) < MIN_RECOVERY_AMPLITUDE_V:
        print(
            f"[FAIL] Recovery amplitude too small: "
            f"|delta_V|={abs(delta_v):.6g} V < {MIN_RECOVERY_AMPLITUDE_V} V."
        )
        hard_unobservable = True

    if n_unique_voltage < MIN_UNIQUE_VOLTAGE_LEVELS:
        print(
            f"[FAIL] Too few unique voltage levels in recovery: "
            f"{n_unique_voltage} < {MIN_UNIQUE_VOLTAGE_LEVELS}."
        )
        hard_unobservable = True

    if np.isfinite(voltage_resolution) and abs(delta_v) <= 3.0 * voltage_resolution:
        print(
            f"[FAIL] Recovery amplitude is not sufficiently above voltage quantization: "
            f"|delta_V|={abs(delta_v):.6g} V, "
            f"resolution≈{voltage_resolution:.6g} V."
        )
        hard_unobservable = True

    if hard_unobservable:
        print()
        print("Verdict: tau is NOT observable from this CSV.")
        print("Reason: voltage recovery is quantized, flattened, or too small before fitting.")
        print("Action: fit tau from raw internal voltage / v_rc_raw, not from CAN-decoded voltage.")
        return None

    raise RuntimeError(
        "Voltage-only fitting without known OCV is disabled for this project. "
        "Use raw_trace.csv with v_rc_raw or ocv_raw."
    )


def fit_tau(csv_file: str) -> int:
    csv_path = Path(csv_file)
    df = pd.read_csv(csv_path)

    current_col = "pack_current"

    if current_col not in df.columns:
        raise RuntimeError(f"Missing required column: {current_col}")

    rest_idx = find_rest_start_index(df, current_col=current_col)

    t_all = infer_time_s(df)
    t_rest = t_all[rest_idx:] - t_all[rest_idx]

    current_rest = df[current_col].iloc[rest_idx:].to_numpy(dtype=float)

    dt = np.diff(t_rest)
    positive_dt = dt[dt > 0]

    print(f"[file] {csv_path}")
    print(f"[rows] {len(df)}")
    print(f"[rest_idx] {rest_idx}")
    print(f"[rest_duration_s] {t_rest[-1]:.3f}")

    if len(positive_dt) > 0:
        print(f"[median_positive_dt] {np.median(positive_dt):.6g} s")
    else:
        print("[median_positive_dt] unavailable")

    if "v_rc_raw" in df.columns:
        mode = "v_rc_raw"
        v_rc_rest = df["v_rc_raw"].iloc[rest_idx:].to_numpy(dtype=float)

        print(f"[fit_mode] {mode}")
        print(f"[v_rc_start] {v_rc_rest[0]:.9g} V")
        print(f"[v_rc_end]   {v_rc_rest[-1]:.9g} V")

        tau, amplitude, fit_mask = fit_decay_from_positive_state(t_rest, v_rc_rest)

        print(f"[A]   {amplitude:.9g} V")
        print(f"[tau] {tau:.6g} s")

        plt.figure()
        plt.plot(t_rest, v_rc_rest, marker="o", label="v_rc_raw")
        plt.scatter(t_rest[fit_mask], v_rc_rest[fit_mask], label="fit points")
        plt.title(f"RC-state decay fit, tau ≈ {tau:.2f} s")
        plt.xlabel("Time since rest start (s)")
        plt.ylabel("v_rc_raw (V)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

        return 0

    if "pack_voltage_raw" in df.columns and "ocv_raw" in df.columns:
        mode = "pack_voltage_raw + ocv_raw"
        voltage_rest = df["pack_voltage_raw"].iloc[rest_idx:].to_numpy(dtype=float)
        ocv_rest = df["ocv_raw"].iloc[rest_idx:].to_numpy(dtype=float)

        v_rc_rest = ocv_rest - voltage_rest

        print(f"[fit_mode] {mode}")
        print(f"[ocv_start] {ocv_rest[0]:.9g} V")
        print(f"[ocv_end]   {ocv_rest[-1]:.9g} V")
        print(f"[v_rc_start] {v_rc_rest[0]:.9g} V")
        print(f"[v_rc_end]   {v_rc_rest[-1]:.9g} V")

        tau, amplitude, fit_mask = fit_decay_from_voltage_with_known_ocv(
            t_rest,
            voltage_rest,
            ocv_rest,
        )

        print(f"[A]   {amplitude:.9g} V")
        print(f"[tau] {tau:.6g} s")

        plt.figure()
        plt.plot(t_rest, voltage_rest, marker="o", label="pack_voltage_raw")
        plt.scatter(t_rest[fit_mask], voltage_rest[fit_mask], label="fit points")
        plt.title(f"Voltage recovery fit with known OCV, tau ≈ {tau:.2f} s")
        plt.xlabel("Time since rest start (s)")
        plt.ylabel("pack_voltage_raw (V)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

        return 0

    if "pack_voltage" in df.columns:
        mode = "pack_voltage"
        voltage_rest = df["pack_voltage"].iloc[rest_idx:].to_numpy(dtype=float)

        print(f"[fit_mode] {mode}")
        result = fit_voltage_without_known_ocv(t_rest, voltage_rest)

        if result is None:
            return 2

    raise RuntimeError(
        "No usable voltage/state column found. Expected one of: "
        "v_rc_raw, pack_voltage_raw + ocv_raw, or pack_voltage."
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/fit_tau.py <csv_file>")
        raise SystemExit(1)

    raise SystemExit(fit_tau(sys.argv[1]))