# 导入必要的库
from agno.agent import Agent  # 导入Agno框架的Agent类
from agno.models.deepseek import DeepSeek  # 导入DeepSeek模型
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools  # 导入推理工具
from agno.tools.yfinance import YFinanceTools  # 导入Yahoo Finance工具

import sys
from pathlib import Path

# 确保可以导入config模块
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))
import config  # 使用绝对导入
from config import model_config_manager  # 导入模型配置管理器
from core.utils import search_bochai
print(model_config_manager.models)
# 导入日志模块
from core.logging_config import setup_logging, get_logger  # 使用绝对导入

# 初始化日志
logger = setup_logging()
logger.info(model_config_manager.models)

# 初始化AI代理
agent = Agent(
    # 配置DeepSeek模型，使用配置文件中的模型参数
    # model=DeepSeek(
    #     id=model_config_manager.models["deepseek-r1"].model_name,  # 模型ID
    #     name=model_config_manager.models["deepseek-r1"].model_name,  # 模型名称
    #     api_key=model_config_manager.models["deepseek-r1"].api_key,  # API密钥
    #     base_url=model_config_manager.models["deepseek-r1"].url  # API基础URL
    # ),
    model=OpenAIChat(
        id=model_config_manager.models["Qwen3-235B"].model_name,  # 模型ID
        name=model_config_manager.models["Qwen3-235B"].model_name,  # 模型名称
        api_key=model_config_manager.models["Qwen3-235B"].api_key,  # API密钥
        base_url=model_config_manager.models["Qwen3-235B"].url  # API基础URL
    ),
    # 配置代理的工具
    tools=[
        ReasoningTools(add_instructions=True),  # 添加推理工具，并包含指令
        search_bochai
    ],
    # 给模型的指令
    instructions=[
        "你是一个专业的分析师，提取用户的指令中的主题，使用博查搜索引擎搜索相关的新闻和图片,至少搜索20条",
    ],
    markdown=True,  # 启用Markdown格式输出
    show_tool_calls=True
)

# 如果是作为主程序运行
if __name__ == "__main__":
    # 运行代理并生成关于NVDA(NVIDIA)的报告

    agent.print_response(
        "搜索关于芯片产业的新闻和图片",  # 生成关于NVDA的报告
        stream=True,  # 启用流式输出
        show_full_reasoning=True,  # 显示完整的推理过程
        stream_intermediate_steps=True,  # 流式输出中间步骤
    )
    print("报告生成已完成")