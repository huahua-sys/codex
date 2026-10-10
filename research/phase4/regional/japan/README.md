# 日本地域研究复现与证据边界

只创建Phase4日本文件，不改旧价格、旧预测、主ledger或已有冻结结果。本地域不读取新增未来价格。

建议阅读：`MARKET_ECOLOGY_JAPAN.md` → `MARGINAL_PLAYER_MAP_JAPAN.md` → `events.json` → `missing_slots.json` → `SOURCE_MANIFEST.json`。

选择锁：`selection.v001.json` SHA由`selection.v001.sha256`记录。219 BOJstatement等序10；11 GPIF行动/披露等序10；3治理原版本全部；8 JPX公司回购原目录记录全部；52 foreign周报等序10缺发布日，全部只入缺失槽。15parents /30dates /13years不是独立N估计。31合格日期记录只有8期间实际回购数（5正、3零），另23规则/公告/其他披露不能当作实流。

原source由`acquire_japan_sources.py`通过urllib下载，日期目录解析与等序选择在读原事件内容/任何新价格之前保存。下载错误原样记录。`build_japan_events.py`解析已锁选择的原字节，并作SHA检查，不取市场价格。`build_japan_maps.py`生成22类×22字段机制地图。这些acquisition/build程序是原过程留档，**不要在冻结项目覆盖式重跑**；若要从网络复现，应在新目录/新版本保存并比较原SHA，当前网站变更应显式记录vintage drift。

数据读取依赖Python3标准库及系统`pdftotext`，无需pandas/大型模型。XLSX以zip+XML抽取sharedStrings，只作原持仓报告确认，不推导净流量。原文件、派生text和清单可离线审阅。

离线验原bytes：

```python
import hashlib, json, pathlib
root = pathlib.Path('/workspace/investment-research-lab')
rows = json.loads((root/'research/phase4/sources/japan/SOURCE_MANIFEST.json').read_text())
for row in rows:
    if row['status'] == 'FETCHED':
        assert hashlib.sha256((root/row['path']).read_bytes()).hexdigest() == row['sha256']
events = json.loads((root/'research/phase4/regional/japan/events.json').read_text())
assert len(events) == 31
assert all(e['available_at'].endswith('23:59:59+09:00') for e in events)
assert sum(e['flow_size'] is not None and e['flow_size']['value'] == 0 for e in events) == 3
```

日期精度是保守JST日末；官方日期证明不是独立WebArchive版本证明。GPIF时滞不能回填会计期末；zero回购不能删除；BOJ2024停止买与2025规划卖没有当作实际出售。信用/盈利缺失保持null。研究收益由root按预定宽基NIKKEI开放式实验另处理，不表示日本个股alpha。
