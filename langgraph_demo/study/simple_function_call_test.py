# -*- coding: utf-8 -*-
"""
简单的 Function Call 测试
"""

import os
import sys
sys.path.append('.')

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import config

# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 初始化语言模型
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,
    max_tokens=1000
)

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    weather_data = {
        "北京": {"temperature": "25°C", "condition": "晴天"},
        "上海": {"temperature": "28°C", "condition": "多云"},
        "广州": {"temperature": "30°C", "condition": "小雨"},
        "深圳": {"temperature": "29°C", "condition": "晴天"}
    }
    
    if city in weather_data:
        data = weather_data[city]
        return f"{city}天气: {data['condition']}, 温度{data['temperature']}"
    else:
        return f"抱歉，没有找到 {city} 的天气信息"

@tool
def calculate_math(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_model_info(query: str = "") -> str:
    """获取模型信息工具"""
    return f"您好，我是default的AI模型，是Cursor IDE内置的AI助手，致力于提升您的开发效率。你问的是：{query}"

def test_simple_function_call():
    """测试简单的 function call"""
    print("🧪 测试简单 Function Call")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        "查询北京的天气怎么样",
        "请帮我计算 15 * 3 + 10",
        "你是什么模型？"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"输入: {test_input}")
        
        try:
            # 直接调用大模型，让它决定使用哪个工具
            prompt = f"""
请根据用户的问题，选择合适的工具来帮助用户。

可用工具：
- get_weather: 查询指定城市的天气信息
- calculate_math: 计算数学表达式
- get_model_info: 获取模型信息

用户问题：{test_input}

请分析问题并选择合适的工具。如果用户询问你的身份，请使用 get_model_info 工具。
"""
            
            # 调用大模型
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages)
            
            print(f"模型回答: {response.content}")
            
            # 根据模型回答执行相应工具
            if "get_weather" in response.content.lower():
                if "北京" in test_input:
                    result = get_weather("北京")
                    print(f"执行天气工具: {result}")
                elif "上海" in test_input:
                    result = get_weather("上海")
                    print(f"执行天气工具: {result}")
                else:
                    print("需要指定城市名称")
            
            elif "calculate_math" in response.content.lower():
                import re
                expression = re.findall(r'[\d\+\-\*\/\(\)]+', test_input)
                if expression:
                    result = calculate_math(expression[0])
                    print(f"执行数学计算: {result}")
                else:
                    print("需要提供数学表达式")
            
            elif "get_model_info" in response.content.lower():
                result = get_model_info(test_input)
                print(f"执行模型信息工具: {result}")
            
            else:
                print("模型没有明确选择工具")
                
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    test_simple_function_call() 