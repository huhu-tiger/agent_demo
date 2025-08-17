# -*- coding: utf-8 -*-
"""
LangGraph 子图导航 Command 示例
学习要点：Command.PARENT 跨层级跳转

这种模式的优势：
1. 模块化设计：子图可以独立开发和测试
2. 复用性：子图可以在多个父图中使用
3. 复杂控制流：支持跨层级的动态路由
4. 状态隔离：子图和父图可以有独立的状态管理

适用场景：
- 复杂工作流：将大工作流拆分为多个子工作流
- 微服务架构：每个子图对应一个微服务
- 插件系统：子图作为可插拔的功能模块
- 多层级处理：需要跨层级控制流的场景

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import random
import operator
from typing import TypedDict, Literal
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END  # 状态图、开始/结束节点
from langgraph.types import Command                  # Command 对象

import config  # 配置文件

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url  # 设置 API 基础地址
os.environ["OPENAI_API_KEY"] = config.api_key    # 设置 API 密钥
MODEL_NAME = config.model                         # 获取模型名称

# 获取日志器
logger = config.logger  # 用于记录执行过程和调试信息

# ============================================================================
# 子图导航 - Command.PARENT 的使用
# ============================================================================

class SubgraphState(TypedDict):
    """
    子图状态定义
    
    用于子图内部的状态管理：
    - subgraph_data: 子图处理的数据
    """
    subgraph_data: str  # 子图处理的数据，会被传递给父图

class ParentState(TypedDict):
    """
    主图状态定义
    
    用于主图的状态管理：
    - parent_data: 使用 operator.add reducer 合并数据
    - current_flow: 记录当前执行流程
    """
    parent_data: Annotated[str, operator.add]  # 使用 reducer 合并字符串
    current_flow: str                          # 记录当前执行流程

def demo_subgraph_navigation():
    """
    演示子图导航中的 Command 使用
    
    展示如何使用 Command.PARENT 在子图中
    跳转到父图的节点
    
    这种模式的优势：
    1. 模块化设计：子图可以独立开发和测试
    2. 复用性：子图可以在多个父图中使用
    3. 复杂控制流：支持跨层级的动态路由
    4. 状态隔离：子图和父图可以有独立的状态管理
    
    适用场景：
    - 复杂工作流：将大工作流拆分为多个子工作流
    - 微服务架构：每个子图对应一个微服务
    - 插件系统：子图作为可插拔的功能模块
    - 多层级处理：需要跨层级控制流的场景
    """
    logger.info("\n" + "="*60)
    logger.info("🔄 子图导航 Command 演示")
    logger.info("Command.PARENT 跳转到父图")
    logger.info("特点：跨层级跳转、模块化设计、状态隔离")
    logger.info("="*60)
    def parent_node_a(state: ParentState) -> ParentState:
        """
        父图节点 A
        
        主图的第一个节点，负责初始化处理
        """
        logger.info("🔧 父图节点 A: 开始处理")
        return {
            "parent_data": "a",
            "current_flow": "parent_node_a"
        }
    
    def parent_node_b(state: ParentState) -> ParentState:
        """
        父图节点 B
        
        处理分支 B 的逻辑
        """
        logger.info("🔧 父图节点 B: 处理分支 B")
        logger.info(f"   📊 当前数据: {state.get('parent_data', '')}")
        return {
            "parent_data": "b",
            "current_flow": "parent_node_b"
        }
    
    def parent_node_c(state: ParentState) -> ParentState:
        """
        父图节点 C
        
        处理分支 C 的逻辑
        """
        logger.info("🔧 父图节点 C: 处理分支 C")
        logger.info(f"   📊 当前数据: {state.get('parent_data', '')}")
        return {
            "parent_data": "c",
            "current_flow": "parent_node_c"
        }
    def subgraph_node(state: SubgraphState) -> Command[Literal["parent_node_b", "parent_node_c"]]:
        """
        子图节点
        
        使用 Command.PARENT 跳转到父图的节点
        
        这个节点演示了子图如何跳转到父图的节点：
        1. 处理子图内部逻辑
        2. 使用 Command.PARENT 跳转到父图的指定节点
        3. 同时更新子图状态
        
        Command.PARENT 的作用：
        - 告诉 LangGraph 跳转到父图（而不是当前图）
        - 支持跨层级的控制流
        - 保持状态的一致性
        
        Args:
            state: 子图状态
            
        Returns:
            Command 对象，指定跳转到父图的哪个节点
        """
        logger.info("🔧 子图节点: 准备跳转到父图")
        
        # 随机选择父图中的目标节点
        # 这模拟了子图根据处理结果动态选择父图路径
        target = random.choice(["parent_node_b", "parent_node_c"])
        logger.info(f"   🎯 ！！！！选择目标: {target}")
        
        return Command(
            update={"subgraph_data": "子图处理完成"},  # 更新子图状态
            goto=target,                                # 指定父图中的目标节点
            graph=Command.PARENT                        # 跳转到父图（关键参数）
        )
    
    # 构建子图
    logger.info("📋 构建子图...")
    subgraph_builder = StateGraph(SubgraphState)
    subgraph_builder.add_node("subgraph_node", subgraph_node)
    subgraph_builder.add_edge(START, "subgraph_node")
    
    # 添加出口节点 - 这是关键！
    # 子图需要知道它可以跳转到哪些父图节点
    # 这些函数在子图中只是声明，不会真正执行
    def exit_to_parent_b(state: SubgraphState) -> SubgraphState:
        """出口节点：跳转到父图的 parent_node_b"""
        # 这个函数在子图中永远不会被调用
        # 它只是告诉编译器"这个节点存在"
        return state
    
    def exit_to_parent_c(state: SubgraphState) -> SubgraphState:
        """出口节点：跳转到父图的 parent_node_c"""
        # 这个函数在子图中永远不会被调用
        # 它只是告诉编译器"这个节点存在"
        return state
    
    subgraph_builder.add_node("parent_node_b", exit_to_parent_b)  # 出口节点  # 简洁写法（推荐）lambda x: x

    subgraph_builder.add_node("parent_node_c", exit_to_parent_c)  # 出口节点
    
    subgraph = subgraph_builder.compile()
    

    
    # 构建主图
    logger.info("📋 构建主图...")
    parent_builder = StateGraph(ParentState)
    
    # 添加节点
    parent_builder.add_node("parent_node_a", parent_node_a)
    parent_builder.add_node("subgraph", subgraph)
    parent_builder.add_node("parent_node_b", parent_node_b)
    parent_builder.add_node("parent_node_c", parent_node_c)
    
    # 设置边
    parent_builder.add_edge(START, "parent_node_a")
    parent_builder.add_edge("parent_node_a", "subgraph")
    parent_builder.add_edge("parent_node_b", END)
    parent_builder.add_edge("parent_node_c", END)
    
    # 编译主图
    parent_graph = parent_builder.compile()
    # todo 可视化 
    from show_graph import show_workflow_graph
    show_workflow_graph(parent_graph, "10_子图导航工作流",logger)
    logger.info("✅ 子图导航工作流编译完成")
    
    # 执行工作流
    logger.info("\n🚀 执行子图导航工作流...")
    
    try:
        # 执行多次以观察不同的随机结果
        for i in range(3):
            logger.info(f"\n--- 第 {i+1} 次执行 ---")
            result = parent_graph.invoke({
                "parent_data": "",
                "current_flow": ""
            })
            logger.info(f"📊 最终结果: {result}")
            
    except Exception as e:
        logger.error(f"执行工作流时出错: {e}")

# ============================================================================
# 主测试函数
# ============================================================================

def test_subgraph_navigation():
    """
    测试子图导航 Command 功能的主函数
    
    学习要点：
    - 使用 Command.PARENT 在子图中跳转到父图的节点
    - 支持跨层级的动态路由
    - 模块化设计和状态隔离
    - 复杂工作流的组织
    
    适用场景：
    - 复杂工作流：将大工作流拆分为多个子工作流
    - 微服务架构：每个子图对应一个微服务
    - 插件系统：子图作为可插拔的功能模块
    - 多层级处理：需要跨层级控制流的场景
    """
    logger.info("🎯 测试 LangGraph 子图导航 Command 功能")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    logger.info("📚 学习目标：掌握 Command.PARENT 跨层级跳转的方式")
    
    # 演示子图导航
    demo_subgraph_navigation()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 子图导航 Command 演示完成！")
    logger.info("📋 总结：Command.PARENT 实现了跨层级的动态路由")
    logger.info("🔗 相关概念：子图、父图、模块化设计、状态隔离、跨层级控制")
    logger.info("="*60)

if __name__ == "__main__":
    test_subgraph_navigation() 