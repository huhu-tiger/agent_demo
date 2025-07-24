
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Mon Mar 15 08:25:46 2025
"""


# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()


import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os

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
)


# 创建主代理和批评代理
primary_agent = AssistantAgent(
    "primary",
    model_client=Qwen_model_client,
    system_message="你是一个有帮助的人工智能助手。你的任务是根据给定的主题写诗。"
)

critic_agent = AssistantAgent(
    "critic",
    model_client=Qwen_model_client,
    system_message="你是一个评论者。你的任务是评估主代理写的诗，并提供反馈。当对诗满意时回复 '通过'。"
)

# 定义文本终止条件
text_termination = TextMentionTermination("通过")

# 创建外部终止条件
external_termination = ExternalTermination()

# 创建团队，结合外部终止条件和文本终止条件
team = RoundRobinGroupChat(
    [primary_agent, critic_agent],
    termination_condition=external_termination | text_termination  # 使用按位或运算符组合条件
)






async def main():
    # 在后台运行任务
    run = asyncio.create_task(Console(team.run_stream(task="写一首关于秋天的短诗。")))

    # 等待一段时间
    # await asyncio.sleep(1.1)
    await asyncio.sleep(0.1)

    # 停止团队
    external_termination.set()

    # 等待团队完成
    return await run

# # 运行主函数
result = asyncio.run(main())
print(result)

#使用CancellationToken引发异常，来停止团队任务
async def mainv2():
    from autogen_core import CancellationToken
    #创建一个cancellation token.
    cancellation_token = CancellationToken()
    
    # 在后台运行任务
    run = asyncio.create_task(
        team.run(
            task="写一首关于秋天的短诗。",
            cancellation_token=cancellation_token,
        )
    )
    
    # 停止团队 
    cancellation_token.cancel()
    
    try:
        result = await run  # This will raise a CancelledError.
        print(result)
    except asyncio.CancelledError:
        print("Task was cancelled.")

    return result


# 运行主函数
asyncio.run(mainv2())



