import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def fit_tau(csv_file):
    df = pd.read_csv(csv_file)

    # 找 rest 开始点（I=0）
    rest_idx = df[df["pack_current"] == 0.0].index[0]

    df_rest = df.iloc[rest_idx:].copy()
    df_rest["t"] = np.arange(len(df_rest)) * 0.1  # cycle_time

    V = df_rest["pack_voltage"].values
    V_inf = V[-1]

    y = V_inf - V
    y = np.clip(y, 1e-6, None)

    logy = np.log(y)

    slope, _ = np.polyfit(df_rest["t"], logy, 1)

    tau = -1 / slope

    print(f"Estimated tau: {tau:.2f} s")

    plt.plot(df_rest["t"], V, label="Voltage")
    plt.title(f"Relaxation, tau ≈ {tau:.2f} s")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (V)")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    import sys
    fit_tau(sys.argv[1])