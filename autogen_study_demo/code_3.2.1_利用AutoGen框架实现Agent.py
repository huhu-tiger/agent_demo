"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码    
"""


# #兼容spyder运行
import nest_asyncio
nest_asyncio.apply()



###################################################################
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient


base_url="http://localhost:11434/v1"
model="qwen2.5:32b-instruct-q5_K_M"
api_key=  "Not-required" # 对于本地模型，API密钥不是必需的
 
#非openai的模型，需要指定模型能力
model_capabilities={ 
     "vision": False,
     "function_calling": True,
     "json_output": False,
 },


async def main():
    # 初始化OpenAI客户端（适配Ollama本地模型）
    model_client = OpenAIChatCompletionClient(
        model=model,
        base_url=base_url,
        api_key="Ollama",
        model_capabilities=model_capabilities,#非openai的模型，需要指定模型能力
    )

    # 创建一个名为"assistant"的代理
    agent = AssistantAgent( name="客服助手",  model_client=model_client  )
    
    response = await agent.run(task="中国的首都在哪？")
    print(response)
    

asyncio.run(main())


 
