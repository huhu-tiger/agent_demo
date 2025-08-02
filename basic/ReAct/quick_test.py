#!/usr/bin/env python3
"""
快速测试脚本 - 验证提示词优化效果
"""

import os
from dotenv import load_dotenv
from demo import create_agent

def quick_test():
    """快速测试"""
    print("🚀 快速测试 - 验证提示词优化效果")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 创建智能体
    agent = create_agent()
    
    # 测试用例
    test_cases = [
        {
            "category": "身份问题",
            "questions": [
                "你是什么模型？",
                "你是谁？",
                "你是什么技术？",
                "你是什么工具？"
            ]
        },
        {
            "category": "工具调用",
            "questions": [
                "计算 10 + 20",
                "现在几点了？",
                "北京天气怎么样？"
            ]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 {test_case['category']}测试")
        print("-" * 30)
        
        for question in test_case['questions']:
            print(f"\n❓ 问题: {question}")
            try:
                response = agent.think(question)
                print(f"✅ 回答: {response}")
                
                # 验证身份问题的标准回答
                if test_case['category'] == "身份问题":
                    expected_start = "我是基于default模型的AI助手"
                    if expected_start in response:
                        print("✅ 身份回答正确")
                    else:
                        print("❌ 身份回答不正确")
                        
            except Exception as e:
                print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 快速测试完成")

if __name__ == "__main__":
    quick_test() 