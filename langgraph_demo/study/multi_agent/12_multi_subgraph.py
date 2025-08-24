# -*- coding: utf-8 -*-
"""
LangGraph 多智能体示例 - 子图方式实现
学习要点：多智能体架构、子图实现、状态管理、最终结果共享
参考：https://langchain-ai.github.io/langgraph/concepts/multi_agent/#multi-agent-architectures

本示例演示了如何使用 LangGraph 构建多智能体系统，每个智能体都是独立的子图，
智能体间只共享最终结果，实现了良好的模块化和状态隔离。

架构特点：
1. 主图负责协调各个智能体子图
2. 每个智能体子图有独立的状态空间
3. 智能体间通过共享消息传递最终结果
4. 支持流式执行和实时状态监控
"""

import os
import sys
import time
import json
from typing import TypedDict, Annotated, Literal
import operator

# 添加当前脚本所在目录到路径，确保能导入本目录下的 config.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

# 导入必要的库
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.types import Command
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 获取日志器
logger = config.logger

# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 初始化语言模型
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,  # 较低的温度确保输出的一致性
    max_tokens=1000   # 限制输出长度
)

# ===== 配置和工具函数 =====

# 新增：是否以 JSON（SSE 风格）输出流
# 当设置为 True 时，会输出 Server-Sent Events 格式的 JSON 流
# 便于前端实时接收和显示执行状态
JSON_STREAM = True

def sse_send(event: str, payload: dict):
    """
    以 SSE 风格输出一条 JSON 事件
    
    SSE (Server-Sent Events) 格式：
    event: <event-name>\n
    data: {json}\n\n
    
    Args:
        event: 事件名称，如 'log', 'state', 'start', 'end'
        payload: 要发送的数据字典
    """
    try:
        data_str = json.dumps(payload, ensure_ascii=False)
    except Exception as e:
        data_str = json.dumps({"error": f"无法序列化payload: {str(e)}"}, ensure_ascii=False)
    print(f"event: {event}")
    print(f"data: {data_str}")
    print()
    sys.stdout.flush()  # 确保立即输出

def serialize_state_snapshot(state: dict) -> dict:
    """
    提取可序列化的关键状态快照，避免复杂对象导致的 JSON 化失败
    
    这个函数的作用是：
    1. 提取状态中的关键字段
    2. 处理复杂对象（如 Message 对象）
    3. 限制数据长度，防止输出过大
    4. 确保 JSON 序列化成功
    
    Args:
        state: 原始状态字典
        
    Returns:
        处理后的安全状态字典
    """
    safe_state = {}
    
    # 提取基本状态字段
    for key in ["current_agent", "step_count", "next_agent", "task_description"]:
        if key in state:
            safe_state[key] = state[key]
    
    # 处理共享消息 - 将 Message 对象转换为简单字典
    msgs = state.get("shared_messages", []) or []
    safe_msgs = []
    for m in msgs:
        content = getattr(m, "content", None)
        if content is None:
            content = str(m)
        msg_type = m.__class__.__name__ if hasattr(m, "__class__") else "Message"
        
        # 限制长度，防止过长输出
        if isinstance(content, str) and len(content) > 1000:
            content = content[:1000] + "..."
        safe_msgs.append({"type": msg_type, "content": content})
    safe_state["shared_messages"] = safe_msgs
    
    # 执行日志仅保留最后 3 条，避免日志过多
    logs = state.get("execution_log", [])
    if isinstance(logs, list):
        safe_state["execution_log"] = logs[-3:]
    else:
        safe_state["execution_log"] = []
    
    return safe_state

def log_message(message: str, level: str = "INFO", agent: str = "SYSTEM", line_number: int = None):
    """
    使用 config.logger 记录日志，同时支持 JSON 流式输出
    
    这个函数实现了双重日志记录：
    1. 使用 config.logger 记录到日志文件（生产环境）
    2. 当 JSON_STREAM=True 时，同时发送 SSE 事件（开发调试）
    
    Args:
        message: 日志消息
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, SUCCESS, START, END)
        agent: 智能体名称
        line_number: 代码行号（可选，会自动获取）
    """
    import inspect
    
    # 如果没有提供行号，自动获取调用位置的行号
    if line_number is None:
        # 获取调用栈信息
        frame = inspect.currentframe()
        # 向上查找调用者
        caller_frame = frame.f_back
        if caller_frame:
            line_number = caller_frame.f_lineno
        else:
            line_number = 0
    
    timestamp = time.strftime("%H:%M:%S")
    
    # 使用 config.logger 记录日志
    log_message_full = f"[{agent}:L{line_number}] {message}"
    
    # 根据级别调用相应的日志方法
    if level == "DEBUG":
        logger.debug(log_message_full)
    elif level == "INFO":
        logger.info(log_message_full)
    elif level == "WARNING":
        logger.warning(log_message_full)
    elif level == "ERROR":
        logger.error(log_message_full)
    else:
        logger.info(log_message_full)
    
    # 如果启用 JSON 流式输出，同时发送 SSE 事件
    if JSON_STREAM:
        emoji_map = {
            "INFO": "ℹ️",
            "DEBUG": "🔍",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "SUCCESS": "✅",
            "START": "🚀",
            "END": "🏁"
        }
        emoji = emoji_map.get(level, "ℹ️")
        
        payload = {
            "timestamp": timestamp,
            "level": level,
            "agent": agent,
            "line": line_number,
            "message": message,
            "emoji": emoji
        }
        sse_send("log", payload)

def analyze_chunk_content(chunk, chunk_count: int):
    """
    分析并打印chunk的详细内容
    
    这个函数用于调试流式执行过程，详细分析每个数据块的内容：
    1. 识别数据类型
    2. 分析数据结构
    3. 提取关键信息
    4. 智能截断长内容
    
    Args:
        chunk: 流式数据块
        chunk_count: 数据块序号
    """
    log_message(f"=== Chunk {chunk_count} 详细分析 ===", "DEBUG", "SYSTEM")
    log_message(f"类型: {type(chunk)}", "DEBUG", "SYSTEM")
    
    if isinstance(chunk, dict):
        # 处理字典类型
        log_message(f"字典类型，包含 {len(chunk)} 个键", "DEBUG", "SYSTEM")
        log_message(f"键列表: {list(chunk.keys())}", "DEBUG", "SYSTEM")
        
        for key, value in chunk.items():
            value_type = type(value).__name__
            log_message(f"键 '{key}' (类型: {value_type}):", "DEBUG", "SYSTEM")
            
            if isinstance(value, str):
                # 字符串类型，限制长度
                if len(value) > 300:
                    log_message(f"  值: {value[:300]}...", "DEBUG", "SYSTEM")
                else:
                    log_message(f"  值: {value}", "DEBUG", "SYSTEM")
            elif isinstance(value, list):
                # 列表类型，只显示前几个项目
                log_message(f"  列表长度: {len(value)}", "DEBUG", "SYSTEM")
                for i, item in enumerate(value[:3]):  # 只显示前3个
                    log_message(f"  项目 {i}: {item}", "DEBUG", "SYSTEM")
                if len(value) > 3:
                    log_message(f"  ... 还有 {len(value) - 3} 个项目", "DEBUG", "SYSTEM")
            elif isinstance(value, dict):
                # 嵌套字典
                log_message(f"  字典，包含 {len(value)} 个键: {list(value.keys())}", "DEBUG", "SYSTEM")
            else:
                # 其他类型
                log_message(f"  值: {value}", "DEBUG", "SYSTEM")
    
    elif hasattr(chunk, 'values'):
        # 处理包含 values 属性的对象（如状态对象）
        log_message("对象类型，包含 'values' 属性", "DEBUG", "SYSTEM")
        values = chunk.values
        if isinstance(values, dict):
            log_message(f"values 是字典，包含 {len(values)} 个键: {list(values.keys())}", "DEBUG", "SYSTEM")
            for key, value in values.items():
                if isinstance(value, str) and len(value) > 200:
                    log_message(f"  {key}: {value[:200]}...", "DEBUG", "SYSTEM")
                else:
                    log_message(f"  {key}: {value}", "DEBUG", "SYSTEM")
        else:
            log_message(f"values 内容: {values}", "DEBUG", "SYSTEM")
    
    else:
        # 处理其他类型的对象
        log_message(f"其他类型对象", "DEBUG", "SYSTEM")
        log_message(f"字符串表示: {str(chunk)}", "DEBUG", "SYSTEM")
        if hasattr(chunk, '__dict__'):
            log_message(f"__dict__: {chunk.__dict__}", "DEBUG", "SYSTEM")
    
    log_message(f"=== Chunk {chunk_count} 分析完成 ===", "DEBUG", "SYSTEM")

def print_agent_state(agent_name: str, state: dict, stage: str = "执行中"):
    """
    打印智能体状态
    
    Args:
        agent_name: 智能体名称
        state: 状态字典
        stage: 执行阶段
    """
    config = get_agent_config(agent_name)
    emoji = config.get("emoji", "🔧")
    name = config.get("name", agent_name)
    
    log_message(f"=== {emoji} {name} 状态 ({stage}) ===", "INFO", "STATE")
    
    if isinstance(state, dict):
        for key, value in state.items():
            if isinstance(value, str):
                if len(value) > 200:
                    log_message(f"  {key}: {value[:200]}...", "INFO", "STATE")
                else:
                    log_message(f"  {key}: {value}", "INFO", "STATE")
            elif isinstance(value, list):
                log_message(f"  {key}: 列表，包含 {len(value)} 个项目", "INFO", "STATE")
                for i, item in enumerate(value[:2]):  # 只显示前2个
                    if isinstance(item, dict):
                        log_message(f"    项目 {i}: 字典 {list(item.keys())}", "INFO", "STATE")
                    else:
                        log_message(f"    项目 {i}: {str(item)[:100]}", "INFO", "STATE")
                if len(value) > 2:
                    log_message(f"    ... 还有 {len(value) - 2} 个项目", "INFO", "STATE")
            elif isinstance(value, dict):
                log_message(f"  {key}: 字典，包含 {len(value)} 个键: {list(value.keys())}", "INFO", "STATE")
            else:
                log_message(f"  {key}: {value}", "INFO", "STATE")
    else:
        log_message(f"  状态类型: {type(state)}", "INFO", "STATE")
        log_message(f"  状态内容: {str(state)[:200]}", "INFO", "STATE")
    
    log_message(f"=== {name} 状态结束 ===", "INFO", "STATE")

def print_state_transition(from_agent: str, to_agent: str, transition_data: dict = None):
    """
    打印状态转换过程
    
    Args:
        from_agent: 源智能体
        to_agent: 目标智能体
        transition_data: 转换数据
    """
    from_config = get_agent_config(from_agent)
    to_config = get_agent_config(to_agent)
    
    log_message(f"🔄 状态转换: {from_config.get('emoji', '🔧')} {from_config.get('name', from_agent)} → {to_config.get('emoji', '🔧')} {to_config.get('name', to_agent)}", "INFO", "TRANSITION")
    
    if transition_data:
        log_message(f"  转换数据: {transition_data}", "DEBUG", "TRANSITION")
    
    log_message(f"  转换时间: {time.strftime('%H:%M:%S')}", "INFO", "TRANSITION")

def print_main_state_snapshot(state: dict, step: str = "当前"):
    """
    打印主图状态快照
    
    Args:
        state: 主图状态
        step: 步骤描述
    """
    log_message(f"📊 主图状态快照 ({step})", "INFO", "MAIN_STATE")
    
    if isinstance(state, dict):
        # 基本信息
        current_agent = state.get("current_agent", "unknown")
        step_count = state.get("step_count", 0)
        next_agent = state.get("next_agent", "unknown")
        task_description = state.get("task_description", "")
        
        log_message(f"  当前智能体: {current_agent}", "INFO", "MAIN_STATE")
        log_message(f"  步骤计数: {step_count}", "INFO", "MAIN_STATE")
        log_message(f"  下一个智能体: {next_agent}", "INFO", "MAIN_STATE")
        log_message(f"  任务描述: {task_description[:100]}", "INFO", "MAIN_STATE")
        
        # 共享消息
        shared_messages = state.get("shared_messages", [])
        log_message(f"  共享消息数量: {len(shared_messages)}", "INFO", "MAIN_STATE")
        for i, msg in enumerate(shared_messages[-2:]):  # 只显示最后2条
            if hasattr(msg, 'content'):
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                log_message(f"    消息 {i}: {content}", "INFO", "MAIN_STATE")
        
        # 执行日志
        execution_log = state.get("execution_log", [])
        log_message(f"  执行日志数量: {len(execution_log)}", "INFO", "MAIN_STATE")
        for log in execution_log[-2:]:  # 只显示最后2条
            log_message(f"    日志: {log.get('agent_name', 'unknown')} - {log.get('action', 'unknown')}", "INFO", "MAIN_STATE")
    
    log_message(f"📊 主图状态快照结束", "INFO", "MAIN_STATE")

# ===== 状态定义 =====

class MainState(TypedDict):
    """
    主图状态定义
    
    主图负责协调各个智能体子图，维护全局状态：
    - user_input: 用户输入
    - shared_messages: 智能体间共享的消息（仅最终结果）
    - current_agent: 当前执行的智能体
    - execution_log: 执行日志
    - step_count: 步骤计数
    - next_agent: 下一个智能体
    - task_description: 任务描述
    """
    user_input: str                    # 用户输入
    shared_messages: Annotated[list, operator.add]  # 共享消息列表（仅最终结果）
    current_agent: str                 # 当前执行的智能体
    execution_log: Annotated[list, operator.add]  # 执行日志
    step_count: int                    # 步骤计数
    next_agent: str                    # 下一个智能体
    task_description: str              # 任务描述

class PlannerState(TypedDict):
    """
    规划者子图状态定义
    
    规划者智能体负责分析用户需求并制定执行计划：
    - user_input: 用户输入
    - planning_result: 规划结果
    - analysis_notes: 分析笔记
    - planning_start_time: 开始时间
    - planning_end_time: 结束时间
    - next_agent: 下一个智能体
    - task_description: 任务描述
    """
    user_input: str                    # 用户输入
    planning_result: str               # 规划结果
    analysis_notes: list               # 分析笔记
    planning_start_time: float         # 开始时间
    planning_end_time: float           # 结束时间
    next_agent: str                    # 下一个智能体
    task_description: str              # 任务描述

class ResearcherState(TypedDict):
    """
    研究者子图状态定义
    
    研究者智能体负责收集和分析相关信息：
    - task: 研究任务
    - research_result: 研究结果
    - research_notes: 研究笔记
    - research_start_time: 开始时间
    - research_end_time: 结束时间
    - sources: 信息来源
    """
    task: str                          # 研究任务
    research_result: str               # 研究结果
    research_notes: list               # 研究笔记
    research_start_time: float         # 开始时间
    research_end_time: float           # 结束时间
    sources: list                      # 信息来源

class WriterState(TypedDict):
    """
    写作者子图状态定义
    
    写作者智能体负责整合信息并生成最终内容：
    - requirements: 创作要求
    - research_data: 研究数据
    - final_content: 最终内容
    - draft_notes: 草稿笔记
    - writing_start_time: 开始时间
    - writing_end_time: 结束时间
    """
    requirements: str                  # 创作要求
    research_data: str                 # 研究数据
    final_content: str                 # 最终内容
    draft_notes: list                  # 草稿笔记
    writing_start_time: float          # 开始时间
    writing_end_time: float            # 结束时间

# ===== 智能体配置 =====

# 智能体配置字典，定义每个智能体的属性
AGENT_CONFIGS = {
    "planner": {
        "name": "📋 任务规划者",
        "description": "分析用户需求并制定执行计划",
        "emoji": "📋",
        "system_prompt": """你是一个专业的任务规划者。你的职责是：
1. 分析用户的需求和问题
2. 制定详细的执行计划
3. 确定需要哪些专家智能体参与
4. 为每个智能体分配具体任务

请以结构化的方式输出你的规划结果。"""
    },
    "researcher": {
        "name": "🔍 信息研究者",
        "description": "收集和分析相关信息",
        "emoji": "🔍",
        "system_prompt": """你是一个专业的信息研究者。你的职责是：
1. 根据任务要求收集相关信息
2. 分析信息的可靠性和相关性
3. 整理和总结关键信息
4. 提供有见地的分析结果

请提供清晰、准确的研究结果。"""
    },
    "writer": {
        "name": "✍️ 内容写作者",
        "description": "整合信息并生成最终内容",
        "emoji": "✍️",
        "system_prompt": """你是一个专业的内容写作者。你的职责是：
1. 整合所有收集到的信息
2. 按照规划者的要求组织内容
3. 生成清晰、有逻辑的最终输出
4. 确保内容的完整性和可读性

请生成高质量的最终内容。"""
    }
}

def get_agent_config(agent_name: str) -> dict:
    """
    获取智能体配置
    
    Args:
        agent_name: 智能体名称
        
    Returns:
        智能体配置字典，如果不存在则返回默认配置
    """
    return AGENT_CONFIGS.get(agent_name, {
        "name": f"🔧 {agent_name}",
        "description": "默认智能体描述",
        "emoji": "🔧",
        "system_prompt": "你是一个智能体，请完成分配给你的任务。"
    })

def create_execution_log(agent_name: str, action: str, step_count: int, **kwargs) -> dict:
    """
    创建执行日志
    
    Args:
        agent_name: 智能体名称
        action: 执行动作
        step_count: 步骤计数
        **kwargs: 其他日志信息
        
    Returns:
        执行日志字典
    """
    config = get_agent_config(agent_name)
    return {
        "step": step_count,
        "agent": agent_name,
        "agent_name": config["name"],
        "description": config["description"],
        "emoji": config["emoji"],
        "action": action,
        "timestamp": time.strftime("%H:%M:%S"),
        **kwargs
    }

# ===== 规划者子图节点函数 =====

def planner_analyzer(state: PlannerState) -> PlannerState:
    """
    规划者分析节点
    
    这个节点负责：
    1. 分析用户输入
    2. 制定执行计划
    3. 确定下一个智能体
    4. 生成任务描述
    
    Args:
        state: 规划者状态
        
    Returns:
        更新后的规划者状态
    """
    user_input = state["user_input"]
    
    # 打印输入状态
    print_agent_state("planner", state, "输入")
    
    log_message(f"开始分析用户输入: {user_input[:50]}...", "START", "PLANNER")
    
    # 获取智能体配置
    config = get_agent_config("planner")
    
    # 使用LLM进行任务分析
    prompt = f"""
{config['system_prompt']}

用户输入: {user_input}

请分析这个任务并制定执行计划。考虑以下方面：
1. 任务类型和复杂度
2. 需要的信息类型
3. 执行步骤
4. 需要的专家智能体

请直接返回JSON格式的分析结果，不要包含任何markdown格式或其他文本。
JSON必须包含以下字段：
- task_analysis: 任务分析
- execution_plan: 执行计划
- required_agents: 需要的智能体列表
- next_agent: 下一个应该执行的智能体
- task_description: 给下一个智能体的任务描述

示例格式：
{{
  "task_analysis": "任务分析内容",
  "execution_plan": "执行计划",
  "required_agents": ["智能体1", "智能体2"],
  "next_agent": "researcher",
  "task_description": "具体任务描述"
}}
"""
    
    log_message("正在调用LLM进行任务分析...", "INFO", "PLANNER")
    response = llm.invoke([HumanMessage(content=prompt)])
    log_message("llm response: " + response.content, "DEBUG", "PLANNER")
    log_message("LLM分析完成", "SUCCESS", "PLANNER")
    
    try:
        # 清理响应内容，移除可能的markdown格式
        content = response.content.strip()
        
        # 如果包含markdown代码块，提取其中的JSON
        if content.startswith("```json"):
            content = content[7:]  # 移除 ```json
        if content.startswith("```"):
            content = content[3:]  # 移除 ```
        if content.endswith("```"):
            content = content[:-3]  # 移除结尾的 ```
        
        content = content.strip()
        
        # 尝试解析JSON响应
        analysis_result = json.loads(content)
        task_description = analysis_result.get("task_description", "执行研究任务")
        next_agent = analysis_result.get("next_agent", "researcher")
        
        log_message(f"分析完成，下一个智能体: {next_agent}", "SUCCESS", "PLANNER")
        log_message(f"任务描述: {task_description[:50]}...", "INFO", "PLANNER")
        
        # 构建输出状态
        output_state = {
            "planning_result": response.content,
            "analysis_notes": [analysis_result],
            "next_agent": next_agent,
            "task_description": task_description
        }
        
        # 打印输出状态
        print_agent_state("planner", output_state, "输出")
        
        return output_state
        
    except json.JSONDecodeError as e:
        # 如果JSON解析失败，使用默认值
        log_message(f"JSON解析失败: {e}", "WARNING", "PLANNER")
        log_message("使用默认路由", "WARNING", "PLANNER")
        
        output_state = {
            "planning_result": response.content,
            "analysis_notes": [{"error": f"JSON解析失败: {e}"}],
            "next_agent": "researcher",
            "task_description": "研究用户需求并提供相关信息"
        }
        
        # 打印输出状态
        print_agent_state("planner", output_state, "输出(错误回退)")
        
        return output_state

def planner_finalizer(state: PlannerState) -> PlannerState:
    """
    规划者完成节点
    
    记录规划完成的时间戳
    
    Args:
        state: 规划者状态
        
    Returns:
        更新后的规划者状态
    """
    log_message("规划者子图执行完成", "END", "PLANNER")
    
    final_state = {
        "planning_end_time": time.time()
    }
    
    # 打印最终状态
    print_agent_state("planner", {**state, **final_state}, "完成")
    
    return final_state

# ===== 研究者子图节点函数 =====

def researcher_analyzer(state: ResearcherState) -> ResearcherState:
    """
    研究者分析节点
    
    这个节点负责：
    1. 根据任务要求进行研究
    2. 收集相关信息
    3. 分析信息可靠性
    4. 生成研究结果
    
    Args:
        state: 研究者状态
        
    Returns:
        更新后的研究者状态
    """
    task = state["task"]
    
    # 打印输入状态
    print_agent_state("researcher", state, "输入")
    
    log_message(f"开始研究任务: {task[:50]}...", "START", "RESEARCHER")
    
    # 获取智能体配置
    config = get_agent_config("researcher")
    
    # 使用LLM进行研究
    prompt = f"""
{config['system_prompt']}

研究任务: {task}

请进行深入的研究和分析，提供以下内容：
1. 相关信息收集
2. 关键发现
3. 分析见解
4. 建议和推荐

请提供详细、准确的研究结果。
"""
    
    log_message("正在调用LLM进行研究分析...", "INFO", "RESEARCHER")
    response = llm.invoke([HumanMessage(content=prompt)])
    research_result = response.content
    log_message("LLM研究完成", "SUCCESS", "RESEARCHER")
    
    log_message(f"研究结果长度: {len(research_result)} 字符", "INFO", "RESEARCHER")
    
    output_state = {
        "research_result": research_result,
        "research_notes": [{
            "timestamp": time.strftime("%H:%M:%S"),
            "note": "研究完成，准备转移给写作者"
        }]
    }
    
    # 打印输出状态
    print_agent_state("researcher", output_state, "输出")
    
    return output_state

def researcher_finalizer(state: ResearcherState) -> ResearcherState:
    """
    研究者完成节点
    
    记录研究完成的时间戳和来源信息
    
    Args:
        state: 研究者状态
        
    Returns:
        更新后的研究者状态
    """
    log_message("研究者子图执行完成", "END", "RESEARCHER")
    
    final_state = {
        "research_end_time": time.time(),
        "sources": ["内部分析", "知识库", "推理"]
    }
    
    # 打印最终状态
    print_agent_state("researcher", {**state, **final_state}, "完成")
    
    return final_state

# ===== 写作者子图节点函数 =====

def writer_analyzer(state: WriterState) -> WriterState:
    """
    写作者分析节点
    
    这个节点负责：
    1. 整合研究数据
    2. 按照要求组织内容
    3. 生成最终输出
    4. 确保内容质量
    
    Args:
        state: 写作者状态
        
    Returns:
        更新后的写作者状态
    """
    requirements = state["requirements"]
    research_data = state["research_data"]
    
    # 打印输入状态
    print_agent_state("writer", state, "输入")
    
    log_message(f"开始内容创作，要求: {requirements[:50]}...", "START", "WRITER")
    
    # 获取智能体配置
    config = get_agent_config("writer")
    
    # 使用LLM进行内容创作
    prompt = f"""
{config['system_prompt']}

创作要求: {requirements}

研究数据: {research_data}

请基于研究数据和要求，创作高质量的最终内容。内容应该：
1. 结构清晰，逻辑合理
2. 信息准确，来源可靠
3. 语言流畅，易于理解
4. 满足用户需求

请提供完整的最终内容。
"""
    
    log_message("正在调用LLM进行内容创作...", "INFO", "WRITER")
    response = llm.invoke([HumanMessage(content=prompt)])
    final_content = response.content
    log_message("LLM创作完成", "SUCCESS", "WRITER")
    
    log_message(f"最终内容长度: {len(final_content)} 字符", "INFO", "WRITER")
    
    output_state = {
        "final_content": final_content,
        "draft_notes": [{
            "timestamp": time.strftime("%H:%M:%S"),
            "note": "内容创作完成"
        }]
    }
    
    # 打印输出状态
    print_agent_state("writer", output_state, "输出")
    
    return output_state

def writer_finalizer(state: WriterState) -> WriterState:
    """
    写作者完成节点
    
    记录创作完成的时间戳
    
    Args:
        state: 写作者状态
        
    Returns:
        更新后的写作者状态
    """
    log_message("写作者子图执行完成", "END", "WRITER")
    
    final_state = {
        "writing_end_time": time.time()
    }
    
    # 打印最终状态
    print_agent_state("writer", {**state, **final_state}, "完成")
    
    return final_state

# ===== 子图创建函数 =====

def create_planner_subgraph():
    """
    创建规划者子图
    
    子图结构：
    START → analyzer → finalizer → END
    
    Returns:
        编译后的规划者子图
    """
    log_message("创建规划者子图", "DEBUG", "SYSTEM")
    workflow = StateGraph(PlannerState)
    
    # 添加节点
    workflow.add_node("analyzer", planner_analyzer)
    workflow.add_node("finalizer", planner_finalizer)
    
    # 设置流程
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "finalizer")
    workflow.add_edge("finalizer", END)
    
    return workflow.compile()

def create_researcher_subgraph():
    """
    创建研究者子图
    
    子图结构：
    START → analyzer → finalizer → END
    
    Returns:
        编译后的研究者子图
    """
    log_message("创建研究者子图", "DEBUG", "SYSTEM")
    workflow = StateGraph(ResearcherState)
    
    # 添加节点
    workflow.add_node("analyzer", researcher_analyzer)
    workflow.add_node("finalizer", researcher_finalizer)
    
    # 设置流程
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "finalizer")
    workflow.add_edge("finalizer", END)
    
    return workflow.compile()

def create_writer_subgraph():
    """
    创建写作者子图
    
    子图结构：
    START → analyzer → finalizer → END
    
    Returns:
        编译后的写作者子图
    """
    log_message("创建写作者子图", "DEBUG", "SYSTEM")
    workflow = StateGraph(WriterState)
    
    # 添加节点
    workflow.add_node("analyzer", writer_analyzer)
    workflow.add_node("finalizer", writer_finalizer)
    
    # 设置流程
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "finalizer")
    workflow.add_edge("finalizer", END)
    
    return workflow.compile()

# ===== 主图节点函数 =====

def main_planner(state: MainState) -> Command[Literal["researcher", "writer", END]]:
    """
    主图规划者节点
    
    这个节点负责：
    1. 创建并执行规划者子图
    2. 根据规划结果决定路由
    3. 更新主图状态
    4. 记录执行日志
    
    Args:
        state: 主图状态
        
    Returns:
        Command 对象，指定下一个节点
    """
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    # 打印主图状态快照
    print_main_state_snapshot(state, f"步骤 {step_count} 开始")
    
    log_message(f"=== 主图规划者节点执行 (步骤 {step_count}) ===", "START", "MAIN")
    log_message(f"用户输入: {user_input}", "INFO", "MAIN")
    
    # 创建执行日志
    log_entry = create_execution_log(
        agent_name="planner",
        action="开始任务规划",
        step_count=step_count,
        input=user_input
    )
    
    # 准备规划者子图输入
    planner_input = {
        "user_input": user_input,
        "planning_start_time": time.time()
    }
    
    log_message("准备执行规划者子图...", "INFO", "MAIN")
    
    # 执行规划者子图
    planner_graph = create_planner_subgraph()
    planner_result = planner_graph.invoke(planner_input)
    
    log_message("规划者子图执行完成", "SUCCESS", "MAIN")
    
    # 提取结果
    next_agent = planner_result.get("next_agent", "researcher")
    task_description = planner_result.get("task_description", "执行任务")
    planning_result = planner_result.get("planning_result", "")
    
    log_message(f"规划结果: 下一个智能体 = {next_agent}", "INFO", "MAIN")
    log_message(f"任务描述: {task_description}", "INFO", "MAIN")
    
    log_entry["result"] = planning_result[:200] + "..." if len(planning_result) > 200 else planning_result
    log_entry["status"] = "completed"
    
    # 根据结果决定下一步
    if next_agent == "researcher":
        log_message("路由到研究者智能体", "INFO", "MAIN")
        # 打印状态转换
        print_state_transition("planner", "researcher", {
            "next_agent": next_agent,
            "task_description": task_description
        })
        return Command(
            goto="researcher",
            update={
                "current_agent": "researcher",
                "next_agent": next_agent,
                "task_description": task_description,
                "step_count": step_count,
                "execution_log": [log_entry]
            }
        )
    elif next_agent == "writer":
        log_message("路由到写作者智能体", "INFO", "MAIN")
        # 打印状态转换
        print_state_transition("planner", "writer", {
            "next_agent": next_agent,
            "task_description": task_description
        })
        return Command(
            goto="writer",
            update={
                "current_agent": "writer",
                "next_agent": next_agent,
                "task_description": task_description,
                "step_count": step_count,
                "execution_log": [log_entry]
            }
        )
    else:
        # 如果不需要其他智能体，直接完成任务
        log_message("直接完成任务", "INFO", "MAIN")
        # 打印状态转换
        print_state_transition("planner", "END", {
            "final_result": planning_result[:100]
        })
        return Command(
            goto=END,
            update={
                "current_agent": "completed",
                "shared_messages": [AIMessage(content=planning_result)],
                "step_count": step_count,
                "execution_log": [log_entry]
            }
        )

def main_researcher(state: MainState) -> Command[Literal["writer", END]]:
    """
    主图研究者节点
    
    这个节点负责：
    1. 创建并执行研究者子图
    2. 将研究结果添加到共享消息
    3. 路由到写作者智能体
    4. 记录执行日志
    
    Args:
        state: 主图状态
        
    Returns:
        Command 对象，指定下一个节点
    """
    step_count = state.get("step_count", 0) + 1
    task_description = state.get("task_description", "执行研究任务")
    
    # 打印主图状态快照
    print_main_state_snapshot(state, f"步骤 {step_count} 开始")
    
    log_message(f"=== 主图研究者节点执行 (步骤 {step_count}) ===", "START", "MAIN")
    log_message(f"研究任务: {task_description}", "INFO", "MAIN")
    
    # 创建执行日志
    log_entry = create_execution_log(
        agent_name="researcher",
        action="开始信息研究",
        step_count=step_count,
        task=task_description
    )
    
    # 准备研究者子图输入
    researcher_input = {
        "task": task_description,
        "research_start_time": time.time()
    }
    
    log_message("准备执行研究者子图...", "INFO", "MAIN")
    
    # 执行研究者子图
    researcher_graph = create_researcher_subgraph()
    researcher_result = researcher_graph.invoke(researcher_input)
    
    log_message("研究者子图执行完成", "SUCCESS", "MAIN")
    
    # 提取结果
    research_result = researcher_result.get("research_result", "")
    
    log_message(f"研究结果长度: {len(research_result)} 字符", "INFO", "MAIN")
    
    log_entry["result"] = research_result[:200] + "..." if len(research_result) > 200 else research_result
    log_entry["status"] = "completed"
    
    # 将研究结果添加到共享消息，然后转移给写作者
    log_message("路由到写作者智能体", "INFO", "MAIN")
    # 打印状态转换
    print_state_transition("researcher", "writer", {
        "research_result_length": len(research_result),
        "shared_message": f"研究结果: {research_result[:100]}..."
    })
    return Command(
        goto="writer",
        update={
            "current_agent": "writer",
            "shared_messages": [AIMessage(content=f"研究结果: {research_result[:500]}...")],
            "step_count": step_count,
            "execution_log": [log_entry]
        }
    )

def main_writer(state: MainState) -> Command[Literal[END]]:
    """
    主图写作者节点
    
    这个节点负责：
    1. 创建并执行写作者子图
    2. 生成最终内容
    3. 完成任务
    4. 记录执行日志
    
    Args:
        state: 主图状态
        
    Returns:
        Command 对象，结束执行
    """
    step_count = state.get("step_count", 0) + 1
    task_description = state.get("task_description", "生成内容")
    
    # 打印主图状态快照
    print_main_state_snapshot(state, f"步骤 {step_count} 开始")
    
    log_message(f"=== 主图写作者节点执行 (步骤 {step_count}) ===", "START", "MAIN")
    log_message(f"创作要求: {task_description}", "INFO", "MAIN")
    
    # 创建执行日志
    log_entry = create_execution_log(
        agent_name="writer",
        action="开始内容创作",
        step_count=step_count,
        requirements=task_description
    )
    
    # 准备写作者子图输入
    writer_input = {
        "requirements": task_description,
        "research_data": "基于前面的研究结果",
        "writing_start_time": time.time()
    }
    
    log_message("准备执行写作者子图...", "INFO", "MAIN")
    
    # 执行写作者子图
    writer_graph = create_writer_subgraph()
    writer_result = writer_graph.invoke(writer_input)
    
    log_message("写作者子图执行完成", "SUCCESS", "MAIN")
    
    # 提取结果
    final_content = writer_result.get("final_content", "")
    
    log_message(f"最终内容长度: {len(final_content)} 字符", "INFO", "MAIN")
    
    log_entry["result"] = final_content[:200] + "..." if len(final_content) > 200 else final_content
    log_entry["status"] = "completed"
    
    # 完成任务，将最终结果添加到共享消息
    log_message("任务完成，添加到共享消息", "SUCCESS", "MAIN")
    # 打印状态转换
    print_state_transition("writer", "END", {
        "final_content_length": len(final_content),
        "final_message": final_content[:100]
    })
    return Command(
        goto=END,
        update={
            "current_agent": "completed",
            "shared_messages": [AIMessage(content=final_content)],
            "step_count": step_count,
            "execution_log": [log_entry]
        }
    )

# ===== 主图工作流创建 =====

def create_multi_agent_workflow():
    """
    创建多智能体工作流（使用子图）
    
    工作流结构：
    START → planner → researcher → writer → END
    
    每个节点都会：
    1. 创建对应的子图
    2. 执行子图逻辑
    3. 根据结果决定路由
    4. 更新主图状态
    
    Returns:
        编译后的多智能体工作流
    """
    log_message("创建多智能体工作流", "DEBUG", "SYSTEM")
    workflow = StateGraph(MainState)
    
    # 添加主图节点
    workflow.add_node("planner", main_planner)
    workflow.add_node("researcher", main_researcher)
    workflow.add_node("writer", main_writer)
    
    # 设置入口点
    workflow.set_entry_point("planner")
    
    # 编译工作流
    return workflow.compile()

# ===== 测试和演示函数 =====

def test_multi_agent_system():
    """
    测试多智能体系统
    
    这个函数会：
    1. 创建多智能体工作流
    2. 使用多个测试输入
    3. 执行流式处理
    4. 显示详细结果
    5. 分析执行过程
    """
    if not JSON_STREAM:
        print("\n" + "="*80)
        print("🚀 多智能体系统测试（子图方式）")
        print("="*80)
    
    # 创建工作流
    log_message("初始化多智能体工作流", "INFO", "SYSTEM")
    graph = create_multi_agent_workflow()
    
    # 测试输入
    test_inputs = [
        "我想了解人工智能的发展趋势",
        "请帮我制定一个学习计划",
        "分析当前编程语言的市场需求"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        if not JSON_STREAM:
            print(f"\n{'='*60}")
            print(f"📝 测试 {i}: {user_input}")
            print(f"{'='*60}")
        
        # 准备输入状态
        inputs = {
            "user_input": user_input,
            "shared_messages": [],
            "current_agent": "",
            "execution_log": [],
            "step_count": 0,
            "next_agent": "",
            "task_description": ""
        }
        
        try:
            log_message(f"开始执行测试 {i}", "START", "SYSTEM")
            if JSON_STREAM:
                sse_send("start", {"test_index": i, "input": user_input})
            config = {}
            config["thread_id"] = "test"
            # 执行工作流
            log_message("开始流式执行工作流...", "INFO", "SYSTEM")
            stream_result = graph.stream(inputs, config=config, stream_mode="values")
            
            # 处理流式结果
            final_result = None
            chunk_count = 0
            for chunk in stream_result:
                chunk_count += 1
                log_message(f"接收到流式数据块 {chunk_count}", "DEBUG", "SYSTEM")
                
                # 使用专门的函数分析chunk内容
                analyze_chunk_content(chunk, chunk_count)
                
                # 获取最后一个chunk作为最终结果
                if isinstance(chunk, dict):
                    final_result = chunk
                    log_message(f"数据块 {chunk_count}: 字典类型，包含 {len(chunk)} 个键", "DEBUG", "SYSTEM")
                else:
                    # 如果是其他类型，尝试提取状态
                    final_result = getattr(chunk, 'values', chunk)
                    log_message(f"数据块 {chunk_count}: 对象类型，提取values属性", "DEBUG", "SYSTEM")
                
                # 显示/推送当前执行状态
                if final_result and isinstance(final_result, dict):
                    current_agent = final_result.get('current_agent', 'unknown')
                    step_count = final_result.get('step_count', 0)
                    if current_agent != 'unknown':
                        log_message(f"当前执行: {current_agent} (步骤 {step_count})", "INFO", "SYSTEM")
                    if JSON_STREAM:
                        sse_send("state", serialize_state_snapshot(final_result))
            
            if final_result is None:
                raise Exception("未能获取有效的执行结果")
            
            log_message(f"流式执行完成，共处理 {chunk_count} 个数据块", "SUCCESS", "SYSTEM")
            log_message(f"测试 {i} 执行完成", "SUCCESS", "SYSTEM")
            if JSON_STREAM:
                sse_send("end", serialize_state_snapshot(final_result))
            if not JSON_STREAM:
                print(f"\n✅ 执行完成")
                print(f"📊 总步骤数: {final_result.get('step_count', 0)}")
                print(f"🤖 最终智能体: {final_result.get('current_agent', 'unknown')}")
                print(f"📦 流式数据块数量: {chunk_count}")
                
                # 显示执行日志
                print("\n📋 执行日志:")
                for log in final_result.get("execution_log", []):
                    print(f"  {log['emoji']} {log['agent_name']}: {log['action']}")
                    print(f"     时间: {log['timestamp']}")
                    if "result" in log:
                        result_preview = log["result"]
                        if len(result_preview) > 100:
                            result_preview = result_preview[:100] + "..."
                        print(f"     结果: {result_preview}")
                    print()
                
                # 显示最终结果
                print("🎯 最终结果:")
                shared_messages = final_result.get("shared_messages", [])
                for msg in shared_messages:
                    if hasattr(msg, 'content'):
                        content = msg.content
                        if len(content) > 300:
                            content = content[:300] + "..."
                        print(f"  {content}")
            
            print(f"\n{'='*60}")
            
        except Exception as e:
            log_message(f"测试 {i} 执行失败: {e}", "ERROR", "SYSTEM")
            if not JSON_STREAM:
                print(f"❌ 错误: {e}")
            if JSON_STREAM:
                sse_send("error", {"test_index": i, "error": str(e)})

def demonstrate_subgraph_structure():
    """
    演示子图结构
    
    这个函数展示：
    1. 各个子图的结构
    2. 主图的协调机制
    3. 子图的优势
    4. 架构设计理念
    """
    print("\n🏗️ 子图结构演示")
    print("=" * 60)
    
    print("📋 规划者子图结构:")
    print("  START → analyzer → finalizer → END")
    print("  功能: 任务分析、计划制定、路由决策")
    
    print("\n🔍 研究者子图结构:")
    print("  START → analyzer → finalizer → END")
    print("  功能: 信息收集、分析处理、结果整理")
    
    print("\n✍️ 写作者子图结构:")
    print("  START → analyzer → finalizer → END")
    print("  功能: 内容整合、最终输出生成")
    
    print("\n🎯 主图结构:")
    print("  START → planner → researcher → writer → END")
    print("  功能: 智能体协调、状态管理、结果聚合")
    
    print("\n💡 子图优势:")
    print("✅ 每个智能体都有独立的状态空间")
    print("✅ 支持复杂的内部逻辑和流程")
    print("✅ 便于测试和维护单个智能体")
    print("✅ 可以独立扩展和优化")
    print("✅ 支持状态隔离和隐私保护")

def show_agent_configurations():
    """
    显示智能体配置
    
    这个函数展示：
    1. 所有可用的智能体
    2. 每个智能体的配置
    3. 配置的特点和优势
    """
    print("\n🎨 智能体配置展示")
    print("=" * 60)
    
    print("可用智能体配置:")
    for agent_name, config in AGENT_CONFIGS.items():
        print(f"\n{config['emoji']} {config['name']}")
        print(f"   智能体名: {agent_name}")
        print(f"   描述: {config['description']}")
        print(f"   系统提示: {config['system_prompt'][:100]}...")
    
    print("\n配置特点:")
    print("✅ 支持中文智能体名称")
    print("✅ 支持emoji表情符号")
    print("✅ 详细的智能体描述")
    print("✅ 自定义系统提示")
    print("✅ 统一的配置管理")

# ===== 主程序入口 =====

if __name__ == "__main__":
    """
    主程序入口
    
    根据 JSON_STREAM 配置决定运行模式：
    - True: 输出 JSON 流式数据（适合前端集成）
    - False: 输出标准格式（适合命令行调试）
    """
    if JSON_STREAM:
        # JSON 流式模式：直接执行测试，输出 SSE 格式
        test_multi_agent_system()
    else:
        # 标准模式：显示完整信息
        print("🎯 LangGraph 多智能体示例 - 子图方式实现")
        print("=" * 60)
        
        # 显示智能体配置
        show_agent_configurations()
        
        # 演示子图结构
        demonstrate_subgraph_structure()
        
        # 测试多智能体系统
        test_multi_agent_system()
        
        print("\n✅ 多智能体子图示例完成！")
        print("\n📚 学习要点总结:")
        print("1. 子图架构: 每个智能体都是独立的子图")
        print("2. 状态隔离: 子图有独立的状态空间")
        print("3. 模块化设计: 便于测试和维护")
        print("4. 主图协调: 统一的状态管理和路由")
        print("5. 最终结果共享: 智能体间只传递必要信息")
        print("6. 可扩展性: 支持复杂的内部逻辑") 