#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用新闻爬虫
Author: GCH空城
Date: 2025-07-08
Description: 支持多个新闻网站的通用爬虫系统
"""

import requests
import time
import random
import logging
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from .config import (
    NEWS_SITES, REQUEST_TIMEOUT, MAX_RETRIES, DELAY_RANGE,
    SUMMARY_MAX_LENGTH, MIN_TITLE_LENGTH, MIN_SUMMARY_LENGTH
)
from .utils import setup_logger, clean_text, is_valid_url
from .site_detector import SiteDetector


class UniversalNewsSpider:
    """通用新闻爬虫类"""
    
    def __init__(self, site_name=None):
        """
        初始化爬虫
        
        Args:
            site_name: 指定要爬取的网站名称，如果为None则自动选择
        """
        self.logger = setup_logger('universal_spider')
        self.ua = UserAgent()
        self.session = requests.Session()
        self.site_detector = SiteDetector()
        
        # 选择目标网站
        if site_name and site_name in NEWS_SITES:
            self.site_name = site_name
            self.site_config = NEWS_SITES[site_name]
            self.logger.info(f"使用指定网站: {site_name}")
        else:
            self.logger.info("自动检测最佳可用网站...")
            self.site_name, self.site_config = self._select_best_site()
            
        if not self.site_config:
            raise Exception("未找到可用的新闻网站")
            
        self.base_url = self.site_config['url']
        self.selectors = self.site_config['selectors']
        
        self.logger.info(f"✓ 选定网站: {self.site_name}")
        self.logger.info(f"✓ 网站地址: {self.base_url}")
    
    def _select_best_site(self):
        """选择最佳可用网站"""
        try:
            # 这里用检测器找最好用的网站
            best_name, best_config = self.site_detector.recommend_best_site()
            if best_name:
                return best_name, best_config
            else:
                self.logger.error("卧槽，一个能用的网站都没有？")
                return None, None
        except Exception as e:
            self.logger.error(f"网站检测挂了: {e}")
            return None, None
    
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
    
    def get_page(self, url, retries=0):
        """
        获取页面内容
        这个函数是核心，经常会因为网络问题挂掉
        
        Args:
            url: 页面URL
            retries: 当前重试次数
            
        Returns:
            BeautifulSoup对象或None
        """
        if retries >= MAX_RETRIES:
            self.logger.error(f"重试{MAX_RETRIES}次都失败了，算了: {url}")
            return None
            
        try:
            # 随机等一会儿，免得被当成机器人
            delay = random.uniform(*DELAY_RANGE)
            time.sleep(delay)
            
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                # 设置编码，不然中文会乱码
                encoding = self.site_config.get('encoding', 'utf-8')
                response.encoding = encoding
                
                soup = BeautifulSoup(response.content, 'html.parser')
                self.logger.debug(f"成功获取页面: {url}")
                return soup
            else:
                self.logger.warning(f"页面状态异常: {url} (状态码: {response.status_code})")
                return self.get_page(url, retries + 1)
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"请求异常: {url} - {e}")
            return self.get_page(url, retries + 1)
        except Exception as e:
            self.logger.error(f"未知错误: {url} - {e}")
            return self.get_page(url, retries + 1)
    
    def extract_news_links(self, soup):
        """
        从首页提取新闻链接
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            新闻链接列表
        """
        links = []
        link_selectors = self.selectors.get('links', [])
        
        for selector in link_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href:
                        # 处理相对链接
                        if href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(self.base_url, href)
                        
                        # 验证链接有效性
                        if self._is_valid_news_link(full_url) and full_url not in links:
                            links.append(full_url)
                            
                if links:
                    self.logger.info(f"使用选择器 '{selector}' 找到 {len(links)} 个链接")
                    break
                    
            except Exception as e:
                self.logger.warning(f"选择器 '{selector}' 解析失败: {e}")
                continue
        
        return links[:20]  # 限制链接数量
    
    def _is_valid_news_link(self, url):
        """检查链接是否为有效的新闻链接"""
        if not is_valid_url(url):
            return False
        
        # 排除非新闻链接
        exclude_patterns = [
            r'javascript:',
            r'mailto:',
            r'^#',
            r'\\.(jpg|jpeg|png|gif|pdf|doc|docx|zip|rar|exe)$',
            r'/search/',
            r'/login',
            r'/register',
            r'/about',
            r'/contact',
            r'/privacy',
            r'/terms',
            r'/sitemap',
            r'/rss',
            r'/feed',
            r'#comment',
            r'#reply',
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # 检查是否包含日期或新闻标识
        news_indicators = [
            r'/\d{4}/\d{2}/\d{2}/',  # 日期格式
            r'/\d{4}-\d{2}-\d{2}/',  # 日期格式
            r'/\d{8}/',              # 8位数字日期
            r'\\.html$',              # html结尾
            r'\\.shtml$',             # shtml结尾
            r'/article/',            # 文章路径
            r'/news/',               # 新闻路径
            r'/finance/',            # 财经路径
            r'/money/',              # 财经路径
        ]
        
        for pattern in news_indicators:
            if re.search(pattern, url):
                return True
        
        return False
    
    def extract_news_content(self, soup, url):
        """
        从新闻页面提取标题和内容
        
        Args:
            soup: BeautifulSoup对象
            url: 新闻页面URL
            
        Returns:
            包含标题和摘要的字典或None
        """
        try:
            # 提取标题
            title = self._extract_title(soup)
            if not title or len(title) < MIN_TITLE_LENGTH:
                self.logger.debug(f"标题无效或过短: {url}")
                return None
            
            # 提取内容摘要
            summary = self._extract_summary(soup)
            if not summary or len(summary) < MIN_SUMMARY_LENGTH:
                self.logger.debug(f"摘要无效或过短: {url}")
                return None
            
            return {
                'title': title,
                'url': url,
                'summary': summary[:SUMMARY_MAX_LENGTH],
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': self.site_name
            }
            
        except Exception as e:
            self.logger.warning(f"内容提取失败: {url} - {e}")
            return None
    
    def _extract_title(self, soup):
        """提取新闻标题"""
        title_selectors = self.selectors.get('title', [])
        
        for selector in title_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = clean_text(element.get_text())
                    if text and len(text) >= MIN_TITLE_LENGTH:
                        # 过滤掉无效的标题
                        if self._is_valid_title(text):
                            return text
            except Exception:
                continue
        
        # 备选方案：使用页面title标签
        title_tag = soup.find('title')
        if title_tag:
            title = clean_text(title_tag.get_text())
            # 清理常见的网站后缀
            for suffix in ['_网易财经', '_新浪财经', '_腾讯财经', '_央视网', '_人民网']:
                if title.endswith(suffix):
                    title = title[:-len(suffix)]
                    break
            if self._is_valid_title(title):
                return title
            
        return None
    
    def _is_valid_title(self, title):
        """检查标题是否有效"""
        if not title or len(title) < MIN_TITLE_LENGTH:
            return False
        
        # 过滤无效的标题模式
        invalid_patterns = [
            r'更多$',  # 以"更多"结尾
            r'^更多',  # 以"更多"开头
            r'^\s*$',  # 只有空白字符
            r'广告',   # 包含"广告"
            r'版权',   # 包含"版权"
            r'免责',   # 包含"免责"
            r'登录',   # 包含"登录"
            r'注册',   # 包含"注册"
            r'客服',   # 包含"客服"
            r'联系我们', # 包含"联系我们"
            r'关于我们', # 包含"关于我们"
            r'^[\\d\\s\\-\\|]+$',  # 只包含数字、空格、横线、竖线
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, title):
                return False
        
        return True
    
    def _extract_summary(self, soup):
        """提取新闻摘要"""
        content_selectors = self.selectors.get('content', [])
        
        for selector in content_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    # 合并所有段落文本
                    paragraphs = []
                    for element in elements:
                        text = clean_text(element.get_text())
                        if text and len(text) > 10:  # 过滤掉过短的文本
                            # 进一步过滤无效内容
                            if self._is_valid_paragraph(text):
                                paragraphs.append(text)
                    
                    if paragraphs:
                        # 取前几个段落作为摘要
                        summary = ' '.join(paragraphs[:3])
                        return summary[:SUMMARY_MAX_LENGTH]
                        
            except Exception:
                continue
        
        return "暂无摘要"
    
    def _is_valid_paragraph(self, text):
        """检查段落是否有效"""
        if not text or len(text) < 10:
            return False
        
        # 过滤无效的段落模式
        invalid_patterns = [
            r'广告',
            r'免责声明',
            r'版权所有',
            r'联系我们',
            r'关于我们',
            r'客服电话',
            r'投诉建议',
            r'意见反馈',
            r'^\\d+$',  # 只有数字
            r'^[\\s\\-\\|]+$',  # 只有空白和分隔符
            r'分享到',
            r'收藏',
            r'点赞',
            r'评论',
            r'转发',
            r'举报',
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, text):
                return False
        
        return True
    
    def crawl_news(self, max_count=20):
        """
        爬取新闻
        
        Args:
            max_count: 最大爬取数量
            
        Returns:
            新闻数据列表
        """
        self.logger.info(f"开始爬取 {self.site_name} 新闻...")
        
        # 获取首页
        soup = self.get_page(self.base_url)
        if not soup:
            self.logger.error("无法获取首页内容")
            return []
        
        # 提取新闻链接
        self.logger.info("正在提取新闻链接...")
        news_links = self.extract_news_links(soup)
        
        if not news_links:
            self.logger.error("未找到任何新闻链接")
            return []
        
        self.logger.info(f"找到 {len(news_links)} 个新闻链接")
        
        # 爬取新闻内容
        news_data = []
        success_count = 0
        
        for i, link in enumerate(news_links[:max_count], 1):
            self.logger.info(f"正在处理第 {i}/{min(len(news_links), max_count)} 个新闻...")
            
            news_soup = self.get_page(link)
            if news_soup:
                news_info = self.extract_news_content(news_soup, link)
                if news_info:
                    news_data.append(news_info)
                    success_count += 1
                    self.logger.info(f"✓ 成功: {news_info['title'][:50]}...")
                else:
                    self.logger.warning(f"✗ 内容提取失败: {link}")
            else:
                self.logger.warning(f"✗ 页面获取失败: {link}")
        
        self.logger.info(f"爬取完成: 成功 {success_count}/{len(news_links[:max_count])} 条新闻")
        return news_data
    
    def get_site_info(self):
        """获取当前使用的网站信息"""
        return {
            'name': self.site_name,
            'url': self.base_url,
            'config': self.site_config
        }


# 为了向后兼容，保留原类名
class NetEaseFinanceSpider(UniversalNewsSpider):
    """网易财经爬虫（向后兼容）"""
    
    def __init__(self):
        super().__init__(site_name="网易财经")


if __name__ == "__main__":
    # 测试代码
    spider = UniversalNewsSpider()
    news_data = spider.crawl_news(max_count=5)
    
    print(f"\n爬取到 {len(news_data)} 条新闻:")
    for i, news in enumerate(news_data, 1):
        print(f"\n{i}. {news['title']}")
        print(f"   来源: {news['source']}")
        print(f"   摘要: {news['summary'][:100]}...")
