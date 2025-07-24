# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Fri Mar  7 13:25:33 2025   
"""
# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()


################################################################




from autogen_agentchat.messages import TextMessage
# 创建一个 TextMessage
message = TextMessage(content="Hello World", source="User")
# 打印这条消息的内容
print(message.content)


import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken
import os

# 创建一个基于"gemini-2.0-flash"模型的客户端，使用环境变量中的API密钥进行初始化。
# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了GEMINI_API_KEY
# )
from config import model_client

message = TextMessage(content="Hello World", source="User")
# 定义一个 dialog_agent 实例
dialog_agent = AssistantAgent("dialog_agent", description="聊天代理",
                               model_client=model_client)



async def get_dialog_info():
    # 调用 dialog_agent 的 on_messages() 方法，发送消息并获取响应。
    response = await dialog_agent.on_messages(
        [message],cancellation_token=CancellationToken())

    # 打印响应中的内部消息 (inner_messages) 和最终的聊天消息 (chat_message)。
    print("内部消息：", response.inner_messages)
    print("聊天消息：", response.chat_message)
    print(dir(response))
# 使用 asyncio.run() 运行异步函数 (如果在脚本中运行)
asyncio.run(get_dialog_info())

