
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 13 11:14:58 2025
"""

# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()




import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.http import HttpTool
import os

import requests

from pydantic import BaseModel
from typing import Literal

class SmartHomeResponse(BaseModel):
    thoughts: str  # 助手的思考过程
    response: Literal["ok", "error"]  # 最终的响应状态
    action: str  # 执行的操作

from autogen_agentchat.base import Response
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
# from google import genai  # 假设我们使用 Google 的 Gemini 模型

# 初始化模型客户端
# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
#     response_format=SmartHomeResponse,  # 指定结构化输出格式
    
# )

from config import model_client

# print(model_client.__dict__)



# 创建 AssistantAgent，指定结构化输出格式
agent = AssistantAgent(
    name="smart_home_assistant",
    model_client=model_client,
    system_message="你是一个智能家居助手，能够理解用户的指令并执行相应的操作。",
    output_content_type=SmartHomeResponse,
    
)



async def handle_smart_home_command():
    # 用户输入指令
    user_input = "请打开客厅的灯"
    
    # 使用代理处理指令
    response = await agent.on_messages(
        [TextMessage(content=user_input, source="user")],
        cancellation_token=CancellationToken()
    )
    
    # 输出结构化响应
    print(response.chat_message.content)

# 使用 asyncio.run() 在脚本中运行
import asyncio
asyncio.run(handle_smart_home_command())







