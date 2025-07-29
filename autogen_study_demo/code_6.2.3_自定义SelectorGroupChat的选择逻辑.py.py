
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Mon Mar 15 08:25:46 2025
"""
# import nest_asyncio
# nest_asyncio.apply()



from typing import Sequence
import os
# from google import genai
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

import asyncio

# Ollama_model_client = OpenAIChatCompletionClient(
#     model="qwen2.5:32b-instruct-q5_K_M",      #使用qwen32模型
#     base_url=os.getenv("OWN_OLLAMA_URL_165"), #从环境变量里获得本地ollama地址
#     api_key="Ollama",
#     model_capabilities={
#         "vision": False,
#         "function_calling": True,
#         "json_output": True,
#     },
#     # timeout = 10
# )
from config import model_client as Ollama_model_client
# 模拟数据收集工具
def collect_market_data(query: str) -> str:
    # 在实际应用中，这里将调用API或数据库来收集数据
    # 这里使用模拟数据以便于示例演示
    if "人工智能" in query  or 'artificial intelligence'in query:
        return """人工智能市场数据：
        - 全球市场规模：2023年为500亿美元，预计2025年达到800亿美元
        - 主要参与者：Google、Microsoft、Baidu
        - 应用领域：医疗、金融、教育
        """
    elif "区块链" in query:
        return """区块链市场数据：
        - 全球市场规模：2023年为50亿美元，预计2025年达到150亿美元
        - 主要参与者：Coinbase、Ripple、蚂蚁区块链
        - 应用领域：金融、供应链、物联网
        """
    return "这是模拟例子，先不去找相关数据了"

# 模拟报告生成工具
def generate_report(title: str, content: str) -> str:
    # 在实际应用中，这里将生成正式的报告文档
    # 这里使用模拟数据以便于示例演示
    return f"""# {title}
    {content}
    """




# 创建规划代理，负责任务分解和分配
planning_agent = AssistantAgent(
    "PlanningAgent",  # 代理名称
    description="任务规划代理，当接收到新任务时应首先参与。",  # 描述，有助于模型选择合适的发言人
    model_client=Ollama_model_client,
    system_message="""
    你是一个任务规划代理。
    你的工作是将复杂的任务分解成更小、更易于管理的子任务。
    你的团队成员包括：
        数据收集员：负责收集和整理市场数据
        报告撰写员：负责分析结果
    
    你只负责规划和分配任务 - 自己不执行任务。

    分配任务时，请使用以下格式：
    1. <代理> : <任务>

    待所有任务完成后，总结发现并以“TERMINATE”结束。如果没有完成，不要输出含有“TERMINATE”的句子。
    """,
)

# 创建数据收集员智能体
data_collector_agent = AssistantAgent(
    "DataCollectorAgent",
    description="数据收集员，负责收集和整理市场数据",
    tools=[collect_market_data],
    model_client=Ollama_model_client,
    system_message="""
    你是一个网络搜索代理。
    你唯一的工具是collect_market_data - 使用它来查找信息。
    每次只进行一次搜索调用。
    获得结果后，不要基于它们进行任何计算。
    """,
)

# 创建报告撰写员智能体
report_writer_agent = AssistantAgent(
    "ReportWriterAgent",
    description="报告撰写员，负责分析结果",
    tools=[generate_report],
    model_client=Ollama_model_client,
    system_message="""
    你是一位专业的报告撰写员，
    根据你被分配的任务，你应该分析数据并使用提供的工具提供结果。
    你需要确保报告结构清晰、内容详实，符合专业报告的格式和要求。
    当需要更多数据或分析时，可以请求市场分析师或数据收集员提供支持。
    """,
)    
    
 # 定义终止条件
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination_condition = text_mention_termination | max_messages_termination   
  

def selector_func(messages: Sequence[AgentEvent | ChatMessage]) -> str | None:
    """
    自定义Selector 函数示例
    如果上一条消息不是来自 planning_agent，则返回 planning_agent 的名称。
    """
    if messages[-1].source != planning_agent.name:
        return planning_agent.name
    return None



selector_prompt = """选择一个智能体来执行任务。

{roles}

当前对话上下文：
{history}

阅读上述对话，然后从 {participants} 中选择一个智能体来执行下一个任务。
当任务完成后，让用户审批或否决任务。
"""  


# # 重置先前的Team, 然后传入 selector_func 函数来运行
# team = SelectorGroupChat(
#     [planning_agent, data_collector_agent, report_writer_agent],
#     model_client=Ollama_model_client,
#     termination_condition=termination_condition,
#     selector_prompt=selector_prompt,
#     allow_repeated_speaker=True,
#     selector_func=selector_func,  # 使用自定义的Selector 函数
# )

from typing import List
def candidate_func(messages: Sequence[AgentEvent | ChatMessage]) -> List[str]:
    # 保持planning_agent作为第一个规划任务的人
    if messages[-1].source == "user":
        return [planning_agent.name]

    # 如果上一个代理是planning_agent，并且明确要求web_search_agent
    # 或data_analyst_agent或两者（在重新规划或重新分配任务的情况下）
    # 则返回那些特定的代理
    last_message = messages[-1]
    if last_message.source == planning_agent.name:
        participants = []
        if data_collector_agent.name in last_message.content:
            participants.append(data_collector_agent.name)
        if report_writer_agent.name in last_message.content:
            participants.append(report_writer_agent.name)
        if participants:
            return participants  # SelectorGroupChat将从剩下的两个代理中选择。

    # 我们可以假设一旦web_search_agent和data_analyst_agent完成了他们的轮次，任务就结束了，
    # 因此我们发送planning_agent来终止聊天
    previous_set_of_agents = set(message.source for message in messages)
    if data_collector_agent.name in previous_set_of_agents and report_writer_agent.name in previous_set_of_agents:
        return [planning_agent.name]

    # 如果没有条件满足，则返回所有代理
    return [planning_agent.name, data_collector_agent.name, report_writer_agent.name]


# 重置之前的团队并再次运行聊天，这次使用选择器函数。
team = SelectorGroupChat(
    [planning_agent, data_collector_agent, report_writer_agent],
    model_client=Ollama_model_client,
    termination_condition=termination_condition,
    candidate_func=candidate_func,
)





  
 

async def run_agent():

    # 定义任务
    task = "请分析当前人工智能领域的最新科技趋势，并生成一份市场研究报告。"

    # 运行团队
    await Console(team.run_stream(task=task))   
        


# 运行代理
if __name__ == "__main__":
    asyncio.run(run_agent())    


