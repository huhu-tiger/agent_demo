
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Sun Mar 16 07:58:06 2025
"""

# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()


import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os
from autogen_agentchat.ui import Console

# 创建待办事项列表（模拟用户的任务清单）
todo_list = ["买牛奶", "支付水电费", "预约牙医"]

# 定义任务处理工具
def process_task(current_task:str) -> str:
    """处理一个待办事项并返回完成情况"""
    if current_task in todo_list:
        todo_list.remove(current_task)
    else:
        return "没有待办事项：{current_task}"
    if len(todo_list)==0:
        return "所有待办事项已完成"
    return f"已完成：{current_task}"

def get_tasknames()-> list:
    """获得待办事项"""
    return todo_list



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
# 创建任务助手
task_assistant = AssistantAgent(
    name="looped_assistant",
    model_client=Ollama_model_client,
    tools=[process_task,get_tasknames],  # 注册任务处理工具
    system_message="""
    你是一个AI助手，使用工具处理待办事项"""  # 初始化时显示任务列表
)


# 设置终止条件（当收到特定消息时停止）
termination_condition = TextMessageTermination("looped_assistant")
# 创建单代理团队
team = RoundRobinGroupChat(
    [task_assistant],
    termination_condition=termination_condition
)



async def main():
   # 运行任务处理流程
   print("开始处理待办事项...")
   stream = await Console(team.run_stream(task=f"请帮我处理所有的待办事项"))
   return stream

result = asyncio.run(main())
print(result)
result.messages[-1].content



