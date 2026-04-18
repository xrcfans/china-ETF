#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数基金数据自动获取脚本
数据源：中证指数有限公司（通过AKShare）
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime

# 五大指数配置
INDICES = {
    'hs300': {'code': '000300', 'name': '沪深300'},
    'zz500': {'code': '000905', 'name': '中证500'},
    'a500': {'code': '000510', 'name': '中证A500'},
    'sz180': {'code': '000010', 'name': '上证180'},
    'cyb': {'code': '399006', 'name': '创业板指'}
}

def main():
    print(f"⏰ 开始更新数据：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = {}
    
    for key, info in INDICES.items():
        try:
            print(f"\n📊 获取 {info['name']} ({info['code']})...")
            df = ak.index_stock_cons_weight_csindex(info['code'])
            
            # 数据清洗
            df = df[['成分券代码', '成分券名称', '权重']].copy()
            df.columns = ['code', 'name', 'weight']
            df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
            
            # 转换为记录
            records = df.to_dict('records')
            result[key] = records
            
            # 显示前3大权重
            top3 = sorted(records, key=lambda x: x['weight'], reverse=True)[:3]
            print(f"   ✅ {len(records)}只股票")
            for i, stock in enumerate(top3, 1):
                print(f"      {i}. {stock['name']}: {stock['weight']:.2f}%")
                
        except Exception as e:
            print(f"   ❌ 错误：{e}")
            result[key] = []  # 失败时返回空数组
    
    # 保存为JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 保存紧凑版（给iPhone用）
    with open('data-compact.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))
    
    # 保存合并版（去重）
    merge_data(result)
    
    print(f"\n✅ 完成！文件已更新")
    print(f"   📄 data.json - 完整格式")
    print(f"   📱 data-compact.json - iPhone紧凑格式")
    print(f"   📊 data-merged.json - 去重合并且排序")

def merge_data(all_data):
    """合并所有指数数据，去重"""
    stock_dict = {}
    
    for index_key, stocks in all_data.items():
        index_name = INDICES[index_key]['name']
        for stock in stocks:
            code = stock['code']
            if code not in stock_dict:
                stock_dict[code] = {
                    'code': code,
                    'name': stock['name'],
                    'hs300': 0, 'zz500': 0, 'a500': 0, 'sz180': 0, 'cyb': 0,
                    'indices': []
                }
            stock_dict[code][index_key] = stock['weight']
            stock_dict[code]['indices'].append(index_name)
    
    # 转换为列表，按沪深300权重排序
    merged_list = list(stock_dict.values())
    merged_list.sort(key=lambda x: x['hs300'], reverse=True)
    
    with open('data-merged.json', 'w', encoding='utf-8') as f:
        json.dump(merged_list, f, ensure_ascii=False, indent=2)
    
    print(f"   📊 合并后共 {len(merged_list)} 只不重复股票")

if __name__ == '__main__':
    main()
