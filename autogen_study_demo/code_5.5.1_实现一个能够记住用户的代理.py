
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Mon Mar 15 08:25:46 2025
"""

# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()


import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient



#设置模型客户端
model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
)


# Ollama_model_client = OpenAIChatCompletionClient(
#     model="qwen2.5:32b-instruct-q5_K_M",      #使用qwen32模型
#     base_url=os.getenv("OWN_OLLAMA_URL_165"), #从环境变量里获得本地ollama地址
#     api_key="Ollama",
#     model_capabilities={
#         "vision": False,
#         "function_calling": True,
#         "json_output": True,
#     },
#     # timeout = 10
# )


# 初始化用户记忆
user_memory = ListMemory()

# 添加用户偏好
async def add_preferences():
    await user_memory.add(MemoryContent(content="用户A 喜欢 科幻片", mime_type=MemoryMimeType.TEXT))
    await user_memory.add(MemoryContent(content="用户B 收藏 诺兰导演作品", mime_type=MemoryMimeType.TEXT))
    print("用户偏好已添加。")

# 批量导入偏好（这里为了演示，实际上也是逐条添加）
async def import_preferences():
    await user_memory.add(MemoryContent(content="用户B 喜欢 星际穿越", mime_type=MemoryMimeType.TEXT))
    await user_memory.add(MemoryContent(content="用户B 喜欢 盗梦空间", mime_type=MemoryMimeType.TEXT))
    print("用户B的偏好已批量导入。")

# 条件查询
async def query_preferences(query_str: str):
    results = await user_memory.query(query_str)
    print(f"查询'{query_str}'的结果：")
    
    for result in results:
        for ret in result[1]: 
            print(ret.content)

# 动态更新
async def update_preferences():
    await user_memory.add(MemoryContent(content="用户A 最近喜欢 悬疑片", mime_type=MemoryMimeType.TEXT))
    print("用户A的偏好已更新。")
# 创建 AssistantAgent 实例，并注入 memory
assistant_agent = AssistantAgent(
    name="movie_recommendation_agent",
    model_client=model_client,
    memory=[user_memory],
)

async def main():

    await add_preferences()
    await import_preferences()
    await query_preferences("用户A")
    await update_preferences()
    await query_preferences("用户A")
    
    #使用memory进行一次实际的对话
    stream = assistant_agent.run_stream(task="为用户A推荐一部电影")
    await Console(stream)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


