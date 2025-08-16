#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
并发处理示例：演示如何结合使用协程和多线程提升处理效率
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ttfunds import configure
from ttfunds.fetcher import (
    get_fund_realtime,
    batch_get_fund_realtime
)


def test_single_thread_performance(codes):
    """测试单线程性能"""
    print("=== 单线程逐个获取基金数据 ===")
    start_time = time.time()
    
    results = {}
    for code in codes:
        data = get_fund_realtime(code)
        if data:
            results[code] = data
    
    end_time = time.time()
    print(f"处理 {len(codes)} 只基金耗时: {end_time - start_time:.2f} 秒")
    return results


def test_multi_thread_performance(codes, max_workers=5):
    """测试多线程+协程性能"""
    print(f"=== 多线程+协程并发获取基金数据 (最大线程数: {max_workers}) ===")
    start_time = time.time()
    
    results = batch_get_fund_realtime(codes, max_workers)
    
    end_time = time.time()
    print(f"处理 {len(codes)} 只基金耗时: {end_time - start_time:.2f} 秒")
    return results


def test_configured_performance(codes):
    """测试使用配置的性能"""
    print("=== 使用全局配置的多线程+协程并发获取基金数据 ===")
    start_time = time.time()
    
    results = batch_get_fund_realtime(codes)
    
    end_time = time.time()
    print(f"处理 {len(codes)} 只基金耗时: {end_time - start_time:.2f} 秒")
    return results


def main():
    # 配置参数
    configure(
        timeout=15,
        retries=3,
        max_workers_realtime=5,
        max_workers_history=3
    )
    
    # 测试基金代码列表
    test_codes = ["001186", "000001", "005827", "000002", "161725", "000003", "000004", "000005"]
    
    print("开始性能对比测试...\n")
    
    # 测试单线程性能
    single_results = test_single_thread_performance(test_codes)
    
    print()
    
    # 测试多线程性能（指定线程数）
    multi_results = test_multi_thread_performance(test_codes, max_workers=3)
    
    print()
    
    # 测试使用配置的性能
    config_results = test_configured_performance(test_codes)
    
    print("\n=== 结果统计 ===")
    print(f"单线程成功获取: {len([r for r in single_results.values() if r])} 只基金")
    print(f"多线程成功获取: {len([r for r in multi_results.values() if r])} 只基金")
    print(f"配置方式成功获取: {len([r for r in config_results.values() if r])} 只基金")
    
    # 显示部分结果
    print("\n=== 部分结果展示 ===")
    for code in test_codes[:3]:
        data = config_results.get(code)
        if data:
            print(f"{code} - {data['name']}: {data['gszzl']}%")


if __name__ == "__main__":
    main()