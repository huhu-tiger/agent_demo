"""
Centralized logging configuration for the multi-agent system.
多智能体系统的集中式日志配置。
"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# 创建一个自定义的日志格式化器，添加 agent 字段
class AgentLogFormatter(logging.Formatter):
    """
    Custom log formatter that adds an 'agent' field to log records.
    自定义日志格式化器，为日志记录添加 'agent' 字段。
    """
    def format(self, record):
        # 如果记录中没有 agent 属性，则添加一个默认值
        if not hasattr(record, 'agent'):
            record.agent = 'system'
        return super().format(record)

# 配置根日志记录器
def setup_logging(level: Optional[str] = None, log_to_file: bool = True):
    """
    Set up logging configuration for the application.
    为应用程序设置日志配置。
    
    Args:
        level: Optional log level override. If None, uses LOG_LEVEL from environment or defaults to INFO.
              可选的日志级别覆盖。如果为 None，则使用环境变量 LOG_LEVEL 或默认为 INFO。
        log_to_file: Whether to log to a file in addition to console. Defaults to True.
                    是否除了控制台外还记录到文件。默认为 True。
    """
    # 获取日志级别，优先使用传入的参数，然后是环境变量，最后是默认值
    log_level = level or os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # 打印当前使用的日志级别，帮助调试
    print(f"设置日志级别为: {log_level}")
    
    # 创建格式化器 - 添加文件名和行号
    formatter = AgentLogFormatter(
        fmt="%(asctime)s | %(levelname)s | %(agent)s | %(pathname)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除任何现有的处理程序，以避免重复
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理程序
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 如果启用了文件日志
    if log_to_file:
        # 创建logs目录（如果不存在）
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # 使用当前日期和时间创建日志文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = logs_dir / f"agent_log_{current_time}.log"
        
        # 创建文件处理程序
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        print(f"日志将写入文件: {log_file_path}")
    
    # 记录一条初始化日志，确认级别设置成功
    root_logger.info(f"日志系统初始化完成，级别: {log_level}")
    
    # 返回根日志记录器
    return root_logger

# 创建一个日志记录器获取函数
def get_logger(name: str, agent_name: Optional[str] = None):
    """
    Get a logger with the specified name and optional agent name.
    获取具有指定名称和可选代理名称的日志记录器。
    
    Args:
        name: The logger name, typically __name__.
              日志记录器名称，通常为 __name__。
        agent_name: Optional agent name to include in logs.
                   可选的代理名称，包含在日志中。
    
    Returns:
        A configured logger instance.
        一个已配置的日志记录器实例。
    """
    logger = logging.getLogger(name)
    
    # 添加一个过滤器来设置 agent 属性
    class AgentFilter(logging.Filter):
        def filter(self, record):
            record.agent = agent_name or name
            return True
    
    # 移除任何现有的过滤器
    for f in logger.filters[:]:
        logger.removeFilter(f)
    
    # 添加新的过滤器
    logger.addFilter(AgentFilter())
    
    return logger

# 默认设置日志
# logger = setup_logging() 
