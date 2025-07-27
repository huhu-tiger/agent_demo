# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Sun Mar 16 07:58:06 2025
"""
# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()


import os
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


# 创建 Gemini 模型客户端.
# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了GEMINI_API_KEY
# )
from config import model_client
# 创建 AssistantAgent，名为 "writer"，负责生成文章内容。
writer = AssistantAgent("writer", model_client=model_client)

# 创建 UserProxyAgent，名为 "user_proxy"，作为用户与 AI 之间的桥梁，接收用户输入。
# input_func=input 表示从控制台获取用户输入。
user_proxy = UserProxyAgent("user_proxy", input_func=input)

# 创建 TextMentionTermination 终止条件，当用户输入中包含 "发布" 时，终止对话。
termination = TextMentionTermination("发布")

# 创建 RoundRobinGroupChat 团队，包含 writer 和 user_proxy 两个成员。
# termination_condition=termination 指定了终止条件。
team = RoundRobinGroupChat([writer, user_proxy], termination_condition=termination)

# 启动对话流程，task="请写一篇关于家常红烧肉做法的博文，要求图文并茂。" 为初始任务。
stream = team.run_stream(task="请写一篇关于家常红烧肉做法的博文，要求图文并茂。")

# 使用 asyncio.run(...) 运行对话，并通过 Console 显示交互过程。
import asyncio
asyncio.run(Console(stream))
