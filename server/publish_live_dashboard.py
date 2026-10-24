"""Publish the same sanitized monitor fields as the public Pages site.

Run as root from a timer. The web process reads only the output directory.
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path("/opt/strategy-dashboard")
DATA = ROOT / "site/afml-study/results/_server_live"
SOURCES = {
    "week33": Path("/root/week22-okx-4h-live/run"),
    "week42": Path("/root/week42-listfold-live/run"),
}
sys.path.insert(0, str(ROOT))
from build_public_site import public_state, public_status  # noqa: E402


def write_atomic(path: Path, payload: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def publish() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    for prefix, source in SOURCES.items():
        status = json.loads((source / "status.json").read_text(encoding="utf-8-sig"))
        state = json.loads((source / "state.json").read_text(encoding="utf-8-sig"))
        if status.get("strategy_version") != state.get("strategy_version"):
            raise ValueError(f"{prefix}: status/state version mismatch")
        history_path = source / f"{prefix}_equity_history.csv"
        with history_path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        fields = ("timestamp_utc", "equity_usdt", "source")
        if not rows or not set(fields).issubset(rows[0]):
            raise ValueError(f"{prefix}: invalid equity history")
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})
        content = {
            f"{prefix}_status.json": json.dumps(public_status(status), ensure_ascii=False, separators=(",", ":")).encode(),
            f"{prefix}_state.json": json.dumps(public_state(state), ensure_ascii=False, separators=(",", ":")).encode(),
            f"{prefix}_equity_history.csv": output.getvalue().encode(),
        }
        for name, payload in content.items():
            write_atomic(DATA / name, payload)


if __name__ == "__main__":
    publish()
