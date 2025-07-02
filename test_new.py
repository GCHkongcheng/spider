#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能新闻爬虫系统 - 测试脚本
Author: GitHub Copilot
Date: 2025-06-30
Description: 测试爬虫各个功能模块
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.site_detector import SiteDetector
from crawler.universal_spider import UniversalNewsSpider
from crawler.data_manager import DataManager
from crawler.config import NEWS_SITES


def test_site_detection():
    """测试网站检测功能"""
    print("=" * 60)
    print("           网站检测功能测试")
    print("=" * 60)
    
    detector = SiteDetector()
    
    # 检测所有网站
    available_sites, results = detector.get_available_sites()
    
    print(f"\n检测结果:")
    print("=" * 40)
    for site_name, result in results.items():
        status_icon = "✓" if result['status'] == 'success' else "⚠" if result['status'] == 'partial' else "✗"
        print(f"{status_icon} {site_name:12}: {result['message']}")
        if result['info']:
            print(f"  └─ 标题: {result['info']['title'][:50]}...")
    
    print(f"\n✓ 可用网站数量: {len(available_sites)}")
    
    if available_sites:
        # 推荐最佳网站
        best_name, best_config = detector.recommend_best_site()
        print(f"✓ 推荐网站: {best_name}")
        print(f"✓ 网站地址: {best_config['url']}")
        return best_name
    else:
        print("✗ 没有找到可用网站")
        return None


def test_spider_functionality(site_name):
    """测试爬虫功能"""
    print("\n" + "=" * 60)
    print("           爬虫功能测试")
    print("=" * 60)
    
    try:
        # 创建爬虫实例
        spider = UniversalNewsSpider(site_name=site_name)
        print(f"✓ 爬虫初始化完成: {spider.site_name}")
        
        # 爬取少量新闻进行测试
        print(f"\n开始测试爬取 {site_name} 新闻...")
        news_data = spider.crawl_news(max_count=3)
        
        if news_data:
            print(f"✓ 测试成功，爬取到 {len(news_data)} 条新闻")
            
            # 显示测试结果
            for i, news in enumerate(news_data, 1):
                print(f"\n测试新闻 {i}:")
                print(f"  标题: {news['title'][:50]}...")
                print(f"  来源: {news['source']}")
                print(f"  摘要: {news['summary'][:80]}...")
            
            return news_data
        else:
            print("✗ 测试失败，未能获取新闻")
            return None
            
    except Exception as e:
        print(f"✗ 爬虫测试失败: {e}")
        return None


def test_data_manager(news_data):
    """测试数据管理功能"""
    print("\n" + "=" * 60)
    print("           数据管理功能测试")
    print("=" * 60)
    
    try:
        data_manager = DataManager()
        print("✓ 数据管理器初始化完成")
        
        # 生成数据统计
        summary = data_manager.get_data_summary(news_data)
        print(f"\n数据统计:")
        for key, value in summary.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        # 保存测试数据
        print(f"\n保存测试数据:")
        save_results = data_manager.save_all_formats(news_data, filename_prefix="test")
        
        for format_type, filepath in save_results.items():
            if filepath:
                print(f"✓ {format_type.upper()}格式: {filepath}")
            else:
                print(f"✗ {format_type.upper()}格式保存失败")
        
        return True
        
    except Exception as e:
        print(f"✗ 数据管理测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始智能新闻爬虫系统测试")
    
    # 测试1: 网站检测
    best_site = test_site_detection()
    
    if not best_site:
        print("\n❌ 测试终止：没有可用的新闻网站")
        return
    
    # 测试2: 爬虫功能
    news_data = test_spider_functionality(best_site)
    
    if not news_data:
        print("\n❌ 测试终止：爬虫功能测试失败")
        return
    
    # 测试3: 数据管理
    data_success = test_data_manager(news_data)
    
    # 总结
    print("\n" + "=" * 60)
    print("           测试结果总结")
    print("=" * 60)
    
    if data_success:
        print("🎉 所有测试通过！系统运行正常")
        print("💡 您现在可以运行完整的爬虫程序:")
        print("   python run.py")
        print("   或者")
        print("   python crawler/main.py")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
