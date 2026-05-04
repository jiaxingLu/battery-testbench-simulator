import os
import subprocess
import sys
from pathlib import Path

import pandas as pd


def test_runtime_cli_writes_all_output_layers(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]

    output_dir = tmp_path / "runtime_outputs"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    command = [
        sys.executable,
        "-m",
        "battery_testbench_sim.main",
        "--scenario",
        str(repo_root / "configs" / "scenario_discharge.yaml"),
        "--no-sleep",
        "--max-cycles",
        "10",
        "--output-dir",
        str(output_dir),
    ]

    result = subprocess.run(
        command,
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
    )

    assert result.returncode == 0, (
        "Runtime command failed.\n"
        f"STDOUT:\n{result.stdout}\n\n"
        f"STDERR:\n{result.stderr}"
    )

    log_files = sorted(output_dir.glob("run_*.log"))
    raw_trace_files = sorted(output_dir.glob("*_raw_trace.csv"))
    bms_status_files = sorted(output_dir.glob("*_bms_status.csv"))

    assert len(log_files) == 1
    assert len(raw_trace_files) == 1
    assert len(bms_status_files) == 1

    log_file = log_files[0]
    raw_trace_file = raw_trace_files[0]
    bms_status_file = bms_status_files[0]

    assert raw_trace_file.stem.startswith(log_file.stem)
    assert bms_status_file.stem.startswith(log_file.stem)

    raw_df = pd.read_csv(raw_trace_file)
    bms_df = pd.read_csv(bms_status_file)

    assert len(raw_df) == 10
    assert len(bms_df) == 10

    assert {
        "cycle",
        "time_s",
        "soc",
        "pack_current",
        "ocv_raw",
        "v_rc_raw",
        "pack_voltage_raw",
        "state",
        "fault_level",
    }.issubset(raw_df.columns)

    assert {
        "timestamp",
        "signal",
        "pack_voltage",
        "pack_current",
        "soc",
        "state",
        "fault",
    }.issubset(bms_df.columns)

    log_content = log_file.read_text(encoding="utf-8")

    assert "Logging initialized" in log_content
    assert "Raw trace logging enabled" in log_content
    assert "Max cycles reached: 10" in log_content