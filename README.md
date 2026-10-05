# Strategy GitHub Pages site

## 在线访问

- [策略介绍首页](https://blindcreeper.github.io/crypto-test/)
- [实盘监控页面](https://blindcreeper.github.io/crypto-test/crypto-neutral.html)

网页公开可访问。实盘监控页面会显示数据时间；数据更新依赖刷新任务。

This is the public bundle for the strategy introduction, technical notes, and
read-only live monitor. `site/index.html` opens the introduction; the monitor is
`site/crypto-neutral.html`.

## Refresh the local bundle

From `D:\0817`:

```powershell
python github-pages-strategy/build_public_site.py
```

The builder copies only the pages and linked research artifacts listed in
`build_public_site.py`. It creates a small browser-facing snapshot of the two
accounts rather than publishing the full execution-state files. The public
snapshot includes balances, positions, returns, order counts/fees, and recent
risk events; it excludes exchange order IDs, client IDs, pending-order details,
API credentials, and the rest of the local research directory.

## GitHub Pages setup

Use the dedicated public repository `blindcreeper/crypto-test` with
this directory as its repository root. In **Settings → Pages**, choose
**GitHub Actions** as the publishing source. The workflow publishes `site/` on
push and attempts a fresh snapshot every five minutes.

The first push publishes the checked-in snapshot. For scheduled updates, add
repository Actions secrets named `SNAPSHOT_SSH_KEY` (a dedicated SSH private
key) and `SNAPSHOT_SSH_DESTINATION` (the SSH user and host). On the trading
server, the matching public key must be restricted
in `root/.ssh/authorized_keys` to the fixed command in
`server/export_snapshots.py`, with forwarding and PTY disabled. Do not use an
unrestricted root SSH key as the repository secret.

The workflow pins the server's existing Ed25519 host key and reads only six
snapshot files through the restricted command. Raw files exist only inside the
ephemeral Actions runner. `build_public_site.py` strips execution-only fields
before deployment. The candle chart refreshes from OKX public market data;
when that request fails, the last candle cache remains visible.

GitHub Actions schedules can be delayed, so the page shows the source snapshot
time and treats data older than 25 minutes as stale. The public page is
informational; live trading continues on the server independently of Pages.
GitHub can disable scheduled workflows in a public repository after 60 days
without repository activity; re-enable this workflow in Actions if that occurs.
