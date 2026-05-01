from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


class CSVLogger:
    def __init__(self, file_path: Path, fieldnames: list[str]) -> None:
        self.file_path = file_path
        self.fieldnames = fieldnames

        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        self._file = self.file_path.open("w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.fieldnames)
        self._writer.writeheader()

    def write_row(self, row: dict[str, Any]) -> None:
        self._writer.writerow(row)
        self._file.flush()

    def close(self) -> None:
        self._file.close()