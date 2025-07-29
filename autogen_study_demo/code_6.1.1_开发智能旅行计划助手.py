
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Mon Mar 15 08:25:46 2025
"""
# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()


import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, ExternalTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

import asyncio



# Ollama_model_client = OpenAIChatCompletionClient(
#     model="qwen2.5:32b-instruct-q5_K_M",      #使用qwen32模型
#     base_url=os.getenv("OWN_OLLAMA_URL_165"), #从环境变量里获得本地ollama地址
#     api_key="Ollama",
#     model_capabilities={
#         "vision": False,
#         "function_calling": True,
#         "json_output": True,
#     },
#     # timeout = 10
# )
from config import model_client as Ollama_model_client
# 定义旅行规划师智能体
planner_agent = AssistantAgent(
    "planner_agent",
    model_client=Ollama_model_client,
    description="旅行规划师，能够根据用户需求制定旅行计划。",
    system_message="你是一位旅行规划师，基于用户的请求给出的旅行计划。"
)


# 定义本地推荐智能体
local_agent = AssistantAgent(
    "local_agent",
    model_client=Ollama_model_client,
    description="可以推荐本地活动或访问地点的本地助手。",
    system_message="你是一个本地旅游推荐导助手，能够为用户推荐真实有趣的本地活动或参观地点，并能利用提供的任何上下文信息。"
)

# 定义预算控制智能体
budget_agent = AssistantAgent(
    "budget_agent",
    model_client=Ollama_model_client,
    description="预算控制员，负责确保旅行计划符合用户预算。",
    system_message="你是一位预算控制员，负责审核旅行计划，确保其符合用户的预算。不能过少也不能过多，如果计划开销与预算差距太大，请提出调整建议。"
)

# 定义行程总结智能体
summary_agent = AssistantAgent(
    "summary_agent",
    model_client=Ollama_model_client,
    description="行程总结员，负责整合所有信息，生成最终的旅行计划。",
    system_message="你是一位行程总结员，负责整合其他智能体的建议，生成一份完整的旅行计划。请确保计划详细、准确，并符合用户需求。任务完成之后输出 TERMINATE"
)

# 设置终止条件
termination = TextMentionTermination("TERMINATE")
external_termination = ExternalTermination()
# 创建 GroupChat
group_chat = RoundRobinGroupChat(
    [planner_agent,local_agent, budget_agent, summary_agent],
    termination_condition=termination | external_termination
)





async def run_agent():

    # 通过控制台界面启动对话
    await Console(group_chat.run_stream(task="计划一次为期3天的北京之旅，预算为1000元。"))


# 运行代理
if __name__ == "__main__":
    asyncio.run(run_agent())
    















