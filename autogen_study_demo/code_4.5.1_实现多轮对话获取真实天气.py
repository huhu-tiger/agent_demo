

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

import requests


def get_weather_info(city: str)-> dict:
    """
    模拟根据地点和日期查询天气。

    Args:
        city: 城市地点

    Returns:
        返回的天气信息。
    """
    url = f"http://山河API接口地址?city={city}"
    response = requests.get(url)
    current_weather ={}
    if response.status_code == 200:
        data = response.json()
     
        if data.get("code") == 1: # 检查是否成功获取数据
            weather =  data["data"] 
            current_weather = weather.get("current", {})
           
        else:
            print("未能成功获取数据：", data.get("text"))
    else:
        print(f"请求失败，状态码：{response.status_code}")   
    return current_weather



# 初始化模型客户端
model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
)

# 创建 AssistantAgent
agent = AssistantAgent(
    name="weather_assistant",
    model_client=model_client,
    tools=[get_weather_info],
    reflect_on_tool_use=True,
    system_message="你是一个天气查询助手。使用工具查询天气, 并且你能够理解上下文并处理多轮对话。",
)

async def handle_conversation():
    # 第一轮对话
    
    response = await agent.on_messages(
        [TextMessage(content="北京今天天气怎么样？", source="user")],
        cancellation_token=CancellationToken(),
    )
    print(response.chat_message.content)
    # 第二轮对话
    
    response = await agent.on_messages(
        [TextMessage(content="盖州呢？", source="user")],
        cancellation_token=CancellationToken(),
    )
    print(response.chat_message.content)

# 使用 asyncio.run(handle_conversation()) 在脚本中运行
import asyncio
asyncio.run(handle_conversation())
