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
from .config import model_config_manager

from autogen_agentchat.agents import AssistantAgent
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
    save_report_to_file,
)

# 导入日志配置
from .logging_config import get_logger

# 获取日志记录器
logger = get_logger(__name__, "Orchestrator")




# --- Agent Definitions ---
# --- 智能体定义 ---
class OrchestratorAgent:

    def __init__(self, config_list: Dict[str, OpenAIChatCompletionClient]):
        """
        Initializes the OrchestratorAgent.
        初始化协调者智能体。
        
        Args:
            config_list: 包含各个模型配置的列表，用于初始化不同的智能体。
                        每个配置包含模型名称、API密钥等信息。
        """
        # 保存模型配置列表，供后续使用
        self.config_list = config_list
        # logger.info(f"模型配置列表: {self.config_list}")
        for model_name, model_client in self.config_list.items():
            logger.info(f"模型名称: {model_name}, 模型客户端: {model_client._raw_config}")



        self.planning_agent = AssistantAgent(
            name="PlanningAgent",  # 代理名称
            system_message=f"""你是一个任务规划智能体,你的工作是将复杂的任务分解为更小的、可管理的子任务。
                                       
你只计划和委派任务，而不自己执行它们
                                
分配任务时，请使用此格式:
1. <agent> : <task>
                                        
当所有智能体把任务完成后，再总结结果以"TERMINATE"结束。                

""",

            # model_client=self.config_list["qwen-plus"]
            # model_client=self.config_list["deepseek-r1"]
            model_client=self.config_list["Qwen3-235B"]
        )


        # --- 专家智能体 ---
        # 每个专家智能体负责特定的任务，使用特定的模型
        
        # 博查搜索智能体：使用博查API搜索新闻和信息
        self.search_agent_bc = AssistantAgent(
            name="SearchAgent_BC",  # 智能体名称
            system_message="""你是一名专业的搜索专家，负责使用博查API搜索章节名称相关的新闻和信息。
你的任务是：
1. 使用search_bochai工具搜索与主题相关的新闻和信息
2. 提取最相关、最新的信息
3. 整理搜索结果，为报告提供高质量的素材
4. 特别关注新闻、研究报告和权威数据

请确保搜索结果全面覆盖主题的各个方面，并且信息来源可靠。""",
            # model_client=self.config_list["deepseek-v3"],
            model_client=self.config_list["Qwen3-235B"],
            tools=[search_bochai]
        )
        
        # SearXNG搜索智能体：使用SearXNG API搜索新闻和信息
        self.search_agent_sx = AssistantAgent(
            name="SearchAgent_SX",  # 智能体名称
            system_message="""你是一名专业的搜索专家，负责使用SearXNG搜索引擎搜索章节名称相关信息。
你的任务是：
1. 使用search_searxng工具搜索与章节相关的新闻(categories="general")
2. 使用search_searxng工具搜索与章节相关的图片(categories="images")
3. 确保至少进行两次不同的搜索，以获取图片与新闻的信息
4. 提取最相关、最新的信息和图片URL

请确保你的搜索结果与其他搜索智能体的结果互补，提供多样化的信息来源。""",
            # model_client=self.config_list["deepseek-v3"],
            model_client=self.config_list["Qwen3-235B"],
            tools=[search_searxng]
        )
        
        # 视觉智能体：分析图像并生成描述
        self.vision_agent = AssistantAgent(
            name="VisionAgent",  # 智能体名称
            system_message="""你是一名视觉分析专家，负责分析图像并生成描述。
你的任务是：
1. 使用parse_image_url工具分析SearchAgent_SX与SearchAgent_BC 搜索出的图片
2. 分析图片的描述，并返回图片的描述

请确保你的描述客观、准确，并且与报告主题紧密相关。""",
            # model_client=self.config_list["qwen-vl"],
            model_client=self.config_list["Qwen3-235B"],
            tools=[parse_image_url]
        )
        
        # 表格推理智能体：分析数据并创建表格
        self.table_reasoner_agent = AssistantAgent(
            name="TableReasonerAgent",  # 智能体名称
            system_message="""你是一名数据分析专家，负责从文本中提取数据并创建表格。
你的任务是：
1. 分析搜索结果中的数据
2. 从非结构化文本中识别和提取数值、统计数据和关键指标
3. 创建清晰、信息丰富的Markdown表格
4. 确保表格数据准确、有逻辑性，并支持报告的主要观点

请确保你创建的表格易于理解，并为报告提供有价值的数据支持。""",
            model_client=self.config_list["deepseek-r1"]
        )
        
        # 报告撰写智能体：撰写最终的Markdown报告
        self.chapter_planner_agent = AssistantAgent(
            name="ChapterPlannerAgent",  # 智能体名称
            system_message="""你是一名专业的章节内容撰写者，负责收集网络新闻与图片进行整理，生成章节内容。
  ## 章节内容生成步骤：
   1. 根据章节名称，使用[SearchAgent_BC]和[SearchAgent_SX]搜索章节名称相关新闻和图片
   2. 将搜索到的图片URL发送给[VisionAgent]进行分析，分析图片的描述
   3. 将搜索到的新闻发送给[TableReasonerAgent]进行表格整理
   4. 将前3步的数据，使用[ChapterWriterAgent]整理为完整章节内容，采用markdown格式，段落后面要加入引用链接，引用链接和图片链接要使用markdown格式，引用链接要使用[链接文本](链接地址)格式

请确保你生成的章节内容符合章节名称，并且内容丰富、有价值。""",
            # model_client=self.config_list["deepseek-r1"]
            model_client=self.config_list["Qwen3-235B"],
            # tools=[save_report_to_file],
            # reflect_on_tool_use=True
        )

        self.chapter_writer_agent = AssistantAgent(
            name="ChapterWriterAgent",  # 智能体名称
            system_message="""你是一名专业的章节内容撰写者，负责将网络新闻与图片进行整理，生成章节内容。
            
            """,
            model_client=self.config_list["Qwen3-235B"],
        )

        # 章节规划智能体：生成章节名称
        self.chapter_name_agent = AssistantAgent(
            name="ChapterNameAgent",
            system_message="""你是一名章节名称生成专家，负责根据用户输入的研究主题生成三个相关的章节名称。
            要求：
            1. 章节名称应使用中文，简洁且具有专业度
            2. 三个章节应相互独立又层次分明，覆盖主题的核心方面
            3. 输出时以有序列表形式返回，每行一个章节名称\n4. 输出后发送到其他智能体继续流程，不需要撰写任何章节内容
            """,
            # model_client=self.config_list["deepseek-v3"],
            model_client=self.config_list["Qwen3-235B"],
        )

                # 报告保存智能体：将报告写入文件
        self.report_generator_agent = AssistantAgent(
            name="ReportGeneratorAgent",
            system_message="""你是一名报告生成专家，负责将多个章节的内容合并成最终的Markdown报告。
            你的任务：
            1. 接收多个章节的内容
            2. 将多个章节的内容合并成最终的Markdown报告,
            # model_client=self.config_list["qwen-plus"]
            """,
            model_client=self.config_list["Qwen3-235B"],
        )
        
        # 报告保存智能体：将报告写入文件
        self.report_saver_agent = AssistantAgent(
            name="ReportSaverAgent",
            system_message="""你是一名文件处理专家，负责将最终的Markdown报告保存到本地文件。
            你的任务：
            1. 接收多个章节的内容
            2. 调用 save_report_to_file 工具将报告保存为 report.md
            3. 保存成功后，回复 'FILE_SAVED' 以及文件路径""",
            # model_client=self.config_list["qwen-plus"],
            model_client=self.config_list["Qwen3-235B"],
            tools=[save_report_to_file],
            reflect_on_tool_use=True,
        )



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
        2. 运行三阶段报告生成流程：
           - 章节规划：生成三个相关章节的名称
           - 逐章节生成：对每个章节搜索、分析并生成内容
           - 报告合并：将所有章节内容合并成最终报告
        """
        logger.info(f"开始为主题 '{topic}' 生成研究报告")
        
        # 创建群聊，包含所有智能体
        # 群聊是智能体之间交互的场所
        text_mention_termination = TextMentionTermination("TERMINATE") | TextMentionTermination("FILE_SAVED") | TextMentionTermination("报告保存完成")
        max_messages_termination = MaxMessageTermination(max_messages=60)
        termination = text_mention_termination | max_messages_termination
        



        groupchat = SelectorGroupChat(
            participants=[
                self.planning_agent, # 规划智能体
                self.chapter_name_agent,  # 章节名称生成智能体
                self.search_agent_bc, # 博查搜索智能体
                self.search_agent_sx, # SearXNG搜索智能体
                self.vision_agent, # 视觉智能体
                self.table_reasoner_agent, # 表格推理智能体
                self.chapter_planner_agent, # 章节规划智能体
                self.chapter_writer_agent, # 章节内容撰写智能体

                self.report_generator_agent, # 报告生成智能体
                self.report_saver_agent,  # 报告保存智能体
            ],
            # model_client=self.config_list["qwen-plus"],  # 使用qwen-plus模型作为选择器
            model_client=self.config_list["Qwen3-235B"],  # 使用qwen-plus模型作为选择器
            termination_condition=termination,
                    # 构建初始任务提示，融入协调者系统提示的内容
            selector_prompt = f"""需要引导团队完成关于主题的研究报告生成，请按照以下三个阶段进行：
# 1. 章节规划阶段：
   - 首先，指导ChapterNameAgent一次性生成至少三个主题相关的章节名称
   - 确保章节名称相互关联、层次分明，全面覆盖主题的关键方面

# 2. 章节生成阶段:
   - 根据章节名称数量，多次调用[ChapterPlannerAgent]分别生成对应章节名称的章节完整内容

#3. 报告合并阶段：
   - 指导[ReportWriterAgent]将第2步生成的所有章节内容组成最终报告
   - 确保最终报告包含章节中标题、导言、结论，以及所有图片、表格和引用链接

# 4. 报告保存阶段：
   - 指导[ReportSaverAgent]将第3步的报告保存为 report.md
   - 保存成功后，ReportSaverAgent 回复 'FILE_SAVED'

请开始章节名称生成阶段，让ChapterNameAgent生成三个章节名称。"""
        )

        # 启动多智能体对话，实现基于章节的报告生成流程
        logger.info("启动多智能体对话，实现基于章节的报告生成")



        final_report = "No report generated."  # 默认消息：未生成报告
        report_messages = []
        
        try:
            # 运行群聊并收集所有消息
            response_stream = groupchat.run_stream(task=topic)
            async for msg in response_stream:
                # 安全地访问消息内容，避免属性错误
                message_content = ""
                try:
                    content_attr_msg = getattr(getattr(msg, 'message', None), 'content', None)  # type: ignore[attr-defined]
                    if (content_attr := getattr(msg, 'content', None)):
                        message_content = str(content_attr)
                    elif content_attr_msg:
                        message_content = str(content_attr_msg)
                    elif isinstance(msg, dict) and 'content' in msg:
                        message_content = str(msg['content'])
                    else:
                        # 最后尝试通过字符串化整个消息对象
                        message_content = str(msg)
                        # 如果消息过长，只保留部分
                        if len(message_content) > 2000:
                            message_content = message_content[:2000] + "..."

                    # 如果内容仍包含Unicode编码形式的中文（例如 \u4e2d），尝试解码
                    if '\\u' in message_content:
                        try:
                            message_content = bytes(message_content, 'utf-8').decode('unicode_escape')
                        except Exception:
                            pass

                    if message_content:
                        # 仅记录agent与工具调用，不输出工具返回内容
                        agent_names = [
                            self.planning_agent.name,
                            self.chapter_name_agent.name,
                            self.search_agent_bc.name,
                            self.search_agent_sx.name,
                            self.vision_agent.name,
                            self.table_reasoner_agent.name,
                            self.chapter_writer_agent.name,
                            self.report_generator_agent.name,
                            self.report_saver_agent.name,
                        ]
                        tool_names = [
                            "search_bochai",
                            "search_searxng",
                            "parse_image_url",
                            "perform_table_reasoning",
                            "save_report_to_file",
                        ]

                        agent_in_msg = next((a for a in agent_names if a in message_content), None)
                        for tool in tool_names:
                            if tool in message_content:
                                logger.info(f"{agent_in_msg or 'UnknownAgent'} 调用了工具 {tool}")
                                break  # 一条消息通常只包含一次工具调用

                        # 收集消息以便后续提取报告，但不记录内容
                        report_messages.append(message_content)
                        
                        # 检测最终报告
                        if "# " in message_content and "TERMINATE" in message_content:
                            final_report = message_content.replace("TERMINATE", "").strip()
                            logger.info("找到了最终报告")
                            # 不立即break，等待文件保存，但记录报告
                        if "FILE_SAVED" in message_content:
                            logger.info("报告已保存成功，结束对话")
                            return final_report
                except Exception as content_err:
                    logger.warning(f"处理消息内容时出错: {content_err}")
        except Exception as e:
            logger.error(f"生成报告过程中出错: {e}")
            
        # 如果没有找到包含TERMINATE的最终报告，尝试从最后几条消息中提取
        if final_report == "No report generated.":
            logger.warning("未找到带有TERMINATE标记的最终报告，尝试从最后的消息中提取")
            # 从后向前检查消息
            for message in reversed(report_messages):
                if "# " in message and "## " in message and len(message) > 500:
                    # 这看起来像是一个报告（包含标题且长度合理）
                    final_report = message
                    logger.info("从消息历史中提取了可能的最终报告")
                    break
                    
        # 记录报告生成状态
        if final_report == "No report generated.":
            logger.warning("未能生成报告")
        else:
            report_length = len(final_report)
            logger.info(f"成功生成报告，长度: {report_length} 字符")
            
        return final_report
