import json
import csv
import pandas as pd
import os
from datetime import datetime


class DataManager:
    """数据管理类，负责保存和管理爬取的数据"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_to_json(self, data, filename=None):
        """保存数据为JSON格式"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"netease_finance_news_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存为JSON格式: {filepath}")
            return filepath
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
            return None
    
    def save_to_csv(self, data, filename=None):
        """保存数据为CSV格式"""
        if not data:
            print("没有数据可保存")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"netease_finance_news_{timestamp}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"数据已保存为CSV格式: {filepath}")
            return filepath
        except Exception as e:
            print(f"保存CSV文件失败: {e}")
            return None
    
    def save_to_excel(self, data, filename=None):
        """保存数据为Excel格式"""
        if not data:
            print("没有数据可保存")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"netease_finance_news_{timestamp}.xlsx"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
            print(f"数据已保存为Excel格式: {filepath}")
            return filepath
        except Exception as e:
            print(f"保存Excel文件失败: {e}")
            return None
    
    def load_from_json(self, filepath):
        """从JSON文件加载数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"成功从JSON文件加载数据: {filepath}")
            return data
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
            return None
    
    def get_data_summary(self, data):
        """获取数据统计摘要"""
        if not data:
            return "没有数据"
        
        summary = {
            "总新闻数量": len(data),
            "爬取时间范围": {
                "最早": min(item.get('crawl_time', '') for item in data if item.get('crawl_time')),
                "最晚": max(item.get('crawl_time', '') for item in data if item.get('crawl_time'))
            },            "标题长度统计": {
                "平均长度": sum(len(item.get('title', '')) for item in data) / len(data),
                "最长标题": max((item.get('title', '') for item in data), key=len),
                "最短标题": min((item.get('title', '') for item in data), key=len)
            },
            "摘要长度统计": {
                "平均长度": sum(len(item.get('summary', '')) for item in data) / len(data),
                "有摘要的新闻数": len([item for item in data if item.get('summary') and item.get('summary') != '暂无摘要'])
            }
        }
        
        return summary
    
    def save_all_formats(self, data, filename_prefix=None):
        """保存数据为所有格式"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if filename_prefix is None:
            filename_prefix = "news"
        
        base_filename = f"{filename_prefix}_{timestamp}"
        
        results = {}
        results['json'] = self.save_to_json(data, f"{base_filename}.json")
        results['csv'] = self.save_to_csv(data, f"{base_filename}.csv")
        results['excel'] = self.save_to_excel(data, f"{base_filename}.xlsx")
        
        return results
