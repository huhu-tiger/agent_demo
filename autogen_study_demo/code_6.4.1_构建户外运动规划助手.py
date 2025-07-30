
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Wed Mar 19 16:13:28 2025
"""


# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()


import asyncio
import os
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_agentchat.agents import AssistantAgent



# Ollama_model_client = OpenAIChatCompletionClient(
#     model="qwen2.5:32b-instruct-q5_K_M",      #使用qwen32模型
#     base_url=os.getenv("OWN_OLLAMA_URL_165"), #从环境变量里获得本地ollama地址
#     api_key="Ollama",
#     model_capabilities={
#         "vision": False,
#         "function_calling": True,
#         "json_output": True,
#     },
# )
from config import model_client as Ollama_model_client

async def main() -> None:
    
    # 创建一个 MultimodalWebSurfer 实例, 允许智能体浏览网页以获取实时信息
    surfer = MultimodalWebSurfer(
       "WebSurfer",
       model_client=Ollama_model_client,
   )

    # 创建一个 MagenticOneGroupChat 团队，其中只包含 assistant 智能体
    team = MagenticOneGroupChat([surfer], model_client=Ollama_model_client)

    # 启动控制台界面，并运行智能体团队，初始任务是为用户规划北京旅行，预算5000元,偏好博物馆。
    await Console(
        team.run_stream(
            task="为我规划一个明天户外运动计划，我在北京。用中文回答"
        )
    )

asyncio.run(main())
