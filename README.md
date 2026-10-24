# Crypto Test 策略站点

## 在线页面

- [VPS 实盘看板](https://dashboard.add1cter.dpdns.org/crypto-neutral.html)：服务器每分钟导出一次经过筛选的账户快照，页面每 15 秒检查更新；行情缓存每 5 分钟刷新。看板只读，公开可访问。
- [GitHub Pages 镜像](https://blindcreeper.github.io/crypto-test/crypto-neutral.html)：GitHub Actions 尝试定时获取快照并发布；定时任务可能延迟，页面会显示数据时间。
- [策略介绍](https://blindcreeper.github.io/crypto-test/)：GitHub Pages 上的静态介绍页面。

实盘交易服务独立运行，不依赖这两个网站。看板上的账户权益、持仓和盈亏为公开信息，请勿在 `site/` 中加入交易密钥或完整执行状态。

## 仓库内容

- `site/`：公开页面及经过筛选的快照，也是 GitHub Pages 的发布目录。
- `build_public_site.py`：从本地研究目录或 GitHub Actions 下载的原始快照生成公开文件，仅保留页面需要的字段。
- `refresh_candles.py`：从 OKX 公共接口刷新行情缓存；支持 `STRATEGY_CANDLES_PROXY`，校验行情时效后原子替换缓存。
- `server/build_live_site.py`：从 `site/` 生成 VPS 版本的页面，调整数据过期阈值与刷新间隔，去除 GitHub Pages 的手动发布入口。
- `server/live_dashboard_server.py`：仅监听 `127.0.0.1:8765` 的只读网页服务。
- `server/publish_live_dashboard.py`：从两个策略的运行目录导出经过筛选的状态及权益历史。
- `server/strategy-dashboard-*.service` 和 `server/strategy-dashboard-*.timer`：VPS 网页服务、每分钟快照导出和每 5 分钟行情刷新任务的 systemd 配置。

公开快照包含余额、持仓、收益、委托次数与手续费、近期风险事件；不包含交易所订单 ID、客户端 ID、待执行委托详情或 API 凭证。服务端导出使用 `build_public_site.py` 中同一套字段筛选函数。图上的子账户异常区间依据已确认的调仓记录标注；期间权益快照继续记录。

## 更新 VPS 看板

`server/build_live_site.py` 的目标目录必须尚不存在。它复制 `site/` 后生成动态看板页面；部署目录为 `/opt/strategy-dashboard/site`。VPS 上的 `build_public_site.py`、`refresh_candles.py`、`live_dashboard_server.py` 和 `publish_live_dashboard.py` 分别放在 `/opt/strategy-dashboard/` 下，systemd 配置放在 `/etc/systemd/system/`。

网页服务通过现有 Cloudflare Tunnel 主机名路由连接到 `http://localhost:8765`。推送 GitHub 仓库只会触发 GitHub Pages 发布；更新 VPS 页面仍需部署生成后的页面。网页服务读取 `site/`，快照导出任务只写入 `site/afml-study/results/_server_live/`。

## GitHub Pages 镜像

仓库的 `.github/workflows/pages.yml` 在推送时发布 `site/`，并配置了每 5 分钟一次的定时尝试。实际触发时间由 GitHub Actions 决定，不能当作实时监控频率。

定时刷新需要 Actions secrets `SNAPSHOT_SSH_KEY` 和 `SNAPSHOT_SSH_DESTINATION`。服务器上与私钥配对的公钥必须限制为 `server/export_snapshots.py` 固定命令，并禁用转发与 PTY；不要把无限制的 root SSH 密钥放进仓库 secrets。工作流固定服务器 Ed25519 主机密钥，只读取六个快照文件，在临时 runner 中筛选后发布。行情请求失败时，已发布的旧缓存仍可显示。

GitHub Pages 页面会显示源数据时间，并在数据超过 25 分钟时提示过期。GitHub 可能在公开仓库连续 60 天没有活动后禁用定时工作流，届时需要在 Actions 中重新启用。

从本机研究目录重新生成静态内容时，在 `D:\0817` 运行：

```powershell
python github-pages-strategy/build_public_site.py
```
