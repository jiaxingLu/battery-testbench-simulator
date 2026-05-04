#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


EXPECTED_RAW_COLUMNS = {
    "cycle",
    "time_s",
    "soc",
    "pack_current",
    "ocv_raw",
    "v_rc_raw",
    "pack_voltage_raw",
    "state",
    "fault_level",
}

EXPECTED_BMS_COLUMNS = {
    "timestamp",
    "signal",
    "pack_voltage",
    "pack_current",
    "soc",
    "state",
    "fault",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a quick end-to-end audit of simulator output layers."
    )

    parser.add_argument(
        "--scenario",
        default="configs/scenario_discharge.yaml",
        help="Scenario YAML to run.",
    )

    parser.add_argument(
        "--output-base",
        default="logs/quick_audit",
        help="Base output directory for quick audit runs.",
    )

    parser.add_argument(
        "--max-cycles",
        type=int,
        default=70,
        help=(
            "Maximum runtime cycles. Default 70 covers the current discharge "
            "and rest segment so tau can be audited."
        ),
    )

    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_simulator(root: Path, scenario: Path, output_dir: Path, max_cycles: int):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src")

    command = [
        sys.executable,
        "-m",
        "battery_testbench_sim.main",
        "--scenario",
        str(scenario),
        "--no-sleep",
        "--max-cycles",
        str(max_cycles),
        "--output-dir",
        str(output_dir),
    ]

    print("[run]", " ".join(command))

    result = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        timeout=15,
    )

    if result.stdout:
        print("[stdout]")
        print(result.stdout)

    if result.stderr:
        print("[stderr]")
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Simulator command failed with return code {result.returncode}")


def find_single_file(output_dir: Path, pattern: str) -> Path:
    matches = sorted(output_dir.glob(pattern))

    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one file for pattern {pattern}, "
            f"found {len(matches)} in {output_dir}"
        )

    return matches[0]


def find_rest_start_index(df: pd.DataFrame, current_col: str = "pack_current") -> int:
    current = df[current_col].to_numpy(dtype=float)

    candidates = np.where(
        (current[:-1] < -1e-6)
        & (np.abs(current[1:]) <= 1e-6)
    )[0]

    if len(candidates) == 0:
        raise RuntimeError("No discharge-to-rest transition found.")

    return int(candidates[0] + 1)


def fit_tau_from_v_rc_raw(raw_df: pd.DataFrame) -> float:
    rest_idx = find_rest_start_index(raw_df)

    time_s = raw_df["time_s"].to_numpy(dtype=float)
    t_rest = time_s[rest_idx:] - time_s[rest_idx]

    v_rc = raw_df["v_rc_raw"].iloc[rest_idx:].to_numpy(dtype=float)

    max_v = float(np.nanmax(v_rc))
    threshold = max(1e-12, 0.02 * max_v)

    mask = v_rc > threshold

    if mask.sum() < 6:
        raise RuntimeError(f"Not enough v_rc_raw points for tau fit: {mask.sum()}")

    slope, intercept = np.polyfit(t_rest[mask], np.log(v_rc[mask]), 1)

    if slope >= 0:
        raise RuntimeError(f"Invalid tau fit slope: {slope}")

    return float(-1.0 / slope)


def estimate_voltage_resolution(values: np.ndarray) -> float:
    levels = np.unique(np.round(values, 9))

    if len(levels) < 2:
        return float("inf")

    diffs = np.diff(levels)
    diffs = diffs[diffs > 0]

    if len(diffs) == 0:
        return float("inf")

    return float(np.min(diffs))


def assert_bms_tau_not_observable(bms_df: pd.DataFrame) -> None:
    rest_idx = find_rest_start_index(bms_df)

    voltage = bms_df["pack_voltage"].iloc[rest_idx:].to_numpy(dtype=float)

    n_unique = len(np.unique(voltage))
    delta_v = float(voltage[-1] - voltage[0])
    resolution = estimate_voltage_resolution(voltage)

    print(f"[bms observability] n_unique={n_unique}")
    print(f"[bms observability] delta_v={delta_v:.9g} V")
    print(f"[bms observability] resolution≈{resolution:.9g} V")

    if n_unique >= 6 and abs(delta_v) > 3.0 * resolution:
        raise RuntimeError(
            "BMS voltage unexpectedly appears observable for tau fitting. "
            "Expected CAN quantization to make it non-observable."
        )


def audit_outputs(output_dir: Path, expected_rows: int) -> None:
    log_file = find_single_file(output_dir, "run_*.log")
    raw_file = find_single_file(output_dir, "*_raw_trace.csv")
    bms_file = find_single_file(output_dir, "*_bms_status.csv")

    print(f"[log] {log_file}")
    print(f"[raw] {raw_file}")
    print(f"[bms] {bms_file}")

    if not raw_file.stem.startswith(log_file.stem):
        raise RuntimeError("raw_trace filename does not share log-file prefix.")

    if not bms_file.stem.startswith(log_file.stem):
        raise RuntimeError("bms_status filename does not share log-file prefix.")

    raw_df = pd.read_csv(raw_file)
    bms_df = pd.read_csv(bms_file)

    print(f"[raw rows] {len(raw_df)}")
    print(f"[bms rows] {len(bms_df)}")

    if len(raw_df) != expected_rows:
        raise RuntimeError(f"Expected raw rows={expected_rows}, got {len(raw_df)}")

    if len(bms_df) != expected_rows:
        raise RuntimeError(f"Expected bms rows={expected_rows}, got {len(bms_df)}")

    if not EXPECTED_RAW_COLUMNS.issubset(raw_df.columns):
        missing = EXPECTED_RAW_COLUMNS - set(raw_df.columns)
        raise RuntimeError(f"Missing raw_trace columns: {sorted(missing)}")

    if not EXPECTED_BMS_COLUMNS.issubset(bms_df.columns):
        missing = EXPECTED_BMS_COLUMNS - set(bms_df.columns)
        raise RuntimeError(f"Missing bms_status columns: {sorted(missing)}")

    log_content = log_file.read_text(encoding="utf-8")

    if "Logging initialized" not in log_content:
        raise RuntimeError("Log file does not contain logging initialization message.")

    if "Raw trace logging enabled" not in log_content:
        raise RuntimeError("Log file does not contain raw trace initialization message.")

    if "Max cycles reached" not in log_content and "Scenario completed" not in log_content:
        raise RuntimeError("Log file contains neither max-cycle stop nor scenario completion.")

    tau = fit_tau_from_v_rc_raw(raw_df)
    print(f"[tau from v_rc_raw] {tau:.6g} s")

    if not (9.0 <= tau <= 10.5):
        raise RuntimeError(f"Unexpected tau value: {tau:.6g} s")

    assert_bms_tau_not_observable(bms_df)


def main() -> int:
    args = parse_args()

    if args.max_cycles <= 0:
        raise RuntimeError("--max-cycles must be positive for quick audit.")

    root = repo_root()
    scenario = root / args.scenario
    output_base = root / args.output_base

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = output_base / f"run_{stamp}"

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[repo] {root}")
    print(f"[scenario] {scenario}")
    print(f"[output_dir] {output_dir}")
    print(f"[max_cycles] {args.max_cycles}")

    run_simulator(
        root=root,
        scenario=scenario,
        output_dir=output_dir,
        max_cycles=args.max_cycles,
    )

    audit_outputs(
        output_dir=output_dir,
        expected_rows=args.max_cycles,
    )

    print("[PASS] quick audit completed successfully.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"[FAIL] {exc}")
        raise SystemExit(2)