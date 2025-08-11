# -*- coding: utf-8 -*-

"""
简化的 Mem0AI 演示
避免向量维度问题，专注于基本功能
"""

import os
import asyncio
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console

# 从配置文件导入模型客户端
from config import model_client
model_client.model_info["multiple_system_messages"] = True

class SimpleMem0Demo:
    def __init__(self):
        """初始化简化演示"""
        self.memory_data = {}  # 使用简单的字典存储记忆
        self.model_client = model_client
        
    def add_memory(self, user_id: str, content: str, metadata: dict = None):
        """添加记忆到本地存储"""
        if user_id not in self.memory_data:
            self.memory_data[user_id] = []
        
        memory_item = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self.memory_data[user_id].append(memory_item)
        print(f"✅ 记忆已添加: {content}")
        return memory_item
    
    def search_memory(self, user_id: str, query: str, limit: int = 5):
        """简单的关键词搜索"""
        if user_id not in self.memory_data:
            return []
        
        # 简单的关键词匹配
        results = []
        for memory in self.memory_data[user_id]:
            if query.lower() in memory["content"].lower():
                results.append(memory)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_user_context(self, user_id: str, query: str):
        """获取用户上下文"""
        memories = self.search_memory(user_id, query, limit=3)
        if memories:
            context = "\n".join([f"- {mem['content']}" for mem in memories])
            return f"用户相关信息:\n{context}"
        return "暂无相关用户信息"
    
    async def demo_basic_operations(self):
        """演示基本操作"""
        print("=== 基本操作演示 ===")
        
        user_id = "user_123"
        
        # 添加用户偏好
        preferences = [
            "用户喜欢科幻电影，特别是星际穿越类型的",
            "用户偏好有深度剧情的电影",
            "用户不喜欢恐怖片",
            "用户经常在周末看电影",
            "用户喜欢诺兰导演的作品"
        ]
        
        print("📝 添加用户偏好...")
        for pref in preferences:
            self.add_memory(user_id, pref, metadata={"category": "preferences"})
        
        # 搜索用户偏好
        print("\n🔍 搜索用户偏好...")
        results = self.search_memory(user_id, "科幻电影")
        for result in results:
            print(f"  找到: {result['content']}")
        
        # 获取用户上下文
        print("\n📋 获取用户上下文...")
        context = self.get_user_context(user_id, "电影推荐")
        print(context)
    
    async def demo_memory_categories(self):
        """演示记忆分类"""
        print("\n=== 记忆分类演示 ===")
        
        user_id = "user_456"
        
        # 按类别添加记忆
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
        
        print("📝 按类别添加记忆...")
        for category, memories in categories.items():
            for memory in memories:
                self.add_memory(user_id, memory, metadata={"category": category})
        
        # 按类别搜索
        print("\n🔍 按类别搜索记忆...")
        for category in categories.keys():
            print(f"\n--- {category} 类别 ---")
            results = self.search_memory(user_id, category, limit=3)
            for result in results:
                print(f"  - {result['content']}")
    
    async def demo_agent_integration(self):
        """演示智能体集成"""
        print("\n=== 智能体集成演示 ===")
        
        user_id = "user_789"
        
        # 添加用户信息
        user_info = [
            "用户最近看了《盗梦空间》并很喜欢",
            "用户想要看一些有创意的科幻片",
            "用户对AI技术很感兴趣",
            "用户正在学习Python编程"
        ]
        
        print("📝 添加用户信息...")
        for info in user_info:
            self.add_memory(user_id, info)
        
        # 创建智能体（不使用 Mem0AI，使用本地记忆）
        assistant_agent = AssistantAgent(
            name="simple_memory_agent",
            model_client=self.model_client,
        )
        
        # 获取用户上下文
        context = self.get_user_context(user_id, "电影推荐")
        
        # 构建带有上下文的提示
        enhanced_prompt = f"""
基于以下用户信息，为用户推荐一部电影：

{context}

请推荐一部符合用户偏好的电影，并解释为什么推荐这部电影。
"""
        
        print("🤖 使用智能体生成推荐...")
        try:
            stream = assistant_agent.run_stream(task=enhanced_prompt)
            await Console(stream)
        except Exception as e:
            print(f"❌ 智能体对话失败: {e}")
    
    async def demo_conversation_memory(self):
        """演示对话记忆"""
        print("\n=== 对话记忆演示 ===")
        
        user_id = "conversation_user"
        
        # 模拟对话历史
        conversations = [
            "用户问: 你好，请介绍一下你自己",
            "助手答: 你好！我是一个AI助手，可以帮助你解决各种问题。",
            "用户问: 基于我的技术背景，你能推荐一些学习资源吗？",
            "助手答: 当然可以！根据你的背景，我推荐学习Python、机器学习和AutoGen框架。",
            "用户问: 我想了解如何配置本地LLM模型",
            "助手答: 配置本地LLM模型需要安装相应的服务，如Ollama或LM Studio。"
        ]
        
        print("📝 记录对话历史...")
        for i, message in enumerate(conversations, 1):
            self.add_memory(
                user_id, 
                message, 
                metadata={"conversation_id": i, "type": "conversation"}
            )
        
        # 搜索相关对话
        print("\n🔍 搜索相关对话...")
        results = self.search_memory(user_id, "学习资源", limit=3)
        for result in results:
            print(f"  找到: {result['content']}")
        
        # 总结对话
        print("\n📋 对话总结...")
        all_conversations = self.memory_data.get(user_id, [])
        if all_conversations:
            print(f"总共记录了 {len(all_conversations)} 条对话")
            print("对话主题包括：自我介绍、学习资源推荐、本地LLM配置等")
    
    async def run_all_demos(self):
        """运行所有演示"""
        print("🚀 简化 Mem0AI 演示")
        print("=" * 50)
        
        try:
            await self.demo_basic_operations()
            await self.demo_memory_categories()
            await self.demo_agent_integration()
            await self.demo_conversation_memory()
            
            print("\n🎉 简化演示完成！")
            print("\n这个演示展示了基本的记忆功能，避免了复杂的向量操作。")
            print("如果您需要更高级的功能，请先解决 Mem0AI 的配置问题。")
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")

async def main():
    """主函数"""
    print("🎯 简化 Mem0AI 演示启动器")
    print("=" * 50)
    
    # 创建演示实例
    demo = SimpleMem0Demo()
    
    # 运行演示
    await demo.run_all_demos()

if __name__ == "__main__":
    asyncio.run(main()) 