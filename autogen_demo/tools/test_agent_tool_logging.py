#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试智能体工具调用的日志记录功能
"""

import sys
import os
import json
import functools

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging_config import setup_logging, get_logger

# 设置日志
setup_logging(level="DEBUG", log_to_file=True)
logger = get_logger(__name__, "TestModule")

# 模拟智能体类
class MockAgent:
    def __init__(self, name):
        self.name = name
        self.logger = get_logger(__name__, name)
    
    def __str__(self):
        return f"Agent({self.name})"

# 模拟工具调用日志装饰器
def log_tool_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 记录工具名称
        tool_name = func.__name__
        
        # 尝试识别调用者（智能体）
        caller_agent = "未知智能体"
        import inspect
        frame = inspect.currentframe().f_back
        while frame:
            # 检查调用栈，尝试找到智能体名称
            if 'self' in frame.f_locals:
                self_obj = frame.f_locals['self']
                if hasattr(self_obj, 'name') and isinstance(self_obj.name, str):
                    caller_agent = self_obj.name
                    break
            frame = frame.f_back
        
        # 准备参数日志
        safe_kwargs = {}
        for k, v in kwargs.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                # 对于字符串，如果太长则截断
                if isinstance(v, str) and len(v) > 100:
                    safe_kwargs[k] = v[:100] + "... (截断)"
                else:
                    safe_kwargs[k] = v
            else:
                # 对于复杂对象，只记录类型
                safe_kwargs[k] = f"<{type(v).__name__}>"
        
        # 记录调用日志
        log_message = f"智能体 [{caller_agent}] 调用工具: {tool_name}, 参数: {json.dumps(safe_kwargs, ensure_ascii=False)}"
        logger.info(log_message)
        
        try:
            # 执行原始函数
            result = func(*args, **kwargs)
            
            # 记录结果摘要
            if isinstance(result, (str, int, float, bool, type(None))):
                if isinstance(result, str) and len(result) > 100:
                    result_summary = result[:100] + "... (截断)"
                else:
                    result_summary = result
            elif isinstance(result, (list, dict)):
                result_summary = f"<{type(result).__name__}> 长度: {len(result)}"
            else:
                result_summary = f"<{type(result).__name__}>"
                
            logger.info(f"智能体 [{caller_agent}] 工具 {tool_name} 执行成功, 结果: {result_summary}")
            return result
            
        except Exception as e:
            # 记录异常
            logger.error(f"智能体 [{caller_agent}] 工具 {tool_name} 执行失败: {str(e)}")
            raise
    
    return wrapper

# 模拟工具函数
@log_tool_call
def search_tool(query, count=5):
    """模拟搜索工具"""
    logger.debug(f"执行搜索: {query}, 数量: {count}")
    return [f"搜索结果 {i} for {query}" for i in range(count)]

@log_tool_call
def analyze_image(url):
    """模拟图像分析工具"""
    logger.debug(f"分析图像: {url}")
    if "error" in url:
        raise ValueError("无效的图像URL")
    return {"description": "这是一张图片", "tags": ["自然", "风景"]}

@log_tool_call
def generate_report(topic, data):
    """模拟报告生成工具"""
    logger.debug(f"生成报告: {topic}")
    return f"关于 {topic} 的报告: " + "\n".join(data[:3]) + "..."

def main():
    """测试智能体工具调用的日志记录功能"""
    logger.info("开始测试智能体工具调用日志记录")
    
    # 创建模拟智能体
    search_agent = MockAgent("搜索智能体")
    vision_agent = MockAgent("视觉智能体")
    report_agent = MockAgent("报告智能体")
    
    # 模拟智能体调用工具
    logger.info("=== 测试搜索工具 ===")
    try:
        search_results = search_agent.search_tool = search_tool
        results = search_agent.search_tool(query="新能源汽车", count=3)
        logger.info(f"搜索结果: {results}")
    except Exception as e:
        logger.exception("搜索工具调用失败")
    
    logger.info("=== 测试图像分析工具 ===")
    try:
        vision_agent.analyze_image = analyze_image
        image_data = vision_agent.analyze_image(url="https://example.com/image.jpg")
        logger.info(f"图像分析结果: {image_data}")
    except Exception as e:
        logger.exception("图像分析工具调用失败")
    
    # 测试工具调用失败的情况
    logger.info("=== 测试工具调用失败 ===")
    try:
        vision_agent.analyze_image(url="https://example.com/error.jpg")
    except Exception as e:
        logger.warning(f"预期的错误: {e}")
    
    logger.info("=== 测试报告生成工具 ===")
    try:
        report_agent.generate_report = generate_report
        report = report_agent.generate_report(
            topic="新能源汽车发展趋势", 
            data=["数据点1", "数据点2", "数据点3", "数据点4", "数据点5"]
        )
        logger.info(f"报告: {report}")
    except Exception as e:
        logger.exception("报告生成工具调用失败")
    
    logger.info("智能体工具调用日志记录测试完成")
    print("测试完成，请检查logs目录中的日志文件")

if __name__ == "__main__":
    main() 