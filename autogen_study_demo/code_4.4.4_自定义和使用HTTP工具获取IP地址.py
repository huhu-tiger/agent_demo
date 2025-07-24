
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 13 10:04:05 2025
"""

# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()




import asyncio

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.http import HttpTool
import os


ip_schema = {
    "type": "object",
    "properties": {},
    "required": [],
}

ip_tool = HttpTool(
    name="get_ip",
    description="Get your public IP address",
    scheme="https",
    host="api.ipify.org",
    port=443,
    path="/",
    method="GET",
    json_schema=ip_schema,
    return_type="text",  # 因为返回的是纯文本格式的IP地址
)


# # Define a JSON schema for a base64 decode tool
# base64_schema = {
#     "type": "object",
#     "properties": {
#         "value": {"type": "string", "description": "The base64 value to decode"},
#     },
#     "required": ["value"],
# }

# # Create an HTTP tool for the httpbin API
# base64_tool = HttpTool(
#     name="base64_decode",
#     description="base64 decode a value",
#     scheme="https",
#     host="httpbin.org",
#     port=443,
#     path="/base64/{value}",
#     method="GET",
#     json_schema=base64_schema,
# )


# 初始化模型客户端
from config import model_client
model_client = model_client


async def main():
    # Create an assistant with the base64 tool
   
    # assistant = AssistantAgent("base64_assistant", model_client=model_client, tools=[base64_tool,ip_tool])
    # 创建一个包含获取IP工具的助手
    assistant = AssistantAgent("assistant", model_client=model_client, tools=[ip_tool])

     # 用户请求获取自己的IP地址
    response = await assistant.on_messages(
        # [TextMessage(content="Can you base64 decode the value 'YWJjZGU=', please?", source="user")],
        [TextMessage(content="What's my IP address?", source="user")],
        
        CancellationToken(),
    )
    print(response.inner_messages)
    print(response.chat_message)
    print(response.chat_message.content)


asyncio.run(main())
