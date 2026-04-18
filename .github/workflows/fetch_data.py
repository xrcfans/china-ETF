#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import akshare as ak
import pandas as pd
import json
import sys
from datetime import datetime

INDICES = {
    'hs300': {'code': '000300', 'name': '沪深300'},
    'zz500': {'code': '000905', 'name': '中证500'},
    'a500': {'code': '000510', 'name': '中证A500'},
    'sz180': {'code': '000010', 'name': '上证180'},
    'cyb': {'code': '399006', 'name': '创业板指'}
}

def get_index_data_safe(index_key, index_info):
    """
    安全获取数据，带重试和错误处理
    """
    print(f"\n📊 获取 {index_info['name']} ({index_info['code']})...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 方法1：使用AKShare官方接口
            df = ak.index_stock_cons_weight_csindex(symbol=index_info['code'])
            
            if df is None or df.empty:
                raise ValueError("Empty dataframe returned")
            
            # 数据清洗
            df = df[['成分券代码', '成分券名称', '权重']].copy()
            df.columns = ['code', 'name', 'weight']
            df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
            df = df.dropna(subset=['code', 'weight'])
            
            records = df.to_dict('records')
            
            if len(records) == 0:
                raise ValueError("No valid records")
            
            print(f"   ✅ 成功: {len(records)}只股票")
            return records
            
        except Exception as e:
            print(f"   ⚠️ 尝试{attempt+1}/{max_retries}失败: {str(e)[:100]}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)  # 等待2秒后重试
            else:
                print(f"   ❌ 最终失败，使用空数据")
                return []

def main():
    print(f"⏰ 开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    result = {}
    success_count = 0
    
    for key, info in INDICES.items():
        data = get_index_data_safe(key, info)
        result[key] = data
        if len(data) > 0:
            success_count += 1
    
    # 即使部分失败也保存数据
    print(f"\n📊 成功率: {success_count}/{len(INDICES)}个指数")
    
    # 保存为JSON（确保文件存在）
    try:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("✅ 已保存 data.json")
        
        # 紧凑版
        with open('data-compact.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, separators=(',', ':'))
        print("✅ 已保存 data-compact.json")
        
        # 合并版
        merge_data(result)
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        sys.exit(1)  # 退出码1表示失败
    
    print("✅ 全部完成!")

def merge_data(all_data):
    """合并去重"""
    try:
        stock_dict = {}
        
        for index_key, stocks in all_data.items():
            index_name = INDICES[index_key]['name']
            for stock in stocks:
                code = stock['code']
                if code not in stock_dict:
                    stock_dict[code] = {
                        'code': code, 'name': stock['name'],
                        'hs300': 0, 'zz500': 0, 'a500': 0, 'sz180': 0, 'cyb': 0,
                        'indices': []
                    }
                stock_dict[code][index_key] = stock['weight']
                stock_dict[code]['indices'].append(index_name)
        
        merged = list(stock_dict.values())
        merged.sort(key=lambda x: x['hs300'], reverse=True)
        
        with open('data-merged.json', 'w', encoding='utf-8') as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存 data-merged.json ({len(merged)}只不重复股票)")
        
    except Exception as e:
        print(f"⚠️ 合并数据失败: {e}")

if __name__ == '__main__':
    main()
