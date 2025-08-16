import logging
import re
import json
import time
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor


class TTFundsAPI:
    """
    天天基金数据接口封装包
    功能：实时净值、历史净值、基金列表、数据缓存、多线程请求
    """

    def __init__(self, cache_ttl: int = 300, max_workers: int = 5):
        """
        初始化配置
        :param cache_ttl: 缓存有效期(秒)
        :param max_workers: 多线程最大并发数
        """
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.max_workers = max_workers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": "http://fund.eastmoney.com/"
        }

    def _request(self, url: str, retry: int = 3) -> str:
        """带重试机制的请求函数"""
        for attempt in range(retry):
            try:
                resp = requests.get(url, headers=self.headers, timeout=10)
                resp.encoding = 'utf-8'
                if resp.status_code == 200:
                    return resp.text
            except Exception as e:
                if attempt == retry - 1:
                    raise ConnectionError(f"请求失败: {str(e)}")
                time.sleep(2 ** attempt)
        return ""

    def _get_cached(self, key: str) -> Optional[dict]:
        """获取缓存数据"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None

    def _set_cache(self, key: str, data: dict):
        """设置缓存数据"""
        self.cache[key] = (data, time.time())

    # -------------------- 核心接口封装 --------------------
    def get_realtime_net(self, fund_code: str) -> Dict[str, str]:
        """
        获取实时基金净值（带缓存）
        :param fund_code: 6位基金代码
        :return: 包含实时数据的字典
        """
        cache_key = f"realtime_{fund_code}"
        if cached := self._get_cached(cache_key):
            return cached

        url = f"http://fundgz.1234567.com.cn/js/{fund_code}.js"
        try:
            raw_text = self._request(url)
            json_str = re.search(r'\{.*\}', raw_text).group()
            data = json.loads(json_str)
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            raise ValueError(f"数据解析失败: {str(e)}")

    def get_history_net(self, fund_code: str) -> pd.DataFrame:
        cache_key = f"history_{fund_code}"
        if cached := self._get_cached(cache_key):
            return cached

        url = f"http://fund.eastmoney.com/pingzhongdata/{fund_code}.js"
        try:
            js_content = self._request(url)

            # 1. 单位净值解析（改用json.loads确保安全）
            nav_match = re.search(r'Data_netWorthTrend\s*=\s*(\[.*?\])', js_content)
            if not nav_match:
                raise ValueError("单位净值数据未找到")
            nav_data = json.loads(nav_match.group(1))
            nav_df = pd.DataFrame(nav_data)
            nav_df['date'] = pd.to_datetime(nav_df['x'], unit='ms').dt.strftime('%Y-%m-%d')
            nav_df.rename(columns={'y': 'nav', 'equityReturn': 'return_rate'}, inplace=True)
            nav_df = nav_df[['date', 'nav', 'return_rate']].set_index('date')

            # 2. 累计净值解析（关键修复：正则匹配+json安全解析）
            cum_nav_match = re.search(r'Data_ACWorthTrend\s*=\s*(\[\[.*?\]\])', js_content, re.DOTALL)
            if not cum_nav_match:
                raise ValueError("累计净值数据未找到")
            cum_nav_str = cum_nav_match.group(1).replace("'", '"')  # 统一引号格式
            cum_nav_list = json.loads(cum_nav_str)  # 安全解析替代eval
            cum_nav_df = pd.DataFrame(cum_nav_list, columns=['timestamp', 'cumnav'])
            cum_nav_df['date'] = pd.to_datetime(cum_nav_df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')
            cum_nav_df = cum_nav_df[['date', 'cumnav']].set_index('date')

            # 3. 合并数据
            result = pd.merge(nav_df, cum_nav_df, left_index=True, right_index=True, how='left')
            self._set_cache(cache_key, result)
            return result

        except (json.JSONDecodeError, KeyError) as e:
            # 详细错误日志帮助调试
            error_msg = f"数据解析异常: {str(e)} | 基金代码: {fund_code} | URL: {url}"
            logging.error(error_msg)
            raise ValueError(error_msg)

    def get_fund_list(self) -> pd.DataFrame:
        """
        获取全量基金列表（自动缓存1小时）
        """
        cache_key = "fund_list"
        if cached := self._get_cached(cache_key):
            return cached

        url = "http://fund.eastmoney.com/js/fundcode_search.js"
        try:
            raw_data = self._request(url)
            json_str = re.search(r'\[.*\]', raw_data).group()
            fund_list = eval(json_str)

            df = pd.DataFrame(fund_list, columns=[
                'fund_code', 'abbr', 'name', 'type', 'pinyin'
            ]).set_index('fund_code')

            self._set_cache(cache_key, df)
            return df

        except Exception as e:
            raise ConnectionError(f"基金列表获取失败: {str(e)}")

    # -------------------- 批量操作接口 --------------------
    def batch_realtime_net(self, fund_codes: List[str]) -> Dict[str, dict]:
        """多线程批量获取实时净值"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(
                lambda code: (code, self.get_realtime_net(code)),
                fund_codes
            ))
        return {code: data for code, data in results}

    def batch_history_net(self, fund_codes: List[str]) -> Dict[str, pd.DataFrame]:
        """多线程批量获取历史净值"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(
                lambda code: (code, self.get_history_net(code)),
                fund_codes
            ))
        return {code: df for code, df in results}


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 初始化接口
    fund_api = TTFundsAPI(cache_ttl=600)

    # 示例1：获取单只基金实时净值
    realtime_data = fund_api.get_realtime_net("001186")
    print(f"【实时净值】{realtime_data['name']} ({realtime_data['fundcode']})")
    print(f"单位净值: {realtime_data['dwjz']} | 估算净值: {realtime_data['gsz']}({realtime_data['gszzl']}%)")

    # 示例2：获取历史净值
    history_df = fund_api.get_history_net("001186")
    print(f"\n【历史净值前5行】\n{history_df.head()}")

    # 示例3：批量操作
    print("\n【批量获取多只基金】")
    batch_data = fund_api.batch_realtime_net(["001186", "000001", "005827"])
    for code, data in batch_data.items():
        print(f"{code}: {data['name']} | 估算涨跌幅: {data['gszzl']}%")

    # 示例4：获取全量基金列表
    if datetime.now().hour == 3:  # 凌晨3点更新
        fund_list = fund_api.get_fund_list()
        fund_list.to_csv("fund_list.csv")
        print(f"\n已保存基金列表，总计: {len(fund_list)}只基金")