# 导入必要的库
from agno.agent import Agent  # 导入Agno框架的Agent类
from agno.models.deepseek import DeepSeek  # 导入DeepSeek模型
from agno.models.openai import OpenAIChat
from agno.models.deepseek import DeepSeek
from agno.tools.reasoning import ReasoningTools  # 导入推理工具
from agno.models.groq import Groq
from textwrap import dedent
import sys
from pathlib import Path
from core.models import ChapterReport

# 确保可以导入config模块
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))
import config  # 使用绝对导入
from config import model_config_manager  # 导入模型配置管理器
from core.utils import search_web_news,search_web_images
print(model_config_manager.models)
# 导入日志模块
from core.logging_config import setup_logging, get_logger  # 使用绝对导入
import time
md_file = f"{int(time.time())}.md"
print(md_file)
# 初始化日志
logger = setup_logging()
logger.info(model_config_manager.models)

model_name="Qwen3-235B"
reasoning_model_name="deepseek-r1"
# 初始化AI代理
agent = Agent(
    stream=False,
    save_response_to_file="1.md",
    response_model=ChapterReport,
    # 配置DeepSeek模型，使用配置文件中的模型参数
    # model=DeepSeek(
    #     id=model_config_manager.models["deepseek-r1"].model_name,  # 模型ID
    #     name=model_config_manager.models["deepseek-r1"].model_name,  # 模型名称
    #     api_key=model_config_manager.models["deepseek-r1"].api_key,  # API密钥
    #     base_url=model_config_manager.models["deepseek-r1"].url  # API基础URL
    # ),
    description=dedent("""\
生成报告的agent
"""),
    model=OpenAIChat(
        id=model_config_manager.models[model_name].model_name,  # 模型ID
        name=model_config_manager.models[model_name].model_name,  # 模型名称
        api_key=model_config_manager.models[model_name].api_key,  # API密钥
        base_url=model_config_manager.models[model_name].url,  # API基础URL
        role_map={        
            "system": "system",
            "user": "user",
            "assistant": "assistant",
            "tool": "tool",
            "model": "assistant"
            }
    ),
    reasoning_model=DeepSeek(
        id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
        name=model_config_manager.models[reasoning_model_name].model_name,  # 模型名称
        api_key=model_config_manager.models[reasoning_model_name].api_key,  # API密钥
        base_url=model_config_manager.models[reasoning_model_name].url  # API基础URL
    ),
    # 配置代理的工具
    tools=[
        # ReasoningTools(add_instructions=True),  # 添加推理工具，并包含指令
        search_web_images,
        search_web_news,
    ],
    system_message_role="system",
    create_default_system_message=False,
    system_message=dedent("""
你是一名专业的报告生成专家，擅长通过网络搜索新闻和图片，并结合搜索结果生成一篇专业客观的报告
# 步骤如下：
## 1. 使用[search_web_news]搜索相关的新闻,至少搜索20条
## 2. 使用[search_web_images]搜索相关的新闻图片,至少搜索10条
## 3. 仅使用前2步的搜索结果生成一篇专业客观的报告
# 报告生成要求：
## 1. 只能使用 网络搜索到的图片和新闻数据，不可以自己生成数据
## 1. 小节后面必须加入引用的新闻链接，格式![title](url)
## 2. 参考图片的描述信息，在报告合适位置加入图片链接，格式![图片](image_src)
## 3. 报告结构应遵循学术标准，内容要丰富

                        """),
    
    # markdown=True,  # 启用Markdown格式输出
    show_tool_calls=True
)

# 如果是作为主程序运行
if __name__ == "__main__":
    # 运行代理并生成关于NVDA(NVIDIA)的报告

    agent.print_response(
        "芯片产业的报告",  # 生成关于NVDA的报告
        stream=True,  # 启用流式输出
        show_full_reasoning=True,  # 显示完整的推理过程
        stream_intermediate_steps=True,  # 流式输出中间步骤
    )
    print("报告生成已完成")
    print(agent.run_response.content)
    print(dir(agent.run_response.content))
    print(agent.run_response.__dict__)
    dict_chapter=agent.run_response.to_dict()
    for key in dict_chapter.keys():
        print(f"key:{key},value:{dict_chapter[key]}")