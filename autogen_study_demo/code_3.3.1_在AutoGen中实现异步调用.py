"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码    
"""

# #兼容spyder运行
# import nest_asyncio
# nest_asyncio.apply()


# 导入必要的模块和类。
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import UserMessage
import os
import asyncio
from config import model_client

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


# 创建一个基于"gemini-2.0-flash"模型的客户端，使用环境变量中的API密钥进行初始化。
# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了GEMINI_API_KEY
# )


# 定义一个异步函数，用于生成回复。它接收一个问题提示作为输入，并返回模型的回答。
async def async_generate(prompt):
    """异步生成文本"""
    # 初始化客服助手代理，使用上述创建的模型客户端。
    agent = AssistantAgent("客服助手", model_client=model_client,
                           tools=[basic_customer_service],

                           )
    # 使用模型客户端根据用户消息创建回答。
    response = await agent.run(task=prompt) 
    return response.messages[-1].content

# 主异步函数，用于并发处理多个用户的请求。
async def main():
    # 预定义一些常见问题及其对应的答案。
    questions = ["退货政策", "推荐一款笔记本电脑"]

    # 根据预定义的问题列表创建任务列表。每个任务都是调用async_generate函数来获取对应问题的答案。
    tasks = [async_generate(query) for query in questions]
    
    # 并发执行所有任务，并收集它们的结果。
    results = await asyncio.gather(*tasks)
    
    # 将每个问题与其对应的答案配对并打印出来。
    print(f"questions: {questions}")
    print(f"results: {results}")
    for query, result in zip(questions, results):
        print(f"问题：{query}\n回答：{result}\n")
    return  results   




# 当脚本被直接运行时，启动事件循环并执行main函数。
if __name__ == "__main__":
    results = asyncio.run(main())

    
    
      
