
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Tue Feb 18 16:56:48 2025
"""


# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()


import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 初始化模型客户端
# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
# )

from config import model_client_vl_plus


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


from autogen_core.tools import FunctionTool

print(get_air_quality.__doc__)

# This step is automatically performed inside the AssistantAgent if the tool is a Python function.
get_air_quality_function_tool = FunctionTool(get_air_quality, description=get_air_quality.__doc__)

print(get_air_quality_function_tool.schema)


# 创建智能体
agent = AssistantAgent(
    name="smart_home_assistant",
    model_client=model_client_vl_plus,
    tools=[get_air_quality],
    reflect_on_tool_use=True,
    system_message="你是一个智能家居助手，能帮用户查询天气、空气质量，还能处理图片和执行多步任务。"
)




from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.ui import Console
from autogen_core import Image as AGImage
from PIL import Image
import io
import requests

# 创建一个多模态消息，包含文字和图片
pil_image = Image.open("./beijing.png")
# pil_image.show()
img = AGImage(pil_image)
multi_modal_message = MultiModalMessage(
    content=["这张图片中的城市的空气质量怎么样？", img],
    source="user"
)

print(dir(multi_modal_message))
print(multi_modal_message.content)
# print(multi_modal_message.__dict__)
print(multi_modal_message.content[1].__dict__)
# 使用流式消息处理用户请求
async def handle_user_request():
    # async for message in agent.on_messages_stream(
    #     [multi_modal_message],
    #     cancellation_token=CancellationToken()
    # ):
    #     print(message)
    await Console(
        agent.on_messages_stream(
            [ multi_modal_message ],
            cancellation_token=CancellationToken(),
        )
    )

# 运行处理函数
import asyncio
asyncio.run(handle_user_request())