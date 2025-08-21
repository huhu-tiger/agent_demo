#!/usr/bin/env python3
"""
简化版 LangMem 示例
展示LangMem的核心功能：记忆管理、搜索和对话
支持自定义模型配置
"""

import os
import sys
from typing import Optional, Dict, Any

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain.embeddings import init_embeddings
from langchain.chat_models import init_chat_model
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langmem import create_manage_memory_tool, create_search_memory_tool

import config
from config import ModelConfig, custom_config
from config import logger

class LangMemDemo:
    """LangMem演示类"""
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """
        初始化LangMem演示
        
        Args:
            model_config: 模型配置对象
        """
        try:
            # 设置默认模型配置
            if model_config is None:
                model_config = custom_config
            
            self.model_config = model_config
            logger.info(f"初始化LangMem演示，使用模型配置: {model_config.model_provider}:{model_config.model_name}")
            
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
            
            logger.info(f"嵌入模型初始化成功: {model_config.embedding_provider}:{model_config.embedding_model}")
            
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
            
            logger.info(f"聊天模型初始化成功: {model_config.model_provider}:{model_config.model_name}")
            
            # 获取嵌入模型的维度
            embedding_dims = model_config.get_embedding_dimensions()
            logger.info(f"嵌入维度: {embedding_dims}")
            
            # 设置内存存储
            self.store = InMemoryStore(
                index={
                    "dims": embedding_dims,
                    "embed": self.embeddings,
                }
            )
            
            # 创建内存工具 - 使用通用命名空间，支持跨线程搜索
            self.memory_tools = [
                create_manage_memory_tool(namespace=("memories","{org_id}","{user_id}"), store=self.store),
                create_search_memory_tool(namespace=("memories","{org_id}","{user_id}"), store=self.store),
            ]
            
            # 创建带内存的智能体
            self.agent = create_react_agent(
                self.llm,  # 使用已初始化的聊天模型对象
                tools=self.memory_tools, 
                store=self.store, 
                # checkpointer=InMemorySaver()
            )
            
            # 设置默认配置
            # self.default_config = {"configurable": {"thread_id": "default"}}
            
            logger.info("智能体创建成功")
            
            print(f"✅ LangMem演示初始化完成")
            print(f"   聊天模型: {model_config.model_provider}:{model_config.model_name}")
            print(f"   嵌入模型: {model_config.embedding_provider}:{model_config.embedding_model}")
            print(f"   嵌入维度: {embedding_dims}")
            print(f"   存储: InMemoryStore")
            print(f"   命名空间: ('memories',)")
            
        except Exception as e:
            logger.error(f"LangMem演示初始化失败: {e}")
            raise Exception(f"初始化失败: {e}")
    
    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return {
            "chat_model": f"{self.model_config.model_provider}:{self.model_config.model_name}",
            "embedding_model": f"{self.model_config.embedding_provider}:{self.model_config.embedding_model}",
            "chat_base_url": self.model_config.base_url or "默认",
            "embedding_base_url": self.model_config.embedding_base_url or "默认",
            "embedding_dimensions": str(self.model_config.get_embedding_dimensions())
        }
    
    def add_memory(self, content: str, memory_type: str = "general", org_id: str = "acme", user_id: str = "alice") -> str:
        """
        添加记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            thread_id: 线程ID，用于区分不同用户的记忆
            
        Returns:
            添加结果
        """
        try:
            logger.info(f"添加记忆: {content}, 线程: {org_id}, {user_id}")
            # 使用智能体添加记忆，使用线程特定的配置
            config = {"configurable": {"org_id": org_id, "user_id": user_id}}
            response = self.agent.invoke({
                "messages": [{"role": "user", "content": f"记住这个信息: {content}"}]
            }, config=config)
            result = response["messages"][-1].content
            logger.info(f"记忆添加成功: {result}")
            return result
        except Exception as e:
            error_msg = f"添加记忆失败: {e}"
            logger.error(error_msg)
            return error_msg
    
    def search_memories(self, query: str, limit: int = 5, org_id: str = "acme", user_id: str = "alice") -> list:
        """
        搜索记忆
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            thread_id: 线程ID，用于搜索特定线程的记忆
            
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"开始搜索记忆: {query}, 限制: {limit}, 线程: {org_id}, {user_id}")
            
            # 首先搜索所有记忆
            all_results = self.store.search(("memories",org_id,user_id), query=query, limit=limit*2)
            logger.info(f"搜索到 {len(all_results)} 条原始结果")
            
            # 然后按线程ID过滤
            memories = []
            for item in all_results:
                # 检查命名空间是否匹配线程ID
                if len(item.namespace) > 1 and item.namespace[1] == org_id and item.namespace[2] == user_id:
                    memories.append({
                        "id": item.key,
                        "content": item.value.get("content", ""),
                        "created_at": item.created_at,
                        "updated_at": item.updated_at,
                        "score": item.score,
                        "org_id": org_id,
                        "user_id": user_id
                    })
                    logger.info(f"找到匹配的记忆: {item.value.get('content', '')}")
            
            logger.info(f"在线程 {org_id}, {user_id} 中搜索到 {len(memories)} 条记忆")
            return memories
        except Exception as e:
            error_msg = f"搜索记忆失败: {e}"
            logger.error(error_msg)
            return []
    
    def list_all_memories(self, org_id: str = "acme", user_id: str ="") -> list:
        """
        列出所有记忆
        
        Args:
            thread_id: 线程ID，用于列出特定线程的记忆
            
        Returns:
            所有记忆列表
        """
        try:
            logger.info(f"列出线程 {org_id}, {user_id} 的所有记忆")
            if user_id:
                # 搜索所有记忆
                all_results = self.store.search(("memories",org_id,user_id), query="", limit=1000)
            else:
                # 搜索所有记忆
                all_results = self.store.search(("memories",org_id), query="", limit=1000)
            logger.info(f"总共有 {len(all_results)} 条记忆")
            
            # 按线程ID过滤
            memories = []
            for item in all_results:
                if len(item.namespace) > 1 and item.namespace[1] == org_id and item.namespace[2] == user_id:
                    memories.append({
                        "id": item.key,
                        "content": item.value.get("content", ""),
                        "created_at": item.created_at,
                        "updated_at": item.updated_at,
                        "org_id": org_id,
                        "user_id": user_id
                    })
                    logger.info(f"线程 {org_id}, {user_id} 的记忆: {item.value.get('content', '')}")
            
            logger.info(f"线程 {org_id}, {user_id} 总共有 {len(memories)} 条记忆")
            return memories
        except Exception as e:
            error_msg = f"列出记忆失败: {e}"
            logger.error(error_msg)
            return []
    
    def search_across_all_threads(self, query: str, limit: int = 10) -> list:
        """
        跨所有线程搜索记忆
        
        Args:
            query: 搜索查询
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"跨所有线程搜索记忆: {query}")
            # 使用通用命名空间搜索所有记忆
            results = self.store.search(("memories",), query=query, limit=limit)
            
            memories = []
            for item in results:
                # 从命名空间中提取线程ID
                thread_id = item.namespace[1] if len(item.namespace) > 1 else "unknown"
                memories.append({
                    "id": item.key,
                    "content": item.value.get("content", ""),
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "score": item.score,
                    "thread_id": thread_id
                })
            
            logger.info(f"跨所有线程搜索到 {len(memories)} 条记忆")
            return memories
        except Exception as e:
            error_msg = f"跨线程搜索记忆失败: {e}"
            logger.error(error_msg)
            return []
    
    def get_all_thread_ids(self) -> list:
        """
        获取所有线程ID
        
        Returns:
            线程ID列表
        """
        try:
            logger.info("获取所有线程ID")
            # 搜索所有记忆，然后提取唯一的线程ID
            all_results = self.store.search(("memories",), query="", limit=1000)
            
            thread_ids = set()
            for item in all_results:
                if len(item.namespace) > 1:
                    thread_ids.add(item.namespace[1])
            
            thread_ids_list = sorted(list(thread_ids))
            logger.info(f"找到 {len(thread_ids_list)} 个线程: {thread_ids_list}")
            return thread_ids_list
        except Exception as e:
            error_msg = f"获取线程ID失败: {e}"
            logger.error(error_msg)
            return []
    
    def chat_with_memory(self, message: str, org_id: str = "acme", user_id: str = "alice") -> str:
        """
        与智能体对话（带记忆）
        
        Args:
            message: 用户消息
            org_id: 组织ID
            user_id: 用户ID
            
        Returns:
            智能体回复
        """
        try:
            logger.info(f"开始对话，线程: {org_id}, {user_id}, 消息: {message}")
            
            # 打印请求模型的消息
            print(f"\n🤖 发送给模型的消息:")
            print(f"   组织ID: {org_id}")
            print(f"   用户ID: {user_id}")
            print(f"   用户原始消息: {message}")
            
            # 创建线程特定的配置
            config = {"configurable": {"org_id": org_id, "user_id": user_id}}
            
            # 获取当前对话的完整消息历史
            response = self.agent.invoke({
                "messages": [{"role": "user", "content": message}]
            }, config=config)
            
            # 打印实际发送给模型的完整消息
            print(f"\n📤 实际发送给模型的完整消息:")
            if "messages" in response:
                for i, msg in enumerate(response["messages"]):
                    print(f"   消息 {i+1},message:{msg}")
                    # print(f"     角色: {msg.role}")
                    # print(f"     内容: {msg.content}")
                    # if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    #     print(f"     工具调用: {msg.tool_calls}")
                    # print()
            
            result = response["messages"][-1].content
            logger.info(f"对话完成: {result}")
            
            return result
        except Exception as e:
            error_msg = f"对话失败: {e}"
            logger.error(error_msg)
            return error_msg

    def debug_all_memories(self) -> list:
        """
        调试方法：查看所有存储的记忆
        
        Returns:
            所有记忆的详细信息
        """
        try:
            logger.info("调试：查看所有存储的记忆")
            all_results = self.store.search(("memories",), query="", limit=1000)
            
            debug_info = []
            for item in all_results:
                debug_info.append({
                    "id": item.key,
                    "namespace": item.namespace,
                    "content": item.value.get("content", ""),
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "score": item.score
                })
                logger.info(f"记忆: {item.value.get('content', '')} | 命名空间: {item.namespace}")
            
            logger.info(f"总共找到 {len(debug_info)} 条记忆")
            return debug_info
        except Exception as e:
            error_msg = f"调试记忆失败: {e}"
            logger.error(error_msg)
            return []
    
    def debug_store_info(self):
        """调试Store信息"""
        try:
            logger.info("调试Store信息")
            logger.info(f"Store类型: {type(self.store)}")
            logger.info(f"Store配置: {self.store.index if hasattr(self.store, 'index') else 'N/A'}")
            
            # 尝试获取所有记忆
            all_results = self.store.search(("memories",), query="", limit=10)
            logger.info(f"Store中总共有 {len(all_results)} 条记忆")
            
            for i, item in enumerate(all_results, 1):
                logger.info(f"记忆 {i}: {item.value.get('content', '')} | 命名空间: {item.namespace}")
                
        except Exception as e:
            logger.error(f"调试Store信息失败: {e}")

    def debug_agent_invoke(self, message: str, org_id: str = "acme", user_id: str = "alice"):
        """
        调试智能体调用过程，显示详细的工具调用信息
        
        Args:
            message: 用户消息
            org_id: 组织ID
            user_id: 用户ID
        """
        try:
            print(f"\n🔍 调试智能体调用过程:")
            print(f"   组织ID: {org_id}")
            print(f"   用户ID: {user_id}")
            print(f"   用户消息: {message}")
            
            # 创建线程特定的配置
            config = {"configurable": {"org_id": org_id, "user_id": user_id}}
            
            # 使用stream模式来查看详细的调用过程
            print(f"\n📤 开始调用智能体...")
            for chunk in self.agent.stream({
                "messages": [{"role": "user", "content": message}]
            }, config=config):
                print(f"   步骤: {type(chunk).__name__}")
                
                if hasattr(chunk, 'messages') and chunk.messages:
                    for msg in chunk.messages:
                        print(f"     消息: {msg.role} - {msg.content[:100]}...")
                
                if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    for tool_call in chunk.tool_calls:
                        print(f"     工具调用: {tool_call['name']}")
                        print(f"       参数: {tool_call.get('args', {})}")
                
                if hasattr(chunk, 'tool_results') and chunk.tool_results:
                    for result in chunk.tool_results:
                        print(f"     工具结果: {result}")
                
                print()
            
        except Exception as e:
            print(f"❌ 调试失败: {e}")
            import traceback
            traceback.print_exc()


def create_langmem_agent(model_config: Optional[ModelConfig] = None):
    """创建带记忆功能的智能体"""
    
    # 使用LangMemDemo类创建智能体
    demo = LangMemDemo(model_config=model_config)
    return demo.agent, demo.store


def demo_basic_memory(model_config: Optional[ModelConfig] = None):
    """演示基本记忆功能"""
    print("🎯 LangMem 基本记忆演示")
    print("=" * 40)
    
    # 创建演示实例
    demo = LangMemDemo(model_config=model_config)
    
    # 显示模型信息
    model_info = demo.get_model_info()
    print(f"\n🔧 模型配置:")
    print(f"   聊天模型: {model_info['chat_model']}")
    print(f"   嵌入模型: {model_info['embedding_model']}")
    print(f"   聊天API地址: {model_info['chat_base_url']}")
    print(f"   嵌入API地址: {model_info['embedding_base_url']}")
    print(f"   嵌入维度: {model_info['embedding_dimensions']}")
    
    # 调试Store信息
    print("\n🔍 调试Store信息...")
    demo.debug_store_info()
    
    # 添加记忆（不同线程）
    print("\n📝 添加记忆（不同线程）...")
    result1 = demo.add_memory("用户喜欢Python编程", org_id="acme", user_id="alice")
    print(f"   用户A结果: {result1}")
    
    result2 = demo.add_memory("用户住在北京", org_id="acme", user_id="alice")
    print(f"   用户A结果: {result2}")
    
    result3 = demo.add_memory("用户喜欢喝咖啡", org_id="acme", user_id="bob")
    print(f"   用户B结果: {result3}")
    
    result4 = demo.add_memory("用户喜欢JavaScript", org_id="acme", user_id="bob")
    print(f"   用户B结果: {result4}")
    
    # 调试：查看所有记忆
    print("\n🔍 调试：查看所有存储的记忆...")
    all_memories = demo.debug_all_memories()
    print(f"   总共找到 {len(all_memories)} 条记忆")
    
    # 搜索记忆（按线程）
    print("\n🔍 搜索记忆...")
    search_results_a = demo.search_memories("编程", limit=3, org_id="acme", user_id="alice")
    print(f"   用户A搜索'编程'的结果:")
    for i, memory in enumerate(search_results_a, 1):
        print(f"   {i}. {memory['content']} (相似度: {memory['score']:.3f}, org_id: {memory['org_id']})")
    
    search_results_b = demo.search_memories("喜欢", limit=3, org_id="acme", user_id="bob")
    print(f"   用户B搜索'喜欢'的结果:")
    for i, memory in enumerate(search_results_b, 1):
        print(f"   {i}. {memory['content']} (相似度: {memory['score']:.3f}, org_id: {memory['org_id']})")
    
    # 列出所有记忆
    print("\n📋 列出org_id=acme所有记忆...")
    all_memories_all = demo.list_all_memories(org_id="acme")
    print(f"   用户A总共有 {len(all_memories_all)} 条记忆:")
    for i, memory in enumerate(all_memories_all, 1):
        print(f"   {i}. {memory['content']} (org_id: {memory['org_id']})")


    # 列出所有记忆
    print("\n📋 列出org_id=acme, user_id=alice所有记忆...")
    all_memories_a = demo.list_all_memories(org_id="acme", user_id="alice")
    print(f"   用户A总共有 {len(all_memories_a)} 条记忆:")
    for i, memory in enumerate(all_memories_a, 1):
        print(f"   {i}. {memory['content']} (org_id: {memory['org_id']}, user_id: {memory['user_id']})")
    
    print("\n📋 列出org_id=acme, user_id=bob所有记忆...")
    all_memories_b = demo.list_all_memories(org_id="acme", user_id="bob")
    print(f"   用户B总共有 {len(all_memories_b)} 条记忆:")
    for i, memory in enumerate(all_memories_b, 1):
        print(f"   {i}. {memory['content']} (org_id: {memory['org_id']}, user_id: {memory['user_id']})")
    
    # # 跨线程搜索
    # print("\n🔍 跨线程搜索...")
    # cross_thread_results = demo.search_across_all_threads("喜欢", limit=5)
    # print(f"   跨所有线程搜索'喜欢'的结果:")
    # for i, memory in enumerate(cross_thread_results, 1):
    #     print(f"   {i}. {memory['content']} (相似度: {memory['score']:.3f}, 线程: {memory['thread_id']})")
    
    # # 获取所有线程ID
    # print("\n📋 获取所有线程ID...")
    # thread_ids = demo.get_all_thread_ids()
    # print(f"   所有线程: {thread_ids}")
    
    # 对话测试
    print("\n💬 对话测试...")
    response1 = demo.chat_with_memory("你知道我喜欢什么吗？", org_id="acme", user_id="alice")
    print(f"   用户A: 你知道我喜欢什么吗？")
    print(f"   智能体: {response1}")
    
    response2 = demo.chat_with_memory("你知道我喜欢什么吗？", org_id="acme", user_id="bob")
    print(f"   用户B: 你知道我喜欢什么吗？")
    print(f"   智能体: {response2}")
    
    # 调试智能体调用过程
    print("\n🔍 调试智能体调用过程...")
    demo.debug_agent_invoke("你是谁？", org_id="acme", user_id="alice")





def main():
    """主函数"""
    print("🚀 LangMem 简化演示")
    print("=" * 50)
    
    
    try:
        # 使用自定义配置
        print("\n🔧 使用自定义模型配置:")
        from config import custom_config
        
        # 基本记忆演示
        demo_basic_memory(custom_config)
        
        print("\n✅ 演示完成！")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")


if __name__ == "__main__":
    main() 