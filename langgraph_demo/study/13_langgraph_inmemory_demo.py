#!/usr/bin/env python3
"""
LangGraph InMemoryStore 示例
包含语义搜索、添加和删除消息的功能
支持自定义模型配置
"""

import os
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import traceback

from langchain.embeddings import init_embeddings
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

import config
from config import ModelConfig
# 获取日志器
logger = config.logger



class LangGraphMemoryDemo:
    """LangGraph InMemoryStore 演示类"""
    
    def __init__(
        self, 
        model_config: Optional[ModelConfig] = None
    ):
        """
        初始化演示类
        
        Args:
            model_config: 模型配置对象
        """
        self.limit_history = 3
        # 设置默认模型配置
        if model_config is None:
            model_config = ModelConfig()
        
        self.model_config = model_config
        
        # 初始化嵌入模型
        embedding_config = model_config.get_embedding_config()
        if embedding_config:
            # 使用自定义配置初始化嵌入模型
            if model_config.embedding_provider == "openai":
                self.embeddings = init_embeddings(
                    f"openai:{model_config.embedding_model}",
                    **embedding_config
                )
            else:
                # 支持其他提供商
                self.embeddings = init_embeddings(
                    f"{model_config.embedding_provider}:{model_config.embedding_model}",
                    **embedding_config
                )
        else:
            # 使用默认配置
            self.embeddings = init_embeddings(f"{model_config.embedding_provider}:{model_config.embedding_model}")
        
        # 初始化聊天模型
        chat_config = model_config.get_chat_model_config()
        if chat_config:
            # 使用自定义配置初始化聊天模型
            if model_config.model_provider == "openai":
                self.llm = init_chat_model(
                    f"openai:{model_config.model_name}",
                    **chat_config
                )
            else:
                # 支持其他提供商
                self.llm = init_chat_model(
                    f"{model_config.model_provider}:{model_config.model_name}",
                    **chat_config
                )
        else:
            # 使用默认配置
            self.llm = init_chat_model(f"{model_config.model_provider}:{model_config.model_name}")
        
        # 获取嵌入模型的维度
        embedding_dims = model_config.get_embedding_dimensions()
        
        # 创建带有语义搜索的InMemoryStore
        self.store = InMemoryStore(
            index={
                "embed": self.embeddings,
                "dims": embedding_dims,
                "fields": ["text", "content", "summary"]  # 指定要嵌入的字段
            }
        )
        
        # 创建检查点保存器
        self.checkpointer = InMemorySaver()
        
        # 构建图
        self.graph = self._build_graph()
        
        # 用户配置
        self.config = {
            "configurable": {
                "thread_id": "demo_thread",
                "user_id": "demo_user",
            }
        }
    
    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return {
            "chat_model": f"{self.model_config.model_provider}:{self.model_config.model_name}",
            "embedding_model": f"{self.model_config.embedding_provider}:{self.model_config.embedding_model}",
            "chat_base_url": self.model_config.base_url or "默认",
            "embedding_base_url": self.model_config.embedding_base_url or "默认",
            "embedding_dimensions": str(self.model_config.get_embedding_dimensions())
        }
    
    def _build_graph(self):
        """构建LangGraph工作流"""
        
        def chat_with_memory(state, *, store: BaseStore):
            """带有记忆功能的聊天节点"""
            logger.info(f"graph chat_with_memory: {state}")
            user_id = "demo_user"
            namespace = (user_id, "memories")
            
            # 基于用户最后一条消息进行语义搜索
            last_message = state["messages"][-1].content
            logger.info(f"处理用户消息: {last_message}")
            
            items = store.search(
                namespace, 
                query=last_message, 
                limit=self.limit_history
            )
            
            # 构建记忆上下文
            memories = []
            for item in items:
                memory_text = item.value.get("text", item.value.get("content", ""))
                if memory_text:
                    # 添加相似度信息
                    similarity_score = item.score
                    memories.append(f"{memory_text}")
                    logger.info(f"找到记忆: {memory_text} (相似度: {similarity_score:.3f})")
            
            memory_context = ""
            if memories:
                memory_context = f"\n## 用户记忆:\n" + "\n".join(memories)
            logger.info(f"memory_context: {memory_context}")
            
            # 检查是否需要存储新记忆
            if "记住" in last_message or "remember" in last_message.lower():
                # 提取要记住的内容
                memory_content = last_message.replace("记住", "").replace("remember", "").strip()
                if memory_content:
                    memory_id = str(uuid.uuid4())
                    store.put(
                        namespace,
                        memory_id,
                        {
                            "text": memory_content,
                            "timestamp": datetime.now().isoformat(),
                            "type": "user_memory"
                        }
                    )
                    memory_context += f"\n已记住: {memory_content}"
                    logger.info(f"存储新记忆: {memory_content}")
            
            # 构建系统提示
            system_prompt = f"""你是一个有用的AI助手。{memory_context}

请用中文回复用户的问题。如果用户要求记住什么，请确认已经记住。
如果用户询问关于他们自己的信息，请基于记忆中的信息回答。"""
            

            
            try:
                # 调用LLM
                logger.info("开始调用LLM...")
                response = self.llm.invoke(
                    [
                        {"role": "system", "content": system_prompt},
                        *state["messages"]
                    ]
                )
                logger.info(f"系统提示词: {system_prompt}")
                logger.info(f"用户输入: {state['messages']}")
                logger.info(f"LLM调用成功，响应类型: {type(response)}")
                logger.info(f"LLM响应内容: {response.content if hasattr(response, 'content') else response}")
                
                return {"messages": [response]}
                
            except Exception as e:
                logger.error(f"LLM调用失败: {e}")
                logger.error(f"LLM错误详情: {traceback.format_exc()}")
                # 返回错误消息
                error_response = AIMessage(content=f"抱歉，模型调用失败: {str(e)}")
                return {"messages": [error_response]}
        
        def delete_old_messages(state):
            """删除旧消息的节点"""
            messages = state["messages"]
            if len(messages) > self.limit_history + 1:  # 保留最近4条消息
                # 删除最早的消息
                logger.info(f"删除旧消息: {messages[:-(self.limit_history + 1)]}")
                return {"messages": [RemoveMessage(id=m.id) for m in messages[:-(self.limit_history + 1)]]}
            return {}
        
        # 构建图
        builder = StateGraph(MessagesState)
        builder.add_node("chat", chat_with_memory)
        builder.add_node("cleanup", delete_old_messages)
        builder.add_edge(START, "chat")
        builder.add_edge("chat", "cleanup")
        
        return builder.compile(
            checkpointer=self.checkpointer,
            store=self.store
        )
    
    def add_memory(self, content: str, memory_type: str = "general") -> str:
        """
        添加记忆到存储
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            
        Returns:
            记忆ID
        """
        memory_id = str(uuid.uuid4())
        namespace = ("demo_user", "memories")
        
        self.store.put(
            namespace,
            memory_id,
            {
                "text": content,
                "timestamp": datetime.now().isoformat(),
                "type": memory_type
            }
        )
        
        print(f"✅ 已添加记忆: {content}")
        return memory_id
    
    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            
        Returns:
            搜索结果列表
        """
        namespace = ("demo_user", "memories")
        results = self.store.search(namespace, query=query, limit=limit)
        
        memories = []
        for item in results:
            memories.append({
                "id": item.key,
                "content": item.value.get("text", ""),
                "type": item.value.get("type", ""),
                "timestamp": item.value.get("timestamp", ""),
                "score": item.score
            })
        
        return memories
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        删除指定记忆
        
        Args:
            memory_id: 要删除的记忆ID
            
        Returns:
            是否删除成功
        """
        namespace = ("demo_user", "memories")
        
        # 检查记忆是否存在
        existing = self.store.get(namespace, memory_id)
        if existing is None:
            print(f"❌ 记忆 {memory_id} 不存在")
            return False
        
        # 删除记忆（通过存储None来删除）
        self.store.put(namespace, memory_id, None)
        print(f"✅ 已删除记忆: {memory_id}")
        return True
    
    def list_all_memories(self) -> List[Dict[str, Any]]:
        """
        列出所有记忆
        
        Returns:
            所有记忆的列表
        """
        namespace = ("demo_user", "memories")
        # 使用空查询来获取所有记忆
        results = self.store.search(namespace, query="", limit=100)
        memories = []
        for item in results:
            memories.append({
                "id": item.key,
                "content": item.value.get("text", ""),
                "type": item.value.get("type", ""),
                "timestamp": item.value.get("timestamp", ""),
            })
        
        return memories
    
    def chat(self, message: str) -> str:
        """
        与AI助手聊天
        
        Args:
            message: 用户消息
            
        Returns:
            AI回复
        """
        logger.info(f"开始聊天，用户消息: {message}")
        response_content = ""
        event_count = 0
        
        try:
            # for event in self.graph.stream(
            #     {"messages": [HumanMessage(content=message)]},
            #     self.config,
            #     # stream_mode="messages"
            #     stream_mode="values"
            # ):
            result = self.graph.invoke(
                {"messages": [HumanMessage(content=message)]},
                self.config,
            )
            logger.info(f"llm result: {result}")
            response_content = result["messages"][-1].content
                
            return response_content
            
        except Exception as e:
            logger.error(f"聊天过程中出现错误: {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            return f"抱歉，聊天过程中出现错误: {str(e)}"
    
    def clear_all_memories(self):
        """清空所有记忆"""
        namespace = ("demo_user", "memories")
        memories = self.list_all_memories()
        
        for memory in memories:
            self.store.put(namespace, memory["id"], None)
        
        print(f"✅ 已清空所有记忆 ({len(memories)} 条)")


def main():
    """主函数 - 演示InMemoryStore功能"""
    
    print("🚀 LangGraph InMemoryStore 语义搜索演示")
    print("=" * 50)
    
    
    print("\n🔧 模型配置演示...")
    
    # 演示1: 使用默认配置
    print("\n1. 使用默认模型配置:")

    from config import custom_config

    demo_default = LangGraphMemoryDemo(model_config=custom_config)
    model_info = demo_default.get_model_info()
    print(f"   聊天模型: {model_info['chat_model']}")
    print(f"   嵌入模型: {model_info['embedding_model']}")
    print(f"   聊天API地址: {model_info['chat_base_url']}")
    print(f"   嵌入API地址: {model_info['embedding_base_url']}")
    print(f"   嵌入维度: {model_info['embedding_dimensions']}")
    
    # 使用默认配置进行功能演示
    demo = demo_default
    
    print("\n📝 4. 添加一些示例记忆...")
    demo.add_memory("我喜欢吃披萨", "preference")
    demo.add_memory("我是一个程序员", "personal")
    demo.add_memory("我住在北京", "personal")
    demo.add_memory("我喜欢Python编程语言", "preference")
    demo.add_memory("我有一只叫小白的猫", "personal")
    
    print("\n🔍 5. 语义搜索演示...")
    
    # 搜索食物偏好
    print("\n搜索食物偏好:")
    food_memories = demo.search_memories("食物 喜欢", limit=3)
    for i, memory in enumerate(food_memories, 1):
        print(f"  {i}. {memory['content']}")
        print(f"     相似度: {memory['score']:.4f}")
        print(f"     类型: {memory['type']}")
        print(f"     时间: {memory['timestamp']}")
    
    # 搜索个人信息
    print("\n搜索个人信息:")
    personal_memories = demo.search_memories("个人信息 职业", limit=3)
    for i, memory in enumerate(personal_memories, 1):
        print(f"  {i}. {memory['content']}")
        print(f"     相似度: {memory['score']:.4f}")
        print(f"     类型: {memory['type']}")
        print(f"     时间: {memory['timestamp']}")
    
    # 测试不同相似度阈值
    print("\n相似度阈值测试:")
    test_query = "编程"
    all_results = demo.search_memories(test_query, limit=10)
    
    thresholds = [0.5]
    for threshold in thresholds:
        filtered_results = [m for m in all_results if m['score'] >= threshold]
        print(f"  阈值 {threshold:.1f}: {len(filtered_results)} 条结果")
        for memory in filtered_results[:2]:  # 只显示前2条
            print(f"    - {memory['content']} (相似度: {memory['score']:.4f})")
    
    print("\n💬 6. ========================聊天演示===========================")
    
    # 测试记忆功能
    print("\n用户: 记住我喜欢吃火锅")
    response = demo.chat("记住我喜欢吃火锅")
    logger.info(f"AI: {response}")
    
    print("\n用户: 我喜欢吃什么？")
    response = demo.chat("我喜欢吃什么？")
    logger.info(f"AI: {response}")
    
    print("\n用户: 我的职业是什么？")
    response = demo.chat("我的职业是什么？")
    logger.info(f"AI: {response}")
    
    print("\n📋 7. 列出所有记忆...")
    all_memories = demo.list_all_memories()
    for i, memory in enumerate(all_memories, 1):
        print(f"  {i}. {memory['content']}")
        print(f"     类型: {memory['type']}")
        print(f"     时间: {memory['timestamp']}")
        print(f"     相似度: {memory['score']}")  # 空搜索项，相似度为None
        print()
    
    print("\n🗑️ 8. 删除记忆演示...")
    if all_memories:
        # 删除第一条记忆
        first_memory = all_memories[0]
        demo.delete_memory(first_memory["id"])
        
        print("\n删除后的记忆列表:")
        remaining_memories = demo.list_all_memories()
        for i, memory in enumerate(remaining_memories, 1):
            print(f"  {i}. {memory['content']}")
            print(f"     类型: {memory['type']}")
            print(f"     时间: {memory['timestamp']}")
            print(f"     相似度: {memory['score']}")  # 空搜索项，相似度为None
            print()
    
    print("\n🧹 9. 清空所有记忆...")
    demo.clear_all_memories()
    
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    main()
