
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 13 11:14:58 2025
"""

# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()

from collections import defaultdict
from datetime import datetime, timedelta

import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.http import HttpTool
import os


async def get_air_quality(city: str) -> str:
    """获取指定城市的空气质量数据"""
    # 这里模拟从 API 获取数据
    air_quality_data = {
        "北京": "优",
        "上海": "良",
        "广州": "优",
        "深圳": "优"
    }
    return air_quality_data.get(city, "暂无数据")


# 初始化模型客户端
model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
    parallel_tool_calls=False,  # 禁用并行工具调用
)


# 创建智能体
agent = AssistantAgent(
    name="smart_home_assistant",
    model_client=model_client,
    tools=[get_air_quality],
    system_message="你是一个智能家居助手，能帮用户查询天气、空气质量，还能处理图片和执行多步任务。"
)



tool_call_counts = defaultdict(int)
tool_call_limits = {}  # 存储工具的调用限制，格式为 {tool_name: (limit, period)}

def limit_tool_calls(tool_name, limit, period_minutes):
    tool_call_limits[tool_name] = (limit, period_minutes)

def check_tool_call_limit(tool_name):
    now = datetime.now()
    limit, period_minutes = tool_call_limits.get(tool_name, (None, None))
    if limit is not None and period_minutes is not None:
        # 计算时间窗口的开始时间
        window_start = now - timedelta(minutes=period_minutes)
        # 统计当前时间窗口内的调用次数
        calls_in_window = sum(
            1 for timestamp in tool_call_timestamps[tool_name]
            if timestamp >= window_start
        )
        if calls_in_window >= limit:
            return False  # 超过限制
    return True  # 未超过限制

tool_call_timestamps = defaultdict(list)



async def main():
    tool_name = "air_quality_tool"
    limit_tool_calls(tool_name, 5, 60)  # 每小时最多调用5次

    user_input = "北京空气怎么样?"
    if "空气" in user_input.lower():
        if check_tool_call_limit(tool_name):
            # 记录调用时间
            tool_call_timestamps[tool_name].append(datetime.now())
            # 调用天气工具
            response = await agent.on_messages(
                [TextMessage(content=user_input, source="user")],
                CancellationToken(),
            )
            print(response.chat_message.content)
        else:
            print("Tool call limit exceeded. Please try again later.")
    else:
        print("Handling other types of requests...")
        


asyncio.run(main())        