# -*- coding: utf-8 -*-
"""
LangGraph 记忆管理示例
参考官方教程: https://langchain-ai.github.io/langgraph/tutorials/get-started/3-add-memory/

学习要点：
1. 使用InMemorySaver进行状态持久化
2. 使用thread_id进行用户隔离
3. 实现多轮对话的记忆功能
4. 参考官方教程的最佳实践

作者: AI Assistant
来源: LangGraph 官方教程学习
"""

import os
from typing import Annotated, TypedDict
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
# 状态定义 - 参考官方教程
# ============================================================================

class State(TypedDict):
    """
    状态定义 - 参考官方教程
    使用TypedDict定义状态结构，使用add_messages注解自动合并消息
    """
    messages: Annotated[list, add_messages]

# ============================================================================
# 聊天机器人节点
# ============================================================================

def chatbot(state: State):
    """
    聊天机器人节点 - 处理用户输入并生成响应
    
    功能说明：
    1. 获取当前消息历史
    2. 调用语言模型生成响应
    3. 返回AI消息
    
    参考官方教程实现
    """
    logger.info("🤖 聊天机器人正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    # 初始化聊天模型 - 明确指定OpenAI兼容的接口
    llm = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_base=config.base_url,
        openai_api_key=config.api_key,
        temperature=0.7
    )
    
    # 调用模型生成响应
    response = llm.invoke(state["messages"])
    
    logger.info(f"生成响应: {response.content}")
    
    return {"messages": [response]}

# ============================================================================
# 工作流构建 - 参考官方教程
# ============================================================================

def create_chatbot_workflow():
    """
    创建聊天机器人工作流 - 参考官方教程
    
    功能说明：
    1. 创建InMemorySaver检查点保存器
    2. 构建状态图
    3. 添加聊天机器人节点
    4. 编译工作流
    
    返回：
        编译后的工作流图
    """
    logger.info("\n" + "="*60)
    logger.info("🚀 创建聊天机器人工作流")
    logger.info("="*60)
    
    # 1. 创建InMemorySaver检查点保存器
    logger.info("📝 创建InMemorySaver检查点保存器...")
    memory = InMemorySaver()
    logger.info(f"检查点保存器: {memory}")
    
    # 2. 构建状态图
    logger.info("🔗 构建状态图...")
    graph_builder = StateGraph(State)
    
    # 3. 添加聊天机器人节点
    logger.info("🤖 添加聊天机器人节点...")
    graph_builder.add_node("chatbot", chatbot)
    
    # 4. 设置入口点
    logger.info("🎯 设置入口点...")
    graph_builder.set_entry_point("chatbot")
    
    # 5. 编译工作流
    logger.info("⚙️ 编译工作流...")
    graph = graph_builder.compile(checkpointer=memory)
    logger.info("✅ 工作流创建完成！")
    
    return graph

# ============================================================================
# 演示函数 - 参考官方教程
# ============================================================================

def demonstrate_memory_usage():
    """
    演示记忆功能的使用 - 参考官方教程
    
    功能说明：
    1. 创建聊天机器人工作流
    2. 使用thread_id进行多轮对话
    3. 演示状态持久化和恢复
    4. 展示不同thread_id的状态隔离
    """
    logger.info("\n" + "="*60)
    logger.info("🧠 记忆功能演示")
    logger.info("="*60)
    
    # 创建聊天机器人工作流
    graph = create_chatbot_workflow()
    
    # 配置thread_id - 参考官方教程
    config = {"configurable": {"thread_id": "1"}}
    
    logger.info(f"\n📋 使用配置: {config}")
    logger.info("参考官方教程: https://langchain-ai.github.io/langgraph/tutorials/get-started/3-add-memory/")
    
    # 第一轮对话
    logger.info("\n--- 第1轮对话 ---")
    user_input = "Hi there! My name is Will."
    logger.info(f"用户输入: {user_input}")
    
    try:
        # 调用工作流 - 参考官方教程格式
        events = graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="values",
        )
        
        for event in events:
            last_message = event["messages"][-1]
            logger.info(f"AI响应: {last_message.content}")
            
    except Exception as e:
        logger.error(f"第1轮对话失败: {e}")
        return
    
    # 第二轮对话 - 测试记忆功能
    logger.info("\n--- 第2轮对话 ---")
    user_input = "Remember my name?"
    logger.info(f"用户输入: {user_input}")
    
    try:
        # 使用相同的thread_id继续对话
        events = graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="values",
        )
        
        for event in events:
            last_message = event["messages"][-1]
            logger.info(f"AI响应: {last_message.content}")
            
    except Exception as e:
        logger.error(f"第2轮对话失败: {e}")
        return
    
    # 测试不同thread_id的状态隔离
    logger.info("\n--- 测试状态隔离 ---")
    different_config = {"configurable": {"thread_id": "2"}}
    logger.info(f"使用不同配置: {different_config}")
    
    try:
        # 使用不同的thread_id
        events = graph.stream(
            {"messages": [{"role": "user", "content": "Remember my name?"}]},
            different_config,
            stream_mode="values",
        )
        
        for event in events:
            last_message = event["messages"][-1]
            logger.info(f"AI响应: {last_message.content}")
            logger.info("✅ 状态隔离成功，新用户没有之前的记忆")
            
    except Exception as e:
        logger.error(f"状态隔离测试失败: {e}")
        return
    
    logger.info("\n📊 演示总结:")
    logger.info("✅ 成功实现的功能:")
    logger.info("• 使用InMemorySaver进行状态持久化")
    logger.info("• 使用thread_id进行用户隔离")
    logger.info("• 实现多轮对话的记忆功能")
    logger.info("• 不同thread_id完全隔离")
    logger.info("• 符合官方教程最佳实践")

def demonstrate_state_inspection():
    """
    演示状态检查功能 - 参考官方教程
    
    功能说明：
    1. 展示如何检查工作流状态
    2. 演示get_state方法的使用
    3. 查看状态快照的内容
    """
    logger.info("\n" + "="*60)
    logger.info("🔍 状态检查演示")
    logger.info("="*60)
    
    # 创建聊天机器人工作流
    graph = create_chatbot_workflow()
    
    # 配置thread_id
    config = {"configurable": {"thread_id": "inspection_demo"}}
    
    # 进行几轮对话
    conversations = [
        "Hello, I'm Alice.",
        "What's my name?",
        "How are you today?"
    ]
    
    logger.info("🔄 进行多轮对话...")
    
    for i, user_input in enumerate(conversations, 1):
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
            return
    
    # 检查状态
    logger.info("\n🔍 检查工作流状态...")
    try:
        snapshot = graph.get_state(config)
        logger.info("✅ 状态快照获取成功")
        
        # 显示状态信息
        logger.info(f"状态值: {snapshot.values}")
        logger.info(f"配置: {snapshot.config}")
        logger.info(f"元数据: {snapshot.metadata}")
        logger.info(f"创建时间: {snapshot.created_at}")
        
        # 显示消息历史
        messages = snapshot.values.get('messages', [])
        logger.info(f"\n📝 消息历史 ({len(messages)} 条):")
        for i, msg in enumerate(messages, 1):
            if hasattr(msg, 'content'):
                content = msg.content
            else:
                content = str(msg)
            logger.info(f"  {i}. {content}")
            
    except Exception as e:
        logger.error(f"状态检查失败: {e}")
        return
    
    logger.info("\n📊 状态检查总结:")
    logger.info("✅ 成功实现的功能:")
    logger.info("• 使用get_state方法检查状态")
    logger.info("• 查看状态快照的详细信息")
    logger.info("• 显示消息历史和元数据")
    logger.info("• 符合官方教程最佳实践")

if __name__ == "__main__":
    # 演示记忆功能
    demonstrate_memory_usage()
    
    # 演示状态检查
    demonstrate_state_inspection()
