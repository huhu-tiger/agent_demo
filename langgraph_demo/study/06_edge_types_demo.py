# -*- coding: utf-8 -*-
"""
LangGraph 边类型详解示例
学习要点：add_edge 参数的含义和用法

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
# 状态定义
# ============================================================================

class EdgeDemoState(TypedDict):
    """边演示状态"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    current_node: str
    edge_history: List[str]
    response: str

# ============================================================================
# 节点定义
# ============================================================================

def node_a(state: EdgeDemoState) -> EdgeDemoState:
    """节点A"""
    logger.info("🅰️ 节点A正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    edge_history = state.get("edge_history", [])
    edge_history.append("A")
    
    response = f"节点A处理: {user_input}"
    
    return {
        "current_node": "A",
        "edge_history": edge_history,
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def node_b(state: EdgeDemoState) -> EdgeDemoState:
    """节点B"""
    logger.info("🅱️ 节点B正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    edge_history = state.get("edge_history", [])
    edge_history.append("B")
    
    response = f"节点B处理: {user_input}"
    
    return {
        "current_node": "B",
        "edge_history": edge_history,
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def node_c(state: EdgeDemoState) -> EdgeDemoState:
    """节点C"""
    logger.info("🅲 节点C正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    edge_history = state.get("edge_history", [])
    edge_history.append("C")
    
    response = f"节点C处理: {user_input}"
    
    return {
        "current_node": "C",
        "edge_history": edge_history,
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def node_d(state: EdgeDemoState) -> EdgeDemoState:
    """节点D"""
    logger.info("🅳 节点D正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    edge_history = state.get("edge_history", [])
    edge_history.append("D")
    
    response = f"节点D处理: {user_input}"
    
    return {
        "current_node": "D",
        "edge_history": edge_history,
        "response": response,
        "messages": [AIMessage(content=response)]
    }

# ============================================================================
# 边类型演示
# ============================================================================

def demo_direct_edges():
    """
    演示直接边 (Direct Edges)
    
    add_edge(from_node, to_node)
    - from_node: 源节点名称
    - to_node: 目标节点名称或特殊常量 (START/END)
    """
    logger.info("\n" + "="*60)
    logger.info("🔗 直接边演示")
    logger.info("add_edge(from_node, to_node)")
    logger.info("="*60)
    
    # 创建状态图
    workflow = StateGraph(EdgeDemoState)
    
    # 添加节点
    workflow.add_node("node_a", node_a)
    workflow.add_node("node_b", node_b)
    workflow.add_node("node_c", node_c)
    
    # 直接边示例
    logger.info("📝 添加直接边:")
    logger.info("workflow.add_edge(START, 'node_a')     # 从开始到节点A")
    logger.info("workflow.add_edge('node_a', 'node_b')  # 从节点A到节点B")
    logger.info("workflow.add_edge('node_b', 'node_c')  # 从节点B到节点C")
    logger.info("workflow.add_edge('node_c', END)       # 从节点C到结束")
    
    workflow.set_entry_point("node_a")
    workflow.add_edge("node_a", "node_b")
    workflow.add_edge("node_b", "node_c")
    workflow.add_edge("node_c", END)
    
    # 编译并测试
    graph = workflow.compile()
    
    test_input = "直接边测试"
    logger.info(f"\n🧪 测试输入: {test_input}")
    
    try:
        result = graph.invoke({"user_input": test_input})
        logger.info(f"执行路径: {' → '.join(result['edge_history'])}")
        logger.info(f"最终响应: {result['response']}")
    except Exception as e:
        logger.error(f"错误: {e}")

def demo_conditional_edges():
    """
    演示条件边 (Conditional Edges)
    
    add_conditional_edges(from_node, condition_function, edge_map)
    - from_node: 源节点名称
    - condition_function: 条件函数，返回下一个节点名称
    - edge_map: 可选，条件到节点的映射字典
    """
    logger.info("\n" + "="*60)
    logger.info("🔄 条件边演示")
    logger.info("add_conditional_edges(from_node, condition_function, edge_map)")
    logger.info("="*60)
    
    def route_condition(state: EdgeDemoState) -> str:
        """条件路由函数"""
        user_input = state["user_input"].lower()
        
        if "a" in user_input or "第一个" in user_input:
            return "route_to_a"
        elif "b" in user_input or "第二个" in user_input:
            return "route_to_b"
        else:
            return "route_to_c"
    
    # 创建状态图
    workflow = StateGraph(EdgeDemoState)
    
    # 添加节点
    workflow.add_node("decision_node", node_a)
    workflow.add_node("node_a", node_a)
    workflow.add_node("node_b", node_b)
    workflow.add_node("node_c", node_c)
    
    # 条件边示例
    logger.info("📝 添加条件边:")
    logger.info("workflow.add_conditional_edges(")
    logger.info("    'decision_node',")
    logger.info("    route_condition,")
    logger.info("    {")
    logger.info("        'route_to_a': 'node_a',")
    logger.info("        'route_to_b': 'node_b',")
    logger.info("        'route_to_c': 'node_c'")
    logger.info("    }")
    logger.info(")")
    
    workflow.set_entry_point("decision_node")
    workflow.add_conditional_edges(
        "decision_node",
        route_condition,
        {
            "route_to_a": "node_a",
            "route_to_b": "node_b",
            "route_to_c": "node_c"
        }
    )
    
    # 添加结束边
    workflow.add_edge("node_a", END)
    workflow.add_edge("node_b", END)
    workflow.add_edge("node_c", END)
    
    # 编译并测试
    graph = workflow.compile()
    
    test_inputs = [
        "选择第一个选项",
        "选择第二个选项", 
        "其他选项"
    ]
    
    for test_input in test_inputs:
        logger.info(f"\n🧪 测试输入: {test_input}")
        try:
            result = graph.invoke({"user_input": test_input})
            logger.info(f"执行路径: {' → '.join(result['edge_history'])}")
            logger.info(f"最终响应: {result['response']}")
        except Exception as e:
            logger.error(f"错误: {e}")

def demo_parallel_edges():
    """
    演示并行边 (Parallel Edges)
    
    通过多个 add_edge 从同一个源节点到不同目标节点
    """
    logger.info("\n" + "="*60)
    logger.info("⚡ 并行边演示")
    logger.info("多个 add_edge 从同一源节点到不同目标节点")
    logger.info("="*60)
    
    # 创建状态图
    workflow = StateGraph(EdgeDemoState)
    
    # 添加节点
    workflow.add_node("start_node", node_a)
    workflow.add_node("parallel_a", node_a)
    workflow.add_node("parallel_b", node_b)
    workflow.add_node("parallel_c", node_c)
    workflow.add_node("merge_node", node_d)
    
    # 并行边示例
    logger.info("📝 添加并行边:")
    logger.info("workflow.add_edge('start_node', 'parallel_a')")
    logger.info("workflow.add_edge('start_node', 'parallel_b')")
    logger.info("workflow.add_edge('start_node', 'parallel_c')")
    logger.info("workflow.add_edge('parallel_a', 'merge_node')")
    logger.info("workflow.add_edge('parallel_b', 'merge_node')")
    logger.info("workflow.add_edge('parallel_c', 'merge_node')")
    
    workflow.set_entry_point("start_node")
    
    # 从开始节点到三个并行节点
    workflow.add_edge("start_node", "parallel_a")
    workflow.add_edge("start_node", "parallel_b")
    workflow.add_edge("start_node", "parallel_c")
    
    # 从并行节点到合并节点
    workflow.add_edge("parallel_a", "merge_node")
    workflow.add_edge("parallel_b", "merge_node")
    workflow.add_edge("parallel_c", "merge_node")
    
    # 到结束
    workflow.add_edge("merge_node", END)
    
    # 编译并测试
    graph = workflow.compile()
    
    test_input = "并行处理测试"
    logger.info(f"\n🧪 测试输入: {test_input}")
    
    try:
        result = graph.invoke({"user_input": test_input})
        logger.info(f"执行路径: {' → '.join(result['edge_history'])}")
        logger.info(f"最终响应: {result['response']}")
    except Exception as e:
        logger.error(f"错误: {e}")

def demo_edge_parameters():
    """
    演示 add_edge 的详细参数含义
    """
    logger.info("\n" + "="*60)
    logger.info("📚 add_edge 参数详解")
    logger.info("="*60)
    
    logger.info("🔗 add_edge(from_node, to_node)")
    logger.info("")
    logger.info("参数说明:")
    logger.info("• from_node (str): 源节点名称")
    logger.info("  - 必须是已添加的节点名称")
    logger.info("  - 或者特殊常量 START (工作流开始)")
    logger.info("")
    logger.info("• to_node (str): 目标节点名称")
    logger.info("  - 必须是已添加的节点名称")
    logger.info("  - 或者特殊常量 END (工作流结束)")
    logger.info("")
    logger.info("特殊常量:")
    logger.info("• START: 表示工作流的开始点")
    logger.info("• END: 表示工作流的结束点")
    logger.info("")
    logger.info("边类型:")
    logger.info("1. 直接边: 从节点A直接到节点B")
    logger.info("2. 条件边: 根据条件选择下一个节点")
    logger.info("3. 并行边: 从同一节点到多个目标节点")
    logger.info("4. 循环边: 节点可以指向自己或之前的节点")
    logger.info("")
    logger.info("注意事项:")
    logger.info("• 必须先添加节点，再添加边")
    logger.info("• 每个节点必须有至少一个入边和一个出边")
    logger.info("• 工作流必须有明确的开始和结束点")
    logger.info("• 避免创建循环依赖")

# ============================================================================
# 主测试函数
# ============================================================================

def test_edge_types():
    """测试所有边类型"""
    logger.info("🎯 测试 LangGraph 边类型")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 演示各种边类型
    demo_direct_edges()
    demo_conditional_edges()
    demo_parallel_edges()
    demo_edge_parameters()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 边类型演示完成！")
    logger.info("="*60)

if __name__ == "__main__":
    test_edge_types() 