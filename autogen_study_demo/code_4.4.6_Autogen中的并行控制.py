

# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 13 14:07:57 2025
"""

# 设置系统代理（根据你的实际代理地址修改）
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1081'  # 根据你的代理地址修改
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1081'  # 根据你的代理地址修改




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


# Define a JSON schema for a base64 decode tool
base64_schema = {
    "type": "object",
    "properties": {
        "value": {"type": "string", "description": "The base64 value to decode"},
    },
    "required": ["value"],
}

# Create an HTTP tool for the httpbin API
base64_tool = HttpTool(
    name="base64_decode",
    description="base64 decode a value",
    scheme="https",
    host="httpbin.org",
    port=443,
    path="/base64/{value}",
    method="GET",
    json_schema=base64_schema,
)


# 初始化模型客户端
# model_client_no_parallel_tool_call = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
#     parallel_tool_calls=False,  # 禁用并行工具调用
# )

from config import model_client 

model_client_no_parallel_tool_call=model_client
model_client_no_parallel_tool_call.parallel_tool_calls=True





async def main():
   
    # 创建一个包含获取IP工具的助手
    assistant = AssistantAgent("multi_tool_assistant", 
                               model_client=model_client_no_parallel_tool_call, 
                               tools=[base64_tool,ip_tool],
                               system_message="Use tools to solve tasks.",
   
                               reflect_on_tool_use=True #反射工具调用，模型在得到 工具返回结果后，在重新调用模型，输出最终结果
                               )
    

     # 用户请求获取自己的IP地址
    response = await assistant.on_messages(
        [
         TextMessage(content="Can you base64 decode the value 'YWJjZGU=' and base64 decode the value 'MTExMTFhYWRk',and What's my IP address?", source="user")],
        
        CancellationToken(),
    )
    print("="*20+"inner_messages"+"="*20)
    print(response.inner_messages)
    print("="*20+"chat_message"+"="*20)
    print(response.chat_message)



asyncio.run(main())