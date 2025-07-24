
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书<AutoGen代理实战>配套代码 
Created on Mon Mar 17 09:12:38 2025
"""


# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()


import os
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


Ollama_model_client = OpenAIChatCompletionClient(
    model="qwen2.5:32b-instruct-q5_K_M",      #使用qwen32模型
    base_url=os.getenv("OWN_OLLAMA_URL_165"), #从环境变量里获得本地ollama地址
    api_key="Ollama",
    model_capabilities={
        "vision": False,
        "function_calling": True,
        "json_output": True,
    },
    # timeout = 10
)

# 创建一个餐饮推荐代理，设置其在无法完成任务时将任务转交给用户
food_recommender = AssistantAgent(
    "food_recommender",
    model_client=Ollama_model_client,
    handoffs=[Handoff(target="user", message="我需要更多信息才能为您推荐餐厅。请提供更多细节或直接回答问题。")],
    system_message="如果您无法推荐餐厅，请转交给用户。否则，在完成时回复 'TERMINATE'。"
)

# 定义 HandoffTermination 和 TextMentionTermination 终止条件
handoff_termination = HandoffTermination(target="user")
text_termination = TextMentionTermination("TERMINATE")

# 创建一个单代理团队，设置终止条件
food_recommendation_team = RoundRobinGroupChat(
    [food_recommender],
    termination_condition=handoff_termination | text_termination
)

async def main():
    # 运行餐饮推荐系统
    task = "请推荐一家适合我的北京的川菜餐厅"
    while True:
        result = await Console(food_recommendation_team.run_stream(task=task), output_stats=True)
        # print("返回：",result.messages[-1].content)
        # print(result)
        if result.messages[-1].type == 'HandoffMessage':
            # 如果代理触发 HandoffTermination，等待用户输入反馈并继续运行
            task = input(f"{result.messages[-1].content}（输入 'exit' 退出）：")
            if task.lower().strip() == "exit":
                break
        else:
            return result.messages[-1].content
    
  
        
ret = asyncio.run(main())
print(ret)
