# Ttfunds

## 简介
Ttfunds 是一个异步基金数据抓取、存储和分析工具包，支持：
- 实时净值查询
- 历史净值抓取
- 基金列表获取
- 数据库存储（SQLite）
- 数据可视化绘图
- 并发抓取（协程+多线程）
- 异步操作
- 可选代理池扩展

适合快速开发量化分析、数据可视化和科研用途。

---

## 安装

1. 使用 pip 安装依赖：
```bash
pip install -r requirements.txt
````

2. 安装 ttfunds：

* 从源码安装：

```bash
pip install -e .
```

* 或使用打包 zip：

```bash
python build_zip.py
pip install ttfunds.zip
```

---

## 快速开始

### 同步调用

```python
import ttfunds

# 配置参数（可选）
ttfunds.configure(
    timeout=15,
    retries=3,
    max_workers_realtime=5,
    max_workers_history=3
)

# 获取实时净值
data = ttfunds.get_fund_realtime("001186")
print(data)

# 获取历史净值
df = ttfunds.get_fund_history("001186")
print(df.head())

# 获取基金列表
fund_list = ttfunds.get_fund_list()
print(fund_list.head())

# 批量获取实时净值（协程+多线程）
realtime_data = ttfunds.batch_get_fund_realtime(["001186", "000001", "005827"])

# 批量获取历史净值（协程+多线程）
history_data = ttfunds.batch_get_fund_history(["001186", "000001"])

# 绘图
ttfunds.plot_nav("001186", df=df, savepath="nav.png")
```

### 异步调用

```python
import asyncio
from ttfunds.fetcher import (
    get_fund_realtime_async, 
    get_fund_history_async,
    get_fund_list_async,
    batch_get_fund_realtime_async,
    batch_get_fund_history_async
)
from ttfunds.plotter import plot_nav

async def main():
    code = "001186"
    realtime = await get_fund_realtime_async(code)
    print(realtime)
    df = await get_fund_history_async(code)
    print(df.head())
    fund_list = await get_fund_list_async()
    print(fund_list.head())
    
    # 批量获取
    realtime_batch = await batch_get_fund_realtime_async(["001186", "000001", "005827"])
    history_batch = await batch_get_fund_history_async(["001186", "000001"])
    
    plot_nav(code, df, savepath="nav_async.png")

asyncio.run(main())
```

---

## API 文档（中文）

### 基金数据接口

| 函数                                   | 参数          | 返回值          | 说明           |
| ------------------------------------ | ----------- | ------------ | ------------ |
| `get_fund_realtime(code: str)`       | `code` 基金代码 | dict         | 返回实时净值信息（同步） |
| `get_fund_realtime_async(code: str)` | `code` 基金代码 | dict         | 返回实时净值信息（异步） |
| `get_fund_history(code: str)`        | `code` 基金代码 | pd.DataFrame | 返回历史净值信息（同步） |
| `get_fund_history_async(code: str)`  | `code` 基金代码 | pd.DataFrame | 返回历史净值信息（异步） |
| `get_fund_list()`                    | 无           | pd.DataFrame | 返回基金列表（同步）    |
| `get_fund_list_async()`              | 无           | pd.DataFrame | 返回基金列表（异步）    |
| `batch_get_fund_realtime(codes, max_workers=None)` | `codes` 基金代码列表, `max_workers` 最大线程数 | dict | 批量获取实时净值（同步） |
| `batch_get_fund_realtime_async(codes, max_workers=None)` | `codes` 基金代码列表, `max_workers` 最大线程数 | dict | 批量获取实时净值（异步） |
| `batch_get_fund_history(codes, max_workers=None)` | `codes` 基金代码列表, `max_workers` 最大线程数 | dict | 批量获取历史净值（同步） |
| `batch_get_fund_history_async(codes, max_workers=None)` | `codes` 基金代码列表, `max_workers` 最大线程数 | dict | 批量获取历史净值（异步） |

### 配置接口

| 函数                          | 参数                         | 返回值  | 说明             |
| --------------------------- | -------------------------- | ---- | -------------- |
| `configure(**kwargs)`       | 配置参数                     | dict | 全局配置参数        |

配置参数说明：
- `timeout`: 请求超时时间（秒），默认10
- `retries`: 请求失败重试次数，默认3
- `max_workers_realtime`: 实时数据批量获取的最大线程数，默认5
- `max_workers_history`: 历史数据批量获取的最大线程数，默认3

### 数据库接口

| 函数                          | 参数                         | 返回值  | 说明             |
| --------------------------- | -------------------------- | ---- | -------------- |
| `save_realtime(code, data)` | `code` 基金代码，`data` dict    | None | 保存实时净值到数据库（异步） |
| `save_history(code, df)`    | `code` 基金代码，`df` DataFrame | None | 保存历史净值到数据库（异步） |
| `save_fund_list(df)`        | `df` DataFrame              | None | 保存基金列表到数据库（异步） |

### 绘图接口

| 函数                                                            | 参数                                  | 返回值  | 说明               |
| ------------------------------------------------------------- | ----------------------------------- | ---- | ---------------- |
| `plot_nav(code: str, df: pd.DataFrame, savepath: str = None)` | `code` 基金代码，`df` 数据，`savepath` 保存路径 | None | 绘制基金净值走势图，可保存或显示 |

---

## 测试

运行所有功能测试：

```bash
python examples/test_all.py
```

运行并发性能测试：

```bash
python examples/concurrent_demo.py
```

测试内容：

* 实时净值抓取
* 历史净值抓取
* 基金列表获取
* 数据库写入
* 并发抓取（协程+多线程）
* 绘图功能

---

## FAQ

* **代理失效**：当前包默认不使用代理，可在 `config.py` 配置 `proxy_api`。
* **SQLite 锁定**：并发写入数据库时请确保数据库文件路径可写，避免多进程同时操作。
* **matplotlib 中文乱码**：可在绘图前添加：

```python
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
```

* **性能优化**：使用批量获取函数可以显著提升数据获取速度，通过调整`max_workers`参数可以进一步优化性能。