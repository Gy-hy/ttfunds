#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速开始示例
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


def main():
    print("=== 天天基金数据接口示例 ===")
    
    # 1. 获取单个基金实时数据
    print("\n1. 获取单个基金实时数据:")
    realtime_data = get_fund_realtime("001186")
    if realtime_data:
        print(f"   基金名称: {realtime_data['name']}")
        print(f"   单位净值: {realtime_data['dwjz']}")
        print(f"   估算净值: {realtime_data['gsz']}")
        print(f"   估算涨跌幅: {realtime_data['gszzl']}%")
    else:
        print("   获取数据失败")
    
    # 2. 获取基金列表
    print("\n2. 获取基金列表:")
    fund_list = get_fund_list()
    if fund_list is not None:
        print(f"   共有 {len(fund_list)} 只基金")
        print("   前5只基金:")
        for i, (_, fund) in enumerate(fund_list.head().iterrows()):
            print(f"     {fund['fund_code']}: {fund['name']}")
    else:
        print("   获取数据失败")
    
    # 3. 批量获取基金实时数据
    print("\n3. 批量获取基金实时数据:")
    codes = ["001186", "000001", "005827"]
    batch_data = batch_get_fund_realtime(codes)
    for code, data in batch_data.items():
        if data:
            print(f"   {code} ({data['name']}): {data['gszzl']}%")
        else:
            print(f"   {code}: 获取数据失败")


if __name__ == "__main__":
    main()