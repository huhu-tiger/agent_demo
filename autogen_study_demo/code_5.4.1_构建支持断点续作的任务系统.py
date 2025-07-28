
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》s配套代码 
Created on Mon Mar 15 08:25:46 2025
"""

# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()



import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken
# from google import genai

# 设置模型客户端
# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
# )
from config import model_client
# 创建一个 AssistantAgent 代理
assistant_agent = AssistantAgent(
    name="assistant_agent",
    system_message="你是一个智能家庭助手，可以帮助用户管理待办事项。",
    model_client=model_client,
)

# 定义一个异步函数来运行代理并保存状态
async def run_agent_and_save_state():
    # 让代理记录一个待办事项
    response = await assistant_agent.on_messages(
        [TextMessage(content="帮我记录一个待办事项：晚上7点去超市购物", source="user")], 
        CancellationToken()
    )
    print("记录待办事项的响应：")
    print(response.chat_message.content)

    # 保存代理的状态
    agent_state = await assistant_agent.save_state()
    print("\n代理状态已保存。")

    return agent_state

# 定义一个异步函数来加载状态并继续任务
async def load_state_and_continue_task(agent_state):
    # 创建一个新的代理并加载之前保存的状态
    new_assistant_agent = AssistantAgent(
        name="assistant_agent",
        system_message="你是一个智能家庭助手，可以帮助用户管理待办事项。",
        model_client=model_client,
    )
    print(agent_state['llm_context']["messages"])
    # print(agent_state.llm_context.messages)
    await new_assistant_agent.load_state(agent_state)

    print("\n状态已加载。") 

    # 继续执行任务，询问上次记录的待办事项
    response = await new_assistant_agent.on_messages(
        [TextMessage(content="我上次记录的待办事项是什么？", source="user")], 
        CancellationToken()
    )
    print("\n继续任务的响应：")
    print(response.chat_message.content)
    # print(response.inner_messages)
    # print(response.chat_message)

# 运行整个流程
agent_state = asyncio.run(run_agent_and_save_state())
print("--------------------------------")
asyncio.run(load_state_and_continue_task(agent_state))