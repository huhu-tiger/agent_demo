# -*- coding: utf-8 -*-
"""
LangGraph 条件路由示例
学习要点：条件边、动态决策、路由函数

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
from typing import TypedDict, List
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# LangChain 组件
from langchain_core.messages import HumanMessage, AIMessage

import config

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger

# ============================================================================
# 条件路由状态定义
# ============================================================================

class RoutingState(TypedDict):
    """条件路由状态 - 包含决策结果和路由信息"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    decision: str
    route_reason: str
    response: str
    processing_path: List[str]

# ============================================================================
# 决策节点定义
# ============================================================================

def decision_maker(state: RoutingState) -> RoutingState:
    """
    决策制定节点 - 分析用户输入并决定处理路径
    学习要点：智能决策逻辑
    """
    logger.info("🧠 决策制定节点正在分析...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"].lower()
    processing_path = state.get("processing_path", [])
    processing_path.append("decision_maker")
    
    # 决策逻辑
    if any(word in user_input for word in ["计算", "数学", "数字", "+", "-", "*", "/"]):
        decision = "calculator"
        route_reason = "检测到数学计算需求"
    elif any(word in user_input for word in ["天气", "温度", "下雨", "晴天"]):
        decision = "weather"
        route_reason = "检测到天气查询需求"
    elif any(word in user_input for word in ["搜索", "查找", "信息", "资料"]):
        decision = "search"
        route_reason = "检测到信息搜索需求"
    elif any(word in user_input for word in ["翻译", "英文", "中文", "language"]):
        decision = "translator"
        route_reason = "检测到翻译需求"
    else:
        decision = "general"
        route_reason = "通用处理路径"
    
    logger.info(f"决策结果: {decision}")
    logger.info(f"决策原因: {route_reason}")
    
    return {
        "decision": decision,
        "route_reason": route_reason,
        "processing_path": processing_path,
        "messages": [AIMessage(content=f"决策完成: {route_reason}")]
    }

# ============================================================================
# 专业处理节点定义
# ============================================================================

def calculator_agent(state: RoutingState) -> RoutingState:
    """计算器智能体"""
    logger.info("🧮 计算器智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("calculator")
    
    # 简单的计算逻辑
    import re
    numbers = re.findall(r'\d+', user_input)
    operators = re.findall(r'[\+\-\*\/]', user_input)
    
    if len(numbers) >= 2 and operators:
        try:
            num1, num2 = int(numbers[0]), int(numbers[1])
            op = operators[0]
            
            if op == '+':
                result = num1 + num2
            elif op == '-':
                result = num1 - num2
            elif op == '*':
                result = num1 * num2
            elif op == '/':
                result = num1 / num2 if num2 != 0 else "除数不能为零"
            else:
                result = "不支持的运算符"
                
            response = f"计算结果: {num1} {op} {num2} = {result}"
        except Exception as e:
            response = f"计算错误: {str(e)}"
    else:
        response = "请提供有效的数学表达式，例如: '计算 5 + 3'"
    
    return {
        "response": response,
        "processing_path": processing_path,
        "messages": [AIMessage(content=response)]
    }

def weather_agent(state: RoutingState) -> RoutingState:
    """天气智能体"""
    logger.info("🌤️ 天气智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("weather")
    
    # 模拟天气数据
    weather_data = {
        "北京": "晴天，温度 25°C，空气质量良好",
        "上海": "多云，温度 28°C，空气质量一般",
        "广州": "小雨，温度 30°C，空气质量良好",
        "深圳": "晴天，温度 29°C，空气质量优秀"
    }
    
    # 提取城市名
    cities = ["北京", "上海", "广州", "深圳"]
    found_city = None
    for city in cities:
        if city in user_input:
            found_city = city
            break
    
    if found_city:
        response = f"{found_city}的天气: {weather_data[found_city]}"
    else:
        response = "请指定城市名称，例如: '查询北京的天气'"
    
    return {
        "response": response,
        "processing_path": processing_path,
        "messages": [AIMessage(content=response)]
    }

def search_agent(state: RoutingState) -> RoutingState:
    """搜索智能体"""
    logger.info("🔍 搜索智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("search")
    
    # 模拟搜索结果
    response = f"关于 '{user_input}' 的搜索结果:\n"
    response += "1. 相关信息1\n"
    response += "2. 相关信息2\n"
    response += "3. 相关信息3\n"
    response += "(这是模拟的搜索结果)"
    
    return {
        "response": response,
        "processing_path": processing_path,
        "messages": [AIMessage(content=response)]
    }

def translator_agent(state: RoutingState) -> RoutingState:
    """翻译智能体"""
    logger.info("🌐 翻译智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("translator")
    
    # 简单的翻译逻辑
    if any(word in user_input for word in ["hello", "你好"]):
        if "hello" in user_input.lower():
            response = "翻译结果: hello → 你好"
        else:
            response = "翻译结果: 你好 → hello"
    else:
        response = "请提供需要翻译的文本，例如: '翻译 hello'"
    
    return {
        "response": response,
        "processing_path": processing_path,
        "messages": [AIMessage(content=response)]
    }

def general_agent(state: RoutingState) -> RoutingState:
    """通用智能体"""
    logger.info("💬 通用智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("general")
    
    response = f"我理解您说: '{user_input}'。这是一个通用回复，如果您有特定需求，请告诉我。"
    
    return {
        "response": response,
        "processing_path": processing_path,
        "messages": [AIMessage(content=response)]
    }

# ============================================================================
# 路由函数
# ============================================================================

def route_decision(state: RoutingState) -> str:
    """
    路由函数 - 根据决策结果选择下一个节点
    学习要点：条件路由的核心逻辑
    """
    decision = state["decision"]
    logger.info(f"路由决策: {decision}")
    
    routing_map = {
        "calculator": "calculator_agent",
        "weather": "weather_agent", 
        "search": "search_agent",
        "translator": "translator_agent",
        "general": "general_agent"
    }
    
    return routing_map.get(decision, "general_agent")

# ============================================================================
# 工作流构建
# ============================================================================

def create_routing_workflow():
    """
    创建条件路由工作流
    学习要点：条件边的使用
    """
    logger.info("\n" + "="*60)
    logger.info("🧠 条件路由工作流")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(RoutingState)
    
    # 2. 添加节点
    workflow.add_node("decision_maker", decision_maker)
    workflow.add_node("calculator_agent", calculator_agent)
    workflow.add_node("weather_agent", weather_agent)
    workflow.add_node("search_agent", search_agent)
    workflow.add_node("translator_agent", translator_agent)
    workflow.add_node("general_agent", general_agent)
    
    # 3. 设置入口点
    workflow.set_entry_point("decision_maker")
    
    # 4. 添加条件边
    workflow.add_conditional_edges(
        "decision_maker",
        route_decision,
        {
            "calculator_agent": "calculator_agent",
            "weather_agent": "weather_agent",
            "search_agent": "search_agent", 
            "translator_agent": "translator_agent",
            "general_agent": "general_agent"
        }
    )
    
    # 5. 添加结束边
    workflow.add_edge("calculator_agent", END)
    workflow.add_edge("weather_agent", END)
    workflow.add_edge("search_agent", END)
    workflow.add_edge("translator_agent", END)
    workflow.add_edge("general_agent", END)
    
    # 6. 编译工作流
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 测试函数
# ============================================================================

def test_conditional_routing():
    """测试条件路由"""
    logger.info("🎯 测试 LangGraph 条件路由")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 创建工作流
    graph = create_routing_workflow()
    
    # 测试输入
    test_inputs = [
        "请帮我计算 15 + 25",
        "查询北京的天气怎么样",
        "搜索关于人工智能的信息",
        "翻译 hello 这个单词",
        "你好，我想了解一下 LangGraph"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        logger.info(f"\n--- 测试 {i} ---")
        logger.info(f"输入: {test_input}")
        
        try:
            result = graph.invoke({"user_input": test_input})
            logger.info(f"决策: {result['decision']}")
            logger.info(f"决策原因: {result['route_reason']}")
            logger.info(f"处理路径: {' → '.join(result['processing_path'])}")
            logger.info(f"输出: {result['response']}")
        except Exception as e:
            logger.error(f"错误: {e}")

if __name__ == "__main__":
    test_conditional_routing() 