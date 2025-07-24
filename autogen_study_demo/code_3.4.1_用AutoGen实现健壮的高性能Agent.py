# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Fri Mar  7 13:25:33 2025   
"""



# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage
import os
import asyncio
from aiocache import cached, Cache  # pip install aiocache
from aiocache.serializers import JsonSerializer

def basic_customer_service(query: str) -> str:
    """
    简易客服助手函数，接收用户问题，返回回答。
    """
    common_questions = {
        "退货政策": "支持7天无理由退货，请保留原始包装。",
        "运费": "国内订单满99元包邮。"
    }
    # 检查是否为常见问题
    if query in common_questions:
        return common_questions[query]
    return None

# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了GEMINI_API_KEY
# )
from config import model_client

# 使用 Cache.MEMORY 指定内存缓存
@cached( ttl=3600,  serializer=JsonSerializer(), 
    cache=Cache.MEMORY  # 直接使用预定义的内存缓存类型
)
async def async_generate(prompt):
    """异步生成文本"""
    agent = AssistantAgent("客服助手", model_client=model_client,
                           tools=[basic_customer_service])
    response = await agent.run(task=prompt)
    return response.messages[-1].content

async def main():
    questions = ["退货政策", "推荐一款笔记本电脑"]

    # 使用 create_task 并发执行任务
    tasks = [asyncio.create_task(async_generate(query)) for query in questions]

    try:
        # 使用 wait_for 控制超时
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=10)
    except asyncio.TimeoutError:
        print("处理请求超时")
        return []

    for query, result in zip(questions, results):
        print(f"问题：{query}\n回答：{result}\n")

    return results

if __name__ == "__main__":
    results = asyncio.run(main())
