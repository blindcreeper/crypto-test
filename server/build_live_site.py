"""Copy the public site into a fresh directory for the live VPS service."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "site"


def build(target: Path) -> None:
    if target.exists():
        raise FileExistsError(target)
    shutil.copytree(SOURCE, target)
    page = target / "crypto-neutral.html"
    html = page.read_text(encoding="utf-8")
    if "function renderSub(" not in html:
        raise RuntimeError("subaccount section missing")
    if "age<25" not in html or "age>=25" not in html:
        raise RuntimeError("health freshness checks missing")
    html = html.replace("age<25", "age<(sub?3:12)", 1)
    html = html.replace("age>=25", "age>=(sub?3:12)", 1)
    main, sub = html.split("function renderSub(", 1)
    main = main.replace("age>=25", "age>=12").replace("超过 25 分钟", "超过 12 分钟")
    sub = sub.replace("age>=25", "age>=3").replace("超过 25 分钟", "超过 3 分钟")
    html = main + "function renderSub(" + sub
    old = "setInterval(()=>{if(!$('refresh').disabled)load()},60000)"
    if old not in html:
        raise RuntimeError("page polling marker missing")
    html = html.replace(old, "setInterval(()=>{if(!$('refresh').disabled)load()},15000)")
    html, removed = re.subn(r'<a class="refresh" id="trigger-sync"[^>]*>.*?</a>', "", html, count=1)
    if removed != 1 or "async function manualRefresh(){" not in html:
        raise RuntimeError("legacy manual publish controls missing")
    html = html.replace(
        "const isLocalDashboard=['127.0.0.1','localhost'].includes(location.hostname);\n"
        "$('refresh').textContent=isLocalDashboard?'↻ 刷新数据':'↻ 检查最新快照';\n"
        "$('trigger-sync').hidden=isLocalDashboard;\n"
        "$('trigger-sync').addEventListener('click',()=>text('refresh-feedback','在 GitHub 页面点击“Run workflow”；发布完成后，本页会自动读取新快照。'));\n",
        "$('refresh').textContent='↻ 刷新数据';\n",
    )
    start = html.index("async function manualRefresh(){")
    end = html.index("\n", start)
    html = html[:start] + (
        "async function manualRefresh(){if(loading)return;const before=latestSnapshot;"
        "text('refresh-feedback','');$('refresh').textContent='↻ 正在读取服务器…';"
        "try{const ok=await load();text('refresh-feedback',!ok?'读取快照失败，请查看页面错误提示。':"
        "latestSnapshot!==before?'已读取更新的数据。':'服务器暂未生成新快照。')}"
        "finally{$('refresh').textContent='↻ 刷新数据'}}"
    ) + html[end:]
    page.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    build(parser.parse_args().target)
