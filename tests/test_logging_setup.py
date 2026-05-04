import logging
from pathlib import Path

from battery_testbench_sim.infrastructure.logging_setup import setup_logging


def test_setup_logging_writes_to_configured_output_dir(tmp_path):
    output_dir = tmp_path / "custom_logs"

    log_file = setup_logging(output_dir=output_dir)

    assert log_file.parent == output_dir
    assert log_file.name.startswith("run_")
    assert log_file.name.endswith(".log")
    assert log_file.exists()

    logging.getLogger("test").info("hello from test")

    content = log_file.read_text(encoding="utf-8")
    assert "Logging initialized" in content
    assert "hello from test" in content