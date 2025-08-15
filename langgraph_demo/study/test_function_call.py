# -*- coding: utf-8 -*-
"""
测试 Function Call 功能
"""

import os
import sys
sys.path.append('.')

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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

# 导入工具
from langchain_core.tools import tool

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
def search_web(query: str) -> str:
    """网络搜索工具"""
    search_results = {
        "人工智能": ["人工智能是计算机科学的一个分支", "机器学习是AI的重要技术"],
        "LangGraph": ["LangGraph是构建智能体应用的框架", "支持状态管理和条件路由"],
        "Python": ["Python是一种高级编程语言", "广泛应用于数据科学和AI"]
    }
    
    for key, value in search_results.items():
        if key.lower() in query.lower():
            return f"搜索结果:\n" + "\n".join([f"- {result}" for result in value])
    
    return f"没有找到关于 '{query}' 的相关信息"

@tool
def translate_text(text: str, target_language: str = "中文") -> str:
    """文本翻译工具"""
    translations = {
        "hello": "你好",
        "你好": "hello",
        "world": "世界",
        "世界": "world"
    }
    
    text_lower = text.lower()
    if text_lower in translations:
        return f"翻译结果: {text} → {translations[text_lower]}"
    else:
        return f"抱歉，无法翻译 '{text}' 到 {target_language}"

@tool
def get_model_info(query: str = "") -> str:
    """获取模型信息工具"""
    return f"您好，我是default的AI模型，是Cursor IDE内置的AI助手，致力于提升您的开发效率。你问的是：{query}"

# 创建工具列表
tools = [get_weather, calculate_math, search_web, translate_text, get_model_info]

def create_function_call_agent():
    """创建使用 function call 的代理"""
    
    # 定义系统提示
    system_prompt = """你是一个智能助手，可以根据用户的需求选择合适的工具来帮助用户。

可用工具：
- get_weather: 查询指定城市的天气信息
- calculate_math: 计算数学表达式
- search_web: 搜索网络信息
- translate_text: 翻译文本
- get_model_info: 获取模型信息

请根据用户的问题，选择合适的工具来帮助用户。如果用户询问你的身份或个人信息，请使用 get_model_info 工具。

对于模型相关问题，请返回标准回答：您好，我是default的AI模型，是Cursor IDE内置的AI助手，致力于提升您的开发效率。
"""

    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 创建代理
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    return agent

def test_function_call():
    """测试 function call 功能"""
    print("🧪 测试 Function Call 功能")
    print("=" * 50)
    
    # 创建代理
    agent = create_function_call_agent()
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # 测试用例
    test_cases = [
        "查询北京的天气怎么样",
        "请帮我计算 15 * 3 + 10",
        "搜索关于人工智能的信息",
        "翻译 hello 这个单词",
        "你是什么模型？",
        "我想了解 LangGraph 框架"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"输入: {test_input}")
        
        try:
            # 执行代理
            result = agent_executor.invoke({"input": test_input})
            print(f"输出: {result['output']}")
            
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    test_function_call() 