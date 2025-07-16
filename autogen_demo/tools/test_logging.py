#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试日志文件写入功能
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging_config import setup_logging, get_logger

def main():
    """测试日志文件写入功能"""
    # 设置日志级别为DEBUG，并启用文件日志
    setup_logging(level="DEBUG", log_to_file=True)
    
    # 获取测试日志记录器
    logger = get_logger(__name__, "TestAgent")
    
    # 记录不同级别的日志消息
    logger.debug("这是一条调试日志消息")
    logger.info("这是一条信息日志消息")
    logger.warning("这是一条警告日志消息")
    logger.error("这是一条错误日志消息")
    logger.critical("这是一条严重错误日志消息")
    
    # 测试带有异常的日志
    try:
        result = 1 / 0
    except Exception as e:
        logger.exception("发生了一个除零异常")
    
    # 测试带有中文和特殊字符的日志
    logger.info("测试中文日志消息：你好，世界！")
    logger.info("测试特殊字符: !@#$%^&*()_+-=[]{}|;':\",./<>?")
    
    # 测试多个日志记录器
    another_logger = get_logger("another_module", "AnotherAgent")
    another_logger.info("来自另一个代理的日志消息")
    
    print("日志测试完成，请检查logs目录中的日志文件")

if __name__ == "__main__":
    main() 