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

from config import model_client_vl_plus,model_client




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


# 创建智能体
agent = AssistantAgent(
    name="smart_home_assistant",
    model_client=model_client_vl_plus,
    tools=[get_air_quality],
    system_message="调用get_air_quality工具，查询图中城市的空气质量",
    reflect_on_tool_use=True
)


# image_url="./beijing.png"

from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.ui import Console
from autogen_core import Image as AGImage
from PIL import Image
import io,base64
import requests

# 创建一个多模态消息，包含文字和图片
image_path = "./beijing.png"
with open(image_path, "rb") as f:
    img_bytes = f.read()
img_base64 = base64.b64encode(img_bytes).decode("utf-8")
image_uri = f"data:image/png;base64,{img_base64}"

img = AGImage.from_uri(image_uri)
multi_modal_message = MultiModalMessage(
    content=["帮我查询一下，图中城市的空气质量怎么样？", img],
    source="user"
)

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