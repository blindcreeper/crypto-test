"""Build the public GitHub Pages site from the local strategy frontend.

The published monitor JSON is intentionally smaller than the execution state:
it contains only fields read by crypto-neutral.html and omits order IDs and
pending-order details. Run with --skip-static on GitHub Actions after fetching
fresh snapshots from the trading server.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parent
SITE = HERE / "site"
DATA_PATH = Path("afml-study/results/_server_live")

STATIC_FILES = [
    "crypto-neutral.html",
    "strategy-intro.html",
    "strategy-details.html",
    "afml-study/notebooks/12_week33_live_strategy_research.ipynb",
    "afml-study/reports/week33_strategy_research.md",
    "afml-study/reports/week42_strategy_research.md",
    "afml-study/reports/week34_residual_ic_audit.md",
    "afml-study/reports/week46_hourly_dollarbar_ab.md",
    "afml-study/results/week33_strategy_oof_comparison.png",
    "afml-study/results/week33_neutrality_comparison.png",
    "afml-study/results/week33_short_only_nonbear.png",
]
ASSET_FILES = [
    "components.css", "interactions.js", "layout.css", "monitor-headings.js",
    "pnl-attribution.svg", "pygments.css", "rank-ic.svg", "site-switch.css",
    "theme-init.js", "tokens.css",
]


def pick(source: dict, keys: tuple[str, ...]) -> dict:
    return {key: source[key] for key in keys if key in source}


def public_status(raw: dict) -> dict:
    last = raw.get("last") or {}
    checks = raw.get("arm_checks") or {}
    marks = {
        symbol: pick(mark, ("last", "return", "pnl_usdt"))
        for symbol, mark in (last.get("marks") or {}).items()
    }
    return {
        **pick(raw, ("strategy_version", "generated_at", "real_enabled", "last_signal_bar")),
        "arm_checks": {"运行校验": bool(checks) and all(value is True for value in checks.values())},
        "risk_limits": pick(raw.get("risk_limits") or {}, (
            "max_total_equity_fraction", "max_symbol_equity_fraction",
            "position_stop_fraction", "account_unrealized_stop_equity_fraction",
        )),
        "account": pick(raw.get("account") or {}, ("equity_usdt", "available_usdt")),
        "positions": {
            symbol: pick(position, ("quantity",))
            for symbol, position in (raw.get("positions") or {}).items()
        },
        "last": {
            **pick(last, ("action", "unrealized_pnl_usdt")),
            "marks": marks,
        },
    }


def public_state(raw: dict) -> dict:
    pending_count = len(raw.get("pending_intents") or {}) + int(bool(raw.get("pending_intent")))
    return {
        **pick(raw, ("strategy_version", "realized_pnl_usdt")),
        "positions": {
            symbol: pick(position, ("quantity", "entry_time"))
            for symbol, position in (raw.get("positions") or {}).items()
        },
        "orders": [
            pick(order, ("symbol", "contract_value", "filled_qty", "fee"))
            for order in (raw.get("orders") or [])
        ],
        "risk_events": [
            pick(event, ("time", "symbol", "reason", "closed_qty", "reduced_qty", "gross_pnl_usdt"))
            for event in (raw.get("risk_events") or [])[-10:]
        ],
        "pending_intents": {str(index): True for index in range(pending_count)},
    }


def copy_static() -> None:
    for relative in STATIC_FILES:
        source = WORKSPACE / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        target = SITE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for name in ASSET_FILES:
        source = WORKSPACE / "strategy-intro-assets" / name
        target = SITE / "strategy-intro-assets" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    shutil.copy2(WORKSPACE / "strategy-intro.html", SITE / "index.html")
    (SITE / ".nojekyll").touch()

    # The public website cannot ask visitors to run a Windows sync command.
    for page in (SITE / "crypto-neutral.html",):
        html = page.read_text(encoding="utf-8")
        html = html.replace("请运行“启动前端.cmd”同步服务器。", "请稍后刷新；若持续异常，请检查数据发布任务。")
        html = html.replace("请检查本地同步和服务器风控定时器。", "请检查数据发布任务和服务器风控定时器。")
        html = html.replace("age<12", "age<25").replace("age>=12", "age>=25")
        html = html.replace("超过 12 分钟", "超过 25 分钟")
        html = html.replace("请检查本地同步和服务器定时器。", "请检查数据发布任务和服务器定时器。")
        html = html.replace("setInterval(load,30000)", "setInterval(load,60000)")
        page.write_text(html, encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def copy_public_data(raw_dir: Path) -> None:
    target = SITE / DATA_PATH
    target.mkdir(parents=True, exist_ok=True)
    for prefix in ("week33", "week42"):
        raw_status = json.loads((raw_dir / f"{prefix}_status.json").read_text(encoding="utf-8-sig"))
        raw_state = json.loads((raw_dir / f"{prefix}_state.json").read_text(encoding="utf-8-sig"))
        if raw_status.get("strategy_version") != raw_state.get("strategy_version"):
            raise ValueError(f"{prefix}: status/state strategy versions differ")
        write_json(target / f"{prefix}_status.json", public_status(raw_status))
        write_json(target / f"{prefix}_state.json", public_state(raw_state))

        history = raw_dir / f"{prefix}_equity_history.csv"
        with history.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if not rows or not {"timestamp_utc", "equity_usdt", "source"}.issubset(rows[0]):
            raise ValueError(f"{prefix}: invalid equity history")
        with (target / history.name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["timestamp_utc", "equity_usdt", "source"])
            writer.writeheader()
            writer.writerows({key: row[key] for key in writer.fieldnames} for row in rows)

    candles = raw_dir / "week33_candles.json"
    if not candles.is_file():
        candles = target / "week33_candles.json"
    payload = json.loads(candles.read_text(encoding="utf-8-sig"))
    if payload.get("schema_version") != 2 or not isinstance(payload.get("symbols"), dict):
        raise ValueError("week33: invalid candle payload")
    write_json(target / candles.name, payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=WORKSPACE / DATA_PATH)
    parser.add_argument("--skip-static", action="store_true")
    args = parser.parse_args()
    if not args.skip_static:
        if SITE.exists():
            shutil.rmtree(SITE)
    SITE.mkdir(exist_ok=True)
    if not args.skip_static:
        copy_static()
    copy_public_data(args.data_dir)
    print(f"Public site ready: {SITE}")


if __name__ == "__main__":
    main()
