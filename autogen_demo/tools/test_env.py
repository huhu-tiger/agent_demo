"""
测试环境变量加载和日志配置的脚本。
"""

import os
from dotenv import load_dotenv
import logging
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_env_loading():
    """测试环境变量加载"""
    print("1. 测试 .env 文件加载前:")
    print(f"   LOG_LEVEL = {os.environ.get('LOG_LEVEL', '未设置')}")
    
    # 显式加载 .env 文件
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    print(f"2. 尝试从 {dotenv_path} 加载 .env 文件")
    load_dotenv(dotenv_path)
    
    print("3. 测试 .env 文件加载后:")
    print(f"   LOG_LEVEL = {os.environ.get('LOG_LEVEL', '未设置')}")
    
    # 导入 core 包，触发其中的 __init__.py
    print("4. 导入 core 包:")
    import core
    
    print("5. 测试日志级别:")
    logger = logging.getLogger("test")
    logger.debug("这是一条 DEBUG 日志")
    logger.info("这是一条 INFO 日志")
    logger.warning("这是一条 WARNING 日志")
    logger.error("这是一条 ERROR 日志")

if __name__ == "__main__":
    test_env_loading() 