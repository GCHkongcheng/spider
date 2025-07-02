#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能新闻爬虫 - 快速运行脚本
Author: GitHub Copilot
Date: 2025-06-30
Description: 一键运行新闻爬虫系统
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"运行出错: {e}")
        import traceback
        traceback.print_exc()
