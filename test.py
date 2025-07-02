#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.spider import NetEaseFinanceSpider
from crawler.data_manager import DataManager

def test_spider():
    """测试爬虫功能"""
    print("正在测试网易财经新闻爬虫...")
    
    try:
        # 创建爬虫实例
        spider = NetEaseFinanceSpider()
        print("✓ 爬虫初始化成功")
        
        # 测试获取首页
        print("正在测试首页访问...")
        html = spider.get_page(spider.base_url)
        if html:
            print("✓ 首页访问成功")
        else:
            print("❌ 首页访问失败")
            return
        
        # 测试解析新闻链接
        print("正在测试新闻链接解析...")
        news_links = spider.parse_main_page()
        if news_links:
            print(f"✓ 成功解析到 {len(news_links)} 个新闻链接")
            print("前3个新闻链接:")
            for i, link in enumerate(news_links[:3], 1):
                print(f"  {i}. {link['title'][:30]}...")
        else:
            print("❌ 新闻链接解析失败")
        
        # 测试数据管理器
        print("\n正在测试数据管理器...")
        data_manager = DataManager()
        print("✓ 数据管理器初始化成功")
        
        # 创建测试数据
        test_data = [{
            'title': '测试新闻标题',
            'url': 'https://money.163.com/test',
            'summary': '这是一个测试新闻的摘要内容',
            'crawl_time': '2025-06-30 12:00:00'
        }]
        
        # 测试数据保存
        print("正在测试数据保存...")
        json_file = data_manager.save_to_json(test_data, "test_data.json")
        if json_file:
            print("✓ JSON保存测试成功")
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_spider()
