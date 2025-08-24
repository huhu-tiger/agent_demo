# -*- coding: utf-8 -*-
"""
LangGraph 上下文最大窗口设置 - 简化示例

学习要点：
1. 如何设置上下文最大窗口
2. 窗口大小对对话的影响
3. 最佳实践建议

作者: AI Assistant
来源: LangGraph 官方教程学习
"""

import os
from typing import Annotated, TypedDict, List
from typing_extensions import TypedDict

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

# LangChain 组件
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

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

class State(TypedDict):
    """
    状态定义 - 使用TypedDict定义状态结构
    """
    messages: Annotated[list, add_messages]

# ============================================================================
# 上下文窗口管理器 - 简化版
# ============================================================================

class SimpleWindowManager:
    """
    简化的上下文窗口管理器
    
    功能说明：
    1. 设置最大窗口大小
    2. 保留最近的N条消息
    3. 丢弃超出窗口的消息
    """
    
    def __init__(self, max_window_size: int = 10):
        """
        初始化窗口管理器
        
        参数：
            max_window_size: 最大窗口大小（保留最近的消息数量）
        """
        self.max_window_size = max_window_size
        logger.info(f"🪟 设置上下文最大窗口: {max_window_size}")
        
    def apply_window(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        应用窗口限制
        
        参数：
            messages: 原始消息列表
            
        返回：
            处理后的消息列表（不超过最大窗口大小）
        """
        logger.info(f"📊 原始消息数量: {len(messages)}")
        logger.info(f"🪟 最大窗口大小: {self.max_window_size}")
        
        # 如果消息数量在窗口范围内，直接返回
        if len(messages) <= self.max_window_size:
            logger.info(f"✅ 消息数量在窗口范围内，无需处理")
            return messages
        
        # 保留最近的N条消息
        recent_messages = messages[-self.max_window_size:]
        discarded_count = len(messages) - len(recent_messages)
        
        logger.info(f"📝 保留最近 {len(recent_messages)} 条消息")
        logger.info(f"🗑️ 丢弃 {discarded_count} 条旧消息")
        
        return recent_messages

# ============================================================================
# 聊天机器人节点 - 支持窗口管理
# ============================================================================

def create_window_chatbot(window_manager: SimpleWindowManager = None):
    """
    创建支持窗口管理的聊天机器人节点
    """
    
    def window_chatbot(state: State):
        """
        支持窗口管理的聊天机器人节点
        """
        logger.info("🤖 窗口管理聊天机器人正在工作...")
        
        # 获取当前消息
        messages = state["messages"]
        logger.info(f"当前消息数量: {len(messages)}")
        
        # 应用窗口限制
        if window_manager:
            messages = window_manager.apply_window(messages)
            logger.info(f"窗口处理后消息数量: {len(messages)}")
        
        # 初始化聊天模型
        llm = ChatOpenAI(
            model=MODEL_NAME,
            openai_api_base=config.base_url,
            openai_api_key=config.api_key,
            temperature=0.7
        )
        
        # 调用模型生成响应
        response = llm.invoke(messages)
        
        logger.info(f"生成响应: {response.content}")
        
        return {"messages": [response]}
    
    return window_chatbot

# ============================================================================
# 工作流构建
# ============================================================================

def create_workflow_with_window(max_window_size: int = 10):
    """
    创建支持窗口管理的工作流
    
    参数：
        max_window_size: 最大窗口大小
    """
    logger.info("\n" + "="*60)
    logger.info(f"🚀 创建工作流 - 最大窗口: {max_window_size}")
    logger.info("="*60)
    
    # 创建窗口管理器
    window_manager = SimpleWindowManager(max_window_size=max_window_size)
    
    # 创建检查点保存器
    memory = InMemorySaver()
    
    # 构建状态图
    graph_builder = StateGraph(State)
    
    # 添加聊天机器人节点
    chatbot_node = create_window_chatbot(window_manager)
    graph_builder.add_node("chatbot", chatbot_node)
    
    # 设置入口点
    graph_builder.set_entry_point("chatbot")
    
    # 编译工作流
    graph = graph_builder.compile(checkpointer=memory)
    logger.info("✅ 工作流创建完成！")
    
    return graph

# ============================================================================
# 演示函数
# ============================================================================

def demonstrate_window_size_impact():
    """
    演示窗口大小对对话的影响
    """
    logger.info("\n" + "="*60)
    logger.info("🪟 窗口大小影响演示")
    logger.info("="*60)
    
    # 测试不同的窗口大小
    window_sizes = [3, 5, 10]
    
    for window_size in window_sizes:
        logger.info(f"\n--- 窗口大小: {window_size} ---")
        
        # 创建工作流
        graph = create_workflow_with_window(window_size)
        
        # 配置thread_id
        config = {"configurable": {"thread_id": f"window_test_{window_size}"}}
        
        # 进行多轮对话
        test_conversations = [
            "你好，我是小明",
            "今天天气怎么样？",
            "我想学习Python编程",
            "你能推荐一些学习资源吗？",
            "谢谢你的帮助",
            "我们之前聊过什么？",
            "你还记得我的名字吗？"
        ]
        
        logger.info(f"🔄 进行 {len(test_conversations)} 轮对话测试...")
        
        for i, user_input in enumerate(test_conversations, 1):
            logger.info(f"\n第{i}轮: {user_input}")
            
            try:
                events = graph.stream(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config,
                    stream_mode="values",
                )
                
                for event in events:
                    last_message = event["messages"][-1]
                    logger.info(f"AI: {last_message.content}")
                    
            except Exception as e:
                logger.error(f"对话失败: {e}")
                continue
        
        # 检查最终状态
        try:
            snapshot = graph.get_state(config)
            final_message_count = len(snapshot.values.get('messages', []))
            logger.info(f"📊 最终消息数量: {final_message_count}")
            
        except Exception as e:
            logger.error(f"状态检查失败: {e}")

def demonstrate_best_practices():
    """
    演示窗口设置的最佳实践
    """
    logger.info("\n" + "="*60)
    logger.info("📚 窗口设置最佳实践")
    logger.info("="*60)
    
    logger.info("\n🎯 如何设置上下文最大窗口:")
    logger.info("1. 创建窗口管理器:")
    logger.info("   window_manager = SimpleWindowManager(max_window_size=10)")
    
    logger.info("\n2. 在聊天机器人中应用:")
    logger.info("   messages = window_manager.apply_window(messages)")
    
    logger.info("\n3. 创建工作流时传入:")
    logger.info("   graph = create_workflow_with_window(max_window_size=10)")
    
    logger.info("\n📊 窗口大小选择建议:")
    logger.info("• 小窗口 (3-5): 简单问答，快速响应")
    logger.info("• 中等窗口 (10-15): 一般对话，平衡性能")
    logger.info("• 大窗口 (20+): 复杂对话，完整记忆")
    
    logger.info("\n⚡ 性能考虑:")
    logger.info("• 窗口越大，响应越慢")
    logger.info("• 窗口越小，记忆越少")
    logger.info("• 需要根据实际需求平衡")
    
    logger.info("\n🔧 实现要点:")
    logger.info("• 使用 messages[-max_window_size:] 保留最近消息")
    logger.info("• 在每次对话前应用窗口限制")
    logger.info("• 监控窗口使用情况")
    logger.info("• 根据模型能力调整窗口大小")

if __name__ == "__main__":
    # 演示窗口大小影响
    demonstrate_window_size_impact()
    
    # 演示最佳实践
    demonstrate_best_practices() 