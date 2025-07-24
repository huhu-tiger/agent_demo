
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Mon Mar 15 08:25:46 2025
"""
# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio

import  os
# 初始化用户记忆
user_memory = ListMemory()

# 添加用户偏好到记忆
async def add_user_preferences():
    await user_memory.add(MemoryContent(content="用户希望以公制单位显示天气", mime_type=MemoryMimeType.TEXT))
    await user_memory.add(MemoryContent(content="用户偏好素食食谱", mime_type=MemoryMimeType.TEXT))

# 定义获取天气的工具函数
async def get_weather(city: str, units: str = "imperial") -> str:
    if units == "imperial":
        return f"{city} 的天气是 73 °F，晴朗。"
    elif units == "metric":
        return f"{city} 的天气是 23 °C，晴朗。"
    else:
        return f"抱歉，我不知道 {city} 的天气。"


# 创建 Gemini 模型客户端.
model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了GEMINI_API_KEY
)


# 创建助理代理，包含记忆和工具
assistant_agent = AssistantAgent(
    name="assistant_agent",
    model_client=model_client,
    tools=[get_weather],
    memory=[user_memory],
)

# 运行代理，执行任务
async def run_agent_task():
    await add_user_preferences()
    stream = assistant_agent.run_stream(task="北京的天气如何？")
    await Console(stream)

# 执行示例
if __name__ == "__main__":
    asyncio.run(run_agent_task())