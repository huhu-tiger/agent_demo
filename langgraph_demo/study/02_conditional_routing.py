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
from langchain_openai import ChatOpenAI

import config

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger

# 初始化模型 - 支持自定义模型
def create_llm(model_name=None, temperature=0.1):
    """
    创建LLM实例，支持自定义模型
    """
    if model_name is None:
        model_name = MODEL_NAME
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        streaming=False
    )

# 默认模型实例
llm = create_llm()

# 自定义模型实例 - context7
context7_llm = create_llm("context7", temperature=0.1)

# ============================================================================
# 条件路由状态定义
# ============================================================================

class RoutingState(TypedDict):
    """条件路由状态 - 包含决策结果和路由信息"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]  # 消息历史，自动合并
    user_input: str  # 用户输入内容
    decision: str  # 决策结果（决定走哪个分支）
    route_reason: str  # 决策原因说明
    response: str  # 最终响应内容
    processing_path: List[str]  # 处理路径记录（用于追踪执行流程）

# ============================================================================
# 决策节点定义
# ============================================================================

def decision_maker(state: RoutingState) -> RoutingState:
    """
    决策制定节点 - 分析用户输入并决定处理路径
    作用：作为工作流的入口节点，分析用户意图并决定后续处理路径
    学习要点：智能决策逻辑
    """
    logger.info("🧠 决策制定节点正在分析...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"].lower()
    processing_path = state.get("processing_path", [])
    processing_path.append("decision_maker")  # 记录执行路径
    
    # 检查是否是模型相关问题 - 扩展关键词检测
    model_keywords = [
        "模型", "model", "你是谁", "你是什么", "你叫什么", "你由什么", "你用什么", "你基于什么",
        "你是什么模型", "你叫什么名字", "你的身份", "你的背景", "你来自哪里", "你是什么AI",
        "你是什么人工智能", "你是什么助手", "你是什么工具", "你是什么系统"
    ]
    if any(keyword in user_input for keyword in model_keywords):
        decision = "model_info"
        route_reason = "检测到模型相关问题"
    else:
        # 使用模型进行智能决策
        decision_prompt = f"""
        请分析以下用户输入，并决定应该使用哪个专业智能体来处理：
        
        用户输入: {state["user_input"]}
        
        可选的智能体:
        1. calculator - 处理数学计算、数字运算相关请求
        2. weather - 处理天气查询、温度、天气状况相关请求  
        3. search - 处理信息搜索、查找资料相关请求
        4. translator - 处理翻译、语言转换相关请求
        5. general - 处理其他通用请求
        
        请只返回对应的智能体名称（calculator/weather/search/translator/general），不要包含其他内容。
        """
        
        try:
            # 调用模型进行决策
            response = llm.invoke([HumanMessage(content=decision_prompt)])
            logger.info(f"模型输出:{response.content}")
            decision = response.content.strip().lower()
            
            # 验证决策结果
            valid_decisions = ["calculator", "weather", "search", "translator", "general"]
            if decision not in valid_decisions:
                decision = "general"
                route_reason = "模型决策结果无效，使用通用处理"
            else:
                # 根据决策结果设置原因
                decision_reasons = {
                    "calculator": "模型判断为数学计算需求",
                    "weather": "模型判断为天气查询需求", 
                    "search": "模型判断为信息搜索需求",
                    "translator": "模型判断为翻译需求",
                    "general": "模型判断为通用处理需求"
                }
                route_reason = decision_reasons.get(decision, "模型决策")
                
        except Exception as e:
            logger.error(f"模型调用失败: {e}")
            # 回退到关键词匹配
            if any(word in user_input for word in ["计算", "数学", "数字", "+", "-", "*", "/"]):
                decision = "calculator"
                route_reason = "检测到数学计算需求（回退模式）"
            elif any(word in user_input for word in ["天气", "温度", "下雨", "晴天"]):
                decision = "weather"
                route_reason = "检测到天气查询需求（回退模式）"
            elif any(word in user_input for word in ["搜索", "查找", "信息", "资料"]):
                decision = "search"
                route_reason = "检测到信息搜索需求（回退模式）"
            elif any(word in user_input for word in ["翻译", "英文", "中文", "language"]):
                decision = "translator"
                route_reason = "检测到翻译需求（回退模式）"
            else:
                decision = "general"
                route_reason = "通用处理路径（回退模式）"
    
    logger.info(f"决策结果: {decision}")
    logger.info(f"决策原因: {route_reason}")
    
    return {
        "decision": decision,  # 传递给路由函数
        "route_reason": route_reason,  # 记录决策原因
        "processing_path": processing_path,  # 更新执行路径
        "messages": [AIMessage(content=f"决策完成: {route_reason}")]  # 添加决策消息
    }

# ============================================================================
# 专业处理节点定义
# ============================================================================

def model_info_agent(state: RoutingState) -> RoutingState:
    """
    模型信息智能体节点
    作用：处理模型相关问题，返回标准回复
    功能：提供统一的模型介绍信息
    """
    logger.info("🤖 模型信息智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("model_info")  # 记录执行路径
    
    # 标准回复
    response = "您好，我是由default模型提供支持，作为Cursor IDE的核心功能之一，可协助完成各类开发任务，只要是编程相关的问题，都可以问我！你现在有什么想做的吗？"
    
    return {
        "response": response,  # 模型信息回复
        "processing_path": processing_path,  # 更新执行路径
        "messages": [AIMessage(content=response)]  # 添加响应消息
    }

def calculator_agent(state: RoutingState) -> RoutingState:
    """
    计算器智能体节点
    作用：处理数学计算相关的用户请求
    功能：解析数学表达式并计算结果
    """
    logger.info("🧮 计算器智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("calculator")  # 记录执行路径
    
    # 使用模型进行智能计算
    calc_prompt = f"""
    请帮助用户进行数学计算。用户输入: {user_input}
    
    请分析用户的需求，如果是数学计算，请提供详细的计算过程和结果。
    如果不是数学计算，请友好地引导用户提供数学表达式。
    
    请用中文回复，格式要清晰易读。
    """
    
    try:
        response = llm.invoke([HumanMessage(content=calc_prompt)])
        result = response.content
    except Exception as e:
        logger.error(f"计算器模型调用失败: {e}")
        # 回退到简单计算逻辑
        import re
        numbers = re.findall(r'\d+', user_input)  # 提取数字
        operators = re.findall(r'[\+\-\*\/]', user_input)  # 提取运算符
        
        if len(numbers) >= 2 and operators:  # 确保有足够的数字和运算符
            try:
                num1, num2 = int(numbers[0]), int(numbers[1])
                op = operators[0]
                
                # 执行计算
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
                    
                result = f"计算结果: {num1} {op} {num2} = {result}"
            except Exception as e:
                result = f"计算错误: {str(e)}"
        else:
            result = "请提供有效的数学表达式，例如: '计算 5 + 3'"
    
    return {
        "response": result,  # 计算结果
        "processing_path": processing_path,  # 更新执行路径
        "messages": [AIMessage(content=result)]  # 添加响应消息
    }

def weather_agent(state: RoutingState) -> RoutingState:
    """
    天气智能体节点
    作用：处理天气查询相关的用户请求
    功能：根据城市名返回模拟天气信息
    """
    logger.info("🌤️ 天气智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("weather")  # 记录执行路径
    
    # 使用模型进行智能天气查询
    weather_prompt = f"""
    用户想查询天气信息: {user_input}
    
    请分析用户想查询哪个城市的天气，并提供友好的天气信息回复。
    如果用户没有明确指定城市，请询问具体城市。
    
    请用中文回复，格式要清晰易读。
    """
    
    try:
        response = llm.invoke([HumanMessage(content=weather_prompt)])
        result = response.content
    except Exception as e:
        logger.error(f"天气查询模型调用失败: {e}")
        # 回退到模拟天气数据
        weather_data = {
            "北京": "晴天，温度 25°C，空气质量良好",
            "上海": "多云，温度 28°C，空气质量一般",
            "广州": "小雨，温度 30°C，空气质量良好",
            "深圳": "晴天，温度 29°C，空气质量优秀"
        }
        
        # 提取城市名 - 从用户输入中识别城市
        cities = ["北京", "上海", "广州", "深圳"]
        found_city = None
        for city in cities:
            if city in user_input:
                found_city = city
                break
        
        if found_city:
            result = f"{found_city}的天气: {weather_data[found_city]}"
        else:
            result = "请指定城市名称，例如: '查询北京的天气'"
    
    return {
        "response": result,  # 天气信息
        "processing_path": processing_path,  # 更新执行路径
        "messages": [AIMessage(content=result)]  # 添加响应消息
    }

def search_agent(state: RoutingState) -> RoutingState:
    """
    搜索智能体节点
    作用：处理信息搜索相关的用户请求
    功能：返回模拟的搜索结果
    """
    logger.info("🔍 搜索智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("search")  # 记录执行路径
    
    # 使用模型进行智能搜索
    search_prompt = f"""
    用户想搜索信息: {user_input}
    
    请分析用户的搜索需求，并提供相关的信息和建议。
    如果用户搜索的是技术相关的内容，请提供专业的技术信息。
    
    请用中文回复，格式要清晰易读，包含多个要点。
    """
    
    try:
        response = llm.invoke([HumanMessage(content=search_prompt)])
        result = response.content
    except Exception as e:
        logger.error(f"搜索模型调用失败: {e}")
        # 回退到模拟搜索结果
        result = f"关于 '{user_input}' 的搜索结果:\n"
        result += "1. 相关信息1\n"
        result += "2. 相关信息2\n"
        result += "3. 相关信息3\n"
        result += "(这是模拟的搜索结果)"
    
    return {
        "response": result,  # 搜索结果
        "processing_path": processing_path,  # 更新执行路径
        "messages": [AIMessage(content=result)]  # 添加响应消息
    }

def translator_agent(state: RoutingState) -> RoutingState:
    """
    翻译智能体节点
    作用：处理翻译相关的用户请求
    功能：提供中英文互译服务
    """
    logger.info("🌐 翻译智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("translator")  # 记录执行路径
    
    # 使用模型进行智能翻译
    translate_prompt = f"""
    用户需要翻译: {user_input}
    
    请分析用户想要翻译的内容，并提供准确的翻译结果。
    如果是中英文互译，请提供双向翻译。
    如果是其他语言，请说明并提供翻译。
    
    请用中文回复，格式要清晰易读。
    """
    
    try:
        response = llm.invoke([HumanMessage(content=translate_prompt)])
        result = response.content
    except Exception as e:
        logger.error(f"翻译模型调用失败: {e}")
        # 回退到简单翻译逻辑
        if any(word in user_input for word in ["hello", "你好"]):
            if "hello" in user_input.lower():
                result = "翻译结果: hello → 你好"
            else:
                result = "翻译结果: 你好 → hello"
        else:
            result = "请提供需要翻译的文本，例如: '翻译 hello'"
    
    return {
        "response": result,  # 翻译结果
        "processing_path": processing_path,  # 更新执行路径
        "messages": [AIMessage(content=result)]  # 添加响应消息
    }

def general_agent(state: RoutingState) -> RoutingState:
    """
    通用智能体节点
    作用：处理无法分类到其他专业智能体的用户请求
    功能：提供通用的回复和引导
    """
    logger.info("💬 通用智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    processing_path = state["processing_path"]
    processing_path.append("general")  # 记录执行路径
    
    # 使用模型进行通用回复
    general_prompt = f"""
    用户说: {user_input}
    
    请理解用户的意图，并提供友好、有用的回复。
    如果用户有编程相关的问题，请提供技术建议。
    如果用户需要帮助，请提供指导。
    
    请用中文回复，要友好、专业、有帮助。
    """
    
    try:
        response = llm.invoke([HumanMessage(content=general_prompt)])
        result = response.content
    except Exception as e:
        logger.error(f"通用智能体模型调用失败: {e}")
        # 回退到简单回复
        result = f"我理解您说: '{user_input}'。这是一个通用回复，如果您有特定需求，请告诉我。"
    
    return {
        "response": result,  # 通用回复
        "processing_path": processing_path,  # 更新执行路径
        "messages": [AIMessage(content=result)]  # 添加响应消息
    }

# ============================================================================
# 路由函数
# ============================================================================

def route_decision(state: RoutingState) -> str:
    """
    路由函数 - 根据决策结果选择下一个节点
    作用：作为条件边的判断函数，决定工作流的执行路径
    学习要点：条件路由的核心逻辑
    """
    decision = state["decision"]  # 从状态中获取决策结果
    logger.info(f"路由决策: {decision}")
    
    # 路由映射表 - 将决策结果映射到对应的节点名
    routing_map = {
        "model_info": "model_info_agent",    # 模型信息路径
        "calculator": "calculator_agent",     # 计算器路径
        "weather": "weather_agent",          # 天气查询路径
        "search": "search_agent",            # 搜索路径
        "translator": "translator_agent",    # 翻译路径
        "general": "general_agent"           # 通用路径
    }
    
    return routing_map.get(decision, "general_agent")  # 返回目标节点名，默认通用节点

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
    
    # 1. 创建状态图 - 使用 RoutingState 作为状态类型
    workflow = StateGraph(RoutingState)
    
    # 2. 添加节点 - 定义工作流中的所有处理节点
    workflow.add_node("decision_maker", decision_maker)        # 决策节点：分析用户意图
    workflow.add_node("model_info_agent", model_info_agent)    # 模型信息节点：处理模型相关问题
    workflow.add_node("calculator_agent", calculator_agent)    # 计算器节点：处理数学计算
    workflow.add_node("weather_agent", weather_agent)          # 天气节点：处理天气查询
    workflow.add_node("search_agent", search_agent)            # 搜索节点：处理信息搜索
    workflow.add_node("translator_agent", translator_agent)    # 翻译节点：处理翻译请求
    workflow.add_node("general_agent", general_agent)          # 通用节点：处理其他请求
    
    # 3. 设置入口点 - 工作流从决策节点开始
    workflow.set_entry_point("decision_maker")
    
    # 4. 添加条件边 - 根据决策结果动态选择执行路径
    workflow.add_conditional_edges(
        "decision_maker",  # 源节点：决策制定节点
        route_decision,    # 路由函数：决定下一个节点
        {
            # 路由映射：决策结果 -> 目标节点
            "model_info_agent": "model_info_agent",  # 模型信息路径
            "calculator_agent": "calculator_agent",  # 计算器路径
            "weather_agent": "weather_agent",        # 天气查询路径
            "search_agent": "search_agent",          # 搜索路径
            "translator_agent": "translator_agent",  # 翻译路径
            "general_agent": "general_agent"         # 通用路径
        }
    )
    
    # 5. 添加结束边 - 所有专业节点都连接到结束点
    workflow.add_edge("model_info_agent", END)  # 模型信息节点 -> 结束
    workflow.add_edge("calculator_agent", END)  # 计算器节点 -> 结束
    workflow.add_edge("weather_agent", END)     # 天气节点 -> 结束
    workflow.add_edge("search_agent", END)      # 搜索节点 -> 结束
    workflow.add_edge("translator_agent", END)  # 翻译节点 -> 结束
    workflow.add_edge("general_agent", END)     # 通用节点 -> 结束
    
    # 6. 编译工作流 - 将工作流定义编译为可执行图
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
        # todo 可视化 
    from show_graph import show_workflow_graph
    show_workflow_graph(graph, "判断路由工作流",logger)
    # 测试输入
    test_inputs = [
        "你是什么模型？",                    # 测试模型信息路径
        "请帮我计算 15 + 25",               # 测试计算器路径
        "查询北京的天气怎么样",              # 测试天气查询路径
        "搜索关于人工智能的信息",            # 测试搜索路径
        "翻译 hello 这个单词",              # 测试翻译路径
        "你好，我想了解一下 LangGraph"      # 测试通用路径
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        logger.info(f"\n--- 测试 {i} ---")
        logger.info(f"输入: {test_input}")
        
        try:
            # todo invoke 会初始化state，所以每次invoke都会重新执行一次decision_maker
            result = graph.invoke({"user_input": test_input})
            logger.info(f"result:{result}")
            # logger.info(f"决策: {result['decision']}")
            # logger.info(f"决策原因: {result['route_reason']}")
            # logger.info(f"处理路径: {' → '.join(result['processing_path'])}")
            # logger.info(f"输出: {result['response']}")
        except Exception as e:
            logger.error(f"错误: {e}")

if __name__ == "__main__":
    test_conditional_routing() 