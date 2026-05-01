from __future__ import annotations

import sys
import pandas as pd
import matplotlib.pyplot as plt


def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_bms_csv.py <csv_file>")
        return

    csv_file = sys.argv[1]

    df = pd.read_csv(csv_file)

    df["t"] = pd.to_datetime(df["timestamp"])
    t0 = df["t"].iloc[0]
    df["t"] = (df["t"] - t0).dt.total_seconds()

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # Voltage
    axes[0].plot(df["t"], df["pack_voltage"])
    axes[0].set_ylabel("Voltage (V)")
    axes[0].grid()

    # SOC
    axes[1].plot(df["t"], df["soc"])
    axes[1].set_ylabel("SOC (%)")
    axes[1].grid()

    # State / Fault
    axes[2].step(df["t"], df["state"], label="state", where="post")
    axes[2].step(df["t"], df["fault"], label="fault", where="post")
    axes[2].set_ylabel("State / Fault")
    axes[2].legend()
    axes[2].grid()

    axes[2].set_xlabel("Time (s)")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()