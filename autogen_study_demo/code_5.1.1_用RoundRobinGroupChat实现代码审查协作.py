
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 13 11:14:58 2025
"""

# import nest_asyncio
# nest_asyncio.apply()  # 应用nest_asyncio以便在Jupyter、IPython等环境中支持异步IO

import os

from autogen_agentchat.agents import AssistantAgent  # 导入助理代理类
from autogen_agentchat.conditions import TextMentionTermination  # 导入文本提及终止条件
from autogen_agentchat.teams import RoundRobinGroupChat  # 导入轮询小组聊天模式
from autogen_ext.models.openai import OpenAIChatCompletionClient  # 导入OpenAI的客户端模型
from autogen_agentchat.ui import Console




# 创建硅基流动客户端
# Qwen_model_client = OpenAIChatCompletionClient(
#     base_url="https://硅基流动接口地址"
#     model='Qwen/Qwen2.5-7B-Instruct',  # 模型名称
#     api_key=os.getenv("SILICON_FLOW_API_KEY"),  # 使用环境变量中的API密钥
#     model_capabilities={
#             "vision": False,
#             "function_calling": True,
#             "json_output": True,
#         },
#     # timeout = 30
# )

from config import model_client as Qwen_model_client
# 创建Google Gemini模型客户端


# 创建主代码审查员代理
lead_reviewer = AssistantAgent(
    "lead_reviewer",
    model_client=Qwen_model_client,
    system_message="""你是主要代码审查员。你的任务是审查代码以发现潜在问题，提出改进建议，并确保其符合项目标准。
    """,
)

from config import model_client_v3 as model_client

# 创建助理代码审查员代理
assistant_reviewer = AssistantAgent(
    "assistant_reviewer",
    model_client=model_client,
   system_message="""你是助理代码审查员。通过检查代码格式、识别可能的错误以及验证文档是否完整来协助主要审查员。
   如果代码满足所有项目要求且无需进一步修改，中文回复，请在回复结尾处包含"APPROVED".""",
)

# 定义终止条件，当主评审代理在回复中提到"APPROVED"时停止
text_termination = TextMentionTermination("APPROVED")

# 创建代码审查团队
code_review_team = RoundRobinGroupChat([lead_reviewer, assistant_reviewer], termination_condition=text_termination)

# 提供代码片段作为任务输入,此处以一段Python代码作为任务输入，模拟代码待审查场景
code_snippet ="""
def login(user, password):
    if user == "admin" and password == "admin123":
        return True
    else:
        return False
"""


# 启动代码审查任务
async def run_review():
    # result = await code_review_team.run(task=f"审查以下Python代码片段:\n\n{code_snippet}")
    # return result

    stream = await Console(code_review_team.run_stream(task=f"审查以下Python代码片段:\n\n{code_snippet}"))
    return stream

#5.1.4
# from autogen_agentchat.base import TaskResult
# async def run_review():
#     async for message in code_review_team.run_stream(task=f"审查以下Python代码片段:\n\n{code_snippet}"):  # 使用run_stream()方法运行团队并获取消息流
#         if isinstance(message, TaskResult):  # 如果消息是任务结果类型
#             print("停止原因:", message.stop_reason)  # 打印停止原因
#             return message
#         else:
#             print(message)  # 打印消息内容



# 使用 asyncio.run() 在脚本中运行
import asyncio
result = asyncio.run(run_review())
# print(result.messages)
# for one in result.messages:
#     print(f"-----------\n{one.source}:{one.content}")

# print(result.messages[-1].content)
# len(result.messages)
