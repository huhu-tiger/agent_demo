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
from langgraph.prebuilt import create_react_agent
# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# LangChain 组件
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import config

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger

# 初始化语言模型
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,  # 低温度确保回答的一致性
    max_tokens=1000   # 限制输出长度
)



# 创建 function call 代理
def create_function_call_agent():
    """创建使用 function call 的代理"""
    
    # 定义系统提示
    system_prompt = """你是一个智能助手，可以根据用户的需求选择合适的工具来帮助用户。

可用工具：
- get_weather: 查询指定城市的天气信息
- calculate_math: 计算数学表达式
- search_web: 搜索网络信息
- translate_text: 翻译文本
- ask_llm: 使用大语言模型回答问题
- analyze_text: 分析文本（情感、摘要、关键词等）
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

def get_standard_ai_response(user_question: str) -> str:
    """
    获取标准AI回答
    
    Args:
        user_question: 用户问题
        
    Returns:
        标准回答字符串
    """
    # 使用大模型判断是否是模型相关问题
    try:
        # 构建判断提示
        prompt = f"""
请判断以下问题是否是询问AI模型身份、能力或个人信息的问题。
如果是，请回答"MODEL_QUESTION"；如果不是，请回答"NOT_MODEL_QUESTION"。

问题：{user_question}

回答：
"""
        
        # 调用大模型进行判断
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        
        # 检查回答
        if "MODEL_QUESTION" in response.content:
            return f"您好，我是default的AI模型，是Cursor IDE内置的AI助手，致力于提升您的开发效率。你问的是：{user_question}"
        
        return ""
        
    except Exception as e:
        logger.error(f"模型判断失败: {e}")
        # 如果模型调用失败，使用简单的关键词匹配作为备用
        model_related_keywords = ["模型", "ai", "智能", "是什么", "谁", "你是什么", "你叫什么", "你是谁"]
        
        for keyword in model_related_keywords:
            if keyword.lower() in user_question.lower():
                return f"您好，我是default的AI模型，是Cursor IDE内置的AI助手，致力于提升您的开发效率。你问的是：{user_question}"
        
        return ""

# ============================================================================
# 工具定义
# ============================================================================
# 工具是 LangGraph 中扩展功能的核心组件
# 每个工具都是一个独立的函数，可以执行特定的任务
# 使用 @tool 装饰器将函数注册为 LangGraph 工具
# 工具可以被工作流中的节点调用，实现复杂的功能

@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息字符串
    """
    # 步骤1: 记录工具调用开始
    logger.info(f"🌤️ 调用天气工具，查询城市: {city}")
    
    # 步骤2: 定义模拟天气数据库
    # 在实际应用中，这里会调用真实的天气API
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
    
    # 步骤3: 查询天气数据
    if city in weather_data:
        # 步骤3.1: 获取城市天气数据
        data = weather_data[city]
        # 步骤3.2: 格式化天气信息
        result = f"{city}天气: {data['condition']}, 温度{data['temperature']}, 湿度{data['humidity']}, {data['wind']}"
    else:
        # 步骤3.3: 处理城市不存在的情况
        result = f"抱歉，没有找到 {city} 的天气信息"
    
    # 步骤4: 记录工具调用结果并返回
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
    # 步骤1: 记录工具调用开始
    logger.info(f"🧮 调用数学计算工具，表达式: {expression}")
    
    try:
        # 步骤2: 执行数学计算
        # 注意：在实际应用中，应该使用更安全的计算方法，如 ast.literal_eval
        result = eval(expression)
        # 步骤3: 格式化计算结果
        response = f"计算结果: {expression} = {result}"
    except Exception as e:
        # 步骤4: 处理计算错误
        response = f"计算错误: {str(e)}"
    
    # 步骤5: 记录工具调用结果并返回
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
    # 步骤1: 记录工具调用开始
    logger.info(f"🔍 调用网络搜索工具，查询: {query}")
    
    # 步骤2: 定义模拟搜索数据库
    # 在实际应用中，这里会调用真实的搜索引擎API
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
    
    # 步骤3: 执行搜索匹配
    results = []
    for key, value in search_results.items():
        # 步骤3.1: 检查查询是否包含关键词
        if key.lower() in query.lower():
            # 步骤3.2: 添加匹配的结果
            results.extend(value)
    
    # 步骤4: 格式化搜索结果
    if results:
        # 步骤4.1: 限制结果数量并格式化
        response = f"搜索结果:\n" + "\n".join([f"- {result}" for result in results[:3]])
    else:
        # 步骤4.2: 处理无搜索结果的情况
        response = f"没有找到关于 '{query}' 的相关信息"
    
    # 步骤5: 记录工具调用结果并返回
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
    # 步骤1: 记录工具调用开始
    logger.info(f"🌐 调用翻译工具，文本: {text}, 目标语言: {target_language}")
    
    # 步骤2: 定义翻译词典
    # 在实际应用中，这里会调用真实的翻译API
    translations = {
        "hello": "你好",
        "你好": "hello",
        "world": "世界",
        "世界": "world",
        "python": "Python编程语言",
        "ai": "人工智能",
        "人工智能": "artificial intelligence"
    }
    
    # 步骤3: 执行翻译
    text_lower = text.lower()
    if text_lower in translations:
        # 步骤3.1: 找到翻译并格式化结果
        result = f"翻译结果: {text} → {translations[text_lower]}"
    else:
        # 步骤3.2: 处理无法翻译的情况
        result = f"抱歉，无法翻译 '{text}' 到 {target_language}"
    
    # 步骤4: 记录工具调用结果并返回
    logger.info(f"翻译工具返回: {result}")
    return result

@tool
def ask_llm(question: str, context: str = "") -> str:
    """
    向大语言模型提问
    
    Args:
        question: 问题内容
        context: 上下文信息（可选）
        
    Returns:
        模型回答字符串
    """
    # 步骤1: 记录工具调用开始
    logger.info(f"🤖 调用大语言模型，问题: {question}")
    
    try:
        # 步骤2: 构建消息列表
        messages = []
        
        # 步骤2.1: 添加系统消息（如果有上下文）
        if context:
            messages.append(SystemMessage(content=f"上下文信息: {context}"))
        
        # 步骤2.2: 添加用户问题
        messages.append(HumanMessage(content=question))
        
        # 步骤3: 调用语言模型
        response = llm.invoke(messages)
        
        # 步骤4: 提取回答内容
        result = response.content
        
        # 步骤5: 记录工具调用结果并返回
        logger.info(f"大语言模型回答: {result}")
        return result
        
    except Exception as e:
        # 步骤6: 处理调用错误
        error_msg = f"调用大语言模型失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def analyze_text(text: str, analysis_type: str = "general") -> str:
    """
    文本分析工具
    
    Args:
        text: 要分析的文本
        analysis_type: 分析类型（general, sentiment, summary, keywords）
        
    Returns:
        分析结果字符串
    """
    # 步骤1: 记录工具调用开始
    logger.info(f"📊 调用文本分析工具，文本: {text[:50]}..., 分析类型: {analysis_type}")
    
    try:
        # 步骤2: 根据分析类型构建提示
        if analysis_type == "sentiment":
            prompt = f"请分析以下文本的情感倾向（积极、消极或中性）：\n{text}"
        elif analysis_type == "summary":
            prompt = f"请为以下文本生成一个简洁的摘要：\n{text}"
        elif analysis_type == "keywords":
            prompt = f"请从以下文本中提取关键词：\n{text}"
        else:
            prompt = f"请对以下文本进行一般性分析：\n{text}"
        
        # 步骤3: 调用语言模型进行分析
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages)
        
        # 步骤4: 格式化分析结果
        result = f"文本分析结果（{analysis_type}）:\n{response.content}"
        
        # 步骤5: 记录工具调用结果并返回
        logger.info(f"文本分析结果: {result}")
        return result
        
    except Exception as e:
        # 步骤6: 处理分析错误
        error_msg = f"文本分析失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def get_model_info(query: str = "") -> str:
    """
    获取模型信息工具
    
    Args:
        query: 查询内容（可选，用于兼容工具接口）
        
    Returns:
        模型信息字符串
    """
    # 步骤1: 记录工具调用开始
    logger.info(f"🤖 调用模型信息工具，查询: {query}")
    
    # 步骤2: 返回标准回答
    model_info = f"您好，我是default的AI模型，是Cursor IDE内置的AI助手，致力于提升您的开发效率。你问的是：{query}"
    
    # 步骤3: 记录工具调用结果并返回
    logger.info(f"模型信息返回: {model_info}")
    return model_info



# 创建工具列表
tools = [
    get_weather,
    calculate_math,
    search_web,
    translate_text,
    ask_llm,
    analyze_text,
    get_model_info
]

# ============================================================================
# 工具状态定义
# ============================================================================
# 状态是 LangGraph 工作流中节点间传递数据的容器
# ToolState 定义了工具集成工作流所需的所有数据字段
# 每个字段都有特定的用途，支持工作流的完整执行流程

class ToolState(TypedDict):
    """
    工具状态 - 包含工具调用结果和处理信息
    
    状态字段说明:
    - messages: 消息历史，包含用户输入和AI响应
    - user_input: 用户原始输入
    - tool_results: 工具执行结果列表
    - selected_tools: 选择的工具名称列表
    - final_response: 最终合成的响应
    - agent_result: function call 代理的执行结果
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
    # 代理结果：存储 function call 代理的执行结果
    agent_result: str

# ============================================================================
# 工具智能体节点
# ============================================================================
# 节点是工作流中的处理单元，每个节点执行特定的任务
# 工具集成工作流包含三个主要节点：
# 1. tool_selector: 分析用户需求，选择合适的工具
# 2. tool_executor: 执行选定的工具，获取结果
# 3. response_synthesizer: 整合工具结果，生成最终响应

def tool_selector(state: ToolState) -> ToolState:
    """
    工具选择节点 - 使用 function call 方式选择工具
    学习要点：智能工具选择逻辑
    """
    # 步骤1: 记录节点开始工作
    logger.info("🔧 工具选择节点正在分析...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    # 步骤2: 获取用户输入
    user_input = state["user_input"]
    
    # 步骤3: 使用 function call 代理进行工具选择
    try:
        # 步骤3.1: 创建代理
        agent = create_function_call_agent()
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
        
        # 步骤3.2: 调用代理获取工具选择结果
        logger.info(f"用户输入: {user_input}")
        
        # 步骤3.3: 执行代理调用
        result = agent_executor.invoke({"input": user_input})
        
        # 步骤3.4: 记录结果
        logger.info(f"代理执行结果: {result}")
        
        # 步骤3.5: 返回状态更新
        return {
            "selected_tools": ["function_call_agent"],  # 标记使用了 function call
            "agent_result": result.get("output", ""),
            "messages": [AIMessage(content=result.get("output", "处理完成"))]
        }
        
    except Exception as e:
        logger.error(f"Function call 代理执行失败: {e}")
        # 步骤3.6: 如果执行失败，使用备用方案
        logger.info("使用备用工具选择方案")
        
        # 使用简单的关键词匹配作为备用
        selected_tools = []
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["天气", "温度", "下雨", "晴天"]):
            selected_tools.append("get_weather")
        elif any(word in user_input_lower for word in ["计算", "数学", "+", "-", "*", "/"]):
            selected_tools.append("calculate_math")
        elif any(word in user_input_lower for word in ["搜索", "查找", "信息", "资料"]):
            selected_tools.append("search_web")
        elif any(word in user_input_lower for word in ["翻译", "英文", "中文", "language"]):
            selected_tools.append("translate_text")
        elif any(word in user_input_lower for word in ["模型", "ai", "智能", "是什么", "谁", "你是什么", "你叫什么"]):
            selected_tools.append("get_model_info")
        elif any(word in user_input_lower for word in ["分析", "情感", "摘要", "关键词", "总结"]):
            selected_tools.append("analyze_text")
        else:
            selected_tools.append("ask_llm")
        
        return {
            "selected_tools": selected_tools,
            "agent_result": f"使用备用方案选择了工具: {', '.join(selected_tools)}",
            "messages": [AIMessage(content=f"已选择工具: {', '.join(selected_tools)}")]
        }

def tool_executor(state: ToolState) -> ToolState:
    """
    工具执行节点 - 使用 function call 方式执行工具
    学习要点：智能工具调用和结果处理
    """
    # 步骤1: 记录节点开始工作
    logger.info("⚙️ 工具执行节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    # 步骤2: 获取状态信息
    user_input = state["user_input"]
    selected_tools = state["selected_tools"]
    agent_result = state.get("agent_result", "")
    
    # 步骤3: 检查是否使用了 function call 代理
    if "function_call_agent" in selected_tools:
        # 步骤3.1: 如果使用了 function call，直接返回代理结果
        logger.info("使用 function call 代理结果")
        tool_results = [agent_result]
    else:
        # 步骤3.2: 如果没有使用 function call，使用传统方式执行工具
        logger.info("使用传统工具执行方式")
        tool_results = []
        
        for tool_name in selected_tools:
            try:
                # 执行各种工具（保持原有逻辑作为备用）
                if tool_name == "get_weather":
                    cities = ["北京", "上海", "广州", "深圳"]
                    for city in cities:
                        if city in user_input:
                            result = get_weather(city)
                            tool_results.append(f"天气查询: {result}")
                            break
                    else:
                        tool_results.append("天气查询: 请指定城市名称")
                
                elif tool_name == "calculate_math":
                    import re
                    expression = re.findall(r'[\d\+\-\*\/\(\)]+', user_input)
                    if expression:
                        result = calculate_math(expression[0])
                        tool_results.append(result)
                    else:
                        tool_results.append("数学计算: 请提供数学表达式")
                
                elif tool_name == "search_web":
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
                    if "hello" in user_input.lower():
                        result = translate_text("hello")
                    elif "你好" in user_input:
                        result = translate_text("你好")
                    else:
                        result = translate_text(user_input)
                    tool_results.append(result)
                
                elif tool_name == "get_model_info":
                    result = get_model_info(user_input)
                    tool_results.append(result)
                
                elif tool_name == "ask_llm":
                    result = ask_llm(user_input, "")
                    tool_results.append(result)
                
                elif tool_name == "analyze_text":
                    analysis_type = "general"
                    if any(word in user_input for word in ["情感", "情绪"]):
                        analysis_type = "sentiment"
                    elif any(word in user_input for word in ["摘要", "总结"]):
                        analysis_type = "summary"
                    elif any(word in user_input for word in ["关键词", "关键"]):
                        analysis_type = "keywords"
                    
                    text_to_analyze = user_input
                    result = analyze_text(text_to_analyze, analysis_type)
                    tool_results.append(result)
                    
            except Exception as e:
                tool_results.append(f"工具 {tool_name} 执行错误: {str(e)}")
    
    # 步骤4: 处理无工具结果的情况
    if not tool_results:
        tool_results.append("没有找到合适的工具来处理您的请求")
    
    # 步骤5: 记录执行结果
    logger.info(f"工具执行结果: {tool_results}")
    
    # 步骤6: 返回状态更新
    return {
        "tool_results": tool_results,
        "messages": [AIMessage(content="工具执行完成")]
    }

def response_synthesizer(state: ToolState) -> ToolState:
    """
    响应合成节点 - 整合工具结果生成最终响应
    学习要点：结果整合和响应生成
    """
    # 步骤1: 记录节点开始工作
    logger.info("🎯 响应合成节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    # 步骤2: 获取状态信息
    user_input = state["user_input"]
    tool_results = state["tool_results"]
    selected_tools = state["selected_tools"]
    agent_result = state.get("agent_result", "")
    
    # 步骤3: 合成最终响应
    if "function_call_agent" in selected_tools:
        # 步骤3.1: 如果使用了 function call，直接使用代理结果
        final_response = agent_result
        logger.info("使用 function call 代理结果作为最终响应")
    elif tool_results:
        # 步骤3.2: 使用传统工具结果
        final_response = f"根据您的需求 '{user_input}'，我为您提供了以下信息：\n\n"
        
        for i, result in enumerate(tool_results, 1):
            final_response += f"{i}. {result}\n"
        
        final_response += f"\n使用了 {len(selected_tools)} 个工具: {', '.join(selected_tools)}"
    else:
        # 步骤3.3: 处理无结果的情况
        final_response = f"抱歉，我无法处理您的请求 '{user_input}'。请尝试更具体的描述。"
    
    # 步骤4: 记录最终响应
    logger.info(f"最终响应: {final_response}")
    
    # 步骤5: 返回状态更新
    return {
        "final_response": final_response,
        "messages": [AIMessage(content=final_response)]
    }

# ============================================================================
# 工作流构建
# ============================================================================
# 工作流是 LangGraph 的核心概念，定义了节点间的执行顺序
# 通过 StateGraph 创建工作流，添加节点和边，最后编译为可执行图
# 工具集成工作流采用线性流程：工具选择 → 工具执行 → 响应合成

def create_tool_workflow():
    """
    创建工具集成工作流
    学习要点：工具节点的集成
    """
    # 步骤1: 记录工作流创建开始
    logger.info("\n" + "="*60)
    logger.info("🛠️ 工具集成工作流")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 步骤2: 创建状态图
    # 使用 ToolState 作为工作流的状态类型
    workflow = StateGraph(ToolState)

    # 步骤3: 添加工作流节点
    # 步骤3.1: 添加工具选择节点
    workflow.add_node("tool_selector", tool_selector)
    # 步骤3.2: 添加工具执行节点
    workflow.add_node("tool_executor", tool_executor)
    # 步骤3.3: 添加响应合成节点
    workflow.add_node("response_synthesizer", response_synthesizer)
    
    # 步骤4: 设置工作流入口点
    # 工作流从工具选择节点开始
    workflow.set_entry_point("tool_selector")
    
    # 步骤5: 添加节点间的连接边
    # 步骤5.1: 工具选择 → 工具执行
    workflow.add_edge("tool_selector", "tool_executor")
    # 步骤5.2: 工具执行 → 响应合成
    workflow.add_edge("tool_executor", "response_synthesizer")
    # 步骤5.3: 响应合成 → 结束
    workflow.add_edge("response_synthesizer", END)
    
    # 步骤6: 编译工作流
    # 将工作流定义编译为可执行图
    graph = workflow.compile()
    
    # 步骤7: 返回编译后的工作流
    return graph

# ============================================================================
# 测试函数
# ============================================================================
# 测试函数用于验证工作流的正确性和功能完整性
# 通过不同的测试用例，验证各种工具的执行效果
# 测试结果包含工具选择、执行结果和最终响应等信息

def test_tools_integration():
    """测试工具集成"""
    # 步骤1: 记录测试开始
    logger.info("🛠️ 测试 LangGraph 工具集成")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 步骤2: 创建工作流
    # 调用工作流创建函数，获取编译后的图
    graph = create_tool_workflow()
        # todo 可视化 
    from show_graph import show_workflow_graph
    show_workflow_graph(graph, "工具集成工作流",logger)
    # 步骤3: 定义测试用例
    # 包含不同类型的用户输入，测试各种工具功能
    test_inputs = [
        "查询北京的天气怎么样",      # 测试天气工具
        "请帮我计算 15 * 3 + 10",   # 测试数学计算工具
        "搜索关于人工智能的信息",    # 测试搜索工具
        "翻译 hello 这个单词",      # 测试翻译工具
        "我想了解 LangGraph 框架",  # 测试搜索工具
        "你是什么模型？",           # 测试模型信息工具
        "请解释什么是机器学习",      # 测试大语言模型工具
        "分析这段文本的情感：我很开心今天天气很好", # 测试文本分析工具
        "请总结一下人工智能的发展历程"  # 测试文本分析工具
    ]
    
    # 步骤4: 执行测试用例
    for i, test_input in enumerate(test_inputs, 1):
        # 步骤4.1: 记录当前测试
        logger.info(f"\n--- 测试 {i} ---")
        logger.info(f"输入: {test_input}")
        
        try:
            # 步骤4.2: 调用工作流
            # 传入用户输入，执行完整的工作流
            result = graph.invoke({"user_input": test_input})
            logger.info(f"最终响应: {result}")
            # # 步骤4.3: 记录测试结果
            # logger.info(f"选择的工具: {result['selected_tools']}")
            # logger.info(f"工具结果: {result['tool_results']}")
            # logger.info(f"最终响应: {result['final_response']}")
            
        except Exception as e:
            # 步骤4.4: 处理测试错误
            logger.error(f"错误: {e}")

if __name__ == "__main__":
    test_tools_integration() 