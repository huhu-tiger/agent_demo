# -*- coding: utf-8 -*-
"""
LangGraph 基础概念示例
学习要点：状态管理、节点定义、边连接

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
os.environ["OPENAI_API_BASE"] = config.base_url  # 自定义模型地址
os.environ["OPENAI_API_KEY"] = config.api_key  # 自定义模型密钥
MODEL_NAME = config.model  # 自定义模型名称

# 获取日志器
logger = config.logger

# ============================================================================
# 基础状态定义
# ============================================================================

class BasicState(TypedDict):
    """基础状态定义 - 包含消息历史和用户输入"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    response: str
    step_count: int

# ============================================================================
# 基础节点定义
# ============================================================================

def input_processor(state: BasicState) -> BasicState:
    logger.info(f"input_processor state: {state}")
    """
    输入处理节点 - 处理用户输入
    学习要点：节点函数的基本结构
    """
    logger.info("🔄 输入处理节点正在工作...")
    # logger.info(f"使用模型: {MODEL_NAME}")
    # logger.info(f"state: {state}")
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    # 简单的输入处理逻辑
    processed_input = f"已处理: {user_input}"
    
    return {
        "user_input": processed_input,
        "step_count": step_count,
        "messages": [HumanMessage(content=processed_input)]
    }

def response_generator(state: BasicState) -> BasicState:
    logger.info(f"response_generator state: {state}")
    """
    响应生成节点 - 生成智能体响应
    学习要点：状态更新和消息处理
    """
    logger.info("🤖 响应生成节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    processed_input = state["user_input"]
    step_count = state["step_count"] + 1
    
    # 生成响应
    response = f"步骤 {step_count}: 我收到了您的消息 '{processed_input}'。这是一个基础响应示例。"
    logger.info(f"response: {response}")
    return {
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def message_logger(state: BasicState) -> BasicState:
    logger.info(f"message_logger state: {state}")
    """
    消息记录节点 - 记录处理过程
    学习要点：状态读取和日志记录
    """
    logger.info("📝 消息记录节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    messages = state["messages"]
    response = state["response"]
    step_count = state["step_count"] + 1
    
    # 记录处理信息
    log_message = f"处理完成 - 步骤: {step_count}, 消息数量: {len(messages)}"
    # logger.info(log_message)
    # logger.info(f"state: {state}")
    
    return {
        "response": f"{response}\n\n{log_message}"
    }

# ============================================================================
# 工作流构建
# ============================================================================

def create_basic_workflow():
    """
    创建基础工作流
    学习要点：StateGraph 的创建和配置
    """
    logger.info("\n" + "="*60)
    logger.info("🚀 基础概念工作流")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(BasicState)
    
    # 2. 添加节点
    workflow.add_node("input_processor", input_processor)
    workflow.add_node("response_generator", response_generator)
    workflow.add_node("message_logger", message_logger)
    
    # 3. 设置入口点
    workflow.set_entry_point("input_processor")
    
    # 4. 添加边（顺序执行）
    workflow.add_edge("input_processor", "response_generator")
    workflow.add_edge("response_generator", "message_logger")
    workflow.add_edge("message_logger", END)
    
    # 5. 编译工作流
    graph = workflow.compile()
    
    return graph, workflow

# ============================================================================
# 测试函数
# ============================================================================



def test_basic_concepts():
    """测试基础概念"""
    logger.info("🎓 测试 LangGraph 基础概念")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 创建工作流
    graph, workflow = create_basic_workflow()

    # todo 可视化 
    from show_graph import show_workflow_graph
    show_workflow_graph(graph, "基础概念工作流",logger)

    # 测试输入
    test_inputs = [
        "你好，我想学习 LangGraph",
        "请解释一下状态管理的概念",
        "节点和边有什么区别？"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        logger.info(f"\n--- 测试 {i} ---")
        logger.info(f"输入: {test_input}")
        
        try:
            result = graph.invoke({"user_input": test_input})
            logger.info(f"result: {result}")
            # logger.info(f"输出: {result['response']}")
            # logger.info(f"步骤数: {result['step_count']}")
            # logger.info(f"消息数: {len(result['messages'])}")
        except Exception as e:
            logger.error(f"错误: {e}")

if __name__ == "__main__":
    test_basic_concepts() 