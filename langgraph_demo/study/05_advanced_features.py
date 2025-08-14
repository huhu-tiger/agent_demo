# -*- coding: utf-8 -*-
"""
LangGraph 高级特性示例
学习要点：记忆管理、检查点、并行处理、错误处理

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import asyncio
import uuid
from typing import TypedDict, List, Dict
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

# LangChain 组件
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import config

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger

# ============================================================================
# 高级状态定义
# ============================================================================

class AdvancedState(TypedDict):
    """高级状态 - 包含记忆、检查点、并行处理等特性"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    session_id: str
    memory_context: List[str]
    parallel_results: Dict[str, str]
    error_log: List[str]
    checkpoint_data: Dict[str, any]
    final_response: str

# ============================================================================
# 记忆管理智能体
# ============================================================================

def memory_manager(state: AdvancedState) -> AdvancedState:
    """
    记忆管理智能体 - 管理对话历史和上下文
    学习要点：记忆管理和上下文维护
    """
    logger.info("🧠 记忆管理智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    session_id = state.get("session_id", str(uuid.uuid4()))
    memory_context = state.get("memory_context", [])
    
    # 更新记忆上下文
    memory_context.append(f"用户输入: {user_input}")
    
    # 模拟记忆检索
    if len(memory_context) > 1:
        recent_context = memory_context[-3:]  # 保留最近3条记录
        logger.info(f"记忆上下文: {recent_context}")
    else:
        recent_context = memory_context
    
    return {
        "session_id": session_id,
        "memory_context": memory_context,
        "checkpoint_data": {"memory_updated": True, "context_count": len(memory_context)},
        "messages": [SystemMessage(content=f"记忆已更新，会话ID: {session_id}")]
    }

# ============================================================================
# 并行处理智能体
# ============================================================================

def parallel_processor_1(state: AdvancedState) -> AdvancedState:
    """并行处理器1 - 处理任务A"""
    logger.info("⚡ 并行处理器1正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    parallel_results = state.get("parallel_results", {})
    
    # 模拟并行处理
    result = f"处理器1结果: 分析了'{user_input}'的语义特征"
    parallel_results["processor_1"] = result
    
    return {
        "parallel_results": parallel_results,
        "checkpoint_data": {"parallel_1_complete": True}
    }

def parallel_processor_2(state: AdvancedState) -> AdvancedState:
    """并行处理器2 - 处理任务B"""
    logger.info("⚡ 并行处理器2正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    parallel_results = state.get("parallel_results", {})
    
    # 模拟并行处理
    result = f"处理器2结果: 提取了'{user_input}'的关键词"
    parallel_results["processor_2"] = result
    
    return {
        "parallel_results": parallel_results,
        "checkpoint_data": {"parallel_2_complete": True}
    }

def parallel_processor_3(state: AdvancedState) -> AdvancedState:
    """并行处理器3 - 处理任务C"""
    logger.info("⚡ 并行处理器3正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    parallel_results = state.get("parallel_results", {})
    
    # 模拟并行处理
    result = f"处理器3结果: 生成了'{user_input}'的摘要"
    parallel_results["processor_3"] = result
    
    return {
        "parallel_results": parallel_results,
        "checkpoint_data": {"parallel_3_complete": True}
    }

# ============================================================================
# 错误处理智能体
# ============================================================================

def error_handler(state: AdvancedState) -> AdvancedState:
    """
    错误处理智能体 - 处理异常和错误
    学习要点：错误处理和恢复机制
    """
    logger.info("🛡️ 错误处理智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    error_log = state.get("error_log", [])
    parallel_results = state.get("parallel_results", {})
    
    # 检查是否有错误
    if not parallel_results:
        error_msg = "并行处理结果为空，可能存在处理错误"
        error_log.append(error_msg)
        logger.warning(error_msg)
    
    # 模拟错误恢复
    if error_log:
        recovery_msg = "已执行错误恢复机制"
        error_log.append(recovery_msg)
        logger.info(recovery_msg)
    
    return {
        "error_log": error_log,
        "checkpoint_data": {"error_handled": True, "error_count": len(error_log)}
    }

# ============================================================================
# 结果聚合智能体
# ============================================================================

def result_aggregator(state: AdvancedState) -> AdvancedState:
    """
    结果聚合智能体 - 整合所有并行处理结果
    学习要点：结果聚合和状态整合
    """
    logger.info("🎯 结果聚合智能体正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    parallel_results = state.get("parallel_results", {})
    memory_context = state.get("memory_context", [])
    error_log = state.get("error_log", [])
    
    # 聚合结果
    final_response = f"基于'{user_input}'的综合处理结果：\n\n"
    
    if parallel_results:
        final_response += "📊 并行处理结果：\n"
        for processor, result in parallel_results.items():
            final_response += f"• {result}\n"
    
    if memory_context:
        final_response += f"\n🧠 记忆上下文 ({len(memory_context)} 条记录)：\n"
        for i, context in enumerate(memory_context[-3:], 1):
            final_response += f"{i}. {context}\n"
    
    if error_log:
        final_response += f"\n⚠️ 错误日志 ({len(error_log)} 条)：\n"
        for error in error_log:
            final_response += f"• {error}\n"
    
    final_response += "\n✅ 处理完成！"
    
    return {
        "final_response": final_response,
        "messages": [AIMessage(content=final_response)]
    }

# ============================================================================
# 工作流构建
# ============================================================================

def create_advanced_workflow():
    """
    创建高级特性工作流
    学习要点：复杂工作流的构建和配置
    """
    logger.info("\n" + "="*60)
    logger.info("🚀 高级特性工作流")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 1. 创建状态图（带检查点）
    workflow = StateGraph(AdvancedState)
    
    # 2. 添加节点
    workflow.add_node("memory_manager", memory_manager)
    workflow.add_node("parallel_processor_1", parallel_processor_1)
    workflow.add_node("parallel_processor_2", parallel_processor_2)
    workflow.add_node("parallel_processor_3", parallel_processor_3)
    workflow.add_node("error_handler", error_handler)
    workflow.add_node("result_aggregator", result_aggregator)
    
    # 3. 设置入口点
    workflow.set_entry_point("memory_manager")
    
    # 4. 添加边（并行处理）
    workflow.add_edge("memory_manager", "parallel_processor_1")
    workflow.add_edge("memory_manager", "parallel_processor_2")
    workflow.add_edge("memory_manager", "parallel_processor_3")
    
    # 5. 聚合并行结果
    workflow.add_edge("parallel_processor_1", "error_handler")
    workflow.add_edge("parallel_processor_2", "error_handler")
    workflow.add_edge("parallel_processor_3", "error_handler")
    workflow.add_edge("error_handler", "result_aggregator")
    workflow.add_edge("result_aggregator", END)
    
    # 6. 编译工作流
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 检查点管理
# ============================================================================

def create_checkpoint_workflow():
    """
    创建带检查点的工作流
    学习要点：检查点的使用和恢复
    """
    logger.info("\n" + "="*60)
    logger.info("💾 检查点工作流")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 创建检查点保存器
    checkpointer = InMemorySaver()
    
    # 创建状态图
    workflow = StateGraph(AdvancedState, checkpointer=checkpointer)
    
    # 添加节点
    workflow.add_node("memory_manager", memory_manager)
    workflow.add_node("result_aggregator", result_aggregator)
    
    # 设置边
    workflow.set_entry_point("memory_manager")
    workflow.add_edge("memory_manager", "result_aggregator")
    workflow.add_edge("result_aggregator", END)
    
    # 编译
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 测试函数
# ============================================================================

def test_advanced_features():
    """测试高级特性"""
    logger.info("🚀 测试 LangGraph 高级特性")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 创建高级工作流
    graph = create_advanced_workflow()
    
    # 测试输入
    test_inputs = [
        "分析人工智能的发展趋势",
        "设计一个智能推荐系统",
        "构建一个多模态AI应用"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        logger.info(f"\n--- 测试 {i} ---")
        logger.info(f"输入: {test_input}")
        
        try:
            result = graph.invoke({"user_input": test_input})
            logger.info(f"会话ID: {result['session_id']}")
            logger.info(f"并行结果数量: {len(result['parallel_results'])}")
            logger.info(f"记忆上下文数量: {len(result['memory_context'])}")
            logger.info(f"错误日志数量: {len(result['error_log'])}")
            logger.info("高级特性测试完成！")
        except Exception as e:
            logger.error(f"错误: {e}")

def test_checkpoint_features():
    """测试检查点特性"""
    logger.info("\n💾 测试检查点特性")
    
    # 创建检查点工作流
    graph = create_checkpoint_workflow()
    
    # 模拟检查点恢复
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    test_input = "测试检查点功能"
    logger.info(f"输入: {test_input}")
    
    try:
        result = graph.invoke({"user_input": test_input}, config=config)
        logger.info(f"检查点数据: {result['checkpoint_data']}")
        logger.info("检查点测试完成！")
    except Exception as e:
        logger.error(f"错误: {e}")

if __name__ == "__main__":
    test_advanced_features()
    test_checkpoint_features() 