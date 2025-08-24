# -*- coding: utf-8 -*-
"""
LangGraph 上下文最大窗口设置演示

学习要点：
1. 如何设置上下文最大窗口
2. 不同的窗口管理策略
3. 窗口大小对性能的影响
4. 动态窗口调整
5. 最佳实践建议

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
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
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
# 上下文窗口管理器
# ============================================================================

class ContextWindowManager:
    """
    上下文窗口管理器
    
    功能说明：
    1. 管理上下文窗口大小
    2. 提供不同的窗口策略
    3. 动态调整窗口大小
    4. 监控窗口使用情况
    """
    
    def __init__(self, max_window_size: int = 10, strategy: str = "sliding_window"):
        """
        初始化窗口管理器
        
        参数：
            max_window_size: 最大窗口大小
            strategy: 窗口策略 ("sliding_window", "fixed_window", "adaptive_window")
        """
        self.max_window_size = max_window_size
        self.strategy = strategy
        self.current_window_size = 0
        self.window_history = []
        
        logger.info(f"🪟 初始化上下文窗口管理器")
        logger.info(f"  • 最大窗口大小: {max_window_size}")
        logger.info(f"  • 窗口策略: {strategy}")
        
    def apply_window_strategy(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        应用窗口策略
        
        参数：
            messages: 原始消息列表
            
        返回：
            处理后的消息列表
        """
        logger.info(f"🪟 应用窗口策略: {self.strategy}")
        logger.info(f"原始消息数量: {len(messages)}")
        logger.info(f"最大窗口大小: {self.max_window_size}")
        
        if self.strategy == "sliding_window":
            return self._sliding_window_strategy(messages)
        elif self.strategy == "fixed_window":
            return self._fixed_window_strategy(messages)
        elif self.strategy == "adaptive_window":
            return self._adaptive_window_strategy(messages)
        else:
            logger.warning(f"未知策略: {self.strategy}, 使用默认策略")
            return self._sliding_window_strategy(messages)
    
    def _sliding_window_strategy(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        滑动窗口策略 - 保留最近的N条消息
        
        特点：
        - 保留最近的对话内容
        - 丢弃最旧的消息
        - 窗口大小固定
        """
        logger.info("📊 应用滑动窗口策略")
        
        if len(messages) <= self.max_window_size:
            self.current_window_size = len(messages)
            logger.info(f"消息数量在窗口范围内，无需处理")
            return messages
        
        # 保留最近的N条消息
        recent_messages = messages[-self.max_window_size:]
        self.current_window_size = len(recent_messages)
        
        # 记录被丢弃的消息数量
        discarded_count = len(messages) - len(recent_messages)
        logger.info(f"保留最近 {len(recent_messages)} 条消息")
        logger.info(f"丢弃 {discarded_count} 条旧消息")
        
        return recent_messages
    
    def _fixed_window_strategy(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        固定窗口策略 - 严格限制窗口大小
        
        特点：
        - 严格限制窗口大小
        - 超出部分直接截断
        - 适合内存敏感场景
        """
        logger.info("🔒 应用固定窗口策略")
        
        if len(messages) <= self.max_window_size:
            self.current_window_size = len(messages)
            return messages
        
        # 严格截断到最大窗口大小
        fixed_messages = messages[-self.max_window_size:]
        self.current_window_size = len(fixed_messages)
        
        logger.info(f"固定窗口大小: {len(fixed_messages)}")
        logger.info(f"截断 {len(messages) - len(fixed_messages)} 条消息")
        
        return fixed_messages
    
    def _adaptive_window_strategy(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        自适应窗口策略 - 根据消息重要性动态调整
        
        特点：
        - 根据消息重要性动态调整窗口
        - 保留重要消息，压缩次要消息
        - 智能平衡性能和记忆
        """
        logger.info("🧠 应用自适应窗口策略")
        
        if len(messages) <= self.max_window_size:
            self.current_window_size = len(messages)
            return messages
        
        # 分析消息重要性
        important_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                # 系统消息很重要，保留
                important_messages.append(msg)
            elif isinstance(msg, HumanMessage):
                # 用户消息很重要，保留
                important_messages.append(msg)
            elif isinstance(msg, AIMessage):
                # AI消息根据长度判断重要性
                if len(msg.content) > 100:
                    # 长回复很重要，保留
                    important_messages.append(msg)
                else:
                    # 短回复可以压缩
                    compressed_content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                    compressed_msg = AIMessage(content=compressed_content)
                    important_messages.append(compressed_msg)
        
        # 如果重要消息仍然超过窗口大小，使用滑动窗口
        if len(important_messages) > self.max_window_size:
            important_messages = important_messages[-self.max_window_size:]
        
        self.current_window_size = len(important_messages)
        logger.info(f"自适应窗口大小: {len(important_messages)}")
        
        return important_messages
    
    def get_window_stats(self) -> dict:
        """
        获取窗口统计信息
        """
        return {
            "max_window_size": self.max_window_size,
            "current_window_size": self.current_window_size,
            "strategy": self.strategy,
            "utilization_rate": self.current_window_size / self.max_window_size if self.max_window_size > 0 else 0
        }

# ============================================================================
# 聊天机器人节点 - 支持窗口管理
# ============================================================================

def create_window_managed_chatbot(window_manager: ContextWindowManager = None):
    """
    创建支持窗口管理的聊天机器人节点
    """
    
    def window_managed_chatbot(state: State):
        """
        支持窗口管理的聊天机器人节点
        """
        logger.info("🤖 窗口管理聊天机器人正在工作...")
        logger.info(f"使用模型: {MODEL_NAME}")
        
        # 获取当前消息
        messages = state["messages"]
        logger.info(f"当前消息数量: {len(messages)}")
        
        # 应用窗口策略
        if window_manager:
            messages = window_manager.apply_window_strategy(messages)
            logger.info(f"窗口处理后消息数量: {len(messages)}")
            
            # 显示窗口统计信息
            stats = window_manager.get_window_stats()
            logger.info(f"窗口统计: {stats}")
        
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
    
    return window_managed_chatbot

# ============================================================================
# 工作流构建
# ============================================================================

def create_window_managed_workflow(window_manager: ContextWindowManager = None):
    """
    创建支持窗口管理的工作流
    """
    logger.info("\n" + "="*60)
    logger.info("🚀 创建窗口管理工作流")
    logger.info("="*60)
    
    # 创建检查点保存器
    logger.info("💾 创建InMemory检查点保存器...")
    memory = InMemorySaver()
    
    # 构建状态图
    logger.info("🔗 构建状态图...")
    graph_builder = StateGraph(State)
    
    # 添加窗口管理聊天机器人节点
    logger.info("🤖 添加窗口管理聊天机器人节点...")
    chatbot_node = create_window_managed_chatbot(window_manager)
    graph_builder.add_node("chatbot", chatbot_node)
    
    # 设置入口点
    logger.info("🎯 设置入口点...")
    graph_builder.set_entry_point("chatbot")
    
    # 编译工作流
    logger.info("⚙️ 编译工作流...")
    graph = graph_builder.compile(checkpointer=memory)
    logger.info("✅ 窗口管理工作流创建完成！")
    
    return graph

# ============================================================================
# 演示函数
# ============================================================================

def demonstrate_window_size_settings():
    """
    演示不同的窗口大小设置
    
    功能说明：
    1. 展示不同窗口大小的影响
    2. 比较性能和记忆效果
    3. 提供最佳实践建议
    """
    logger.info("\n" + "="*60)
    logger.info("🪟 窗口大小设置演示")
    logger.info("="*60)
    
    # 测试不同的窗口大小
    window_sizes = [3, 5, 10, 15, 20]
    
    for window_size in window_sizes:
        logger.info(f"\n--- 窗口大小: {window_size} ---")
        
        # 创建窗口管理器
        window_manager = ContextWindowManager(
            max_window_size=window_size, 
            strategy="sliding_window"
        )
        
        # 创建工作流
        graph = create_window_managed_workflow(window_manager)
        
        # 配置thread_id
        config = {"configurable": {"thread_id": f"window_size_test_{window_size}"}}
        
        # 进行多轮对话
        test_conversations = [
            "你好，我是小明",
            "今天天气怎么样？",
            "我想学习Python编程",
            "你能推荐一些学习资源吗？",
            "谢谢你的帮助",
            "我们之前聊过什么？",
            "你还记得我的名字吗？",
            "Python有哪些应用？",
            "如何开始学习？",
            "有什么好的教程推荐？"
        ]
        
        logger.info(f"🔄 进行 {len(test_conversations)} 轮对话测试...")
        
        for i, user_input in enumerate(test_conversations, 1):
            logger.info(f"第{i}轮: {user_input}")
            
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
            logger.info(f"📊 窗口大小 {window_size} 最终消息数量: {final_message_count}")
            
            # 显示窗口统计信息
            stats = window_manager.get_window_stats()
            logger.info(f"窗口统计: {stats}")
            
        except Exception as e:
            logger.error(f"状态检查失败: {e}")
    
    logger.info("\n📊 窗口大小对比总结:")
    logger.info("✅ 小窗口 (3-5):")
    logger.info("  • 内存使用最少")
    logger.info("  • 响应速度最快")
    logger.info("  • 记忆能力有限")
    logger.info("  • 适合简单对话")
    
    logger.info("✅ 中等窗口 (10-15):")
    logger.info("  • 平衡性能和记忆")
    logger.info("  • 适合大多数场景")
    logger.info("  • 推荐使用")
    logger.info("  • 支持多轮对话")
    
    logger.info("✅ 大窗口 (20+):")
    logger.info("  • 记忆能力最强")
    logger.info("  • 内存使用较多")
    logger.info("  • 适合复杂对话")
    logger.info("  • 需要更多计算资源")

def demonstrate_window_strategies():
    """
    演示不同的窗口策略
    
    功能说明：
    1. 展示滑动窗口策略
    2. 展示固定窗口策略
    3. 展示自适应窗口策略
    4. 比较不同策略的效果
    """
    logger.info("\n" + "="*60)
    logger.info("🔧 窗口策略演示")
    logger.info("="*60)
    
    # 创建不同的窗口策略
    strategies = {
        "滑动窗口": ContextWindowManager(max_window_size=8, strategy="sliding_window"),
        "固定窗口": ContextWindowManager(max_window_size=8, strategy="fixed_window"),
        "自适应窗口": ContextWindowManager(max_window_size=8, strategy="adaptive_window")
    }
    
    # 测试每种策略
    for strategy_name, window_manager in strategies.items():
        logger.info(f"\n--- {strategy_name} 策略测试 ---")
        
        # 创建工作流
        graph = create_window_managed_workflow(window_manager)
        
        # 配置thread_id
        config = {"configurable": {"thread_id": f"strategy_test_{strategy_name}"}}
        
        # 进行多轮对话测试
        test_conversations = [
            "你好，我是张三",
            "今天天气很好",
            "我想学习机器学习",
            "你能推荐一些书籍吗？",
            "谢谢你的建议",
            "我们之前聊过什么？",
            "你还记得我的名字吗？",
            "机器学习有哪些应用？",
            "深度学习是什么？",
            "如何开始学习？"
        ]
        
        logger.info(f"🔄 进行 {len(test_conversations)} 轮对话测试...")
        
        for i, user_input in enumerate(test_conversations, 1):
            logger.info(f"第{i}轮: {user_input}")
            
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
            logger.info(f"📊 {strategy_name} 最终消息数量: {final_message_count}")
            
            # 显示窗口统计信息
            stats = window_manager.get_window_stats()
            logger.info(f"窗口统计: {stats}")
            
        except Exception as e:
            logger.error(f"状态检查失败: {e}")
    
    logger.info("\n📊 窗口策略对比总结:")
    logger.info("✅ 滑动窗口策略:")
    logger.info("  • 保留最近的N条消息")
    logger.info("  • 简单高效")
    logger.info("  • 适合大多数场景")
    
    logger.info("✅ 固定窗口策略:")
    logger.info("  • 严格限制窗口大小")
    logger.info("  • 内存使用可控")
    logger.info("  • 适合资源受限环境")
    
    logger.info("✅ 自适应窗口策略:")
    logger.info("  • 根据消息重要性调整")
    logger.info("  • 智能平衡性能和记忆")
    logger.info("  • 适合复杂对话场景")

def demonstrate_best_practices():
    """
    演示窗口设置的最佳实践
    
    功能说明：
    1. 提供窗口大小选择建议
    2. 展示性能优化技巧
    3. 说明不同场景的适用策略
    """
    logger.info("\n" + "="*60)
    logger.info("📚 窗口设置最佳实践")
    logger.info("="*60)
    
    logger.info("\n🎯 窗口大小选择建议:")
    logger.info("• 简单问答: 3-5 条消息")
    logger.info("• 一般对话: 10-15 条消息")
    logger.info("• 复杂对话: 20-30 条消息")
    logger.info("• 长期记忆: 50+ 条消息")
    
    logger.info("\n⚡ 性能优化技巧:")
    logger.info("• 使用滑动窗口策略提高效率")
    logger.info("• 定期清理过期消息")
    logger.info("• 监控内存使用情况")
    logger.info("• 根据实际需求调整窗口大小")
    
    logger.info("\n🔧 不同场景的适用策略:")
    logger.info("• 客服系统: 固定窗口 (5-10)")
    logger.info("• 教育助手: 自适应窗口 (15-20)")
    logger.info("• 创意写作: 大窗口 (30-50)")
    logger.info("• 代码助手: 中等窗口 (10-15)")
    
    logger.info("\n⚠️ 注意事项:")
    logger.info("• 窗口过大可能导致响应变慢")
    logger.info("• 窗口过小可能丢失重要上下文")
    logger.info("• 需要根据模型能力调整窗口")
    logger.info("• 定期评估和优化窗口设置")

if __name__ == "__main__":
    # 演示窗口大小设置
    demonstrate_window_size_settings()
    
    # 演示窗口策略
    demonstrate_window_strategies()
    
    # 演示最佳实践
    demonstrate_best_practices() 