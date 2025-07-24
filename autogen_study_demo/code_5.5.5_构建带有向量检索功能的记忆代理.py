
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
from pathlib import Path
import asyncio
# 导入autogen的相关组件用于构建聊天机器人和UI
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
# 导入与记忆存储相关的模块，用于保存和检索上下文信息
from autogen_core.memory import MemoryContent, MemoryMimeType
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
# 导入OpenAI模型客户端，用于与语言模型交互
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 使用自定义配置初始化ChromaDB内存，这里持久化路径设置在用户的主目录下
chroma_user_memory = ChromaDBVectorMemory(
    config=PersistentChromaDBVectorMemoryConfig(
        collection_name="preferences",  # 集合名称，可以理解为数据库表名
        persistence_path=os.path.join(str(Path.home()), ".chromadb_autogen"),  # 数据持久化路径
        k=2,  # 返回最相似的前k个结果
        score_threshold=0.4,  # 设置最小相似度得分阈值
    )
)

async def main():
    # 向内存中添加关于用户偏好的内容，例如：天气单位应该用公制
    await chroma_user_memory.add(
        MemoryContent(
            content="温度单位应该用摄氏度",
            mime_type=MemoryMimeType.TEXT,
            metadata={"category": "preferences", "type": "units"},  # 元数据提供额外的信息
        )
    )
    
    # 添加另一条偏好设置，比如：食谱必须是素食的
    await chroma_user_memory.add(
        MemoryContent(
            content="食谱必须是素食的",
            mime_type=MemoryMimeType.TEXT,
            metadata={"category": "preferences", "type": "dietary"},
        )
    )
    
    # 定义一个异步函数，用于根据城市获取天气情况
    async def get_weather(city: str, units: str = "imperial") -> str:
        if units == "imperial":
            return f"{city} 的天气是 晴天 温度是73 °F。"
        elif units == "metric":
            return f"{city} 的天气是 晴天 温度是23 °C。"
        else:
            return f"对不起, 我不知道{city}的天气。"
    
    # 初始化OpenAI模型客户端，指定使用的模型和API密钥
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    # 创建助理代理，传入模型客户端、工具函数列表（如get_weather）和记忆组件
    assistant_agent = AssistantAgent(
        name="assistant_agent",
        model_client=model_client,
        tools=[get_weather],
        memory=[chroma_user_memory],
    )
    
    # 运行助理代理并传递中文任务："北京天气如何?"
    stream = assistant_agent.run_stream(task="北京天气如何?")
    result = await Console(stream)  # 使用Console UI显示结果
    
    await chroma_user_memory.close()  # 关闭内存连接
    return result

# 执行main函数并打印结果
result = asyncio.run(main())
print(result)
print(result.messages[-1].content)  # 打印最后一条消息的内容




