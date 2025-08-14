# -*- coding: utf-8 -*-
"""
LangGraph 工具集成示例
学习要点：工具定义、工具调用、状态扩展

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import json
import requests
from typing import TypedDict, List
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# LangChain 组件
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

import config

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger

# ============================================================================
# 工具定义
# ============================================================================

@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息字符串
    """
    logger.info(f"🌤️ 调用天气工具，查询城市: {city}")
    
    # 模拟天气数据
    weather_data = {
        "北京": {
            "temperature": "25°C",
            "condition": "晴天",
            "humidity": "45%",
            "wind": "东北风 3级"
        },
        "上海": {
            "temperature": "28°C", 
            "condition": "多云",
            "humidity": "65%",
            "wind": "东南风 4级"
        },
        "广州": {
            "temperature": "30°C",
            "condition": "小雨", 
            "humidity": "80%",
            "wind": "南风 2级"
        },
        "深圳": {
            "temperature": "29°C",
            "condition": "晴天",
            "humidity": "55%", 
            "wind": "东南风 3级"
        }
    }
    
    if city in weather_data:
        data = weather_data[city]
        result = f"{city}天气: {data['condition']}, 温度{data['temperature']}, 湿度{data['humidity']}, {data['wind']}"
    else:
        result = f"抱歉，没有找到 {city} 的天气信息"
    
    logger.info(f"天气工具返回: {result}")
    return result

@tool
def calculate_math(expression: str) -> str:
    """
    计算数学表达式
    
    Args:
        expression: 数学表达式，如 "2 + 3 * 4"
        
    Returns:
        计算结果字符串
    """
    logger.info(f"🧮 调用数学计算工具，表达式: {expression}")
    
    try:
        # 安全计算（实际应用中需要更严格的验证）
        result = eval(expression)
        response = f"计算结果: {expression} = {result}"
    except Exception as e:
        response = f"计算错误: {str(e)}"
    
    logger.info(f"数学工具返回: {response}")
    return response

@tool
def search_web(query: str) -> str:
    """
    网络搜索工具
    
    Args:
        query: 搜索查询
        
    Returns:
        搜索结果字符串
    """
    logger.info(f"🔍 调用网络搜索工具，查询: {query}")
    
    # 模拟搜索结果
    search_results = {
        "人工智能": [
            "人工智能是计算机科学的一个分支",
            "机器学习是AI的重要技术",
            "深度学习在图像识别方面表现优异"
        ],
        "LangGraph": [
            "LangGraph是构建智能体应用的框架",
            "支持状态管理和条件路由",
            "可以创建复杂的多智能体系统"
        ],
        "Python": [
            "Python是一种高级编程语言",
            "广泛应用于数据科学和AI",
            "语法简洁，易于学习"
        ]
    }
    
    # 查找相关结果
    results = []
    for key, value in search_results.items():
        if key.lower() in query.lower():
            results.extend(value)
    
    if results:
        response = f"搜索结果:\n" + "\n".join([f"- {result}" for result in results[:3]])
    else:
        response = f"没有找到关于 '{query}' 的相关信息"
    
    logger.info(f"搜索工具返回: {response}")
    return response

@tool
def translate_text(text: str, target_language: str = "中文") -> str:
    """
    文本翻译工具
    
    Args:
        text: 要翻译的文本
        target_language: 目标语言
        
    Returns:
        翻译结果字符串
    """
    logger.info(f"🌐 调用翻译工具，文本: {text}, 目标语言: {target_language}")
    
    # 简单的翻译映射
    translations = {
        "hello": "你好",
        "你好": "hello",
        "world": "世界",
        "世界": "world",
        "python": "Python编程语言",
        "ai": "人工智能",
        "人工智能": "artificial intelligence"
    }
    
    text_lower = text.lower()
    if text_lower in translations:
        result = f"翻译结果: {text} → {translations[text_lower]}"
    else:
        result = f"抱歉，无法翻译 '{text}' 到 {target_language}"
    
    logger.info(f"翻译工具返回: {result}")
    return result

# ============================================================================
# 工具状态定义
# ============================================================================

class ToolState(TypedDict):
    """工具状态 - 包含工具调用结果和处理信息"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    tool_results: List[str]
    selected_tools: List[str]
    final_response: str

# ============================================================================
# 工具智能体节点
# ============================================================================

def tool_selector(state: ToolState) -> ToolState:
    """
    工具选择节点 - 分析用户需求并选择合适的工具
    学习要点：工具选择逻辑
    """
    logger.info("🔧 工具选择节点正在分析...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"].lower()
    selected_tools = []
    
    # 工具选择逻辑
    if any(word in user_input for word in ["天气", "温度", "下雨", "晴天"]):
        selected_tools.append("get_weather")
    
    if any(word in user_input for word in ["计算", "数学", "+", "-", "*", "/"]):
        selected_tools.append("calculate_math")
    
    if any(word in user_input for word in ["搜索", "查找", "信息", "资料"]):
        selected_tools.append("search_web")
    
    if any(word in user_input for word in ["翻译", "英文", "中文", "language"]):
        selected_tools.append("translate_text")
    
    logger.info(f"选择的工具: {selected_tools}")
    
    return {
        "selected_tools": selected_tools,
        "messages": [AIMessage(content=f"已选择工具: {', '.join(selected_tools) if selected_tools else '无'}")]
    }

def tool_executor(state: ToolState) -> ToolState:
    """
    工具执行节点 - 执行选定的工具
    学习要点：工具调用和结果处理
    """
    logger.info("⚙️ 工具执行节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    selected_tools = state["selected_tools"]
    tool_results = []
    
    # 执行工具
    for tool_name in selected_tools:
        try:
            if tool_name == "get_weather":
                # 提取城市名
                cities = ["北京", "上海", "广州", "深圳"]
                for city in cities:
                    if city in user_input:
                        result = get_weather(city)
                        tool_results.append(f"天气查询: {result}")
                        break
                else:
                    tool_results.append("天气查询: 请指定城市名称")
            
            elif tool_name == "calculate_math":
                # 提取数学表达式
                import re
                expression = re.findall(r'[\d\+\-\*\/\(\)]+', user_input)
                if expression:
                    result = calculate_math(expression[0])
                    tool_results.append(result)
                else:
                    tool_results.append("数学计算: 请提供数学表达式")
            
            elif tool_name == "search_web":
                # 提取搜索关键词
                search_keywords = ["人工智能", "LangGraph", "Python"]
                for keyword in search_keywords:
                    if keyword.lower() in user_input.lower():
                        result = search_web(keyword)
                        tool_results.append(result)
                        break
                else:
                    result = search_web(user_input)
                    tool_results.append(result)
            
            elif tool_name == "translate_text":
                # 提取翻译文本
                if "hello" in user_input.lower():
                    result = translate_text("hello")
                elif "你好" in user_input:
                    result = translate_text("你好")
                else:
                    result = translate_text(user_input)
                tool_results.append(result)
                
        except Exception as e:
            tool_results.append(f"工具 {tool_name} 执行错误: {str(e)}")
    
    if not tool_results:
        tool_results.append("没有找到合适的工具来处理您的请求")
    
    logger.info(f"工具执行结果: {tool_results}")
    
    return {
        "tool_results": tool_results,
        "messages": [AIMessage(content="工具执行完成")]
    }

def response_synthesizer(state: ToolState) -> ToolState:
    """
    响应合成节点 - 整合工具结果生成最终响应
    学习要点：结果整合和响应生成
    """
    logger.info("🎯 响应合成节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    tool_results = state["tool_results"]
    selected_tools = state["selected_tools"]
    
    # 合成最终响应
    if tool_results:
        final_response = f"根据您的需求 '{user_input}'，我为您提供了以下信息：\n\n"
        for i, result in enumerate(tool_results, 1):
            final_response += f"{i}. {result}\n"
        final_response += f"\n使用了 {len(selected_tools)} 个工具: {', '.join(selected_tools)}"
    else:
        final_response = f"抱歉，我无法处理您的请求 '{user_input}'。请尝试更具体的描述。"
    
    logger.info(f"最终响应: {final_response}")
    
    return {
        "final_response": final_response,
        "messages": [AIMessage(content=final_response)]
    }

# ============================================================================
# 工作流构建
# ============================================================================

def create_tool_workflow():
    """
    创建工具集成工作流
    学习要点：工具节点的集成
    """
    logger.info("\n" + "="*60)
    logger.info("🛠️ 工具集成工作流")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(ToolState)
    
    # 2. 添加节点
    workflow.add_node("tool_selector", tool_selector)
    workflow.add_node("tool_executor", tool_executor)
    workflow.add_node("response_synthesizer", response_synthesizer)
    
    # 3. 设置入口点
    workflow.set_entry_point("tool_selector")
    
    # 4. 添加边（顺序执行）
    workflow.add_edge("tool_selector", "tool_executor")
    workflow.add_edge("tool_executor", "response_synthesizer")
    workflow.add_edge("response_synthesizer", END)
    
    # 5. 编译工作流
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 测试函数
# ============================================================================

def test_tools_integration():
    """测试工具集成"""
    logger.info("🛠️ 测试 LangGraph 工具集成")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 创建工作流
    graph = create_tool_workflow()
    
    # 测试输入
    test_inputs = [
        "查询北京的天气怎么样",
        "请帮我计算 15 * 3 + 10",
        "搜索关于人工智能的信息",
        "翻译 hello 这个单词",
        "我想了解 LangGraph 框架"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        logger.info(f"\n--- 测试 {i} ---")
        logger.info(f"输入: {test_input}")
        
        try:
            result = graph.invoke({"user_input": test_input})
            logger.info(f"选择的工具: {result['selected_tools']}")
            logger.info(f"工具结果: {result['tool_results']}")
            logger.info(f"最终响应: {result['final_response']}")
        except Exception as e:
            logger.error(f"错误: {e}")

if __name__ == "__main__":
    test_tools_integration() 