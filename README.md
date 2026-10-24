# Crypto Test · 多币种策略研究

这个项目研究一个具体问题：**能否利用已确认的行情信息，判断未来一段时间哪些加密资产相对更强、哪些相对更弱？**研究从单币涨跌预测转向跨币种比较，再据此构建多空组合。预测分数用于排序，不代表确定的收益。

## 阅读入口

- [策略介绍](https://blindcreeper.github.io/crypto-test/)：用直观例子解释预测目标、多空收益、交易流程和主要风险。
- [技术说明](https://blindcreeper.github.io/crypto-test/strategy-details.html)：数据、特征、样本外检验及两套策略的规则。
- [账户监控](https://dashboard.add1cter.dpdns.org/crypto-neutral.html)：主账户与子账户的权益、持仓、委托和近期风险事件；页面会标明数据时间。

## 研究内容

1. **相对强弱预测。**从历史价格、波动和成交等信息构建特征，比较不同币种未来约 12 小时的表现。
2. **多空组合。**根据模型排序选择相对较强和较弱的币种，分别建立多头与空头；目标是分散单一币种的影响，而不是保证市场风险完全抵消。
3. **真实执行检验。**将样本外模拟与账户实际成交分开观察，重点核对手续费、资金费、未成交委托、仓位偏离和策略中断等影响。

当前公开说明涵盖 Week33 双分类策略与 Week47 ListFold 神经网络策略。两者的特征和仓位规则不同，具体设置以各自的[技术说明](https://blindcreeper.github.io/crypto-test/strategy-details.html)为准。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `site/index.html`、`site/strategy-intro.html` | 面向读者的策略介绍 |
| `site/strategy-details.html` | 方法、样本外结果与实盘证据边界 |
| `site/crypto-neutral.html` | 公开账户监控页面 |
| `site/afml-study/` | 研究笔记、报告、图表与公开快照 |
| `build_public_site.py`、`refresh_candles.py`、`server/` | 公开数据筛选与页面更新辅助代码 |

本仓库展示研究材料和经过筛选的监控数据，不包含交易密钥、模型权重或完整执行状态。图表中的历史模拟结果与真实账户收益属于不同口径；评估策略时应分别查看，并考虑交易成本和执行落差。

## 研究资料

- [Week33 Jupyter 笔记](site/afml-study/notebooks/12_week33_live_strategy_research.ipynb)
- [Week33 策略研究报告](site/afml-study/reports/week33_strategy_research.md)
- [ListFold 策略研究报告](site/afml-study/reports/week42_strategy_research.md)
