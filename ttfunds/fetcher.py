import asyncio
import httpx
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from .config import CONFIG
from .db import save_history, save_realtime, save_fund_list

BASE_URL = "http://fund.eastmoney.com/pingzhongdata/{}.js"
REALTIME_URL = "https://fundgz.1234567.com.cn/js/{}.js"
FUND_LIST_URL = "http://fund.eastmoney.com/js/fundcode_search.js"


async def _fetch(session: httpx.AsyncClient, url: str):
    for _ in range(CONFIG["retries"]):
        try:
            r = await session.get(url, timeout=CONFIG["timeout"])
            if r.status_code == 200:
                return r.text
        except Exception:
            await asyncio.sleep(1)
    return None


async def get_fund_realtime_async(code: str):
    async with httpx.AsyncClient() as client:
        text = await _fetch(client, REALTIME_URL.format(code))
        if not text:
            return None
        # 数据格式类似 jsonpgz({...});
        try:
            data_str = text[text.find("{"):-2]
            import json
            data = json.loads(data_str)
            await save_realtime(code, data)
            return data
        except Exception:
            return None


def get_fund_realtime(code: str):
    return asyncio.run(get_fund_realtime_async(code))


async def get_fund_history_async(code: str):
    url = BASE_URL.format(code)
    async with httpx.AsyncClient() as client:
        text = await _fetch(client, url)
        if not text:
            return None
        try:
            # 历史净值数据格式在 js 里，需要 eval-like 提取
            # 提取单位净值数据
            start = text.find("Data_netWorthTrend")
            start = text.find("[", start)
            end = text.find("]", start) + 1
            json_str = text[start:end]
            import json
            data = json.loads(json_str)
            df = pd.DataFrame(data)
            
            # 提取累计净值数据
            start = text.find("Data_ACWorthTrend")
            start = text.find("[", start)
            end = text.find("]", start) + 1
            json_str = text[start:end].replace("'", '"')
            cum_data = json.loads(json_str)
            cum_df = pd.DataFrame(cum_data, columns=['timestamp', 'cumulative'])
            
            # 合并数据
            df_result = pd.DataFrame()
            df_result['x'] = df['x']
            df_result['y'] = df['y']
            df_result['equityReturn'] = df.get('equityReturn', [None]*len(df))
            df_result['unitMoney'] = df.get('unitMoney', [None]*len(df))
            
            # 添加累计净值列
            df_result = pd.merge(df_result, cum_df, left_on='x', right_on='timestamp', how='left')
            df_result.drop(columns=['timestamp'], inplace=True, errors='ignore')
            
            await save_history(code, df_result)
            return df_result
        except Exception as e:
            print(f"Error processing history data for {code}: {e}")
            return None


def get_fund_history(code: str):
    return asyncio.run(get_fund_history_async(code))


async def get_fund_list_async():
    async with httpx.AsyncClient() as client:
        text = await _fetch(client, FUND_LIST_URL)
        if not text:
            return None
        try:
            # 数据格式类似 var r = [...];
            start = text.find("[")
            end = text.rfind("]")
            json_str = text[start:end+1]
            import json
            data = json.loads(json_str)
            df = pd.DataFrame(data, columns=[
                'fund_code', 'abbr', 'name', 'type', 'pinyin'
            ])
            await save_fund_list(df)
            return df
        except Exception as e:
            print(f"Error processing fund list: {e}")
            return None


def get_fund_list():
    return asyncio.run(get_fund_list_async())


async def batch_get_fund_realtime_async(codes: list, max_workers: int = None):
    # 如果没有指定max_workers，则使用配置中的默认值
    if max_workers is None:
        max_workers = CONFIG["max_workers_realtime"]
    
    async def fetch_single(code):
        return code, await get_fund_realtime_async(code)
    
    # 使用线程池执行器来并发执行多个异步任务
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 将任务分配给线程池
        futures = [loop.run_in_executor(executor, lambda c=code: asyncio.run(get_fund_realtime_async(c))) for code in codes]
        results = await asyncio.gather(*futures)
        return dict(zip(codes, results))


def batch_get_fund_realtime(codes: list, max_workers: int = None):
    return asyncio.run(batch_get_fund_realtime_async(codes, max_workers))


async def batch_get_fund_history_async(codes: list, max_workers: int = None):
    # 如果没有指定max_workers，则使用配置中的默认值
    if max_workers is None:
        max_workers = CONFIG["max_workers_history"]
    
    async def fetch_single(code):
        return code, await get_fund_history_async(code)
    
    # 使用线程池执行器来并发执行多个异步任务
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 将任务分配给线程池
        futures = [loop.run_in_executor(executor, lambda c=code: asyncio.run(get_fund_history_async(c))) for code in codes]
        results = await asyncio.gather(*futures)
        return dict(zip(codes, results))


def batch_get_fund_history(codes: list, max_workers: int = None):
    return asyncio.run(batch_get_fund_history_async(codes, max_workers))