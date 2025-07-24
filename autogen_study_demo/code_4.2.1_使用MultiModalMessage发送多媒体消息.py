
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Tue Feb 18 16:56:48 2025
"""

# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()

from io import BytesIO
import requests
from autogen_agentchat.messages import MultiModalMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
import os
# from PIL import Image
from autogen_core import Image as AGImage
from config import model_client_vl


# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
# )
agent = AssistantAgent(
    name="assistant",
    model_client=model_client_vl,
    system_message="你是一个描述图片的助手."
)


image_url="https://view-cache.book118.com/view31/M02/04/21/wKh2G2Vwes-ALXjAAACbCiT5Grc432.png"
image_url1="https://img95.699pic.com/photo/40241/6812.jpg_wh300.jpg!/fh/300/quality/90"

image_list = [image_url,image_url1]
# 从网络加载图片
# pil_image =Image.open(BytesIO(requests.get("https://view-cache.book118.com/view31/M02/04/21/wKh2G2Vwes-ALXjAAACbCiT5Grc432.png").content))
# pil_image.show()
# img = AGImage(pil_image)
import requests
import base64



async def main():

    for image_url in image_list:
        # 假设 image_url 是网络图片地址
        response = requests.get(image_url)
        img_bytes = response.content
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        image_uri = f"data:image/png;base64,{img_base64}"

        img = AGImage.from_uri(image_uri)

        multi_modal_message = MultiModalMessage(
            content=["你是一名专业的图片分析师，擅长解析图片中的内容与文字。 要求： 1.有非文字，则简述图片的内容 2. 图片中没有图像只有文字，则返回`无效图片`", img],
            source="user"
        )
        response = await agent.on_messages([multi_modal_message], CancellationToken())
        print("智能体返回 description:", response.chat_message.content)


import asyncio
asyncio.run(main())
    
