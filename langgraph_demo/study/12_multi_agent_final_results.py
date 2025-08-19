# -*- coding: utf-8 -*-
"""
LangGraph 多智能体示例 - 子图方式实现
学习要点：多智能体架构、子图实现、状态管理、最终结果共享
参考：https://langchain-ai.github.io/langgraph/concepts/multi_agent/#multi-agent-architectures
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

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.types import Command
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
    temperature=0.1,
    max_tokens=1000
)

# ===== 主图状态定义 =====
class MainState(TypedDict):
    """主图状态"""
    user_input: str                    # 用户输入
    shared_messages: Annotated[list, operator.add]  # 共享消息列表（仅最终结果）
    current_agent: str                 # 当前执行的智能体
    execution_log: Annotated[list, operator.add]  # 执行日志
    step_count: int                    # 步骤计数
    next_agent: str                    # 下一个智能体
    task_description: str              # 任务描述

# ===== 规划者子图状态 =====
class PlannerState(TypedDict):
    """规划者子图状态"""
    user_input: str                    # 用户输入
    planning_result: str               # 规划结果
    analysis_notes: list               # 分析笔记
    planning_start_time: float         # 开始时间
    planning_end_time: float           # 结束时间
    next_agent: str                    # 下一个智能体
    task_description: str              # 任务描述

# ===== 研究者子图状态 =====
class ResearcherState(TypedDict):
    """研究者子图状态"""
    task: str                          # 研究任务
    research_result: str               # 研究结果
    research_notes: list               # 研究笔记
    research_start_time: float         # 开始时间
    research_end_time: float           # 结束时间
    sources: list                      # 信息来源

# ===== 写作者子图状态 =====
class WriterState(TypedDict):
    """写作者子图状态"""
    requirements: str                  # 创作要求
    research_data: str                 # 研究数据
    final_content: str                 # 最终内容
    draft_notes: list                  # 草稿笔记
    writing_start_time: float          # 开始时间
    writing_end_time: float            # 结束时间

# ===== 智能体配置 =====
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
    """获取智能体配置"""
    return AGENT_CONFIGS.get(agent_name, {
        "name": f"🔧 {agent_name}",
        "description": "默认智能体描述",
        "emoji": "🔧",
        "system_prompt": "你是一个智能体，请完成分配给你的任务。"
    })

def create_execution_log(agent_name: str, action: str, step_count: int, **kwargs) -> dict:
    """创建执行日志"""
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

def print_log(message: str, level: str = "INFO", agent: str = "SYSTEM", line_number: int = None):
    """打印日志"""
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
    print(f"[{timestamp}] {emoji} [{agent}:L{line_number}] {message}")

# ===== 规划者子图节点函数 =====
def planner_analyzer(state: PlannerState) -> PlannerState:
    """规划者分析节点"""
    user_input = state["user_input"]
    
    print_log(f"开始分析用户输入: {user_input[:50]}...", "START", "PLANNER")
    
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

请以JSON格式输出你的分析结果，包含：
- task_analysis: 任务分析
- execution_plan: 执行计划
- required_agents: 需要的智能体列表
- next_agent: 下一个应该执行的智能体
- task_description: 给下一个智能体的任务描述
"""
    
    print_log("正在调用LLM进行任务分析...", "INFO", "PLANNER")
    response = llm.invoke([HumanMessage(content=prompt)])
    print_log("LLM分析完成", "SUCCESS", "PLANNER")
    
    try:
        # 尝试解析JSON响应
        analysis_result = json.loads(response.content)
        task_description = analysis_result.get("task_description", "执行研究任务")
        next_agent = analysis_result.get("next_agent", "researcher")
        
        print_log(f"分析完成，下一个智能体: {next_agent}", "SUCCESS", "PLANNER")
        print_log(f"任务描述: {task_description[:50]}...", "INFO", "PLANNER")
        
        return {
            "planning_result": response.content,
            "analysis_notes": [analysis_result],
            "next_agent": next_agent,
            "task_description": task_description
        }
        
    except json.JSONDecodeError:
        # 如果JSON解析失败，使用默认值
        print_log("JSON解析失败，使用默认路由", "WARNING", "PLANNER")
        return {
            "planning_result": response.content,
            "analysis_notes": [{"error": "JSON解析失败"}],
            "next_agent": "researcher",
            "task_description": "研究用户需求并提供相关信息"
        }

def planner_finalizer(state: PlannerState) -> PlannerState:
    """规划者完成节点"""
    print_log("规划者子图执行完成", "END", "PLANNER")
    return {
        "planning_end_time": time.time()
    }

# ===== 研究者子图节点函数 =====
def researcher_analyzer(state: ResearcherState) -> ResearcherState:
    """研究者分析节点"""
    task = state["task"]
    
    print_log(f"开始研究任务: {task[:50]}...", "START", "RESEARCHER")
    
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
    
    print_log("正在调用LLM进行研究分析...", "INFO", "RESEARCHER")
    response = llm.invoke([HumanMessage(content=prompt)])
    research_result = response.content
    print_log("LLM研究完成", "SUCCESS", "RESEARCHER")
    
    print_log(f"研究结果长度: {len(research_result)} 字符", "INFO", "RESEARCHER")
    
    return {
        "research_result": research_result,
        "research_notes": [{
            "timestamp": time.strftime("%H:%M:%S"),
            "note": "研究完成，准备转移给写作者"
        }]
    }

def researcher_finalizer(state: ResearcherState) -> ResearcherState:
    """研究者完成节点"""
    print_log("研究者子图执行完成", "END", "RESEARCHER")
    return {
        "research_end_time": time.time(),
        "sources": ["内部分析", "知识库", "推理"]
    }

# ===== 写作者子图节点函数 =====
def writer_analyzer(state: WriterState) -> WriterState:
    """写作者分析节点"""
    requirements = state["requirements"]
    research_data = state["research_data"]
    
    print_log(f"开始内容创作，要求: {requirements[:50]}...", "START", "WRITER")
    
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
    
    print_log("正在调用LLM进行内容创作...", "INFO", "WRITER")
    response = llm.invoke([HumanMessage(content=prompt)])
    final_content = response.content
    print_log("LLM创作完成", "SUCCESS", "WRITER")
    
    print_log(f"最终内容长度: {len(final_content)} 字符", "INFO", "WRITER")
    
    return {
        "final_content": final_content,
        "draft_notes": [{
            "timestamp": time.strftime("%H:%M:%S"),
            "note": "内容创作完成"
        }]
    }

def writer_finalizer(state: WriterState) -> WriterState:
    """写作者完成节点"""
    print_log("写作者子图执行完成", "END", "WRITER")
    return {
        "writing_end_time": time.time()
    }

# ===== 子图创建函数 =====
def create_planner_subgraph():
    """创建规划者子图"""
    print_log("创建规划者子图", "DEBUG", "SYSTEM")
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
    """创建研究者子图"""
    print_log("创建研究者子图", "DEBUG", "SYSTEM")
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
    """创建写作者子图"""
    print_log("创建写作者子图", "DEBUG", "SYSTEM")
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
    """主图规划者节点"""
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    print_log(f"=== 主图规划者节点执行 (步骤 {step_count}) ===", "START", "MAIN")
    print_log(f"用户输入: {user_input}", "INFO", "MAIN")
    
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
    
    print_log("准备执行规划者子图...", "INFO", "MAIN")
    
    # 执行规划者子图
    planner_graph = create_planner_subgraph()
    planner_result = planner_graph.invoke(planner_input)
    
    print_log("规划者子图执行完成", "SUCCESS", "MAIN")
    
    # 提取结果
    next_agent = planner_result.get("next_agent", "researcher")
    task_description = planner_result.get("task_description", "执行任务")
    planning_result = planner_result.get("planning_result", "")
    
    print_log(f"规划结果: 下一个智能体 = {next_agent}", "INFO", "MAIN")
    print_log(f"任务描述: {task_description}", "INFO", "MAIN")
    
    log_entry["result"] = planning_result[:200] + "..." if len(planning_result) > 200 else planning_result
    log_entry["status"] = "completed"
    
    # 根据结果决定下一步
    if next_agent == "researcher":
        print_log("路由到研究者智能体", "INFO", "MAIN")
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
        print_log("路由到写作者智能体", "INFO", "MAIN")
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
        print_log("直接完成任务", "INFO", "MAIN")
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
    """主图研究者节点"""
    step_count = state.get("step_count", 0) + 1
    task_description = state.get("task_description", "执行研究任务")
    
    print_log(f"=== 主图研究者节点执行 (步骤 {step_count}) ===", "START", "MAIN")
    print_log(f"研究任务: {task_description}", "INFO", "MAIN")
    
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
    
    print_log("准备执行研究者子图...", "INFO", "MAIN")
    
    # 执行研究者子图
    researcher_graph = create_researcher_subgraph()
    researcher_result = researcher_graph.invoke(researcher_input)
    
    print_log("研究者子图执行完成", "SUCCESS", "MAIN")
    
    # 提取结果
    research_result = researcher_result.get("research_result", "")
    
    print_log(f"研究结果长度: {len(research_result)} 字符", "INFO", "MAIN")
    
    log_entry["result"] = research_result[:200] + "..." if len(research_result) > 200 else research_result
    log_entry["status"] = "completed"
    
    # 将研究结果添加到共享消息，然后转移给写作者
    print_log("路由到写作者智能体", "INFO", "MAIN")
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
    """主图写作者节点"""
    step_count = state.get("step_count", 0) + 1
    task_description = state.get("task_description", "生成内容")
    
    print_log(f"=== 主图写作者节点执行 (步骤 {step_count}) ===", "START", "MAIN")
    print_log(f"创作要求: {task_description}", "INFO", "MAIN")
    
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
    
    print_log("准备执行写作者子图...", "INFO", "MAIN")
    
    # 执行写作者子图
    writer_graph = create_writer_subgraph()
    writer_result = writer_graph.invoke(writer_input)
    
    print_log("写作者子图执行完成", "SUCCESS", "MAIN")
    
    # 提取结果
    final_content = writer_result.get("final_content", "")
    
    print_log(f"最终内容长度: {len(final_content)} 字符", "INFO", "MAIN")
    
    log_entry["result"] = final_content[:200] + "..." if len(final_content) > 200 else final_content
    log_entry["status"] = "completed"
    
    # 完成任务，将最终结果添加到共享消息
    print_log("任务完成，添加到共享消息", "SUCCESS", "MAIN")
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
    """创建多智能体工作流（使用子图）"""
    print_log("创建多智能体工作流", "DEBUG", "SYSTEM")
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
    """测试多智能体系统"""
    print("\n" + "="*80)
    print("🚀 多智能体系统测试（子图方式）")
    print("="*80)
    
    # 创建工作流
    print_log("初始化多智能体工作流", "INFO", "SYSTEM")
    graph = create_multi_agent_workflow()
    
    # 测试输入
    test_inputs = [
        "我想了解人工智能的发展趋势",
        # "请帮我制定一个学习计划",
        # "分析当前编程语言的市场需求"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
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
            print_log(f"开始执行测试 {i}", "START", "SYSTEM")
            config = {}
            config["thread_id"] = "test"
            # 执行工作流
            print_log("开始流式执行工作流...", "INFO", "SYSTEM")
            stream_result = graph.stream(inputs, config=config, stream_mode="values")
            
            # 处理流式结果
            final_result = None
            chunk_count = 0
            for chunk in stream_result:
                chunk_count += 1
                print_log(f"接收到流式数据块 {chunk_count}", "DEBUG", "SYSTEM")
                
                # 获取最后一个chunk作为最终结果
                if isinstance(chunk, dict):
                    final_result = chunk
                    print_log(f"数据块 {chunk_count}: 字典类型，包含 {len(chunk)} 个键", "DEBUG", "SYSTEM")
                else:
                    # 如果是其他类型，尝试提取状态
                    final_result = getattr(chunk, 'values', chunk)
                    print_log(f"数据块 {chunk_count}: 对象类型，提取values属性", "DEBUG", "SYSTEM")
                
                # 显示当前执行状态
                if final_result and isinstance(final_result, dict):
                    current_agent = final_result.get('current_agent', 'unknown')
                    step_count = final_result.get('step_count', 0)
                    if current_agent != 'unknown':
                        print_log(f"当前执行: {current_agent} (步骤 {step_count})", "INFO", "SYSTEM")
            
            if final_result is None:
                raise Exception("未能获取有效的执行结果")
            
            print_log(f"流式执行完成，共处理 {chunk_count} 个数据块", "SUCCESS", "SYSTEM")
            print_log(f"测试 {i} 执行完成", "SUCCESS", "SYSTEM")
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
            print_log(f"测试 {i} 执行失败: {e}", "ERROR", "SYSTEM")
            print(f"❌ 错误: {e}")

def demonstrate_subgraph_structure():
    """演示子图结构"""
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
    """显示智能体配置"""
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

if __name__ == "__main__":
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