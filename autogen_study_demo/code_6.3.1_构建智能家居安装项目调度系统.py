
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Wed Mar 19 16:13:28 2025
"""



import nest_asyncio
nest_asyncio.apply()

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import Swarm
from autogen_agentchat.conditions import HandoffTermination
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
import os
import json
from autogen_agentchat.ui import Console
from typing import Dict, List
from autogen_ext.models.openai import OpenAIChatCompletionClient

import asyncio
from autogen_agentchat.messages import HandoffMessage

# 定义工具函数
async def generate_installation_guide(device: str) -> str:
    """生成设备安装指南"""
    guides = {
        "智能门锁": "1. 定位安装位置\n2. 固定背板\n3. 安装锁体\n4. 调试电子部件",
        "网络摄像头": "1. 选择安装高度\n2. 固定支架\n3. 连接电源\n4. 配置无线网络"
    }
    return guides.get(device, "标准安装流程")

async def check_inventory(devices: List[str]) -> Dict[str, bool]:
    """检查设备库存"""
    inventory = {"智能门锁": True, "网络摄像头": False, "智能灯泡": True}
    return {d: inventory.get(d, False) for d in devices}

# 初始化模型客户端
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

# 定义各角色智能体
project_manager = AssistantAgent(
    "project_manager",
    description="项目经理",
    model_client=Ollama_model_client,
    handoffs=["electrician", "network_engineer", "inventory_clerk"],
    system_message="""负责整体项目协调：
    1. 解析用户安装需求
    2. 分配任务给专业工程师
    3. 监控项目进度
    使用TERMINATE结束流程"""
)

electrician = AssistantAgent(
    "electrician",
    description="电工",
    model_client=Ollama_model_client,
    handoffs=["project_manager"],
    tools=[generate_installation_guide],
    system_message="""电气设备安装专家：
    1. 生成电气设备安装指南
    2. 处理电路改造需求
    完成工作后返回项目经理"""
)

network_engineer = AssistantAgent(
    "network_engineer",
    description="网络工程师",
    model_client=Ollama_model_client,
    handoffs=["project_manager"],
    system_message="""网络设备配置专家：
    1. 规划无线网络覆盖
    2. 配置智能设备联网
    完成工作后返回项目经理"""
)

inventory_clerk = AssistantAgent(
    "inventory_clerk",
    description="库存管理员",
    model_client=Ollama_model_client,
    handoffs=["project_manager"],
    tools=[check_inventory],
    system_message="""库存管理系统：
    1. 检查设备库存状态
    2. 生成备货清单
    完成检查后返回项目经理"""
)

# 创建Swarm团队
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")|max_messages_termination
installation_team = Swarm(
    participants=[project_manager, electrician, network_engineer, inventory_clerk],
    termination_condition=termination
)

# 运行任务处理流程
async def run_team_stream(task: str):
    # task_result = await installation_team.run_stream(task=task)
    task_result = await Console(installation_team.run_stream(task=task))
    
    while True:
        last_msg = task_result.messages[-1]
        if isinstance(last_msg, HandoffMessage) and last_msg.target == "user":
            user_input = input("需要补充信息：")
            task_result = await installation_team.run_stream(
                HandoffMessage(source="user", target=last_msg.source, content=user_input)
            )
        else:
            break

# 执行安装任务
if __name__ == "__main__":
    installation_task = "需要安装：3个智能门锁（客厅/主卧/次卧），2个网络摄像头（前门/后院）"
    task_result = asyncio.run(run_team_stream(installation_task))  # 使用asyncio运行异步函数
    
    print(f"{task_result}")
