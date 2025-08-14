# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
使用 Mem0AI 的高级功能演示
"""

import os
import asyncio
from mem0 import Memory
from mem0.llms.configs import LlmConfig
from mem0.utils.factory import LlmFactory, EmbedderFactory
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.memory import MemoryContent, MemoryMimeType, MemoryQueryResult, UpdateContextResult
from autogen_core.memory import ListMemory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从配置文件导入模型客户端
from config import model_client
model_client.model_info["multiple_system_messages"] = True

# 初始化 Mem0AI 内存客户端
os.environ["OPENAI_API_KEY"] = "xxx"
memory_client = Memory()

user_id = "user_123"

config = {
    "llm":{
        "provider": "openai",
        "config": {
            "openai_base_url": "http://39.155.179.5:8002/v1",
            "model": "Qwen3-235B-A22B-Instruct-2507"
        }
    },
    "embedder":{
            "provider": "openai",
            "config": {
                "openai_base_url": "http://10.20.201.212:8013/v1",
                "model": "Qwen3-Embedding-8B",
                "embedding_dims": 4096
                }
            },
    "vector_store": {
            "provider": "faiss",
            "config": {
                "collection_name": "test",
                "path": os.path.join(os.path.dirname(os.path.abspath(__file__)), "faiss_memories"),
                "distance_strategy": "euclidean",
                "embedding_model_dims": 4096
                }
            }
}
memory_client = memory_client.from_config(config)

# # 单独修改llm配置
# memory_client.llm = LlmFactory.create(
#     provider_name="openai", 
#     config={"openai_base_url": "http://39.155.179.5:8002/v1", "model": "Qwen3-235B-A22B-Instruct-2507"}
# )

# 每个agent 有独立的记忆库,以及filter
class Mem0MemoryAdapter:
    """Mem0AI 内存适配器，使其与 AutoGen 兼容"""
    def __init__(self, mem0_client, user_id: str = "default",agent_id: str = "default", filters: dict = None):
        self.mem0_client = mem0_client
        self.user_id = user_id
        self.agent_id = agent_id
        self.filters = filters
    
    async def add(self, content: MemoryContent) -> None:
        """添加记忆内容 - AutoGen 期望的方法"""
        try:
            print(f"🔍 调试: 添加记忆内容: {content.content[:100]}...,metadata: {content.metadata}")
            
            # 确保元数据包含 user_id
            enhanced_metadata = {
                "source": "autogen",
                "mime_type": str(content.mime_type),
                "user_id": self.user_id,  # 添加 user_id 到元数据
                "agent_id": self.agent_id,
                **(content.metadata or {})
            }
            
            # 将 MemoryContent 转换为 Mem0AI 格式并存储
            result = self.mem0_client.add(
                content.content,
                user_id=self.user_id,
                agent_id=self.agent_id,
                metadata=enhanced_metadata  
            )
            print(f"✅ 成功添加记忆到 Mem0AI: {result}")
        except Exception as e:
            print(f"❌ 添加记忆失败: {e}")
    
    async def query(self, query: str | MemoryContent = "", **kwargs) -> MemoryQueryResult:
        """查询记忆内容 - AutoGen 期望的方法"""
        try:
            if query:
                # 从 Mem0AI 搜索特定查询
                results = self.mem0_client.search(str(query), user_id=self.user_id,agent_id=self.agent_id,filters=self.filters)
                if results and 'results' in results:
                    # 转换为 MemoryContent 格式
                    memory_contents = []
                    for mem in results['results']:
                        memory_content = MemoryContent(
                            content=mem['memory'],
                            mime_type=MemoryMimeType.TEXT,
                            metadata=mem.get('metadata', {})
                        )
                        memory_contents.append(memory_content)
                        print(f"🔍 调试: 从 Mem0AI 查询到记忆: {memory_content.content[:100]}...,metadata: {memory_content.metadata}")
                    print(f"🔍 调试: 从 Mem0AI 查询到 {len(memory_contents)} 条记忆")
                    return MemoryQueryResult(results=memory_contents)
            else:
                # 当查询为空时，获取该用户的所有记忆
                try:
                    # 使用 get_all 方法获取用户的所有记忆
                    all_results = self.mem0_client.get_all(user_id=self.user_id,agent_id=self.agent_id,filters=self.filters)
                    if all_results and 'results' in all_results:
                        memory_contents = []
                        for mem in all_results['results']:
                            memory_content = MemoryContent(
                                content=mem['memory'],
                                mime_type=MemoryMimeType.TEXT,
                                metadata=mem.get('metadata', {})
                            )
                            memory_contents.append(memory_content)
                        print(f"🔍 调试: 获取用户 {self.user_id} 的所有记忆: {len(memory_contents)} 条")
                        return MemoryQueryResult(results=memory_contents)
                except Exception as get_all_error:
                    print(f"⚠️ 获取用户所有记忆失败: {get_all_error}")
            
            # 如果 Mem0AI 查询失败，返回空结果
            print(f"🔍 调试: Mem0AI 查询失败，返回空结果")
            return MemoryQueryResult(results=[])
        except Exception as e:
            print(f"❌ 查询记忆失败: {e}")
            return MemoryQueryResult(results=[])
    
    async def update_context(self, model_context, **kwargs) -> UpdateContextResult:
        """更新模型上下文 - AutoGen 期望的方法"""
        try:
            print(f"🔍 调试: update_context 被调用，model_context 类型 = {type(model_context)}")
            
            # 获取所有记忆
            query_result = await self.query()
            memories = query_result.results
            
            if memories:
                # 构建记忆上下文字符串
                memory_strings = [f"{i}. {str(memory.content)}" for i, memory in enumerate(memories, 1)]
                memory_context = "\nRelevant memory content (in chronological order):\n" + "\n".join(memory_strings) + "\n"
                
                # 添加到模型上下文
                from autogen_core.models import SystemMessage
                await model_context.add_message(SystemMessage(content=memory_context))
                
                print(f"✅ 成功更新上下文，添加了 {len(memories)} 条记忆")
            else:
                print("ℹ️ 没有记忆需要添加到上下文")
            
            return UpdateContextResult(memories=query_result)
        except Exception as e:
            print(f"❌ 更新上下文失败: {e}")
            return UpdateContextResult(memories=MemoryQueryResult(results=[]))
    
    async def clear(self) -> None:
        """清空记忆 - AutoGen 期望的方法"""
        try:
            # 清空 Mem0AI 中该用户的记忆
            self.mem0_client.delete_all(user_id=self.user_id,agent_id=self.agent_id)
            print("✅ 用户记忆已清空")
        except Exception as e:
            print(f"❌ 清空记忆失败: {e}")
    
    async def close(self) -> None:
        """清理资源 - AutoGen 期望的方法"""
        try:
            print("🔍 调试: 关闭 Mem0AI 内存适配器")
            # 这里可以添加清理逻辑
        except Exception as e:
            print(f"❌ 关闭内存适配器失败: {e}")
    
    # 为了兼容性，保留旧的方法名
    async def get_context(self, query: str = None, **kwargs):
        """获取上下文 - 兼容旧接口"""
        try:
            query_result = await self.query(query, **kwargs)
            if query_result.results:
                context = "\n".join([mem.content for mem in query_result.results])
                print(f"🔍 调试: 获取到上下文: {context[:100]}...")
                return context
            return ""
        except Exception as e:
            print(f"❌ get_context 失败: {e}")
            return ""

class Mem0EnhancedAgent:
    def __init__(self, name: str, user_id: str):
        self.name = name
        self.user_id = user_id
        self.memory = memory_client
        
    def add_memory(self, content: str, metadata: dict = None):
        """添加记忆到 Mem0AI"""
        try:
            result = self.memory.add(
                content, 
                user_id=self.user_id,
                metadata=metadata
            )
            print(f"✅ 记忆已添加: {content}")
            return result
        except Exception as e:
            print(f"❌ 添加记忆失败: {e}")
            return None
    
    def search_memory(self, query: str, limit: int = 5):
        """搜索相关记忆"""
        try:
            results = self.memory.search(
                query, 
                user_id=self.user_id, 
                limit=limit
            )
            return results
        except Exception as e:
            print(f"❌ 搜索记忆失败: {e}")
            return None
    
    def get_user_context(self, query: str):
        """获取用户上下文信息"""
        memories = self.search_memory(query)
        if memories and 'results' in memories and memories['results']:
            context = "\n".join([f"- {mem['memory']}" for mem in memories['results']])
            return f"用户偏好和背景信息:\n{context}"
        return "暂无相关用户信息"
    
    def clear_memory(self):
        """清空用户的所有记忆"""
        try:
            # 使用 Mem0AI 的 delete_all 方法清空指定用户的记忆
            result = self.memory.delete_all(user_id=self.user_id)
            print(f"✅ 已清空用户 {self.user_id} 的所有记忆: {result}")
        except Exception as e:
            print(f"❌ 清空用户记忆失败: {e}")
            # 如果 delete_all 失败，尝试使用 get_all 然后逐个删除
            try:
                all_memories = self.memory.get_all(user_id=self.user_id)
                if all_memories and 'results' in all_memories and all_memories['results']:
                    for memory in all_memories['results']:
                        self.memory.delete(memory['id'])
                    print(f"✅ 已逐个删除用户 {self.user_id} 的所有记忆")
                else:
                    print(f"ℹ️ 用户 {self.user_id} 没有记忆需要清空")
            except Exception as e2:
                print(f"❌ 逐个删除记忆也失败: {e2}")
    
    def clear_all_memories(self):
        """清空所有用户的记忆（危险操作）"""
        try:
            # 使用 Mem0AI 的 delete_all 方法清空所有记忆
            result = self.memory.delete_all(user_id=self.user_id)
            print(f"✅ 已清空所有记忆user_id: {self.user_id} 的记忆: {result}")
        except Exception as e:
            print(f"❌ 清空所有记忆失败: {e}")
            # 如果 delete_all 失败，尝试使用 reset 方法
            try:
                result = self.memory.reset()
                print(f"✅ 已重置所有记忆: {result}")
            except Exception as e2:
                print(f"❌ 重置记忆也失败: {e2}")

def demo_basic_memory_operations():
    """演示基本的内存操作"""
    print("=== 基本内存操作演示 ===")
    
    # 创建用户代理
    user_agent = Mem0EnhancedAgent("movie_agent", user_id)
    
    # 添加用户偏好
    preferences = [
        "用户喜欢科幻电影，特别是星际穿越类型的",
        "用户偏好有深度剧情的电影",
        "用户不喜欢恐怖片",
        "用户经常在周末看电影",
        "用户喜欢诺兰导演的作品"
    ]
    
    for pref in preferences:
        user_agent.add_memory(pref, metadata={"category": "movie_preferences"})
    
    print("\n--- 搜索用户偏好 ---")
    results = user_agent.search_memory("科幻电影")
    if results and 'results' in results:
        for result in results['results']:
            print(f"找到: {result['memory']}")
    
    print("\n--- 获取用户上下文 ---")
    context = user_agent.get_user_context("电影推荐")
    print(context)

async def demo_agent_with_memory():
    """演示带有记忆功能的智能体"""
    print("\n=== 智能体记忆功能演示 ===")
    
    # 创建 Mem0AI 内存适配器
    mem0_adapter = Mem0MemoryAdapter(memory_client, user_id=user_id, agent_id="movie_agent")
    
    # 预先添加一些用户偏好到记忆
    await mem0_adapter.add(MemoryContent(
        content="用户最近看了《盗梦空间》并很喜欢",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "recent_watch"}
    ))
    await mem0_adapter.add(MemoryContent(
        content="用户想要看一些有创意的科幻片",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "current_interest"}
    ))
    await mem0_adapter.add(MemoryContent(
        content="用户喜欢诺兰导演的作品",
        mime_type=MemoryMimeType.TEXT,
        metadata={"category": "director_preference"}
    ))
    
    # 创建带有记忆的智能体
    assistant_agent = AssistantAgent(
        name="movie_recommendation_agent",
        model_client=model_client,
        memory=[mem0_adapter]
    )
    
    print("正在生成推荐...")
    try:
        # 使用智能体生成推荐
        stream = assistant_agent.run_stream(task="请基于我的偏好推荐一部电影")
        await Console(stream)
    except Exception as e:
        print(f"生成推荐时出错: {e}")

def clear_vector_database():
    """清空向量数据库中的所有数据"""
    print("🧹 清空向量数据库...")
    try:
        # 直接使用 memory_client 清空所有记忆
        result = memory_client.delete_all(user_id=user_id)
        print(f"✅ 向量数据库已清空 user_id: {user_id} 的记忆: {result}")
    except Exception as e:
        print(f"❌ 使用 delete_all 清空失败: {e}")
        try:
            # 尝试使用 reset 方法
            result = memory_client.reset()
            print(f"✅ 向量数据库已重置: {result}")
        except Exception as e2:
            print(f"❌ 使用 reset 也失败: {e2}")
            # 最后尝试创建一个临时代理来清空
            try:
                temp_agent = Mem0EnhancedAgent("temp_clear_agent", "temp_user")
                temp_agent.clear_all_memories()
                print("✅ 通过代理清空向量数据库成功")
            except Exception as e3:
                print(f"❌ 所有清空方法都失败: {e3}")

def demo_memory_categories():
    """演示记忆分类功能"""
    print("\n=== 记忆分类演示 ===")
    
    agent = Mem0EnhancedAgent("categorized_agent", "user_456")
    
    # 添加不同类别的记忆
    categories = {
        "personal": [
            "用户名叫张三",
            "用户是一名软件工程师",
            "用户住在北京"
        ],
        "preferences": [
            "用户喜欢喝咖啡",
            "用户偏好安静的工作环境",
            "用户喜欢阅读科幻小说"
        ],
        "work": [
            "用户正在开发一个AI项目",
            "用户使用Python编程",
            "用户需要学习AutoGen框架"
        ]
    }
    
    for category, memories in categories.items():
        for memory in memories:
            agent.add_memory(memory, metadata={"category": category})
    
    # 按类别搜索
    print("\n--- 搜索个人信息 ---")
    personal_results = agent.search_memory("个人信息", limit=3)
    if personal_results and 'results' in personal_results:
        for result in personal_results['results']:
            print(f"个人信息: {result['memory']}")
    
    print("\n--- 搜索工作相关 ---")
    work_results = agent.search_memory("工作项目", limit=3)
    if work_results and 'results' in work_results:
        for result in work_results['results']:
            print(f"工作信息: {result['memory']}")

async def main():
    """主函数"""
    print("🚀 Mem0AI 基础功能演示")
    print("=" * 50)
    
    # 运行各个演示
    demo_basic_memory_operations()
    demo_memory_categories()

    
    print("\n✅ 演示完成！")

async def main_async():
    """主函数"""
    print("🚀 Mem0AI 高级功能演示")
    print("=" * 50)

    # 运行各个演示
    await demo_agent_with_memory()



if __name__ == "__main__":
        
    print("清空向量库数据")
    clear_vector_database()
    print("=" * 50)
    
    # asyncio.run(main()) 
    asyncio.run(main_async()) 