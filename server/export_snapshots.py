"""Restricted SSH command: stream only the six dashboard snapshot files.

Install on the trading server and bind a dedicated SSH key to this command in
authorized_keys. This script never accepts paths or a caller-supplied command.
"""

from __future__ import annotations

import io
import json
import sys
import tarfile
from pathlib import Path


FILES = {
    "week33_status.json": Path("/root/week22-okx-4h-live/run/status.json"),
    "week33_state.json": Path("/root/week22-okx-4h-live/run/state.json"),
    "week33_equity_history.csv": Path("/root/week22-okx-4h-live/run/week33_equity_history.csv"),
    "week42_status.json": Path("/root/week42-listfold-live/run/status.json"),
    "week42_state.json": Path("/root/week42-listfold-live/run/state.json"),
    "week42_equity_history.csv": Path("/root/week42-listfold-live/run/week42_equity_history.csv"),
}


def main() -> None:
    payloads = {name: path.read_bytes() for name, path in FILES.items()}
    for prefix in ("week33", "week42"):
        status = json.loads(payloads[f"{prefix}_status.json"])
        state = json.loads(payloads[f"{prefix}_state.json"])
        if status.get("strategy_version") != state.get("strategy_version"):
            raise ValueError(f"{prefix}: status/state version mismatch")
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|gz") as archive:
        for name, content in payloads.items():
            member = tarfile.TarInfo(name)
            member.size = len(content)
            member.mode = 0o600
            archive.addfile(member, io.BytesIO(content))


if __name__ == "__main__":
    main()
