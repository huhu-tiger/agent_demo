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
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从配置文件导入模型客户端
from config import model_client
model_client.model_info["multiple_system_messages"] = True

# 初始化 Mem0AI 内存客户端
os.environ["OPENAI_API_KEY"] = "xxx"
memory_client = Memory()


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
            # 获取所有记忆
            all_memories = self.memory.list(user_id=self.user_id)
            if all_memories and 'results' in all_memories and all_memories['results']:
                # 删除所有记忆
                for memory in all_memories['results']:
                    self.memory.delete(memory['id'])
                print(f"✅ 已清空用户 {self.user_id} 的所有记忆")
            else:
                print(f"ℹ️ 用户 {self.user_id} 没有记忆需要清空")
        except Exception as e:
            print(f"❌ 清空记忆失败: {e}")
    
    def clear_all_memories(self):
        """清空所有用户的记忆（危险操作）"""
        try:
            # 获取所有记忆
            all_memories = self.memory.list()
            if all_memories and 'results' in all_memories and all_memories['results']:
                # 删除所有记忆
                for memory in all_memories['results']:
                    self.memory.delete(memory['id'])
                print(f"✅ 已清空所有记忆")
            else:
                print(f"ℹ️ 没有记忆需要清空")
        except Exception as e:
            print(f"❌ 清空所有记忆失败: {e}")

def demo_basic_memory_operations():
    """演示基本的内存操作"""
    print("=== 基本内存操作演示 ===")
    
    # 创建用户代理
    user_agent = Mem0EnhancedAgent("movie_agent", "user_123")
    
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
    
    # 创建带有记忆的智能体
    assistant_agent = AssistantAgent(
        name="movie_recommendation_agent",
        model_client=model_client,
        memory=[memory_client],
    )
    
    # 创建用户代理
    user_agent = Mem0EnhancedAgent("user_proxy", "user_123")
    
    # 添加一些用户信息
    user_agent.add_memory("用户最近看了《盗梦空间》并很喜欢", metadata={"category": "recent_watch"})
    user_agent.add_memory("用户想要看一些有创意的科幻片", metadata={"category": "current_interest"})
    
    # 获取用户上下文
    context = user_agent.get_user_context("电影推荐")
    
    # 构建带有上下文的提示
    enhanced_prompt = f"""
基于以下用户信息，为用户推荐一部电影：

{context}

请推荐一部符合用户偏好的电影，并解释为什么推荐这部电影。
"""
    
    print("正在生成推荐...")
    try:
        # 使用智能体生成推荐
        stream = assistant_agent.run_stream(task=enhanced_prompt)
        await Console(stream)
    except Exception as e:
        print(f"生成推荐时出错: {e}")

def clear_vector_database():
    """清空向量数据库中的所有数据"""
    print("🧹 清空向量数据库...")
    try:
        # 创建一个临时代理来清空所有记忆
        temp_agent = Mem0EnhancedAgent("temp_clear_agent", "temp_user")
        temp_agent.clear_all_memories()
        print("✅ 向量数据库已清空")
    except Exception as e:
        print(f"❌ 清空向量数据库失败: {e}")

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
    
    asyncio.run(main()) 
    asyncio.run(main_async()) 