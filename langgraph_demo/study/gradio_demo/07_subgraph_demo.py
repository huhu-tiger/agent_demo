# -*- coding: utf-8 -*-
"""
LangGraph 子图示例
学习要点：主图调用子图的实现方式

子图（Subgraph）是 LangGraph 中的一个重要概念，允许将复杂的工作流分解为可重用的组件。
本示例演示了两种主要的子图使用场景：
1. 独立状态模式：主图和子图使用完全不同的状态结构
2. 多层嵌套模式：主图调用子图，子图调用孙图的层次化结构

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import operator
from typing import TypedDict, List
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Send

import sys
# 添加路径以导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger

# ============================================================================
# 场景1: 独立状态模式 - 主图和子图使用不同的状态结构
# ============================================================================

class SubgraphState(TypedDict):
    """
    子图状态定义
    
    子图使用独立的状态结构，与主图状态完全分离
    这种模式适合需要状态隔离的场景
    """
    input_data: str      # 输入数据
    processed_data: str  # 处理后的数据
    subgraph_steps: List[str]  # 子图执行步骤

class MainGraphState(TypedDict):
    """
    主图状态定义
    
    主图使用独立的状态结构，与子图状态完全分离
    """
    user_input: str      # 用户输入
    final_result: str    # 最终结果
    main_steps: List[str]  # 主图执行步骤

def subgraph_process_node(state: SubgraphState) -> SubgraphState:
    """
    子图处理节点
    
    Args:
        state: 子图状态
        
    Returns:
        更新后的子图状态
    """
    logger.info("🔧 子图处理节点: 处理数据")
    
    input_data = state.get("input_data", "")
    processed_data = f"子图处理结果: {input_data.upper()}"
    
    return {
        "input_data": state.get("input_data", ""),  # 保持原有值
        "processed_data": processed_data,
        "subgraph_steps": state.get("subgraph_steps", []) + ["subgraph_process"]
    }

def subgraph_validate_node(state: SubgraphState) -> SubgraphState:
    """
    子图验证节点
    
    Args:
        state: 子图状态
        
    Returns:
        更新后的子图状态
    """
    logger.info("🔧 子图验证节点: 验证数据")
    
    processed_data = state.get("processed_data", "")
    validated_data = f"已验证: {processed_data}"
    
    return {
        "input_data": state.get("input_data", ""),  # 保持原有值
        "processed_data": validated_data,
        "subgraph_steps": state.get("subgraph_steps", []) + ["subgraph_validate"]
    }

def demo_independent_state_subgraph():
    """
    演示独立状态模式的子图
    
    在这种模式下，子图使用独立的状态结构，
    需要通过节点函数来调用子图并处理状态转换
    
    特点：
    - 主图和子图有完全不同的状态结构
    - 需要在节点函数中进行状态转换
    - 提供更好的状态隔离和模块化
    - 适合复杂的多模块系统
    """
    logger.info("\n" + "="*60)
    logger.info("🔄 独立状态子图演示")
    logger.info("主图和子图使用不同的状态结构")
    logger.info("特点：状态隔离、模块化设计")
    logger.info("="*60)
    
    # 构建子图
    logger.info("📋 构建独立状态子图...")
    logger.info("   - 子图状态结构: SubgraphState (input_data, processed_data, subgraph_steps)")
    logger.info("   - 子图节点: process -> validate")
    logger.info("   - 子图功能: 数据处理和验证")
    
    subgraph_builder = StateGraph(SubgraphState)
    
    # 添加子图节点
    logger.info("   🔧 添加子图节点...")
    subgraph_builder.add_node("process", subgraph_process_node)    # 数据处理节点
    subgraph_builder.add_node("validate", subgraph_validate_node)  # 数据验证节点
    
    # 设置子图边
    logger.info("   🔗 设置子图边...")
    subgraph_builder.add_edge(START, "process")      # 开始 -> 处理
    subgraph_builder.add_edge("process", "validate") # 处理 -> 验证
    subgraph_builder.add_edge("validate", END)       # 验证 -> 结束
    
    # 编译子图
    subgraph = subgraph_builder.compile()
    logger.info("✅ 独立状态子图编译完成")
    logger.info("   📊 子图结构: START -> process -> validate -> END")
    
    # 构建主图
    logger.info("📋 构建主图...")
    logger.info("   - 主图状态结构: MainGraphState (user_input, final_result, main_steps)")
    logger.info("   - 主图节点: prepare -> call_subgraph -> finalize")
    logger.info("   - 主图功能: 调用子图并处理结果")
    
    def main_prepare_node(state: MainGraphState) -> MainGraphState:
        """
        主图准备节点
        
        负责准备输入数据，为调用子图做准备
        这是主图的第一个节点，处理用户输入
        
        Args:
            state: 主图状态
            
        Returns:
            更新后的主图状态
        """
        logger.info("🏠 主图准备节点: 准备输入数据")
        user_input = state.get("user_input", "默认输入")
        logger.info(f"   📥 用户输入: {user_input}")
        
        return {
            "user_input": user_input,
            "final_result": "",  # 初始化为空字符串
            "main_steps": ["main_prepare"]
        }
    
    def main_call_subgraph_node(state: MainGraphState) -> MainGraphState:
        """
        主图调用子图节点
        
        这是独立状态模式的核心节点，负责：
        1. 将主图状态转换为子图状态
        2. 调用子图进行处理
        3. 将子图结果转换回主图状态
        
        这种模式提供了完全的状态隔离，主图和子图可以独立演化
        
        Args:
            state: 主图状态
            
        Returns:
            更新后的主图状态
        """
        logger.info("🏠 主图调用子图节点: 调用子图处理")
        
        # 1. 状态转换：主图状态 -> 子图状态
        user_input = state.get("user_input", "")
        logger.info(f"   🔄 状态转换: 主图状态 -> 子图状态")
        logger.info(f"   📤 传递给子图的数据: {user_input}")
        
        subgraph_input: SubgraphState = {
            "input_data": user_input,
            "processed_data": "",
            "subgraph_steps": []
        }
        
        # 2. 调用子图
        logger.info("   🚀 调用子图...")
        subgraph_result = subgraph.invoke(subgraph_input)
        logger.info(f"   📥 子图返回结果: {subgraph_result}")
        
        # 3. 状态转换：子图状态 -> 主图状态
        processed_data = subgraph_result.get('processed_data', '')
        final_result = f"主图最终结果: {processed_data}"
        logger.info(f"   🔄 状态转换: 子图状态 -> 主图状态")
        logger.info(f"   📤 最终结果: {final_result}")
        
        return {
            "user_input": state.get("user_input", ""),  # 保持原有值
            "final_result": final_result,
            "main_steps": state.get("main_steps", []) + ["main_call_subgraph"]
        }
    
    def main_finalize_node(state: MainGraphState) -> MainGraphState:
        """
        主图完成节点
        
        负责完成最终的处理和格式化输出
        这是主图的最后一个节点，处理最终结果
        
        Args:
            state: 主图状态
            
        Returns:
            更新后的主图状态
        """
        logger.info("🏠 主图完成节点: 完成处理")
        
        final_result = state.get("final_result", "")
        completed_result = f"✅ 完成: {final_result}"
        logger.info(f"   🎯 最终结果: {completed_result}")
        
        return {
            "user_input": state.get("user_input", ""),  # 保持原有值
            "final_result": completed_result,
            "main_steps": state.get("main_steps", []) + ["main_finalize"]
        }
    
    # 创建主图
    main_builder = StateGraph(MainGraphState)
    
    # 添加主图节点
    logger.info("   🔧 添加主图节点...")
    main_builder.add_node("prepare", main_prepare_node)           # 准备节点
    main_builder.add_node("call_subgraph", main_call_subgraph_node)  # 调用子图的节点（核心）
    main_builder.add_node("finalize", main_finalize_node)         # 完成节点
    
    # 设置主图边
    logger.info("   🔗 设置主图边...")
    main_builder.add_edge(START, "prepare")           # 开始 -> 准备
    main_builder.add_edge("prepare", "call_subgraph") # 准备 -> 调用子图
    main_builder.add_edge("call_subgraph", "finalize") # 调用子图 -> 完成
    main_builder.add_edge("finalize", END)            # 完成 -> 结束
    
    # 编译主图
    main_graph = main_builder.compile()
    logger.info("✅ 主图编译完成")
    logger.info("   📊 主图结构: START -> prepare -> call_subgraph -> finalize -> END")
    
    # 可视化工作流
    from show_graph import show_workflow_graph
    show_workflow_graph(main_graph, "独立状态子图", logger,
                       "主图和子图使用不同状态结构的示例", formats=['png'])
    
    # 执行工作流
    logger.info("\n🚀 执行独立状态子图工作流...")
    logger.info("📋 初始状态: {'user_input': '测试数据', 'final_result': '', 'main_steps': []}")
    
    try:
        # 使用流式输出，观察状态变化
        for chunk in main_graph.stream(
            {"user_input": "测试数据", "final_result": "", "main_steps": []},
            stream_mode="updates"
        ):
            logger.info(f"📊 执行更新: {chunk}")
            
        logger.info("✅ 独立状态子图工作流执行完成")
            
    except Exception as e:
        logger.error(f"执行工作流时出错: {e}")

# ============================================================================
# 场景2: 多层嵌套子图 - 主图 -> 子图 -> 孙图
# ============================================================================

class GrandchildState(TypedDict):
    """孙图状态"""
    grandchild_input: str
    grandchild_output: str

class ChildState(TypedDict):
    """子图状态"""
    child_input: str
    child_output: str

class ParentState(TypedDict):
    """主图状态"""
    parent_input: str
    parent_output: str

def demo_nested_subgraphs():
    """
    演示多层嵌套子图
    
    展示如何构建三层嵌套的图结构：
    主图 -> 子图 -> 孙图
    
    这种模式适合复杂的层次化处理场景，每一层都有独立的职责：
    - 孙图：处理最底层的具体任务
    - 子图：协调多个孙图或处理中间层逻辑
    - 主图：整体流程控制和结果聚合
    """
    logger.info("\n" + "="*60)
    logger.info("🔄 多层嵌套子图演示")
    logger.info("主图 -> 子图 -> 孙图")
    logger.info("特点：层次化处理、职责分离、模块化设计")
    logger.info("="*60)
    
    # 构建孙图（最内层）
    logger.info("📋 构建孙图（最内层）...")
    logger.info("   - 孙图状态结构: GrandchildState (grandchild_input, grandchild_output)")
    logger.info("   - 孙图功能: 执行最底层的具体处理任务")
    
    def grandchild_node(state: GrandchildState) -> GrandchildState:
        """
        孙图节点
        
        执行最底层的具体处理任务，如数据转换、格式处理等
        这是整个嵌套结构的最内层
        
        Args:
            state: 孙图状态
            
        Returns:
            更新后的孙图状态
        """
        logger.info("👶 孙图节点: 处理数据")
        input_data = state.get("grandchild_input", "")
        logger.info(f"   📥 孙图输入: {input_data}")
        
        output = f"孙图处理: {input_data} -> 深度处理完成"
        logger.info(f"   📤 孙图输出: {output}")
        
        return {
            "grandchild_input": state.get("grandchild_input", ""),  # 保持原有值
            "grandchild_output": output
        }
    
    grandchild_builder = StateGraph(GrandchildState)
    grandchild_builder.add_node("grandchild_node", grandchild_node)
    grandchild_builder.add_edge(START, "grandchild_node")
    grandchild_builder.add_edge("grandchild_node", END)
    grandchild_graph = grandchild_builder.compile()
    logger.info("✅ 孙图编译完成")
    logger.info("   📊 孙图结构: START -> grandchild_node -> END")
    
    # 构建子图（中间层）
    logger.info("📋 构建子图（中间层）...")
    logger.info("   - 子图状态结构: ChildState (child_input, child_output)")
    logger.info("   - 子图功能: 调用孙图并处理结果")
    
    def child_node(state: ChildState) -> ChildState:
        """
        子图节点：调用孙图
        
        作为中间层，负责调用孙图并处理其返回结果
        这种设计实现了职责分离和模块化
        
        Args:
            state: 子图状态
            
        Returns:
            更新后的子图状态
        """
        logger.info("👨 子图节点: 调用孙图")
        
        # 准备调用孙图的输入
        child_input = state.get("child_input", "")
        grandchild_input: GrandchildState = {
            "grandchild_input": child_input,
            "grandchild_output": ""  # 初始化为空字符串
        }
        logger.info(f"   📤 调用孙图: {grandchild_input}")
        
        # 调用孙图
        grandchild_result = grandchild_graph.invoke(grandchild_input)
        logger.info(f"   📥 孙图返回结果: {grandchild_result}")
        
        # 处理孙图结果
        grandchild_output = grandchild_result.get('grandchild_output', '')
        child_output = f"子图处理: {grandchild_output}"
        logger.info(f"   📤 子图输出: {child_output}")
        
        return {
            "child_input": state.get("child_input", ""),  # 保持原有值
            "child_output": child_output
        }
    
    child_builder = StateGraph(ChildState)
    child_builder.add_node("child_node", child_node)
    child_builder.add_edge(START, "child_node")
    child_builder.add_edge("child_node", END)
    child_graph = child_builder.compile()
    
    # 构建主图（最外层）
    logger.info("📋 构建主图...")
    
    def parent_node(state: ParentState) -> ParentState:
        """主图节点：调用子图"""
        logger.info("👴 主图节点: 调用子图")
        
        # 调用子图
        child_input: ChildState = {
            "child_input": state.get("parent_input", ""),
            "child_output": ""  # 初始化为空字符串
        }
        logger.info(f"🔄 调用子图: {child_input}")
        child_result = child_graph.invoke(child_input)
        logger.info(f"🔄 子图返回结果: {child_result}")
        # 处理子图结果
        parent_output = f"主图处理: {child_result.get('child_output', '')}"
        logger.info(f"🔄 主图返回结果: {parent_output}")
        return {
            "parent_input": state.get("parent_input", ""),  # 保持原有值
            "parent_output": parent_output
        }
    
    parent_builder = StateGraph(ParentState)
    parent_builder.add_node("parent_node", parent_node)
    parent_builder.add_edge(START, "parent_node")
    parent_builder.add_edge("parent_node", END)
    parent_graph = parent_builder.compile()
    
    # 可视化工作流
    from show_graph import show_workflow_graph
    show_workflow_graph(parent_graph, "多层嵌套子图", logger,
                       "主图调用子图，子图调用孙图的嵌套结构示例", formats=['png'])
    
    # 执行工作流
    logger.info("\n🚀 执行多层嵌套子图工作流...")
    
    try:
        # 使用流式输出，包含所有子图信息
        # subgraphs=True 启用子图输出
        # stream_mode="values" 输出所有值
        for chunk in parent_graph.stream(
            {"parent_input": "主图发送原始数据", "parent_output": ""},
            subgraphs=True, 
            stream_mode="values"
        ):
            logger.info(f"📊 执行更新: {chunk}")
            
    except Exception as e:
        logger.error(f"执行工作流时出错: {e}")

# ============================================================================
# 主测试函数
# ============================================================================

def test_subgraphs():
    """
    测试子图功能的主函数
    
    演示两种不同的子图使用场景：
    1. 独立状态模式：适合需要状态隔离的场景
    2. 多层嵌套模式：适合复杂的层次化处理场景
    """
    logger.info("🎯 测试 LangGraph 子图功能")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 演示独立状态子图
    # demo_independent_state_subgraph()
    
    # 演示多层嵌套子图
    demo_nested_subgraphs()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 子图演示完成！")
    logger.info("="*60)

if __name__ == "__main__":
    test_subgraphs() 