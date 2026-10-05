"""Refresh the public Week33 4-hour candle cache from OKX market data."""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


DATA = Path(__file__).resolve().parent / "site/afml-study/results/_server_live"
STATE = DATA / "week33_state.json"
OUT = DATA / "week33_candles.json"
CORE = {f"{asset}-USDT-SWAP" for asset in ("BTC", "ETH", "SOL", "BNB", "DOGE", "XRP")}


def fetch(symbol: str) -> list[dict]:
    query = urllib.parse.urlencode({"instId": symbol, "bar": "4H", "limit": "100"})
    request = urllib.request.Request(
        f"https://www.okx.com/api/v5/market/candles?{query}",
        headers={"User-Agent": "strategy-pages/1.0"},
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        body = json.load(response)
    if body.get("code") != "0":
        raise ValueError(f"{symbol}: OKX code {body.get('code')}")
    rows = body.get("data") or []
    candles = [
        {
            "time": int(row[0]) // 1000,
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "volume": float(row[7]),
            "confirmed": str(row[8]) == "1",
        }
        for row in rows if len(row) >= 9
    ]
    if len(candles) < 10:
        raise ValueError(f"{symbol}: fewer than 10 candles")
    return sorted(candles, key=lambda row: row["time"])


def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else {}
    symbols = sorted(CORE | set(state.get("positions") or {}))
    previous = old.get("symbols") or {}
    current = {symbol: previous[symbol] for symbol in symbols if symbol in previous}
    now = time.time()
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(fetch, symbol): symbol for symbol in symbols}
        for job in as_completed(jobs):
            symbol = jobs[job]
            try:
                current[symbol] = {"fetched_at": now, "candles": job.result()}
            except Exception as exc:
                print(f"Candle refresh skipped for {symbol}: {exc}")
    payload = {"schema_version": 2, "generated_at": now, "bar": "4H", "symbols": current}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Candles available for {len(current)}/{len(symbols)} symbols")


if __name__ == "__main__":
    main()
