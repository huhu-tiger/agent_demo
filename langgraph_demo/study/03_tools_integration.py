# -*- coding: utf-8 -*-
"""
LangGraph 工具集成示例 - 基于 Context7 文档的最佳实践
学习要点：工具定义、工具调用、状态扩展

作者: AI Assistant
来源: LangGraph 官方文档学习

核心概念说明：
1. 工具（Tools）：封装了可调用函数和输入模式，让模型能够智能决定何时调用工具
2. 工作流（Workflow）：定义了节点间的执行顺序，通过 StateGraph 构建
3. 状态（State）：节点间传递数据的容器，使用 TypedDict 定义
4. 路由（Routing）：根据条件决定工作流的执行路径

架构设计：
用户输入 → 模型调用 → 条件路由 → 工具执行 → 返回模型 → 最终响应
"""

import os
import json
import requests
from typing import TypedDict, List
from typing_extensions import Annotated

# ============================================================================
# LangGraph 核心组件导入
# ============================================================================
# StateGraph: 用于构建状态图工作流
# START/END: 工作流的开始和结束节点
# add_messages: 自动合并消息的注解
# ToolNode: 专门用于执行工具的节点
# create_react_agent: 创建 ReAct 智能体的预构建函数
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, create_react_agent

# ============================================================================
# LangChain 组件导入
# ============================================================================
# HumanMessage/AIMessage/SystemMessage: 不同类型的消息
# tool: 装饰器，用于将函数注册为工具
# ChatOpenAI: OpenAI 聊天模型
# ChatPromptTemplate: 聊天提示模板
# MessagesPlaceholder: 消息占位符
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import config

# ============================================================================
# 环境配置和模型初始化
# ============================================================================
# 设置 OpenAI API 配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger

# 初始化语言模型
# temperature=0.1: 低温度确保回答的一致性
# max_tokens=1000: 限制输出长度，避免过长响应
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,
    max_tokens=1000
)

# ============================================================================
# 工具定义 - 基于 Context7 文档的最佳实践
# ============================================================================
# 工具是 LangGraph 中扩展功能的核心组件
# 每个工具都是一个独立的函数，使用 @tool 装饰器注册
# 工具可以被工作流中的节点调用，实现复杂的功能

@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息
    
    功能说明：
    - 模拟天气查询服务
    - 支持北京、上海、广州、深圳四个城市
    - 返回温度、天气状况、湿度、风力等详细信息
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息字符串，格式：城市天气: 状况, 温度, 湿度, 风力
    """
    logger.info(f"🌤️ 调用天气工具，查询城市: {city}")
    
    # 模拟天气数据库 - 在实际应用中会调用真实的天气API
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
    
    # 查询天气数据并格式化返回
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
    
    功能说明：
    - 支持基本的数学运算：加减乘除、括号
    - 使用 eval() 函数执行计算（注意：生产环境应使用更安全的方法）
    - 包含错误处理机制
    
    Args:
        expression: 数学表达式，如 "2 + 3 * 4"
        
    Returns:
        计算结果字符串，格式：计算结果: 表达式 = 结果
    """
    logger.info(f"🧮 调用数学计算工具，表达式: {expression}")
    
    try:
        # 执行数学计算
        # 注意：在实际应用中，应该使用更安全的计算方法，如 ast.literal_eval
        result = eval(expression)
        response = f"计算结果: {expression} = {result}"
    except Exception as e:
        # 处理计算错误
        response = f"计算错误: {str(e)}"
    
    logger.info(f"数学工具返回: {response}")
    return response

@tool
def search_web(query: str) -> str:
    """
    网络搜索工具
    
    功能说明：
    - 模拟网络搜索功能
    - 支持关键词匹配搜索
    - 返回格式化的搜索结果
    
    Args:
        query: 搜索查询
        
    Returns:
        搜索结果字符串，包含匹配的相关信息
    """
    logger.info(f"🔍 调用网络搜索工具，查询: {query}")
    
    # 模拟搜索数据库 - 在实际应用中会调用真实的搜索引擎API
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
    
    # 执行搜索匹配
    results = []
    for key, value in search_results.items():
        if key.lower() in query.lower():
            results.extend(value)
    
    # 格式化搜索结果
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
    
    功能说明：
    - 支持中英文互译
    - 使用预定义的翻译词典
    - 可扩展支持更多语言
    
    Args:
        text: 要翻译的文本
        target_language: 目标语言（默认为中文）
        
    Returns:
        翻译结果字符串，格式：翻译结果: 原文 → 译文
    """
    logger.info(f"🌐 调用翻译工具，文本: {text}, 目标语言: {target_language}")
    
    # 翻译词典 - 在实际应用中会调用真实的翻译API
    translations = {
        "hello": "你好",
        "你好": "hello",
        "world": "世界",
        "世界": "world",
        "python": "Python编程语言",
        "ai": "人工智能",
        "人工智能": "artificial intelligence"
    }
    
    # 执行翻译
    text_lower = text.lower()
    if text_lower in translations:
        result = f"翻译结果: {text} → {translations[text_lower]}"
    else:
        result = f"抱歉，无法翻译 '{text}' 到 {target_language}"
    
    logger.info(f"翻译工具返回: {result}")
    return result

@tool
def ask_llm(question: str, context: str = "") -> str:
    """
    向大语言模型提问
    
    功能说明：
    - 使用配置的语言模型回答问题
    - 支持上下文信息
    - 包含错误处理机制
    
    Args:
        question: 问题内容
        context: 上下文信息（可选）
        
    Returns:
        模型回答字符串
    """
    logger.info(f"🤖 调用大语言模型，问题: {question}")
    
    try:
        # 构建消息列表
        messages = []
        
        # 添加系统消息（如果有上下文）
        if context:
            messages.append(SystemMessage(content=f"上下文信息: {context}"))
        
        # 添加用户问题
        messages.append(HumanMessage(content=question))
        
        # 调用语言模型
        response = llm.invoke(messages)
        result = response.content
        
        logger.info(f"大语言模型回答: {result}")
        return result
        
    except Exception as e:
        # 处理调用错误
        error_msg = f"调用大语言模型失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def analyze_text(text: str, analysis_type: str = "general") -> str:
    """
    文本分析工具
    
    功能说明：
    - 支持多种分析类型：情感分析、摘要生成、关键词提取
    - 使用语言模型进行分析
    - 可扩展支持更多分析功能
    
    Args:
        text: 要分析的文本
        analysis_type: 分析类型（general, sentiment, summary, keywords）
        
    Returns:
        分析结果字符串
    """
    logger.info(f"📊 调用文本分析工具，文本: {text[:50]}..., 分析类型: {analysis_type}")
    
    try:
        # 根据分析类型构建提示
        if analysis_type == "sentiment":
            prompt = f"请分析以下文本的情感倾向（积极、消极或中性）：\n{text}"
        elif analysis_type == "summary":
            prompt = f"请为以下文本生成一个简洁的摘要：\n{text}"
        elif analysis_type == "keywords":
            prompt = f"请从以下文本中提取关键词：\n{text}"
        else:
            prompt = f"请对以下文本进行一般性分析：\n{text}"
        
        # 调用语言模型进行分析
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        
        # 格式化分析结果
        result = f"文本分析结果（{analysis_type}）:\n{response.content}"
        
        logger.info(f"文本分析结果: {result}")
        return result
        
    except Exception as e:
        # 处理分析错误
        error_msg = f"文本分析失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

# 创建工具列表 - 将所有工具组织在一起供工作流使用
tools = [
    get_weather,
    calculate_math,
    search_web,
    translate_text,
    ask_llm,
    analyze_text
]

# ============================================================================
# 状态定义
# ============================================================================
# 状态是 LangGraph 工作流中节点间传递数据的容器
# 使用 TypedDict 定义状态结构，确保类型安全

class ToolState(TypedDict):
    """
    工具状态 - 包含工具调用结果和处理信息
    
    状态字段说明:
    - messages: 消息历史，使用 add_messages 注解自动合并消息
    - user_input: 用户原始输入
    - tool_results: 工具执行结果列表
    - selected_tools: 选择的工具名称列表
    - final_response: 最终合成的响应
    """
    # 消息历史：使用 add_messages 注解自动合并消息
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    # 用户输入：原始的用户请求
    user_input: str
    # 工具结果：存储各个工具的执行结果
    tool_results: List[str]
    # 选择工具：存储工具选择节点选择的工具列表
    selected_tools: List[str]
    # 最终响应：存储响应合成节点生成的最终回答
    final_response: str

# ============================================================================
# 工作流节点 - 基于 Context7 文档的最佳实践
# ============================================================================
# 节点是工作流中的处理单元，每个节点执行特定的任务
# 基于 Context7 文档，使用标准的 ReAct 模式

def route_tools(state: ToolState):
    """
    路由函数 - 根据消息内容决定是否需要调用工具
    
    功能说明：
    - 检查最后一条消息是否包含工具调用
    - 如果有工具调用，路由到工具执行节点
    - 如果没有工具调用，结束工作流
    - 使用条件路由控制工作流执行
    - 支持动态工具调用决策
    """
    # 获取消息列表
    messages = state.get("messages", [])
    if not messages:
        return END
    
    # 检查最后一条消息
    last_message = messages[-1]
    
    # 如果最后一条消息包含工具调用，则路由到工具节点
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"
    
    # 否则结束工作流
    return END

def call_model(state: ToolState) -> ToolState:
    """
    调用模型节点 - 使用 create_react_agent 和自定义提示词
    
    功能说明：
    - 使用 LangGraph 的 create_react_agent 创建智能体
    - 添加自定义提示词来优化工具选择逻辑
    - 将用户输入传递给智能体
    - 返回智能体的响应消息
    - 确保只调用相关的工具
    """
    logger.info("🧠 调用模型节点正在工作...")
    
    # 获取用户输入
    user_input = state["user_input"]
    
    # 记录用户输入
    logger.info(f"📝 用户输入: {user_input}")
    
    # 创建自定义系统提示词，优化工具选择逻辑
    custom_prompt = """你是一个智能助手，可以根据用户的需求选择合适的工具来帮助用户。

重要原则：
1. 仔细分析用户的问题，理解其真实意图
2. 只选择最相关、最合适的工具
3. 避免调用不相关的工具
4. 优先选择专门针对用户需求的工具

工具选择策略：

get_weather 工具：
- 用途：查询天气信息
- 适用场景：用户询问天气、温度、气候、天气状况等
- 关键词：天气、温度、下雨、晴天、气候、天气预报等

calculate_math 工具：
- 用途：进行数学计算
- 适用场景：用户需要进行数字运算、数学计算、公式计算等
- 关键词：计算、数学、数字、运算、公式、加减乘除等

search_web 工具：
- 用途：搜索和查找信息
- 适用场景：用户想要了解、搜索、查找、获取信息等
- 关键词：了解、搜索、查找、信息、资料、介绍、什么是等

translate_text 工具：
- 用途：翻译文本内容
- 适用场景：用户明确要求翻译文本、单词、短语等
- 关键词：翻译、英文、中文、语言转换等

ask_llm 工具：
- 用途：深度思考和复杂问题解答
- 适用场景：用户询问需要深度思考、解释、分析的问题
- 关键词：解释、什么是、为什么、如何、分析、思考等

analyze_text 工具：
- 用途：文本分析（情感、摘要、关键词等）
- 适用场景：用户要求分析文本内容、情感、摘要、关键词等
- 关键词：分析、情感、摘要、关键词、总结、文本分析等

可用工具：
- get_weather: 查询指定城市的天气信息
- calculate_math: 计算数学表达式
- search_web: 搜索网络信息
- translate_text: 翻译文本
- ask_llm: 使用大语言模型回答问题
- analyze_text: 分析文本（情感、摘要、关键词等）

决策流程：
1. 仔细阅读用户的问题
2. 识别问题的核心意图和关键词
3. 根据工具用途和适用场景进行匹配
4. 选择最合适的工具
5. 避免调用不相关的工具

请根据用户问题的实际内容和意图，选择最合适的工具来帮助用户。"""
    
    # 使用自定义提示词创建智能体
    agent = create_react_agent(llm, tools, prompt=custom_prompt)
    
    # 记录发送给模型的消息
    user_message = HumanMessage(content=user_input)
    logger.info(f"📤 发送给模型的消息: {user_message.content}")
    
    # 调用代理，传入用户消息
    result = agent.invoke({"messages": [user_message]})
    
    # 记录模型返回的消息
    logger.info(f"📥 模型返回的消息数量: {len(result['messages'])}")
    
    for i, msg in enumerate(result['messages']):
        if hasattr(msg, 'content') and msg.content:
            logger.info(f"📥 模型消息 {i+1} 内容: {msg.content}")
        
        # 记录工具调用信息
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            logger.info(f"🔧 模型消息 {i+1} 包含 {len(msg.tool_calls)} 个工具调用:")
            for j, tool_call in enumerate(msg.tool_calls):
                logger.info(f"  🔧 工具调用 {j+1}:")
                logger.info(f"    - 工具名称: {tool_call.get('name', '未知')}")
                logger.info(f"    - 工具参数: {tool_call.get('args', {})}")
                logger.info(f"    - 调用ID: {tool_call.get('id', '未知')}")
    
    logger.info(f"🧠 模型调用完成")
    
    # 返回消息列表
    return {
        "messages": result["messages"]
    }

def call_tools(state: ToolState) -> ToolState:
    """
    调用工具节点 - 使用 ToolNode
    
    功能说明：
    - 使用 LangGraph 的 ToolNode 执行工具调用
    - 处理 AI 消息中的工具调用请求
    - 返回工具执行结果
    - 使用专门的 ToolNode 进行工具执行
    - 支持并行工具调用
    - 自动错误处理
    """
    logger.info("🔧 调用工具节点正在工作...")
    
    # 使用 LangGraph 的 ToolNode 创建工具执行节点
    # ToolNode 会自动处理工具调用和结果返回
    tool_node = ToolNode(tools)
    
    # 获取最后一条消息（应该是包含工具调用的 AI 消息）
    messages = state.get("messages", [])
    if not messages:
        return {"messages": []}
    
    last_message = messages[-1]
    
    # 记录工具调用请求
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        logger.info(f"🔧 准备执行 {len(last_message.tool_calls)} 个工具调用:")
        for i, tool_call in enumerate(last_message.tool_calls):
            logger.info(f"  🔧 工具调用 {i+1}:")
            logger.info(f"    - 工具名称: {tool_call.get('name', '未知')}")
            logger.info(f"    - 工具参数: {tool_call.get('args', {})}")
            logger.info(f"    - 调用ID: {tool_call.get('id', '未知')}")
    
    # 调用工具节点执行工具调用
    result = tool_node.invoke({"messages": [last_message]})
    
    # 记录工具执行结果
    logger.info(f"🔧 工具执行完成，返回 {len(result['messages'])} 个结果消息:")
    for i, msg in enumerate(result['messages']):
        if hasattr(msg, 'content') and msg.content:
            logger.info(f"  📤 工具结果消息 {i+1}: {msg.content}")
        if hasattr(msg, 'name') and msg.name:
            logger.info(f"  📤 工具名称: {msg.name}")
        if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
            logger.info(f"  📤 工具调用ID: {msg.tool_call_id}")
    
    logger.info(f"🔧 工具调用节点完成")
    
    # 返回工具执行结果消息
    return {
        "messages": result["messages"]
    }

# ============================================================================
# 工作流构建 - 基于 Context7 文档的最佳实践
# ============================================================================
# 工作流是 LangGraph 的核心概念，定义了节点间的执行顺序
# 通过 StateGraph 创建工作流，添加节点和边，最后编译为可执行图

def create_tool_workflow():
    """
    工作流设计：
    1. 用户输入 → call_model（调用模型）
    2. call_model → route_tools（条件路由）
    3. route_tools → tools（工具执行）或 END（结束）
    4. tools → call_model（回到模型）
    
    这种设计实现了标准的 ReAct 模式：
    - Reasoning（推理）：模型分析用户输入
    - Acting（行动）：执行工具调用
    - 循环直到完成任务
    """
    logger.info("\n" + "="*60)
    logger.info("🛠️ 工具集成工作流 - 基于 Context7 最佳实践")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 步骤1: 创建状态图
    # 使用 ToolState 作为工作流的状态类型
    workflow = StateGraph(ToolState)

    # 步骤2: 添加工作流节点
    # 添加模型调用节点
    workflow.add_node("call_model", call_model)
    # 添加工具执行节点
    workflow.add_node("tools", call_tools)
    
    # 步骤3: 设置工作流入口点
    # 工作流从模型调用节点开始
    workflow.set_entry_point("call_model")
    
    # 步骤4: 添加条件边
    # 从模型调用节点到条件路由
    workflow.add_conditional_edges(
        "call_model",
        route_tools,  # 路由函数
        {
            "tools": "tools",  # 如果需要工具调用，路由到工具节点
            END: END           # 如果不需要工具调用，结束工作流
        }
    )
    
    # 步骤5: 添加工具执行后的边
    # 工具调用完成后回到模型节点，形成循环
    workflow.add_edge("tools", "call_model")
    
    # 步骤6: 编译工作流
    # 将工作流定义编译为可执行图
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 测试函数
# ============================================================================
# 测试函数用于验证工作流的正确性和功能完整性
# 通过不同的测试用例，验证各种工具的执行效果

def test_tools_integration():
    """
    测试工具集成 - 基于 Context7 文档的最佳实践
    
    测试策略：
    1. 创建完整的工作流
    2. 定义多样化的测试用例
    3. 执行测试并记录结果
    4. 验证工具调用的正确性
    """
    logger.info("🛠️ 测试 LangGraph 工具集成 - 基于 Context7 最佳实践")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 步骤1: 创建工作流
    # 调用工作流创建函数，获取编译后的图
    graph = create_tool_workflow()
    
    # 步骤2: 可视化工作流（可选）
    # 尝试导入可视化模块并显示工作流图
    try:
        from show_graph import show_workflow_graph
        show_workflow_graph(graph, "工具集成工作流", logger)
    except ImportError:
        logger.info("可视化模块未找到，跳过可视化")
    
    # 步骤3: 定义测试用例
    # 包含不同类型的用户输入，测试各种工具功能
    test_inputs = [
        "查询北京的天气怎么样",      # 测试天气工具
        "请帮我计算 15 * 3 + 10",   # 测试数学计算工具
        "搜索关于人工智能的信息",    # 测试搜索工具
        "翻译 hello 这个单词",      # 测试翻译工具
        "我想了解 LangGraph 框架",  # 测试搜索工具
        # "请解释什么是机器学习",      # 测试大语言模型工具
        "分析这段文本的情感：我很开心今天天气很好", # 测试文本分析工具
        "请总结一下人工智能的发展历程"  # 测试文本分析工具
    ]
    
    # 步骤4: 执行测试用例
    for i, test_input in enumerate(test_inputs, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 测试 {i}/{len(test_inputs)}")
        logger.info(f"{'='*80}")
        
        try:
            # 调用工作流
            # 传入用户输入，执行完整的工作流
            logger.info(f"🚀 开始执行工作流...")
            result = graph.invoke({"user_input": test_input})
            
            # 记录最终结果
            logger.info(f"✅ 工作流执行完成")
            logger.info(f"📊 最终结果统计:")
            logger.info(f"  - 消息数量: {len(result.get('messages', []))}")
            logger.info(f"  - 工具结果数量: {len(result.get('tool_results', []))}")
            logger.info(f"  - 选择工具数量: {len(result.get('selected_tools', []))}")
            
            # 显示最终响应
            if result.get('final_response'):
                logger.info(f"🎯 最终响应: {result['final_response']}")
            elif result.get('messages'):
                last_message = result['messages'][-1]
                if hasattr(last_message, 'content') and last_message.content:
                    logger.info(f"🎯 最终响应: {last_message.content}")
            
        except Exception as e:
            # 处理测试错误
            logger.error(f"❌ 测试 {i} 执行失败: {e}")
            import traceback
            logger.error(f"❌ 错误详情: {traceback.format_exc()}")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🎉 所有测试完成！")
    logger.info(f"{'='*80}")

# ============================================================================
# 主程序入口
# ============================================================================
if __name__ == "__main__":
    # 运行测试函数
    test_tools_integration() 