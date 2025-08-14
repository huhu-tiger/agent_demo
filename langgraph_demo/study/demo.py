# -*- coding: utf-8 -*-
"""
LangGraph 智能体学习示例

本示例将帮助您学习 LangGraph 的核心概念：
1. 状态管理 (State)
2. 节点定义 (Nodes) 
3. 边连接 (Edges)
4. 条件路由 (Conditional Edges)
5. 多智能体协作
6. 工具使用

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import asyncio
from typing import TypedDict, List, Dict, Any
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# LangChain 组件
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# 设置环境变量
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# ============================================================================
# 第一部分：基础概念 - 简单的智能体工作流
# ============================================================================

class BasicState(TypedDict):
    """基础状态定义 - 包含消息历史"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    response: str

def basic_agent(state: BasicState) -> BasicState:
    """
    基础智能体节点
    
    这是 LangGraph 中最简单的节点示例：
    - 接收当前状态
    - 处理用户输入
    - 返回更新后的状态
    """
    print("🤖 基础智能体正在处理...")
    
    # 获取用户输入
    user_input = state["user_input"]
    
    # 简单的响应逻辑
    if "你好" in user_input:
        response = "你好！我是基础智能体，很高兴为您服务！"
    elif "天气" in user_input:
        response = "抱歉，我还没有天气查询功能，但我可以帮您聊天！"
    else:
        response = f"我收到了您的消息：'{user_input}'。这是一个基础智能体的回复。"
    
    return {
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def create_basic_workflow():
    """创建基础工作流"""
    print("\n" + "="*60)
    print("🚀 第一部分：基础智能体工作流")
    print("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(BasicState)
    
    # 2. 添加节点
    workflow.add_node("basic_agent", basic_agent)
    
    # 3. 设置入口点
    workflow.set_entry_point("basic_agent")
    
    # 4. 添加边（从智能体到结束）
    workflow.add_edge("basic_agent", END)
    
    # 5. 编译工作流
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 第二部分：条件路由 - 智能决策工作流
# ============================================================================

class DecisionState(TypedDict):
    """决策状态 - 包含用户输入和决策结果"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    decision: str
    response: str

def decision_agent(state: DecisionState) -> DecisionState:
    """
    决策智能体 - 分析用户输入并做出决策
    """
    print("🧠 决策智能体正在分析...")
    
    user_input = state["user_input"].lower()
    
    # 简单的决策逻辑
    if any(word in user_input for word in ["计算", "数学", "数字"]):
        decision = "calculator"
        response = "我检测到您需要计算功能，正在为您准备计算器..."
    elif any(word in user_input for word in ["搜索", "查找", "信息"]):
        decision = "search"
        response = "我检测到您需要搜索功能，正在为您准备搜索引擎..."
    elif any(word in user_input for word in ["聊天", "对话", "闲聊"]):
        decision = "chat"
        response = "我检测到您想要聊天，让我们开始愉快的对话吧！"
    else:
        decision = "unknown"
        response = "我不太确定您想要什么，让我为您提供通用回复。"
    
    return {
        "decision": decision,
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def calculator_agent(state: DecisionState) -> DecisionState:
    """计算器智能体"""
    print("🧮 计算器智能体正在工作...")
    
    user_input = state["user_input"]
    # 简单的计算逻辑（实际应用中会使用更复杂的计算库）
    try:
        # 提取数字和运算符
        import re
        numbers = re.findall(r'\d+', user_input)
        if len(numbers) >= 2:
            result = int(numbers[0]) + int(numbers[1])  # 简单加法
            response = f"计算结果：{numbers[0]} + {numbers[1]} = {result}"
        else:
            response = "请提供需要计算的数字，例如：'计算 5 加 3'"
    except:
        response = "抱歉，我无法理解您的计算请求。"
    
    return {
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def search_agent(state: DecisionState) -> DecisionState:
    """搜索智能体"""
    print("🔍 搜索智能体正在工作...")
    
    user_input = state["user_input"]
    response = f"我正在搜索关于 '{user_input}' 的信息...\n（这是模拟搜索结果）"
    
    return {
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def chat_agent(state: DecisionState) -> DecisionState:
    """聊天智能体"""
    print("💬 聊天智能体正在工作...")
    
    user_input = state["user_input"]
    response = f"很高兴和您聊天！您说：'{user_input}'，这很有趣！"
    
    return {
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def route_decision(state: DecisionState) -> str:
    """
    路由函数 - 根据决策结果选择下一个节点
    """
    decision = state["decision"]
    
    if decision == "calculator":
        return "calculator_agent"
    elif decision == "search":
        return "search_agent"
    elif decision == "chat":
        return "chat_agent"
    else:
        return "chat_agent"  # 默认到聊天智能体

def create_decision_workflow():
    """创建决策工作流"""
    print("\n" + "="*60)
    print("🧠 第二部分：条件路由决策工作流")
    print("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(DecisionState)
    
    # 2. 添加节点
    workflow.add_node("decision_agent", decision_agent)
    workflow.add_node("calculator_agent", calculator_agent)
    workflow.add_node("search_agent", search_agent)
    workflow.add_node("chat_agent", chat_agent)
    
    # 3. 设置入口点
    workflow.set_entry_point("decision_agent")
    
    # 4. 添加条件边
    workflow.add_conditional_edges(
        "decision_agent",
        route_decision,
        {
            "calculator_agent": "calculator_agent",
            "search_agent": "search_agent", 
            "chat_agent": "chat_agent"
        }
    )
    
    # 5. 添加结束边
    workflow.add_edge("calculator_agent", END)
    workflow.add_edge("search_agent", END)
    workflow.add_edge("chat_agent", END)
    
    # 6. 编译工作流
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 第三部分：工具使用 - 增强智能体能力
# ============================================================================

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 模拟天气数据
    weather_data = {
        "北京": "晴天，温度 25°C，空气质量良好",
        "上海": "多云，温度 28°C，空气质量一般", 
        "广州": "小雨，温度 30°C，空气质量良好",
        "深圳": "晴天，温度 29°C，空气质量优秀"
    }
    return weather_data.get(city, f"抱歉，没有找到 {city} 的天气信息")

@tool
def calculate_math(expression: str) -> str:
    """计算数学表达式"""
    try:
        # 安全计算（实际应用中需要更严格的验证）
        result = eval(expression)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

class ToolState(TypedDict):
    """工具状态 - 包含消息和工具调用结果"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    tool_results: List[str]

def tool_agent(state: ToolState) -> ToolState:
    """
    工具智能体 - 使用工具处理用户请求
    """
    print("🛠️ 工具智能体正在工作...")
    
    user_input = state["user_input"].lower()
    tool_results = []
    
    # 检测工具使用需求
    if "天气" in user_input:
        # 提取城市名
        cities = ["北京", "上海", "广州", "深圳"]
        for city in cities:
            if city in user_input:
                result = get_weather(city)
                tool_results.append(f"天气查询结果：{result}")
                break
        else:
            tool_results.append("请指定城市名称，例如：'查询北京的天气'")
    
    elif any(word in user_input for word in ["计算", "数学", "+", "-", "*", "/"]):
        # 提取数学表达式
        import re
        expression = re.findall(r'[\d\+\-\*\/\(\)]+', user_input)
        if expression:
            result = calculate_math(expression[0])
            tool_results.append(result)
        else:
            tool_results.append("请提供数学表达式，例如：'计算 5 + 3'")
    
    else:
        tool_results.append("我理解您的需求，但目前没有合适的工具。让我为您提供一般性回复。")
    
    response = "\n".join(tool_results)
    
    return {
        "tool_results": tool_results,
        "messages": [AIMessage(content=response)]
    }

def create_tool_workflow():
    """创建工具工作流"""
    print("\n" + "="*60)
    print("🛠️ 第三部分：工具使用工作流")
    print("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(ToolState)
    
    # 2. 添加节点
    workflow.add_node("tool_agent", tool_agent)
    
    # 3. 设置入口点
    workflow.set_entry_point("tool_agent")
    
    # 4. 添加边
    workflow.add_edge("tool_agent", END)
    
    # 5. 编译工作流
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 第四部分：多智能体协作 - 复杂工作流
# ============================================================================

class CollaborationState(TypedDict):
    """协作状态 - 多个智能体共享状态"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    research_result: str
    analysis_result: str
    final_response: str

def researcher_agent(state: CollaborationState) -> CollaborationState:
    """
    研究员智能体 - 负责信息收集
    """
    print("🔬 研究员智能体正在收集信息...")
    
    user_input = state["user_input"]
    
    # 模拟研究过程
    research_result = f"关于 '{user_input}' 的研究发现：\n"
    research_result += "1. 这是一个热门话题\n"
    research_result += "2. 有很多相关讨论\n"
    research_result += "3. 存在不同的观点\n"
    
    return {
        "research_result": research_result,
        "messages": [AIMessage(content=f"研究完成：{research_result}")]
    }

def analyst_agent(state: CollaborationState) -> CollaborationState:
    """
    分析师智能体 - 负责数据分析
    """
    print("📊 分析师智能体正在分析数据...")
    
    research_result = state["research_result"]
    
    # 模拟分析过程
    analysis_result = f"基于研究结果的分析：\n"
    analysis_result += "• 信息可信度：高\n"
    analysis_result += "• 相关性：强\n"
    analysis_result += "• 建议：值得深入探讨\n"
    
    return {
        "analysis_result": analysis_result,
        "messages": [AIMessage(content=f"分析完成：{analysis_result}")]
    }

def coordinator_agent(state: CollaborationState) -> CollaborationState:
    """
    协调员智能体 - 整合所有结果
    """
    print("🎯 协调员智能体正在整合结果...")
    
    research_result = state["research_result"]
    analysis_result = state["analysis_result"]
    user_input = state["user_input"]
    
    # 整合所有信息
    final_response = f"关于 '{user_input}' 的综合报告：\n\n"
    final_response += "📋 研究结果：\n" + research_result + "\n"
    final_response += "📈 分析结论：\n" + analysis_result + "\n"
    final_response += "💡 总结：这是一个经过深入研究的话题，具有很高的讨论价值。"
    
    return {
        "final_response": final_response,
        "messages": [AIMessage(content=final_response)]
    }

def create_collaboration_workflow():
    """创建协作工作流"""
    print("\n" + "="*60)
    print("🤝 第四部分：多智能体协作工作流")
    print("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(CollaborationState)
    
    # 2. 添加节点
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("coordinator", coordinator_agent)
    
    # 3. 设置入口点
    workflow.set_entry_point("researcher")
    
    # 4. 添加边（顺序执行）
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "coordinator")
    workflow.add_edge("coordinator", END)
    
    # 5. 编译工作流
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

async def run_examples():
    """运行所有 LangGraph 示例"""
    
    print("🎓 LangGraph 智能体学习示例")
    print("本示例将展示 LangGraph 的核心概念和用法")
    
    # 测试输入
    test_inputs = [
        "你好，我想了解一下 LangGraph",
        "请帮我计算 15 + 25",
        "我想搜索关于人工智能的信息", 
        "让我们聊聊天吧",
        "查询北京的天气",
        "请分析一下机器学习的发展趋势"
    ]
    
    # 1. 基础工作流
    basic_graph = create_basic_workflow()
    print(f"\n📝 测试基础工作流：")
    result = basic_graph.invoke({"user_input": test_inputs[0]})
    print(f"输入：{test_inputs[0]}")
    print(f"输出：{result['response']}")
    
    # 2. 决策工作流
    decision_graph = create_decision_workflow()
    print(f"\n📝 测试决策工作流：")
    for i, test_input in enumerate(test_inputs[1:4]):
        print(f"\n--- 测试 {i+1} ---")
        result = decision_graph.invoke({"user_input": test_input})
        print(f"输入：{test_input}")
        print(f"决策：{result['decision']}")
        print(f"输出：{result['response']}")
    
    # 3. 工具工作流
    tool_graph = create_tool_workflow()
    print(f"\n📝 测试工具工作流：")
    for test_input in test_inputs[4:5]:
        result = tool_graph.invoke({"user_input": test_input})
        print(f"输入：{test_input}")
        print(f"输出：{result['tool_results']}")
    
    # 4. 协作工作流
    collaboration_graph = create_collaboration_workflow()
    print(f"\n📝 测试协作工作流：")
    result = collaboration_graph.invoke({"user_input": test_inputs[5]})
    print(f"输入：{test_inputs[5]}")
    print(f"输出：{result['final_response']}")
    
    print("\n" + "="*60)
    print("🎉 所有示例运行完成！")
    print("="*60)

def interactive_demo():
    """交互式演示"""
    print("\n🎮 交互式演示模式")
    print("您可以输入任何问题，智能体会为您处理")
    print("输入 'quit' 退出")
    
    # 选择工作流
    print("\n请选择工作流类型：")
    print("1. 基础智能体")
    print("2. 决策智能体") 
    print("3. 工具智能体")
    print("4. 协作智能体")
    
    choice = input("请输入选择 (1-4): ").strip()
    
    workflows = {
        "1": create_basic_workflow(),
        "2": create_decision_workflow(),
        "3": create_tool_workflow(),
        "4": create_collaboration_workflow()
    }
    
    if choice not in workflows:
        print("无效选择，使用基础智能体")
        choice = "1"
    
    graph = workflows[choice]
    
    while True:
        user_input = input("\n您: ").strip()
        if user_input.lower() == 'quit':
            break
            
        try:
            result = graph.invoke({"user_input": user_input})
            
            # 根据工作流类型显示结果
            if choice == "1":
                print(f"智能体: {result['response']}")
            elif choice == "2":
                print(f"智能体: {result['response']}")
            elif choice == "3":
                print(f"智能体: {result['tool_results']}")
            elif choice == "4":
                print(f"智能体: {result['final_response']}")
                
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    # 运行示例
    asyncio.run(run_examples())
    
    # 交互式演示
    interactive_demo()
