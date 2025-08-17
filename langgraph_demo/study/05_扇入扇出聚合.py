# -*- coding: utf-8 -*-
"""
LangGraph 扇入扇出示例
学习要点：扇入和扇出模式的创建和使用

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
    current_node:  Annotated[List[str], operator.add] # 使用 Annotated 处理多个值
    edge_history: Annotated[List[str], operator.add]
    response: Annotated[List[str], operator.add]
    parallel_results: Annotated[List[str], operator.add]

# ============================================================================
# 节点定义
# ============================================================================

def node_a(state: EdgeDemoState) -> EdgeDemoState:
    """节点A"""
    logger.info("🅰️ 节点A正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    edge_history = ["A"]
    
    response = f"节点A处理: {user_input}"
    
    return {
        "current_node": ["A"],
        "edge_history": edge_history,
        "response": [response],
        "messages": [AIMessage(content=response)]
    }

def node_d(state: EdgeDemoState) -> EdgeDemoState:
    """节点D - 合并节点"""
    logger.info("🅳 节点D正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    edge_history = ["D"]
    
    # 收集并行处理的结果
    parallel_results = state.get("parallel_results", [])
    if parallel_results:
        response = f"节点D合并结果: {user_input} + {' + '.join(parallel_results)}"
    else:
        response = f"节点D处理: {user_input}"
    logger.info(f"节点D合并结果: {response}")
    return {
        "current_node": ["D"],
        "edge_history": edge_history,
        "response": [response],
        "messages": [AIMessage(content=response)]
    }

def final_node(state: EdgeDemoState) -> EdgeDemoState:
    """最终节点"""
    logger.info("🏁 最终节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    edge_history = ["Final"]
    
    response = f"最终节点处理: {user_input}"
    
    return {
        "current_node": ["Final"],
        "edge_history": edge_history,
        "response": [response],
        "messages": [AIMessage(content=response)]
    }

def parallel_worker_1(state: EdgeDemoState) -> EdgeDemoState:
    """并行工作节点1"""
    logger.info("🔧 并行工作节点1正在工作...")
    
    user_input = state["user_input"]
    edge_history = ["Worker1"]
    
    # 只添加自己的结果
    parallel_results = ["Worker1结果"]
    
    response = f"Worker1 处理: {user_input}"
    logger.info(f"Worker1 结果: {response}")
    return {
        "current_node": ["Worker1"],
        "edge_history": edge_history,
        "parallel_results": parallel_results,
        "response": [response],
        "messages": [AIMessage(content=response)]
    }

def parallel_worker_2(state: EdgeDemoState) -> EdgeDemoState:
    """并行工作节点2"""
    logger.info("🔧 并行工作节点2正在工作...")
    
    user_input = state["user_input"]
    edge_history = ["Worker2"]
    
    # 只添加自己的结果
    parallel_results = ["Worker2结果"]
    
    response = f"Worker2 处理: {user_input}"
    logger.info(f"Worker2 结果: {response}")
    return {
        "current_node": ["Worker2"],
        "edge_history": edge_history,
        "parallel_results": parallel_results,
        "response": [response],
        "messages": [AIMessage(content=response)]
    }

def parallel_worker_3(state: EdgeDemoState) -> EdgeDemoState:
    """并行工作节点3"""
    logger.info("🔧 并行工作节点3正在工作...")
    
    user_input = state["user_input"]
    edge_history = ["Worker3"]
    
    # 只添加自己的结果
    parallel_results = ["Worker3结果"]
    response = f"Worker3 处理: {user_input}"
    logger.info(f"Worker3 结果: {response}")

    return {
        "current_node": ["Worker3"],
        "edge_history": edge_history,
        "parallel_results": parallel_results,
        "response": [response],
        "messages": [AIMessage(content=response)]
    }

def parallel_worker_2_1(state: EdgeDemoState) -> EdgeDemoState:
    """并行工作节点2的分支节点"""
    logger.info("🔧 并行工作节点2_1正在工作...")
    
    user_input = state["user_input"]
    edge_history = ["Worker2_1"]
    
    # 只添加自己的结果，不继承父节点的结果
    parallel_results = ["Worker2_1结果"]
    
    response = f"Worker2_1 处理: {user_input}"
    logger.info(f"Worker2_1 结果: {response}")

    return {
        "current_node": ["Worker2_1"],
        "edge_history": edge_history,
        "parallel_results": parallel_results,
        "response": [response],
        "messages": [AIMessage(content=response)]
    }

# ============================================================================
# 扇入扇出组合演示
# ============================================================================

def demo_fan_in_fan_out():
    """
    演示扇入扇出组合模式
    
    先扇出并行处理，再扇入合并结果
    """
    logger.info("\n" + "="*60)
    logger.info("🔄⚡ 扇入扇出组合演示")
    logger.info("先扇出并行处理，再扇入合并结果")
    logger.info("="*60)
    
    # 创建状态图
    workflow = StateGraph(EdgeDemoState)
    
    # 添加节点
    workflow.add_node("start_node", node_a)
    workflow.add_node("parallel_1", parallel_worker_1)
    workflow.add_node("parallel_2", parallel_worker_2)
    workflow.add_node("parallel_2_1", parallel_worker_2_1) 
    workflow.add_node("parallel_3", parallel_worker_3)
    workflow.add_node("merge_node", node_d)
    workflow.add_node("final_node", final_node)
    
    # 组合模式示例
    logger.info("📝 扇入扇出组合:")
    logger.info("1. 扇出: start_node → parallel_1, parallel_2, parallel_3")
    logger.info("2. 扇入: parallel_1, parallel_2, parallel_3 → merge_node")
    logger.info("3. 继续: merge_node → final_node")
    
    workflow.set_entry_point("start_node")
    
    # 扇出阶段
    workflow.add_edge("start_node", "parallel_1")
    workflow.add_edge("start_node", "parallel_2")
    workflow.add_edge("start_node", "parallel_3")
    
    workflow.add_edge("parallel_2", "parallel_2_1") # parallel_2的分支节点
    # 扇入阶段
    workflow.add_edge(["parallel_1", "parallel_3", "parallel_2_1"], "merge_node") # 保证所有并行节点都执行完，再合并
    
    # 继续处理
    workflow.add_edge("merge_node", "final_node")
    workflow.add_edge("final_node", END)
    
    # 编译并测试
    graph = workflow.compile()
        # 可视化工作流程图
    from show_graph import show_workflow_graph
    
    # 生成工作流图的 PNG 格式，用于文档和演示
    # 可以根据需要选择不同的格式：
    # - formats=['md']: 只生成 Markdown 文件
    # - formats=['mmd']: 只生成 Mermaid 代码文件  
    # - formats=['png']: 只生成 PNG 图片
    # - formats=['png', 'md', 'mmd']: 生成多种格式
    show_workflow_graph(graph, "扇入扇出工作流", logger, "扇入扇出模式演示", formats=['png'])
    test_input = "扇入扇出组合测试"
    logger.info(f"\n🧪 测试输入: {test_input}")
    
    try:
        result = graph.invoke({"user_input": test_input}, config={"configurable": {"thread_id": "foo"},"recursion_limit": 100})
        logger.info(f"执行路径: {' → '.join(result['edge_history'])}")
        logger.info(f"并行结果: {result.get('parallel_results', [])}")
        logger.info(f"最终响应: {' | '.join(result['response'])}")
    except Exception as e:
        logger.error(f"错误: {e}")

# ============================================================================
# 主测试函数
# ============================================================================

def test_fan_in_fan_out():
    """测试扇入扇出模式"""
    logger.info("🎯 测试 LangGraph 扇入扇出模式")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 演示扇入扇出组合模式
    demo_fan_in_fan_out()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 扇入扇出演示完成！")
    logger.info("="*60)

if __name__ == "__main__":
    test_fan_in_fan_out() 