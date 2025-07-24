# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Sun Mar 16 07:58:06 2025
"""
# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()


import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

# 创建硅基流动客户端
Qwen_model_client = OpenAIChatCompletionClient(
    base_url="https://硅基流动接口地址"
    model='Qwen/Qwen2.5-7B-Instruct',  # 模型名称
    api_key=os.getenv("SILICON_FLOW_API_KEY"),  # 使用环境变量中的API密钥
    model_capabilities={
            "vision": False,
            "function_calling": True,
            "json_output": True,
        },
    # timeout = 30
    parallel_tool_calls=False,  # type: ignore
)

# 创建智能体。
assistant = AssistantAgent("assistant", model_client=Qwen_model_client)

# 创建团队，设置最大轮数为 1。
team = RoundRobinGroupChat([assistant], max_turns=1)

async def main():
    task = "写一首关于海洋的四行诗。"
    while True:
        # 运行对话并流式传输到控制台。
        stream = team.run_stream(task=task)
        # 在脚本中运行时使用 asyncio.run(...)。
        await Console(stream)
        # 获取用户响应。
        task = input("请输入您的反馈（输入 'exit' 退出）：")
        if task.lower().strip() == "exit":
            break


import asyncio
asyncio.run(main())