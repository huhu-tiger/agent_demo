
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 13 11:14:58 2025
"""
# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()

import asyncio
from typing import AsyncGenerator, List, Sequence, Tuple

from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import AgentEvent, ChatMessage, TextMessage
from autogen_core import CancellationToken
from config import model_client


class CountDownAgent(BaseChatAgent):
    def __init__(self, name: str, count: int = 3):
        """
        初始化CountDownAgent。
        
        参数:
            name (str): 代理的名称。
            count (int): 倒数开始的数字，默认为3。
        """
        super().__init__(name, "一个简单的倒计时代理。")
        self._count = count  # 设置倒数的起始数字

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        """
        返回代理可以产生的消息类型。
        
        返回:
            Sequence[type[ChatMessage]]: 包含TextMessage类型的元组。
        """
        return (TextMessage,)

    

    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        """
        流式处理消息，逐步生成倒计时消息。
        
        参数:
            messages (Sequence[ChatMessage]): 接收到的消息列表。
            cancellation_token (CancellationToken): 取消令牌。
            
        生成:
            AgentEvent | ChatMessage | Response: 每次迭代生成一条消息或响应。
        """
        inner_messages: List[AgentEvent | ChatMessage] = []
        for i in range(self._count, 0, -1):
            msg = TextMessage(content=f"{i}...", source=self.name)
            inner_messages.append(msg)
            yield msg  # 逐条发送倒计时消息
        # 在流结束时返回包含最终消息和所有内部消息的响应
        yield Response(chat_message=TextMessage(content="完成！", source=self.name), 
                       inner_messages=inner_messages)

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        """
        处理接收到的消息，并调用on_messages_stream方法。
        
        参数:
            messages (Sequence[ChatMessage]): 接收到的消息列表。
            cancellation_token (CancellationToken): 取消令牌。
            
        返回:
            Response: 包含最终消息和所有内部消息的响应对象。
        """
        response: Response | None = None
        async for message in self.on_messages_stream(messages, cancellation_token):
            if isinstance(message, Response):
                response = message
        assert response is not None
        return response

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        """
        重置代理的状态。
        
        参数:
            cancellation_token (CancellationToken): 取消令牌。
        """
        pass  # 在这个例子中不需要做任何操作

async def run_countdown_agent() -> None:
    """
    运行倒计时代理并打印每条消息。
    """
    # 创建一个倒计时代理实例
    countdown_agent = CountDownAgent(name="countdown")

    # 使用给定的任务运行代理，并流式输出响应
    async for message in countdown_agent.on_messages_stream([], CancellationToken()):
        if isinstance(message, Response):
            print(message.chat_message)  # 打印最终消息
            print(message.inner_messages)
        else:
            print(message.content)  # 打印每条倒计时消息

# 确保在脚本中使用asyncio.run(...)来运行异步函数
if __name__ == "__main__":
    asyncio.run(run_countdown_agent())
    # await run_countdown_agent()
