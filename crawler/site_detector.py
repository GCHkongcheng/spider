#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻网站检测器
Author: GCH空城
Date: 2025-07-08
Description: 检测和验证新闻网站的可用性和结构
"""

import requests
import time
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .config import NEWS_SITES, REQUEST_TIMEOUT, CONNECTION_TEST_TIMEOUT
from .utils import setup_logger


class SiteDetector:
    """网站检测器类"""
    
    def __init__(self):
        """初始化检测器"""
        self.logger = setup_logger('site_detector')
        self.ua = UserAgent()
        self.session = requests.Session()
        
    def get_headers(self):
        """获取随机请求头"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def test_site_connectivity(self, url):
        """测试网站连通性"""
        try:
            self.logger.info(f"测试网站连通性: {url}")
            response = self.session.get(
                url, 
                headers=self.get_headers(), 
                timeout=CONNECTION_TEST_TIMEOUT,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.logger.info(f"✓ 网站可访问: {url} (状态码: {response.status_code})")
                return True, response
            else:
                self.logger.warning(f"✗ 网站访问异常: {url} (状态码: {response.status_code})")
                return False, None
                
        except requests.exceptions.ConnectTimeout:
            self.logger.error(f"✗ 连接超时: {url}")
            return False, None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"✗ 连接错误: {url}")
            return False, None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"✗ 请求异常: {url} - {e}")
            return False, None
        except Exception as e:
            self.logger.error(f"✗ 未知错误: {url} - {e}")
            return False, None
    
    def test_site_structure(self, url, selectors):
        """测试网站结构和选择器有效性"""
        try:
            is_connected, response = self.test_site_connectivity(url)
            if not is_connected:
                return False, "网站无法访问"
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 测试标题选择器
            title_found = False
            title_selectors = selectors.get('title', [])
            for selector in title_selectors:
                elements = soup.select(selector)
                if elements:
                    # 检查是否有实际的文本内容
                    valid_titles = [elem for elem in elements if elem.get_text(strip=True)]
                    if valid_titles:
                        title_found = True
                        self.logger.info(f"✓ 找到标题选择器: {selector} (找到 {len(valid_titles)} 个)")
                        break
            
            # 测试链接选择器
            links_found = False
            link_selectors = selectors.get('links', [])
            for selector in link_selectors:
                elements = soup.select(selector)
                if elements:
                    # 检查是否有href属性
                    valid_links = [elem for elem in elements if elem.get('href')]
                    if valid_links:
                        links_found = True
                        self.logger.info(f"✓ 找到链接选择器: {selector} (找到 {len(valid_links)} 个)")
                        break
            
            # 判断结果
            if title_found and links_found:
                return True, "网站结构检测通过"
            elif title_found:
                return False, "找到标题但未找到有效链接"
            elif links_found:
                return False, "找到链接但未找到有效标题"
            else:
                return False, "未找到有效的标题和链接选择器"
                
        except Exception as e:
            self.logger.error(f"结构检测异常: {url} - {e}")
            return False, f"结构检测异常: {e}"
    
    def get_site_info(self, url, response):
        """获取网站基本信息"""
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 获取网站标题
            title_tag = soup.find('title')
            site_title = title_tag.get_text(strip=True) if title_tag else "未知"
            
            # 获取编码
            charset = response.encoding or 'utf-8'
            
            # 获取页面大小
            content_length = len(response.content)
            
            return {
                'title': site_title,
                'encoding': charset,
                'content_length': content_length,
                'status_code': response.status_code
            }
        except Exception as e:
            self.logger.error(f"获取网站信息失败: {e}")
            return None
    
    def detect_all_sites(self):
        """检测所有配置的新闻网站"""
        self.logger.info("开始检测所有配置的新闻网站...")
        results = {}
        
        for site_name, site_config in NEWS_SITES.items():
            self.logger.info(f"\n正在检测: {site_name}")
            
            url = site_config['url']
            selectors = site_config['selectors']
            
            # 测试连通性
            is_connected, response = self.test_site_connectivity(url)
            
            if is_connected:
                # 测试结构
                is_valid, message = self.test_site_structure(url, selectors)
                
                # 获取网站信息
                site_info = self.get_site_info(url, response)
                
                results[site_name] = {
                    'status': 'success' if is_valid else 'partial',
                    'message': message,
                    'url': url,
                    'info': site_info,
                    'selectors_valid': is_valid
                }
                
                if is_valid:
                    self.logger.info(f"[OK] {site_name}: {message}")
                else:
                    self.logger.warning(f"[WARN] {site_name}: {message}")
            else:
                results[site_name] = {
                    'status': 'failed',
                    'message': '网站无法访问',
                    'url': url,
                    'info': None,
                    'selectors_valid': False
                }
                self.logger.error(f"✗ {site_name}: 网站无法访问")
            
            # 添加延迟避免请求过快
            time.sleep(1)
        
        return results
    
    def get_available_sites(self):
        """获取所有可用的新闻网站"""
        detection_results = self.detect_all_sites()
        available_sites = {}
        
        for site_name, result in detection_results.items():
            if result['status'] == 'success':
                available_sites[site_name] = NEWS_SITES[site_name]
        
        return available_sites, detection_results
    
    def recommend_best_site(self):
        """推荐最佳可用网站"""
        available_sites, detection_results = self.get_available_sites()
        
        if not available_sites:
            return None, "没有找到可用的新闻网站"
        
        # 简单推荐策略：选择第一个可用的网站
        best_site_name = list(available_sites.keys())[0]
        best_site_config = available_sites[best_site_name]
        
        return best_site_name, best_site_config


if __name__ == "__main__":
    # 测试代码
    detector = SiteDetector()
    
    print("=" * 60)
    print("           新闻网站检测器")
    print("=" * 60)
    
    # 检测所有网站
    available_sites, results = detector.get_available_sites()
    
    print(f"\n检测结果:")
    print("=" * 40)
    for site_name, result in results.items():
        status_icon = "[OK]" if result['status'] == 'success' else "[WARN]" if result['status'] == 'partial' else "[FAIL]"
        print(f"{status_icon} {site_name}: {result['message']}")
    
    print(f"\n可用网站数量: {len(available_sites)}")
    
    if available_sites:
        # 推荐最佳网站
        best_name, best_config = detector.recommend_best_site()
        print(f"推荐网站: {best_name}")
        print(f"网站地址: {best_config['url']}")
