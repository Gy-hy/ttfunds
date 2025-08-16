#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试所有功能的示例文件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ttfunds.fetcher import (
    get_fund_realtime,
    get_fund_history,
    get_fund_list,
    batch_get_fund_realtime,
    batch_get_fund_history
)


def test_single_fund_realtime():
    """测试单个基金实时数据获取"""
    print("=== 测试单个基金实时数据 ===")
    code = "001186"
    data = get_fund_realtime(code)
    if data:
        print(f"基金代码: {data['fundcode']}")
        print(f"基金名称: {data['name']}")
        print(f"单位净值: {data['dwjz']}")
        print(f"估算净值: {data['gsz']}")
        print(f"估算涨跌幅: {data['gszzl']}%")
        print(f"更新时间: {data['gztime']}")
    else:
        print("获取数据失败")
    print()


def test_single_fund_history():
    """测试单个基金历史数据获取"""
    print("=== 测试单个基金历史数据 ===")
    code = "001186"
    df = get_fund_history(code)
    if df is not None:
        print(f"历史数据前5行:")
        print(df.head())
    else:
        print("获取数据失败")
    print()


def test_fund_list():
    """测试获取基金列表"""
    print("=== 测试获取基金列表 ===")
    df = get_fund_list()
    if df is not None:
        print(f"基金列表总数: {len(df)}")
        print("前10只基金:")
        print(df.head(10))
    else:
        print("获取数据失败")
    print()


def test_batch_realtime():
    """测试批量获取基金实时数据"""
    print("=== 测试批量获取基金实时数据 ===")
    codes = ["001186", "000001", "005827"]
    data = batch_get_fund_realtime(codes)
    for code, fund_data in data.items():
        if fund_data:
            print(f"{code} - {fund_data['name']}: 估算涨跌幅 {fund_data['gszzl']}%")
        else:
            print(f"{code} - 获取数据失败")
    print()


def test_batch_history():
    """测试批量获取基金历史数据"""
    print("=== 测试批量获取基金历史数据 ===")
    codes = ["001186", "000001"]
    data = batch_get_fund_history(codes)
    for code, df in data.items():
        if df is not None:
            print(f"{code} - 历史数据获取成功，共 {len(df)} 条记录")
        else:
            print(f"{code} - 获取数据失败")
    print()


if __name__ == "__main__":
    test_single_fund_realtime()
    test_single_fund_history()
    test_fund_list()
    test_batch_realtime()
    test_batch_history()
import asyncio
import ttfunds
from ttfunds.fetcher import get_fund_realtime_async, get_fund_history_async, batch_get_fund_realtime_async, batch_get_fund_history_async
from ttfunds.plotter import plot_nav

CODES = ["001186", "161725"]

async def test_async():
    # 并发实时
    reals = await asyncio.gather(*(get_fund_realtime_async(c) for c in CODES))
    print("Realtime results:", reals)

    # 历史
    hists = await asyncio.gather(*(get_fund_history_async(c) for c in CODES))
    for c, df in zip(CODES, hists):
        print(c, len(df))
        plot_nav(c, df, savepath=f"{c}_nav.png")

if __name__ == "__main__":
    asyncio.run(test_async())