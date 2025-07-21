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
    # response_model=ChapterReport,
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
    # reasoning_model=DeepSeek(
    #     id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
    #     name=model_config_manager.models[reasoning_model_name].model_name,  # 模型名称
    #     api_key=model_config_manager.models[reasoning_model_name].api_key,  # API密钥
    #     base_url=model_config_manager.models[reasoning_model_name].url  # API基础URL
    # ),
    # 配置代理的工具
    tools=[
        search_web_images,
        search_web_news,
    ],
    tool_choice="auto",  # 强制模型调用一个工具
    instructions=[
        "首先，使用 `search_web_news` 工具搜索关于主题的至少20条新闻。",
        "然后，使用 `search_web_images` 工具搜索至少10张相关的图片。",
        "最后，只使用前面步骤的搜索结果来生成一份专业、客观的报告。",
    ],
    system_message_role="system",
    create_default_system_message=False,  # 设置为False，因为我们提供了自定义系统消息
    system_message=dedent("""
你是一名专业的报告生成专家。你擅长通过网络搜索新闻和图片来创建专业、客观的报告。

# 报告生成要求：
1. 你必须使用提供的工具来搜索信息。不要使用你自己的知识。
2. 在报告中，你必须使用以下格式引用新闻文章：![title](url)。
3. 你必须在报告中包含图片，格式为：![图片](image_src)。
4. 报告结构必须遵循学术标准并且内容全面。
                        """),
    
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