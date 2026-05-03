#!/usr/bin/env python3

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


def detect_csv_type(df: pd.DataFrame) -> str:
    if {"ocv_raw", "v_rc_raw", "pack_voltage_raw"}.issubset(df.columns):
        return "raw_trace"

    if {"timestamp", "pack_voltage", "pack_current", "soc", "state", "fault"}.issubset(
        df.columns
    ):
        return "bms_status"

    return "unknown"


def infer_x_axis(df: pd.DataFrame):
    if "time_s" in df.columns:
        return df["time_s"], "Time (s)"

    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        if ts.notna().all():
            t = (ts - ts.iloc[0]).dt.total_seconds()
            return t, "Time since start (s)"

    return df.index, "Sample index"


def plot_bms_status(df: pd.DataFrame, csv_path: Path) -> None:
    x, x_label = infer_x_axis(df)

    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(10, 8))

    axes[0].plot(x, df["pack_voltage"], marker="o")
    axes[0].set_ylabel("Pack voltage (V)")
    axes[0].set_title("CAN-decoded BMS status")
    axes[0].grid(True)

    axes[1].plot(x, df["pack_current"], marker="o")
    axes[1].set_ylabel("Pack current (A)")
    axes[1].grid(True)

    axes[2].plot(x, df["soc"], marker="o", label="SOC")
    axes[2].plot(x, df["state"], marker="x", label="state")
    axes[2].plot(x, df["fault"], marker="s", label="fault")
    axes[2].set_ylabel("SOC / state / fault")
    axes[2].set_xlabel(x_label)
    axes[2].grid(True)
    axes[2].legend()

    fig.suptitle(csv_path.name)
    fig.tight_layout()
    plt.show()


def plot_raw_trace(df: pd.DataFrame, csv_path: Path) -> None:
    x, x_label = infer_x_axis(df)

    fig, axes = plt.subplots(4, 1, sharex=True, figsize=(10, 10))

    axes[0].plot(x, df["pack_voltage_raw"], marker="o", label="pack_voltage_raw")
    axes[0].plot(x, df["ocv_raw"], marker=".", label="ocv_raw")
    axes[0].set_ylabel("Voltage (V)")
    axes[0].set_title("Raw physical trace before CAN quantization")
    axes[0].grid(True)
    axes[0].legend()

    axes[1].plot(x, df["v_rc_raw"], marker="o", label="v_rc_raw")
    axes[1].set_ylabel("v_rc_raw (V)")
    axes[1].grid(True)
    axes[1].legend()

    axes[2].plot(x, df["pack_current"], marker="o", label="pack_current")
    axes[2].set_ylabel("Current (A)")
    axes[2].grid(True)
    axes[2].legend()

    axes[3].plot(x, df["soc"], marker="o", label="SOC")
    axes[3].plot(x, df["state"], marker="x", label="state")
    axes[3].plot(x, df["fault_level"], marker="s", label="fault_level")
    axes[3].set_ylabel("SOC / state / fault")
    axes[3].set_xlabel(x_label)
    axes[3].grid(True)
    axes[3].legend()

    fig.suptitle(csv_path.name)
    fig.tight_layout()
    plt.show()


def plot_csv(csv_file: str) -> int:
    csv_path = Path(csv_file)
    df = pd.read_csv(csv_path)

    csv_type = detect_csv_type(df)

    print(f"[file] {csv_path}")
    print(f"[rows] {len(df)}")
    print(f"[columns] {df.columns.tolist()}")
    print(f"[detected_type] {csv_type}")

    if csv_type == "bms_status":
        plot_bms_status(df, csv_path)
        return 0

    if csv_type == "raw_trace":
        plot_raw_trace(df, csv_path)
        return 0

    print("ERROR: Unknown CSV type.")
    print("Expected either:")
    print("  - bms_status CSV with timestamp, pack_voltage, pack_current, soc, state, fault")
    print("  - raw_trace CSV with time_s, ocv_raw, v_rc_raw, pack_voltage_raw")
    return 2


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/plot_bms_csv.py <csv_file>")
        raise SystemExit(1)

    raise SystemExit(plot_csv(sys.argv[1]))