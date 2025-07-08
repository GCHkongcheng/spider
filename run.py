#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻爬虫启动器
Author: GCH空城
Date: 2025-07-08
Description: 懒人专用，直接双击就能跑

用法：python run.py 或者直接双击这个文件
"""

import sys
import os

# 把当前目录加到路径里，不然import会报错
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.main import main

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("[START] 启动新闻爬虫...")
        print("=" * 50)
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] 用户手动停止了程序")
    except Exception as e:
        print(f"\n[ERROR] 程序跑崩了: {e}")
        print("详细错误信息:")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")  # 防止窗口直接关闭
