"""Install the dedicated read-only Pages export key on the trading server.

Run once as root after copying export_snapshots.py and the new public key to
/root/strategy_pages_export.py and /root/strategy_pages_export.pub.
"""

from __future__ import annotations

import os
from pathlib import Path


PUBLIC_KEY = Path("/root/strategy_pages_export.pub")
AUTHORIZED_KEYS = Path("/root/.ssh/authorized_keys")
COMMAND = "/usr/bin/python3 /root/strategy_pages_export.py"
TAG = "github-pages-readonly-20261005"


def main() -> None:
    parts = PUBLIC_KEY.read_text(encoding="ascii").strip().split()
    if len(parts) != 3 or parts[0] != "ssh-ed25519" or parts[2] != TAG:
        raise ValueError("unexpected dedicated public key")
    key = " ".join(parts)
    line = f'restrict,command="{COMMAND}" {key}'
    old = AUTHORIZED_KEYS.read_text(encoding="utf-8") if AUTHORIZED_KEYS.exists() else ""
    lines = [entry for entry in old.splitlines() if TAG not in entry]
    lines.append(line)
    temporary = AUTHORIZED_KEYS.with_name("authorized_keys.strategy_pages_tmp")
    temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.chmod(temporary, 0o600)
    os.replace(temporary, AUTHORIZED_KEYS)
    print("Restricted Pages export key installed")


if __name__ == "__main__":
    main()
