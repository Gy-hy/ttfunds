### 天天基金数据接口文档  
**版本**: 0.1.0  
**最后更新**: 2025-08-16  
**作者**: huangyancqie@gmail.com / [github](https://github.com/Gy-hy)  

---

### 🧩 **1. 核心方法说明**

#### **1.1 获取实时基金净值**  
```python
get_fund_realtime(fund_code: str) -> Dict[str, str]
```  
- **功能**: 获取基金最新交易日的单位净值、估算净值及涨跌幅等实时数据。  
- **输入参数**:  
  | 参数名       | 类型   | 必填 | 说明                     |  
  |--------------|--------|------|--------------------------|  
  | `fund_code`  | `str`  | 是   | 6位基金代码（如 `"001186"`） |  

- **返回字段**:  
  | 字段名     | 类型   | 说明                     |  
  |------------|--------|--------------------------|  
  | `fundcode` | `str`  | 基金代码                 |  
  | `name`     | `str`  | 基金名称                 |  
  | `jzrq`     | `str`  | 净值日期（格式 `YYYY-MM-DD`） |  
  | `dwjz`     | `float`| 单位净值                 |  
  | `gsz`      | `float`| 估算净值                 |  
  | `gszzl`    | `float`| 估算涨跌幅（百分比，如 `0.61`） |  
  | `gztime`   | `str`  | 估值时间（格式 `YYYY-MM-DD HH:MM`） |  

- **示例**:  
  ```python
  from ttfunds.fetcher import get_fund_realtime
  
  data = get_fund_realtime("001186")
  print(data)  # 输出: {'fundcode':'001186', 'name':'富国文体健康股票A', ...}
  ``` 

---

#### **1.2 获取历史净值数据**  
```python
get_fund_history(fund_code: str) -> pd.DataFrame
```  
- **功能**: 获取基金历史单位净值、累计净值及回报率。  
- **输入参数**:  
  | 参数名       | 类型   | 必填 | 说明                     |  
  |--------------|--------|------|--------------------------|  
  | `fund_code`  | `str`  | 是   | 6位基金代码              |  

- **返回字段**（DataFrame 格式）:  
  | 列名          | 类型     | 说明                     |  
  |---------------|----------|--------------------------|  
  | `x`           | `float`  | 时间戳                   |  
  | `y`           | `float`  | 单位净值                 |  
  | `equityReturn`| `float`  | 日回报率（百分比）       |  
  | `unitMoney`   | `str`    | 单位货币                 |  
  | `cumulative`  | `float`  | 累计净值                 |  

- **示例**:  
  ```python
  from ttfunds.fetcher import get_fund_history
  
  df = get_fund_history("001186")
  print(df.head())  # 输出前5行历史数据
  ```

---

#### **1.3 获取全量基金列表**  
```python
get_fund_list() -> pd.DataFrame
```  
- **功能**: 获取所有基金的基本信息（代码、简称、类型等）。  
- **返回字段**（DataFrame 格式）:  
  | 列名          | 类型   | 说明               |  
  |---------------|--------|--------------------|  
  | `fund_code`   | `str`  | 基金代码           |  
  | `abbr`        | `str`  | 基金简称           |  
  | `name`        | `str`  | 基金全称           |  
  | `type`        | `str`  | 基金类型（如股票型） |  
  | `pinyin`      | `str`  | 拼音全拼           |  

- **示例**:  
  ```python
  from ttfunds.fetcher import get_fund_list
  
  fund_list = get_fund_list()
  print(fund_list.head(10))  # 查看前10只基金
  ``` 

---

### ⚙️ **2. 高级方法**

#### **2.1 批量获取实时净值**  
```python
batch_get_fund_realtime(fund_codes: List[str], max_workers: int = None) -> Dict[str, dict]
```  
- **功能**: 并发获取多只基金的实时数据，提高获取效率。支持协程和多线程结合的方式。  
- **输入参数**:  
  | 参数名        | 类型        | 必填 | 说明                  |  
  |---------------|-------------|------|-----------------------|  
  | `fund_codes`  | `List[str]` | 是   | 基金代码列表          |  
  | `max_workers` | `int`       | 否   | 最大线程数，默认使用配置中的值   |  

- **返回**: 字典格式，键为基金代码，值为对应基金的实时数据。  

- **示例**:  
  ```python
  from ttfunds.fetcher import batch_get_fund_realtime
  
  codes = ["001186", "000001", "005827"]
  data = batch_get_fund_realtime(codes, max_workers=3)
  for code, fund_data in data.items():
      print(f"{code}: {fund_data['name']} - {fund_data['gszzl']}%")
  ```

#### **2.2 批量获取历史净值**  
```python
batch_get_fund_history(fund_codes: List[str], max_workers: int = None) -> Dict[str, pd.DataFrame]
```  
- **功能**: 并发获取多只基金的历史净值数据。支持协程和多线程结合的方式。  
- **输入参数**:  
  | 参数名        | 类型        | 必填 | 说明                  |  
  |---------------|-------------|------|-----------------------|  
  | `fund_codes`  | `List[str]` | 是   | 基金代码列表          |  
  | `max_workers` | `int`       | 否   | 最大线程数，默认使用配置中的值   |  

- **返回**: 字典格式，键为基金代码，值为对应基金的历史净值 DataFrame。  

- **示例**:  
  ```python
  from ttfunds.fetcher import batch_get_fund_history
  
  codes = ["001186", "000001"]
  data = batch_get_fund_history(codes, max_workers=2)
  for code, df in data.items():
      print(f"{code}: 共{len(df)}条历史数据")
  ```

---

### ⚙️ **3. 配置管理**

#### **3.1 全局配置**
```python
from ttfunds import configure

# 配置参数
configure(
    timeout=15,                    # 请求超时时间
    retries=5,                     # 重试次数
    max_workers_realtime=10,       # 实时数据批量获取的最大线程数
    max_workers_history=5          # 历史数据批量获取的最大线程数
)
```

- **配置参数说明**:
  | 参数名                 | 类型  | 默认值 | 说明                           |
  |------------------------|-------|--------|--------------------------------|
  | `timeout`              | `int` | 10     | 请求超时时间（秒）             |
  | `retries`              | `int` | 3      | 请求失败重试次数               |
  | `max_workers_realtime` | `int` | 5      | 实时数据批量获取的最大线程数   |
  | `max_workers_history`  | `int` | 3      | 历史数据批量获取的最大线程数   |

---

### 💡 **4. 注意事项**  
1. **数据库机制**: 所有获取的数据都会自动保存到本地数据库中，无需额外缓存设置。  
2. **错误处理**:  
   - 无效基金代码将返回 `None`。  
   - 网络请求失败会自动重试，默认重试3次。  
3. **性能建议**:  
   - 获取大量数据时，推荐使用批量方法以提高效率。  
   - 历史净值数据较大，建议按需获取。  
   - 可以通过调整 `max_workers` 参数或全局配置来优化并发性能。  

---

### 🚀 **5. 完整调用示例**
```python
from ttfunds import configure
from ttfunds.fetcher import (
    get_fund_realtime, 
    get_fund_history, 
    get_fund_list,
    batch_get_fund_realtime,
    batch_get_fund_history
)

# 全局配置
configure(
    timeout=15,
    retries=5,
    max_workers_realtime=10,
    max_workers_history=5
)

# 获取基金列表
fund_list = get_fund_list()
print(f"共{len(fund_list)}只基金")

# 单基金实时数据
realtime = get_fund_realtime("001186")

# 单基金历史数据
history = get_fund_history("001186")

# 多基金实时数据（并发，协程+多线程）
realtime_batch = batch_get_fund_realtime(["001186", "000001", "005827"])

# 多基金历史数据（并发，协程+多线程）
history_batch = batch_get_fund_history(["001186", "000001"])
```

> 此文档描述了新版本的API接口，所有数据自动保存到数据库中，无需手动管理缓存。新版本支持协程和多线程结合的方式，进一步提升批量数据获取的性能。