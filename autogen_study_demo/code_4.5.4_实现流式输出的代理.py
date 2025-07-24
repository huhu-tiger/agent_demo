
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 13 11:14:58 2025
"""

# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()




import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.http import HttpTool
import os
from autogen_agentchat.base import Response
import requests

from pydantic import BaseModel
from typing import Literal

class SmartHomeResponse(BaseModel):
    thoughts: str  # 助手的思考过程
    response: Literal["ok", "error"]  # 最终的响应状态
    action: str  # 执行的操作

    
Ollama_model_client = OpenAIChatCompletionClient(
    model="qwen2.5:32b-instruct-q5_K_M",      #使用qwen32模型
    base_url=os.getenv("OWN_OLLAMA_URL_165"), #从环境变量里获得本地ollama地址
    api_key="Ollama",
    response_format=SmartHomeResponse,  # 指定结构化输出格式
    model_capabilities={
        "vision": False,
        "function_calling": True,
        "json_output": True,
    },
)



# 创建 AssistantAgent，指定结构化输出格式
streaming_agent = AssistantAgent(
    name="smart_home_assistant",
    model_client=Ollama_model_client,
    system_message="你是一个智能家居助手，能够理解用户的指令并执行相应的操作。",
    model_client_stream=True # 启用流式传输
)

async def stream_smart_home_command():
    # 用户输入指令
    user_input = "请关闭所有电器"
    
    # 使用流式传输处理指令
    async for message in streaming_agent.on_messages_stream(
        [TextMessage(content=user_input, source="user")],
        cancellation_token=CancellationToken()
    ):
        if isinstance(message, Response):
            print("\n",message.chat_message.content) #输出最终结果
        else:
            print(message.content, end='')  # 每条消息后手动添加换行符

# 使用 asyncio.run() 在脚本中运行
asyncio.run(stream_smart_home_command())




