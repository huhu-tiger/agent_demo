# -*- coding: utf-8 -*-
"""
LangGraph 工具调用 Command 示例
学习要点：工具返回 Command 更新状态

这种模式的优势：
1. 工具可以直接更新工作流状态，无需额外的状态转换
2. 工具执行结果可以立即反映在工作流中
3. 支持复杂的工具链和状态管理
4. 便于调试和追踪工具执行过程

适用场景：
- 数据库操作工具：更新用户信息、查询数据
- API 调用工具：调用外部服务、获取实时数据
- 文件操作工具：读写文件、处理文档
- 计算工具：执行复杂计算、数据处理

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
from typing import TypedDict, List
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END  # 状态图、开始/结束节点
from langgraph.graph.message import add_messages    # 消息合并器
from langgraph.types import Command                  # Command 对象

import config  # 配置文件

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url  # 设置 API 基础地址
os.environ["OPENAI_API_KEY"] = config.api_key    # 设置 API 密钥
MODEL_NAME = config.model                         # 获取模型名称

# 获取日志器
logger = config.logger  # 用于记录执行过程和调试信息

# ============================================================================
# 工具调用 - 返回 Command 的工具
# ============================================================================

class ToolState(TypedDict):
    """
    工具状态定义
    
    用于演示工具调用和状态更新：
    - 工具执行结果：记录工具的执行状态和结果
    - 状态更新：通过 Command 更新工作流状态
    - 消息历史：使用 add_messages reducer 合并消息
    
    这种模式特别适用于：
    - 数据库操作：更新用户信息、查询数据
    - API 调用：调用外部服务、获取数据
    - 状态管理：维护工作流的全局状态
    """
    user_name: str       # 用户名，由工具更新
    messages: Annotated[List[str], add_messages]  # 消息历史，使用 reducer 合并
    tool_results: List[str]  # 工具执行结果，记录调用了哪些工具

def demo_tool_commands():
    """
    演示工具调用中的 Command 使用
    
    展示如何创建返回 Command 的工具，
    以及如何在工具中更新状态
    
    这种模式的优势：
    1. 工具可以直接更新工作流状态，无需额外的状态转换
    2. 工具执行结果可以立即反映在工作流中
    3. 支持复杂的工具链和状态管理
    4. 便于调试和追踪工具执行过程
    
    适用场景：
    - 数据库操作工具：更新用户信息、查询数据
    - API 调用工具：调用外部服务、获取实时数据
    - 文件操作工具：读写文件、处理文档
    - 计算工具：执行复杂计算、数据处理
    """
    logger.info("\n" + "="*60)
    logger.info("🔄 工具调用 Command 演示")
    logger.info("工具返回 Command 更新状态")
    logger.info("特点：直接状态更新、工具链集成、状态追踪")
    logger.info("="*60)
    
    def update_user_name_tool(new_name: str) -> Command:
        """
        更新用户名的工具
        
        返回 Command 来更新状态
        
        这个工具演示了如何通过 Command 直接更新工作流状态：
        1. 更新 user_name 字段
        2. 添加一条消息到消息历史
        3. 记录工具执行结果
        
        Args:
            new_name: 新的用户名
            
        Returns:
            Command 对象，包含状态更新信息
        """
        logger.info(f"🔧 工具: 更新用户名 -> {new_name}")
        
        return Command(
            update={
                "user_name": new_name,                    # 直接更新用户名
                "messages": [f"用户名已更新为: {new_name}"], # 添加消息到历史
                "tool_results": ["update_user_name"]      # 记录工具执行
            }
        )
    
    def get_user_info_tool() -> Command:
        """
        获取用户信息的工具
        
        返回 Command 来更新状态
        """
        logger.info("🔧 工具: 获取用户信息")
        
        # 模拟获取用户信息
        user_info = "用户信息: 活跃用户，VIP 会员"
        
        return Command(
            update={
                "messages": [f"获取到用户信息: {user_info}"],
                "tool_results": ["get_user_info"]
            }
        )
    
    def tool_execution_node(state: ToolState) -> ToolState:
        """
        工具执行节点
        
        模拟工具调用和状态更新
        
        这个节点演示了如何：
        1. 调用返回 Command 的工具
        2. 手动应用 Command 的状态更新
        3. 处理不同类型的状态字段（列表 vs 标量）
        
        在实际应用中，通常会使用 LangGraph 的 ToolNode 或
        create_react_agent 来自动处理工具调用和状态更新。
        
        Args:
            state: 当前工作流状态
            
        Returns:
            更新后的状态
        """
        logger.info("🔧 工具执行节点: 执行工具调用")
        
        # 模拟工具调用序列
        tools_to_call = [
            ("update_user_name", "Alice"),  # 更新用户名为 Alice
            ("get_user_info", None)         # 获取用户信息
        ]
        
        for tool_name, tool_args in tools_to_call:
            logger.info(f"   🛠️ 调用工具: {tool_name}")
            
            # 根据工具名称调用相应的工具
            if tool_name == "update_user_name":
                command = update_user_name_tool(tool_args)
            elif tool_name == "get_user_info":
                command = get_user_info_tool()
            
            # 手动应用 Command 的更新
            # 在实际应用中，LangGraph 会自动处理这个过程
            for key, value in command["update"].items():
                if key in state:
                    if isinstance(value, list):
                        # 对于列表类型，使用 reducer 合并
                        if key == "messages":
                            state[key] = state[key] + value  # 使用 add_messages reducer
                        else:
                            state[key] = state[key] + value  # 使用 operator.add reducer
                    else:
                        # 对于其他类型，直接更新
                        state[key] = value
        
        return {
            "messages": ["工具执行完成"],      # 添加完成消息
            "tool_results": ["tool_execution"] # 记录节点执行
        }
    
    # 构建工作流
    logger.info("📋 构建工具调用工作流...")
    builder = StateGraph(ToolState)
    
    # 添加节点
    builder.add_node("tool_execution", tool_execution_node)
    
    # 设置边
    builder.add_edge(START, "tool_execution")
    builder.add_edge("tool_execution", END)
    
    # 编译图
    graph = builder.compile()
    logger.info("✅ 工具调用工作流编译完成")
    
    # 执行工作流
    logger.info("\n🚀 执行工具调用工作流...")
    
    try:
        result = graph.invoke({
            "user_name": "",
            "messages": [],
            "tool_results": []
        })
        
        logger.info(f"📊 最终结果: {result}")
        
    except Exception as e:
        logger.error(f"执行工作流时出错: {e}")

# ============================================================================
# 主测试函数
# ============================================================================

def test_tool_commands():
    """
    测试工具调用 Command 功能的主函数
    
    学习要点：
    - 工具可以直接更新工作流状态，无需额外的状态转换
    - 工具执行结果可以立即反映在工作流中
    - 支持复杂的工具链和状态管理
    - 便于调试和追踪工具执行过程
    
    适用场景：
    - 数据库操作工具：更新用户信息、查询数据
    - API 调用工具：调用外部服务、获取实时数据
    - 文件操作工具：读写文件、处理文档
    - 计算工具：执行复杂计算、数据处理
    """
    logger.info("🎯 测试 LangGraph 工具调用 Command 功能")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    logger.info("📚 学习目标：掌握工具返回 Command 更新状态的方式")
    
    # 演示工具调用
    demo_tool_commands()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 工具调用 Command 演示完成！")
    logger.info("📋 总结：工具可以直接更新工作流状态，实现无缝集成")
    logger.info("🔗 相关概念：工具集成、状态管理、Command 对象、reducer")
    logger.info("="*60)

if __name__ == "__main__":
    test_tool_commands() 