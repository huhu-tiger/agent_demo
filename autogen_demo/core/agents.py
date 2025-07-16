"""
Core components for the multi-agent research report generation system.
多智能体研究报告生成系统的核心组件。

本模块实现了基于 AutoGen 框架的多智能体协作系统，用于自动生成研究报告。
系统包含多个专业智能体，每个智能体负责特定任务，通过群聊方式协作完成复杂任务。
"""

import logging
import os
import json
import functools
from typing import Any, Dict, List, Optional, Callable

from autogen_agentchat.agents import (
    AssistantAgent, # 助手智能体，使用 LLM 生成回复
    UserProxyAgent, # 用户代理智能体，可以执行工具函数
    
)
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import (
    RoundRobinGroupChat, # 轮流群聊，智能体轮流发言 
    BaseGroupChat, # 群聊类，管理多个智能体之间的对话
    SelectorGroupChat # 选择器群聊，根据条件选择智能体发言
    )
from autogen_ext.models.openai import (
    OpenAIChatCompletionClient, # OpenAI 模型客户端
    )


# 导入数据模型
from .models import  ImageAnalysis, TableData

# 导入工具函数
from .utils import (
    search_bochai,  # 博查搜索
    search_searxng,  # SearXNG 搜索
    parse_image_url,  # 图像 URL 解析
    perform_table_reasoning,  # 表格推理
    write_markdown_report,  # Markdown 报告生成
)

# 导入日志配置
from .logging_config import get_logger

# 获取日志记录器
logger = get_logger(__name__, "Orchestrator")


# --- 工具调用日志装饰器 ---
def log_tool_call(func: Callable) -> Callable:
    """
    Decorator to log tool calls with their parameters.
    装饰器，用于记录工具调用及其参数。
    
    Args:
        func: The function to decorate.
              要装饰的函数。
    
    Returns:
        The decorated function.
        装饰后的函数。
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 记录工具名称
        tool_name = func.__name__
        
        # 尝试识别调用者（智能体）
        caller_agent = "未知智能体"
        import inspect
        frame = inspect.currentframe().f_back
        while frame:
            # 检查调用栈，尝试找到智能体名称
            if 'self' in frame.f_locals:
                self_obj = frame.f_locals['self']
                if hasattr(self_obj, 'name') and isinstance(self_obj.name, str):
                    caller_agent = self_obj.name
                    break
            frame = frame.f_back
        
        # 准备参数日志（排除过大的参数）
        safe_kwargs = {}
        for k, v in kwargs.items():
            if isinstance(v, (str, int, float, bool, type(None))):
                # 对于字符串，如果太长则截断
                if isinstance(v, str) and len(v) > 100:
                    safe_kwargs[k] = v[:100] + "... (截断)"
                else:
                    safe_kwargs[k] = v
            else:
                # 对于复杂对象，只记录类型
                safe_kwargs[k] = f"<{type(v).__name__}>"
        
        # 记录调用日志
        log_message = f"智能体 [{caller_agent}] 调用工具: {tool_name}, 参数: {json.dumps(safe_kwargs, ensure_ascii=False)}"
        logger.info(log_message)
        
        try:
            # 执行原始函数
            result = func(*args, **kwargs)
            
            # 记录结果摘要（避免记录过大的结果）
            if isinstance(result, (str, int, float, bool, type(None))):
                if isinstance(result, str) and len(result) > 100:
                    result_summary = result[:100] + "... (截断)"
                else:
                    result_summary = result
            elif isinstance(result, (list, dict)):
                result_summary = f"<{type(result).__name__}> 长度: {len(result)}"
            else:
                result_summary = f"<{type(result).__name__}>"
                
            logger.info(f"智能体 [{caller_agent}] 工具 {tool_name} 执行成功, 结果: {result_summary}")
            return result
            
        except Exception as e:
            # 记录异常
            logger.error(f"智能体 [{caller_agent}] 工具 {tool_name} 执行失败: {str(e)}")
            raise
    
    return wrapper


# 装饰原始工具函数，添加日志记录功能
search_bochai_logged = log_tool_call(search_bochai)
search_searxng_logged = log_tool_call(search_searxng)
parse_image_url_logged = log_tool_call(parse_image_url)
perform_table_reasoning_logged = log_tool_call(perform_table_reasoning)
write_markdown_report_logged = log_tool_call(write_markdown_report)


# --- Agent Definitions ---
# --- 智能体定义 ---
class OrchestratorAgent:
    """
    The main agent responsible for orchestrating the report generation process.
    It decomposes the task, manages other agents, and aggregates the final report.
    
    主要负责协调报告生成过程的智能体。
    它分解任务，管理其他智能体，并汇总最终报告。
    
    工作流程:
    1. 初始化各个专家智能体（搜索、视觉、表格、报告撰写）
    2. 接收用户任务请求
    3. 协调专家智能体按顺序执行子任务
    4. 收集所有结果并生成最终报告
    
    多智能体协作机制:
    - GroupChat: 提供智能体之间的通信平台，所有对话都在群聊中进行
    - GroupChatManager: 管理群聊流程，决定下一个发言的智能体
    - UserProxyAgent: 执行实际工具调用的代理，其他智能体通过它调用工具
    - AssistantAgent: 基于大语言模型的智能体，负责特定领域的任务
    """

    def __init__(self, config_list: List[Dict[str, Any]]):
        """
        Initializes the OrchestratorAgent.
        初始化协调者智能体。
        
        Args:
            config_list: 包含各个模型配置的列表，用于初始化不同的智能体。
                        每个配置包含模型名称、API密钥等信息。
        """
        # 保存模型配置列表，供后续使用
        self.config_list = config_list
        
        # 创建用户代理，作为人类用户的代理
        # 该代理不会请求人类输入，完全自动化运行
        self.planning_agent = AssistantAgent(
            name="PlanningAgent",  # 代理名称
            system_message="""用于规划的Agent，负责执行其他智能体请求的工具函数。
你的主要职责是：
1. 接收其他智能体的请求
2. 执行相应的工具函数
3. 返回执行结果
4. 不要自行分析或解释结果，将这些任务留给专家智能体

你可以执行的工具函数包括：
- search_bochai: 使用博查API搜索新闻和信息
- search_searxng: 使用SearXNG搜索新闻和图片
- parse_image_url: 分析图像URL并生成描述
- perform_table_reasoning: 从文本中提取数据并创建表格
- write_markdown_report: 撰写Markdown格式的研究报告

请确保准确执行每个工具函数，并将结果完整返回给请求的智能体。"""
        )

        # --- 专家智能体 ---
        # 每个专家智能体负责特定的任务，使用特定的模型
        
        # 博查搜索智能体：使用博查API搜索新闻和信息
        self.search_agent_bc = AssistantAgent(
            name="SearchAgent_BC",  # 智能体名称
            system_message="""你是一名专业的搜索专家，负责使用博查API搜索相关信息。
你的任务是：
1. 使用search_bochai工具搜索与主题相关的新闻和信息
2. 提取最相关、最新的信息
3. 整理搜索结果，为报告提供高质量的素材
4. 特别关注新闻、研究报告和权威数据

请确保搜索结果全面覆盖主题的各个方面，并且信息来源可靠。""",
            llm_config={"config_list": self._get_llm_config("deepseek-v3")},  # 使用deepseek-v3模型
        )
        
        # SearXNG搜索智能体：使用SearXNG API搜索新闻和信息
        self.search_agent_sx = AssistantAgent(
            name="SearchAgent_SX",  # 智能体名称
            system_message="""你是一名专业的搜索专家，负责使用SearXNG搜索引擎搜索相关信息。
你的任务是：
1. 使用search_searxng工具搜索与主题相关的新闻(categories="general")
2. 使用search_searxng工具搜索与主题相关的图片(categories="images")
3. 确保至少进行两次不同的搜索，以获取全面的信息
4. 提取最相关、最新的信息和图片URL

请确保你的搜索结果与其他搜索智能体的结果互补，提供多样化的信息来源。""",
            llm_config={"config_list": self._get_llm_config("deepseek-v3")},  # 使用deepseek-v3模型
        )
        
        # 视觉智能体：分析图像并生成描述
        self.vision_agent = AssistantAgent(
            name="VisionAgent",  # 智能体名称
            system_message="""你是一名视觉分析专家，负责分析图像并生成描述。
你的任务是：
1. 使用parse_image_url工具分析搜索结果中的图像
2. 为每张图像生成详细、准确的中文描述
3. 识别图像中的关键元素、主题和情感
4. 提供与研究报告主题相关的图像解读

请确保你的描述客观、准确，并且与报告主题紧密相关。""",
            llm_config={"config_list": self._get_llm_config("deepseek-r1")},  # 使用deepseek-r1模型（具有推理能力）
        )
        
        # 表格推理智能体：分析数据并创建表格
        self.table_reasoner_agent = AssistantAgent(
            name="TableReasonerAgent",  # 智能体名称
            system_message="""你是一名数据分析专家，负责从文本中提取数据并创建表格。
你的任务是：
1. 使用perform_table_reasoning工具分析搜索结果中的数据
2. 从非结构化文本中识别和提取数值、统计数据和关键指标
3. 创建清晰、信息丰富的Markdown表格
4. 确保表格数据准确、有逻辑性，并支持报告的主要观点

请确保你创建的表格易于理解，并为报告提供有价值的数据支持。""",
            llm_config={"config_list": self._get_llm_config("deepseek-r1")},  # 使用deepseek-r1模型（具有推理能力）
        )
        
        # 报告撰写智能体：撰写最终的Markdown报告
        self.report_writer_agent = AssistantAgent(
            name="ReportWriterAgent",  # 智能体名称
            system_message="""你是一名专业的报告撰写者，负责整合所有信息并撰写最终报告。
你的任务是：
1. 使用write_markdown_report工具撰写全面、专业的研究报告
2. 整合搜索结果、图像分析和表格数据
3. 确保报告结构清晰，包括引言、主体内容、结论等部分
4. 使用Markdown格式，包括标题、列表、引用和表格等元素
5. 报告必须使用中文撰写，语言专业、流畅
6. 报告应包含以下部分：
   - 标题和简介
   - 行业现状分析
   - 关键数据和趋势
   - 未来发展方向
   - 结论和建议

完成报告后，请输出完整的Markdown格式报告，并在最后添加"TERMINATE"表示任务完成。""",
            llm_config={"config_list": self._get_llm_config("deepseek-r1")},  # 使用deepseek-r1模型（具有推理能力）
        )


    def _get_llm_config(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Filters the config list for a specific model.
        为特定模型筛选配置列表。
        
        Args:
            model_name: 要筛选的模型名称，如"qwen-plus"、"deepseek-v3"、"deepseek-r1"
            
        Returns:
            包含指定模型配置的列表（可能为空）
        """
        return [config for config in self.config_list if config.get("model") == model_name]

    async def run(self, topic: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Runs the entire report generation workflow.
        运行整个报告生成工作流。

        Args:
            topic: The main topic for the research report. 研究报告的主题。
            filters: Optional filters for the search (e.g., date range). 可选的搜索过滤条件（如日期范围）。

        Returns:
            The generated Markdown report as a string. 生成的Markdown报告字符串。
            
        工作流程:
        1. 创建包含所有智能体的群聊
        2. 设置群聊管理器，定义工作流程
        3. 启动对话，触发工作流程
        4. 从对话历史中提取最终报告
        
        多智能体协作原理:
        - 群聊中的智能体轮流发言，每个智能体根据自己的专长和系统提示做出回应
        - 群聊管理器根据对话上下文决定下一个发言的智能体
        - 用户代理可以调用工具函数，执行实际操作（如搜索、图像分析等）
        - 其他智能体通过向用户代理发出指令，间接调用工具函数
        - 整个过程由系统消息定义的高级工作流程指导
        """
        logger.info(f"开始为主题 '{topic}' 生成研究报告")
        
        # 创建群聊，包含所有智能体
        # 群聊是智能体之间交互的场所
        text_mention_termination = TextMentionTermination("TERMINATE")
        max_messages_termination = MaxMessageTermination(max_messages=25)
        termination = text_mention_termination | max_messages_termination
        groupchat = SelectorGroupChat(
            participants=[
                self.planning_agent,  # 用户代理（负责调用工具函数）
                self.search_agent_bc,  # 博查搜索智能体
                self.search_agent_sx,  # SearXNG搜索智能体
                self.vision_agent,  # 视觉智能体
                self.table_reasoner_agent,  # 表格推理智能体
                self.report_writer_agent,  # 报告撰写智能体
            ],
            model_client=OpenAIChatCompletionClient(model="qwen-plus"),  # 使用qwen-plus模型作为选择器
            termination_condition=termination,
        )
        
        # 获取管理者（协调者）的模型配置
        # 管理者使用qwen-plus模型，具有function-call和reasoning能力
        manager_llm_config = self._get_llm_config("qwen-plus")
        if not manager_llm_config:
            logger.error("找不到管理者的 qwen-plus 模型配置")
            raise ValueError("Configuration for qwen-plus model not found for the manager.")  # 找不到管理者的qwen-plus模型配置
        logger.info(f"Manager LLM Config: {manager_llm_config}")
        
        # 使用群聊直接启动对话
        logger.info("启动多智能体对话")
        # self.user_proxy.initiate_chat(
        #     recipient=groupchat,  # 使用群聊对象
        #     message=f"Please generate a research report on the topic: {topic}",  # 请生成关于主题的研究报告：{topic}
        # )

        response_stream = groupchat.run_stream(task=f"Please generate a research report on the topic: {topic}")
        async for msg in response_stream:
            if hasattr(msg, "source") and msg.source != "user" and hasattr(msg, "content"):
                logger.info(f"msg.content: {msg.content}")

        # 从对话历史中提取最终报告
        # 最终报告应该在ReportWriterAgent的最后一条消息中
        final_report = "No report generated."  # 默认消息：未生成报告
        
        # 获取群聊中的所有消息
        # chat_messages = groupchat.chat_history
        
        # 从最后一条消息开始向前搜索
        # for msg in reversed(chat_messages):
        #     # 检查是否是ReportWriterAgent的消息
        #     if msg["role"] == "assistant" and msg.get("name") == "ReportWriterAgent":
        #         # 检查消息内容是否包含Markdown报告
        #         content = msg.get("content", "")
        #         if "# " in content and "## " in content:  # 简单检查是否包含Markdown标题
        #             logger.info("找到了最终报告")
        #             final_report = content
        #             break
        
        # # 记录报告生成状态
        # if final_report == "No report generated.":
        #     logger.warning("未能生成报告")
        # else:
        #     logger.info("成功生成报告")
            
        return final_report
