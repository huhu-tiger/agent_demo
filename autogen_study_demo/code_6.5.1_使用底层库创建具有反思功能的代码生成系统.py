
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Wed Mar 19 16:13:28 2025
"""

# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()


import os
from autogen_core import MessageContext, RoutedAgent, TopicId, default_subscription, message_handler
from autogen_core.models import AssistantMessage, ChatCompletionClient, LLMMessage, SystemMessage, UserMessage
from dataclasses import dataclass
from autogen_ext.models.openai import OpenAIChatCompletionClient
import uuid
from typing import AsyncGenerator, List, Sequence, Tuple,Union,Dict
import re
import asyncio
from dataclasses import dataclass
import json

import logging
import re

class BetterUnicodeFormatter(logging.Formatter):
    """
    一个更健壮的日志格式化器，可以解码最终日志消息中的 unicode 转义序列。
    它使用正则表达式来避免处理已解码字符时出错。
    """
    def format(self, record):
        # 首先，让父类处理初始的格式化（例如，msg % args）。
        formatted_string = super().format(record)
        
        # 安全地从最终格式化的字符串中解码 unicode 转义序列。
        try:
            # 这个正则表达式会查找所有的 \\uXXXX 序列并进行替换。
            # 如果字符串中已经包含了 unicode 字符，它不会失败。
            return re.sub(
                r'\\u([0-9a-fA-F]{4})',
                lambda m: chr(int(m.group(1), 16)),
                formatted_string
            )
        except Exception:
            # 如果发生任何意想不到的错误，只需返回原始字符串。
            return formatted_string

# --- 清理并配置日志 ---
# 获取根日志记录器并移除所有现有的处理器，以防止重复日志。
root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# 创建一个带有我们自定义格式化器的新处理器
handler = logging.StreamHandler()
formatter = BetterUnicodeFormatter('%(levelname)s:%(name)s:%(message)s')
handler.setFormatter(formatter)

# 将我们的处理器添加到根日志记录器
root_logger.addHandler(handler)

# 设置所需的日志级别
root_logger.setLevel(logging.INFO)  # 其他库的默认级别
logging.getLogger("autogen_core").setLevel(logging.DEBUG)  # autogen_core 的特定级别
logging.getLogger("autogen_core.events").setLevel(logging.DEBUG) # 同时为事件日志启用
# 设置 LLM 客户端
# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
# )

from config import model_client

 
# 定义代码编写任务的消息类
@dataclass
class CodeWritingTask:
    task: str  # 编写代码的任务描述

# 定义代码编写结果的消息类
@dataclass
class CodeWritingResult:
    task: str  # 原始任务描述
    code: str  # 生成的代码
    review: str  # 评审意见

# 定义代码评审任务的消息类
@dataclass
class CodeReviewTask:
    session_id: str  # 会话ID，用于追踪特定任务
    code_writing_task: str  # 编写代码的任务描述
    code_writing_scratchpad: str  # 编写代码时使用的草稿板
    code: str  # 需要评审的代码

# 定义代码评审结果的消息类
@dataclass
class CodeReviewResult:
    review: str  # 评审意见
    session_id: str  # 关联的会话ID
    approved: bool  # 是否批准了代码   
    

@default_subscription
class CoderAgent(RoutedAgent):
    """执行代码编写任务的智能体。"""

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("一个代码编写智能体。")
        self._system_messages: List[LLMMessage] = [
            SystemMessage(
                content="""你是一个熟练的编码人员。你编写代码来解决问题。
与评审人员合作改进你的代码。
始终将所有完成的代码放在一个 Markdown 代码块中。
例如：
```python
def hello_world():
    print("Hello, World!")  
```  
使用以下格式回复：
Thoughts: <Your comments>
Code: <Your code>""",
            )
        ]
        self._model_client = model_client
        self._session_memory: Dict[str, List[CodeWritingTask | CodeReviewTask | CodeReviewResult]] = {}


    # xxx message_handler 根据message参数的类型 自动匹配到对应的函数
    @message_handler 
    async def handle_code_writing_task(self, message: CodeWritingTask, ctx: MessageContext) -> None:
        # 为这个请求仅存储消息到临时内存中。
        session_id = str(uuid.uuid4())
        self._session_memory.setdefault(session_id, []).append(message)
        # 使用聊天完成 API 生成响应。
        response = await self._model_client.create(
            self._system_messages + [UserMessage(content=message.task, source=self.metadata["type"])],
            cancellation_token=ctx.cancellation_token,
        )
        assert isinstance(response.content, str)
        # 从响应中提取代码块。
        code_block = self._extract_code_block(response.content)
        if code_block is None:
            raise ValueError("未找到代码块。")
        # 创建代码评审任务。
        code_review_task = CodeReviewTask(
            session_id=session_id,
            code_writing_task=message.task,
            code_writing_scratchpad=response.content,
            code=code_block,
        )
        # 将代码评审任务存储在会话内存中。
        self._session_memory[session_id].append(code_review_task)
        # todo 发布代码评审任务, 会进入ReviewerAgent的handle_code_review_task函数
        await self.publish_message(code_review_task, topic_id=TopicId("default", self.id.key))

    
    @message_handler
    async def handle_code_review_result(self, message: CodeReviewResult, ctx: MessageContext) -> None:
        # 将评审结果存储在会话内存中。
        self._session_memory[message.session_id].append(message)
        # 从之前的消息中获取请求。
        review_request = next(
            m for m in reversed(self._session_memory[message.session_id]) if isinstance(m, CodeReviewTask)
        )
        assert review_request is not None
        # 检查代码是否通过评审。
        if message.approved:
            # 发布代码编写结果。
            await self.publish_message(
                CodeWritingResult(
                    code=review_request.code,
                    task=review_request.code_writing_task,
                    review=message.review,
                ),
                topic_id=TopicId("default", self.id.key),
            )
            print("代码编写结果：")
            print("-" * 80)
            print(f"任务：\n{review_request.code_writing_task}")
            print("-" * 80)
            print(f"代码：\n{review_request.code}")
            print("-" * 80)
            print(f"评审：\n{message.review}")
            print("-" * 80)
        else:
            # 创建要发送到模型的 LLM 消息列表。
            # xxx 如果没有approved, 则需要重新生成代码,提取之前所有的message 记录
            messages: List[LLMMessage] = [*self._system_messages]
            for m in self._session_memory[message.session_id]:
                if isinstance(m, CodeReviewResult):
                    messages.append(UserMessage(content=m.review, source="Reviewer"))
                elif isinstance(m, CodeReviewTask):
                    messages.append(AssistantMessage(content=m.code_writing_scratchpad, source="Coder"))
                elif isinstance(m, CodeWritingTask):
                    messages.append(UserMessage(content=m.task, source="User"))
                else:
                    raise ValueError(f"意外的消息类型：{m}")
            logging.info(f"111111messages: {messages}")
            # 使用聊天完成 API 生成修订。
            response = await self._model_client.create(messages, cancellation_token=ctx.cancellation_token)
            assert isinstance(response.content, str)
            # 从响应中提取代码块。
            code_block = self._extract_code_block(response.content)
            if code_block is None:
                raise ValueError("未找到代码块。")
            # 创建新的代码评审任务。
            code_review_task = CodeReviewTask(
                session_id=message.session_id,
                code_writing_task=review_request.code_writing_task,
                code_writing_scratchpad=response.content,
                code=code_block,
            )
            # 将新的代码评审任务存储在会话内存中。
            self._session_memory[message.session_id].append(code_review_task)
            # 发布新的代码评审任务。
            await self.publish_message(code_review_task, topic_id=TopicId("default", self.id.key))

    
    def _extract_code_block(self, markdown_text: str) -> Union[str, None]:
        pattern = r"```(\w+)\n(.*?)\n```"
        # 在 markdown 文本中搜索模式
        match = re.search(pattern, markdown_text, re.DOTALL)
        # 如果找到匹配项，提取语言和代码块
        if match:
            return match.group(2)
        return None


    
@default_subscription
class ReviewerAgent(RoutedAgent):
    """执行代码评审任务的智能体。"""

    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("一个代码评审智能体。")
        self._system_messages: List[LLMMessage] = [
            SystemMessage(
                content="""你是一个代码评审人员。你关注代码的正确性、效率和安全性。
用如下 JSON 格式回复：
{
    "correctness": "<你的评论>",
    "efficiency": "<你的评论>",
    "safety": "<你的评论>",
    "approval": "<APPROVE 或 REVISE>",
    "suggested_changes": "<你的评论>"
}
""",
            )
        ]
        self._session_memory: Dict[str, List[CodeReviewTask | CodeReviewResult]] = {}
        self._model_client = model_client


    @message_handler
    async def handle_code_review_task(self, message: CodeReviewTask, ctx: MessageContext) -> None:
        # 为代码评审格式化提示。
        # 如果可用，收集之前的反馈。
        previous_feedback = ""
        """
reversed(): 从最新的消息开始向前查找（倒序）
生成器表达式: (m for m in ... if isinstance(m, CodeReviewResult))
遍历会话中的所有消息
只选择类型为 CodeReviewResult 的消息
next(): 获取第一个匹配的结果
None: 如果没有找到，返回 None
        """
        if message.session_id in self._session_memory:
            previous_review = next(
                (m for m in reversed(self._session_memory[message.session_id]) if isinstance(m, CodeReviewResult)),
                None,
            )
            if previous_review is not None:
                previous_feedback = previous_review.review
        # 为这个请求仅存储消息到临时内存中。
        self._session_memory.setdefault(message.session_id, []).append(message)
        prompt = f"""问题陈述是：{message.code_writing_task}
代码是：
{message.code}  
```

之前的反馈：
{previous_feedback}

请评审代码。如果提供了之前的反馈，请查看是否已解决。"""
        # 使用聊天完成 API 生成响应。
        response = await self._model_client.create(
            self._system_messages + [UserMessage(content=prompt, source=self.metadata["type"])],
            cancellation_token=ctx.cancellation_token,
            json_output=True,
        )
        assert isinstance(response.content, str)
        # TODO：使用结构化生成库（例如 guidance）来确保响应符合预期格式。
        # 解析响应 JSON。
        review = json.loads(response.content)
        # 构造评审文本。
        review_text = "代码评审：\n" + "\n".join([f"{k}: {v}" for k, v in review.items()])
        approved = review["approval"].lower().strip() == "approve"
        result = CodeReviewResult(
            review=review_text,
            session_id=message.session_id,
            approved=approved,
        )
        # 将评审结果存储在会话内存中。
        self._session_memory[message.session_id].append(result)
        # 发布评审结果。
        await self.publish_message(result, topic_id=TopicId("default", self.id.key))

            





from autogen_core import DefaultTopicId, SingleThreadedAgentRuntime

 
async def main() -> None:
    runtime = SingleThreadedAgentRuntime()
    # 注册代理
    """
    实际使用时才创建实例
    runtime 会在需要时调用 lambda() 来创建 ReviewerAgent 实例
    """
    await ReviewerAgent.register(
        runtime, "ReflexionAgent", lambda: ReviewerAgent(model_client=model_client)
    )
    await CoderAgent.register(
        runtime, "CoderAgent", lambda: CoderAgent(model_client=model_client)
    )
    runtime.start()
    # 发布代码编写任务
    await runtime.publish_message(
        message=CodeWritingTask(task="编写一个函数，用于计算列表中所有偶数的和。"),
        topic_id=DefaultTopicId()
    )
    await runtime.stop_when_idle()  # 当没有未处理或排队的消息时，停止运行时消息处理循环。

asyncio.run(main())

    
    