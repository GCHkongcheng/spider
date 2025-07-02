#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
Author: GitHub Copilot
Date: 2025-06-30
Description: 通用工具函数
"""

import re
import logging
import os
import time
import random
from urllib.parse import urljoin, urlparse
from datetime import datetime


def setup_logger(name, level=logging.INFO):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 确保日志目录存在
    log_dir = "data"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 如果已经有处理器，直接返回
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    log_file = os.path.join(log_dir, 'spider.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def clean_text(text):
    """
    清理文本内容
    
    Args:
        text: 原始文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 替换多个空白字符为单个空格
    text = re.sub(r'\s+', ' ', text)
    
    # 移除首尾空白
    text = text.strip()
    
    # 移除特殊字符但保留中文标点
    text = re.sub(r'[^\w\s\u4e00-\u9fff，。、；：""''！？（）【】《》]', '', text)
    
    return text


def is_valid_url(url):
    """
    验证URL是否有效
    
    Args:
        url: 待验证的URL
        
    Returns:
        bool: URL是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url, base_url):
    """
    标准化URL
    
    Args:
        url: 原始URL
        base_url: 基础URL
        
    Returns:
        str: 标准化后的URL
    """
    if not url:
        return None
    
    # 处理相对链接
    if url.startswith('//'):
        url = 'https:' + url
    elif url.startswith('/'):
        url = urljoin(base_url, url)
    
    return url if is_valid_url(url) else None


def random_delay(min_seconds=1, max_seconds=3):
    """
    随机延时
    
    Args:
        min_seconds: 最小延时秒数
        max_seconds: 最大延时秒数
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def extract_date_from_url(url):
    """
    从URL中提取日期
    
    Args:
        url: URL地址
        
    Returns:
        str: 日期字符串或None
    """
    date_pattern = r'/(\d{4})/(\d{2})/(\d{2})/'
    match = re.search(date_pattern, url)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"
    return None


def is_news_url(url, keywords=None):
    """
    判断URL是否为新闻链接
    
    Args:
        url: URL地址
        keywords: 关键词列表
        
    Returns:
        bool: 是否为新闻链接
    """
    if not url:
        return False
    
    if keywords is None:
        keywords = [
            'news', 'article', 'finance', 'money', 
            '新闻', '财经', '金融', '经济'
        ]
    
    # 新闻URL特征
    news_patterns = [
        r'/\d{4}/\d{2}/\d{2}/',  # 日期格式
        r'\.html$',  # html结尾
        r'/article/',  # 文章路径
        r'/news/',   # 新闻路径
    ]
    
    for pattern in news_patterns:
        if re.search(pattern, url):
            return True
    
    # 检查关键词
    url_lower = url.lower()
    if any(keyword.lower() in url_lower for keyword in keywords):
        return True
    
    # 排除非新闻链接
    exclude_patterns = [
        r'javascript:',
        r'mailto:',
        r'^#',
        r'\.(jpg|png|gif|pdf|doc|zip|rar)$'
    ]
    
    for pattern in exclude_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    
    return True


def generate_filename(prefix="news", extension="json"):
    """
    生成带时间戳的文件名
    
    Args:
        prefix: 文件名前缀
        extension: 文件扩展名
        
    Returns:
        str: 带时间戳的文件名
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def format_timestamp(timestamp=None):
    """
    格式化时间戳
    
    Args:
        timestamp: 时间戳，默认为当前时间
        
    Returns:
        str: 格式化的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime('%Y%m%d_%H%M%S')


def ensure_dir_exists(directory):
    """
    确保目录存在，如不存在则创建
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def truncate_text(text, max_length):
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        str: 截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def extract_domain(url):
    """
    从URL中提取域名
    
    Args:
        url: URL地址
        
    Returns:
        str: 域名
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def get_file_size(filepath):
    """
    获取文件大小
    
    Args:
        filepath: 文件路径
        
    Returns:
        str: 格式化的文件大小
    """
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    except Exception:
        return "未知"


def format_file_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f}{size_names[i]}"
