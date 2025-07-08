import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent
import logging
from urllib.parse import urljoin, urlparse
import re


class NetEaseFinanceSpider:
    """网易财经新闻爬虫类"""
    
    def __init__(self):
        self.base_url = "https://money.163.com/"
        self.session = requests.Session()
        self.ua = UserAgent()
        self.news_data = []
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/spider.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # 设置请求头
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
    
    def get_page(self, url, max_retries=3):
        """获取页面内容"""
        for attempt in range(max_retries):
            try:
                # 随机延时，避免反爬
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                self.logger.info(f"成功获取页面: {url}")
                return response.text
                
            except requests.RequestException as e:
                self.logger.warning(f"第{attempt + 1}次请求失败: {url}, 错误: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"获取页面失败，已重试{max_retries}次: {url}")
                    return None
                time.sleep(random.uniform(2, 5))
        
        return None
    
    def parse_main_page(self):
        """解析首页，获取新闻链接"""
        html = self.get_page(self.base_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        news_links = []
        
        # 查找新闻链接的各种选择器
        selectors = [
            'a[href*="money.163.com"]',
            'a[href*="/finance/"]',
            '.news_title a',
            '.titleBar a',
            '.cm_news_main a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and title and len(title) > 5:
                    # 处理相对链接
                    if href.startswith('//'):
                        href = 'https:' + href
                    elif href.startswith('/'):
                        href = urljoin(self.base_url, href)
                    
                    # 过滤有效的新闻链接
                    if self.is_valid_news_url(href) and title:
                        news_links.append({
                            'url': href,
                            'title': title
                        })
        
        # 去重
        seen_urls = set()
        unique_links = []
        for link in news_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        self.logger.info(f"从首页获取到 {len(unique_links)} 个新闻链接")
        return unique_links[:20]  # 限制数量，避免过多请求
    
    def is_valid_news_url(self, url):
        """判断是否为有效的新闻URL"""
        if not url:
            return False
        
        # 检查是否包含新闻相关的路径
        news_patterns = [
            r'/\d{4}/\d{2}/\d{2}/',  # 日期格式
            r'\\.html$',  # html结尾
            r'/article/',  # 文章路径
            r'/news/',   # 新闻路径
        ]
        
        for pattern in news_patterns:
            if re.search(pattern, url):
                return True
        
        # 排除非新闻链接
        exclude_patterns = [
            r'javascript:',
            r'mailto:',
            r'#',
            r'\.(jpg|png|gif|pdf|doc)$'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return 'money.163.com' in url
    
    def parse_news_content(self, url):
        """解析新闻详情页，提取摘要"""
        html = self.get_page(url)
        if not html:
            return ""
        
        soup = BeautifulSoup(html, 'lxml')
        
        # 多种内容选择器
        content_selectors = [
            '.post_content_main',
            '.post_body',
            '.article_body',
            '.content',
            '.news_content',
            '.endText',
            'p'
        ]
        
        content_text = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # 提取文本内容
                texts = []
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:
                        texts.append(text)
                
                if texts:
                    content_text = ' '.join(texts)
                    break
        
        # 如果没有找到内容，尝试提取所有p标签
        if not content_text:
            paragraphs = soup.find_all('p')
            texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 10]
            content_text = ' '.join(texts)
        
        # 生成摘要（取前200字）
        summary = self.generate_summary(content_text)
        return summary
    
    def generate_summary(self, content, max_length=200):
        """生成文章摘要"""
        if not content:
            return "暂无摘要"
        
        # 清理文本
        content = re.sub(r'\\s+', ' ', content)
        content = content.strip()
        
        # 如果内容较短，直接返回
        if len(content) <= max_length:
            return content
        
        # 按句号分割，尝试保持句子完整性
        sentences = content.split('。')
        summary = ""
        
        for sentence in sentences:
            if len(summary + sentence + '。') <= max_length:
                summary += sentence + '。'
            else:
                break
        
        # 如果没有合适的句子，直接截取
        if not summary:
            summary = content[:max_length] + '...'
        
        return summary.strip()
    
    def crawl_news(self):
        """爬取新闻的主要方法"""
        self.logger.info("开始爬取网易财经新闻...")
        
        # 获取新闻链接
        news_links = self.parse_main_page()
        if not news_links:
            self.logger.error("未能获取到新闻链接")
            return []
        
        # 爬取每个新闻的详情
        for i, news in enumerate(news_links, 1):
            self.logger.info(f"正在处理第 {i}/{len(news_links)} 条新闻: {news['title']}")
            
            # 获取摘要
            summary = self.parse_news_content(news['url'])
            
            news_item = {
                'title': news['title'],
                'url': news['url'],
                'summary': summary,
                'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.news_data.append(news_item)
            self.logger.info(f"成功获取新闻: {news['title'][:30]}...")
            
            # 随机延时
            time.sleep(random.uniform(1, 2))
        
        self.logger.info(f"爬取完成，共获取 {len(self.news_data)} 条新闻")
        return self.news_data
    
    def get_news_data(self):
        """获取爬取的新闻数据"""
        return self.news_data
