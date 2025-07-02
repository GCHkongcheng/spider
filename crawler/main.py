#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用新闻爬虫主程序
Author: GitHub Copilot
Date: 2025-06-30
Description: 智能检测并爬取多个新闻网站
"""

import sys
import os
from datetime import datetime

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.universal_spider import UniversalNewsSpider
from crawler.data_manager import DataManager
from crawler.site_detector import SiteDetector
from crawler.config import NEWS_SITES


def show_banner():
    """显示程序横幅"""
    print("=" * 70)
    print("                    智能新闻爬虫系统")
    print("                  Universal News Crawler")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def select_news_site():
    """用户选择新闻网站"""
    print("🔍 正在检测可用的新闻网站...")
    detector = SiteDetector()
    available_sites, detection_results = detector.get_available_sites()
    
    # 显示检测结果
    print("\n" + "=" * 50)
    print("网站检测结果:")
    print("=" * 50)
    
    for site_name, result in detection_results.items():
        if result['status'] == 'success':
            icon = "✅"
        elif result['status'] == 'partial':
            icon = "⚠️"
        else:
            icon = "❌"
        
        print(f"{icon} {site_name:12} - {result['message']}")
        if result['info']:
            print(f"   └─ 网站标题: {result['info']['title'][:40]}...")
    
    if not available_sites:
        print("\n❌ 没有找到可用的新闻网站，程序无法继续")
        return None
    
    # 用户选择
    print(f"\n✅ 发现 {len(available_sites)} 个可用网站")
    print("\n请选择要爬取的新闻网站:")
    print("0. 自动选择最佳网站")
    
    site_list = list(available_sites.keys())
    for i, site_name in enumerate(site_list, 1):
        print(f"{i}. {site_name}")
    
    while True:
        try:
            choice = input(f"\n请输入选择 (0-{len(site_list)}): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                # 自动选择
                best_name, _ = detector.recommend_best_site()
                print(f"✅ 自动选择: {best_name}")
                return best_name
            elif 1 <= choice_num <= len(site_list):
                selected_site = site_list[choice_num - 1]
                print(f"✅ 用户选择: {selected_site}")
                return selected_site
            else:
                print("❌ 选择无效，请重新输入")
        except ValueError:
            print("❌ 请输入数字")
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            return None


def main():
    """主函数"""
    show_banner()
    
    try:
        # 用户选择新闻网站
        selected_site = select_news_site()
        if not selected_site:
            return
        
        print(f"\n{'='*50}")
        print(f"开始爬取: {selected_site}")
        print(f"网站地址: {NEWS_SITES[selected_site]['url']}")
        print(f"{'='*50}")
        
        # 创建爬虫实例
        spider = UniversalNewsSpider(site_name=selected_site)
        print("✅ 爬虫初始化完成")
        
        # 创建数据管理器
        data_manager = DataManager()
        print("✅ 数据管理器初始化完成")
        
        # 开始爬取新闻
        print(f"\n🚀 开始爬取 {selected_site} 新闻...")
        news_data = spider.crawl_news()
        
        if not news_data:
            print("❌ 未能获取到任何新闻数据")
            return
        
        print(f"\n✅ 成功爬取 {len(news_data)} 条新闻")
        
        # 显示数据统计
        print(f"\n{'='*50}")
        print("📊 数据统计摘要:")
        print(f"{'='*50}")
        summary = data_manager.get_data_summary(news_data)
        for key, value in summary.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  📌 {sub_key}: {sub_value}")
            else:
                print(f"📌 {key}: {value}")
        
        # 保存数据
        print(f"\n{'='*50}")
        print("💾 保存数据:")
        print(f"{'='*50}")
        save_results = data_manager.save_all_formats(news_data)
        
        for format_type, filepath in save_results.items():
            if filepath:
                print(f"✅ {format_type.upper()}格式: {filepath}")
            else:
                print(f"❌ {format_type.upper()}格式保存失败")
        
        # 显示新闻预览
        print(f"\n{'='*50}")
        print("📰 新闻预览 (前3条):")
        print(f"{'='*50}")
        for i, news in enumerate(news_data[:3], 1):
            print(f"\n📰 新闻 {i}:")
            print(f"   🏷️  标题: {news['title']}")
            print(f"   📝 摘要: {news['summary'][:100]}{'...' if len(news['summary']) > 100 else ''}")
            print(f"   🔗 链接: {news['url']}")
            print(f"   🌐 来源: {news['source']}")
            print(f"   ⏰ 时间: {news['crawl_time']}")
        
        if len(news_data) > 3:
            print(f"\n... 还有 {len(news_data) - 3} 条新闻已保存到文件中")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n程序结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)


if __name__ == "__main__":
    main()