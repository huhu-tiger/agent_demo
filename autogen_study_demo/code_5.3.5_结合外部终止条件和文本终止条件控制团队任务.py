
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Mon Mar 15 08:25:46 2025
"""


# # #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()


import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os


from config import model_client as Qwen_model_client

async def main():
    # 在函数内部创建代理和团队，以确保它们在正确的事件循环中被创建
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
    text_termination = TextMentionTermination("通过")
    external_termination = ExternalTermination()
    team = RoundRobinGroupChat(
        [primary_agent, critic_agent],
        termination_condition=external_termination | text_termination
    )

    # 在后台运行任务
    run = asyncio.create_task(Console(team.run_stream(task="写一首关于秋天的短诗。")))

    # 等待一小段时间以确保任务开始运行
    await asyncio.sleep(0.1)

    # 停止团队
    print("\n--- [MAIN] 发出外部终止信号 ---")
    external_termination.set()

    # 等待团队完成
    return await run

# # 运行主函数
print("--- 正在运行 main() ---")
result = asyncio.run(main())
print("--- main() 执行结果 ---")
print(result)


print("\n--------------main end------------------\n")

#使用CancellationToken引发异常，来停止团队任务
async def mainv2():
    from autogen_core import CancellationToken
    
    # 在函数内部创建代理和团队以避免事件循环问题
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
    team = RoundRobinGroupChat(
        [primary_agent, critic_agent],
        termination_condition=TextMentionTermination("通过")
    )
    
    #创建一个cancellation token.
    cancellation_token = CancellationToken()
    
    # 在后台运行任务
    run = asyncio.create_task(
        team.run(
            task="写一首关于秋天的短诗。",
            cancellation_token=cancellation_token,
        )
    )
    
    # 等待一小段时间以确保任务开始运行
    await asyncio.sleep(0.1)
    
    # 停止团队 
    print("\n--- [MAIN_V2] 发出取消信号 ---")
    cancellation_token.cancel()
    
    result_v2 = None
    try:
        result_v2 = await run  # This will raise a CancelledError.
        print("--- mainv2() 未被取消 ---")
        print(result_v2)
    except asyncio.CancelledError:
        print("--- mainv2() 任务被成功取消 ---")
        result_v2 = "Task was cancelled."

    return result_v2


# 运行主函数
print("--- 正在运行 mainv2() ---")
asyncio.run(mainv2())
print("--- mainv2() 执行完毕 ---")



