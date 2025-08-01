#!/usr/bin/env python3
"""
ReAct智能体测试脚本
"""

import os
import sys
from demo import create_agent

def test_agent():
    """测试智能体功能"""
    print("=== ReAct智能体测试 ===")
    
    # 创建智能体
    agent = create_agent()
    
    # 测试用例
    test_cases = [
        "你是什么模型？",
        "计算 25 * 4 + 10",
        "北京今天天气怎么样？",
        "现在几点了？",
        "搜索关于人工智能的信息",
        "计算 (15 + 5) * 2"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i}: {test_input} ---")
        try:
            response = agent.think(test_input)
            print(f"响应: {response}")
        except Exception as e:
            print(f"测试失败: {str(e)}")
        
        print("-" * 40)

def test_tools():
    """测试工具功能"""
    print("\n=== 工具功能测试 ===")
    
    from demo import get_current_time, calculate, get_weather, search_web
    
    # 测试时间工具
    print(f"当前时间: {get_current_time()}")
    
    # 测试计算工具
    print(f"计算 10 + 20: {calculate('10 + 20')}")
    print(f"计算 5 * 6: {calculate('5 * 6')}")
    
    # 测试天气工具
    print(f"北京天气: {get_weather('北京')}")
    print(f"上海天气: {get_weather('上海')}")
    
    # 测试搜索工具
    print(f"搜索结果: {search_web('Python编程')}")

if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("警告: 未设置OPENAI_API_KEY环境变量")
        print("请设置API密钥: export OPENAI_API_KEY='your-key-here'")
        print("或者直接在代码中设置")
    
    # 运行测试
    test_tools()
    test_agent() 