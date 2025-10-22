# -*- coding: utf-8 -*-
"""
LangGraph 节点名称自定义示例
学习要点：节点名称跟踪、自定义显示名称、动态名称配置
"""

import os
import sys
import time
import json
from typing import TypedDict, Annotated
import operator

# 添加当前脚本所在目录到路径，确保能导入本目录下的 config.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
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
    max_tokens=500
)

# 定义状态结构
class NodeTrackingState(TypedDict):
    """节点跟踪状态定义"""
    user_input: str                    # 用户输入
    current_node: str                  # 当前节点名称
    node_display_name: str             # 节点显示名称
    node_description: str              # 节点描述
    execution_log: Annotated[list, operator.add]  # 执行日志
    step_count: int                    # 步骤计数

# 节点配置字典
NODE_CONFIGS = {
    "data_processor": {
        "display_name": "📊 数据预处理引擎",
        "description": "智能处理和分析输入数据",
        "emoji": "📊"
    },
    "ai_analyzer": {
        "display_name": "🧠 AI智能分析器",
        "description": "使用深度学习技术分析用户意图",
        "emoji": "🧠"
    },
    "recommendation_engine": {
        "display_name": "🎯 智能推荐引擎",
        "description": "基于AI算法生成个性化推荐",
        "emoji": "🎯"
    },
    "response_generator": {
        "display_name": "✨ 响应生成器",
        "description": "整合所有结果生成最终响应",
        "emoji": "✨"
    }
}

def get_node_config(node_name: str) -> dict:
    """获取节点配置"""
    return NODE_CONFIGS.get(node_name, {
        "display_name": f"🔧 {node_name}",
        "description": "默认节点描述",
        "emoji": "🔧"
    })

def create_node_log(node_name: str, action: str, step_count: int, **kwargs) -> dict:
    """创建节点日志"""
    config = get_node_config(node_name)
    return {
        "step": step_count,
        "node": node_name,
        "display_name": config["display_name"],
        "description": config["description"],
        "emoji": config["emoji"],
        "action": action,
        "timestamp": time.strftime("%H:%M:%S"),
        **kwargs
    }

# 定义节点函数
def data_processor_node(state: NodeTrackingState) -> NodeTrackingState:
    """
    数据预处理节点
    学习要点：节点名称配置、日志记录
    """
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    node_name = "data_processor"
    
    # 获取节点配置
    config = get_node_config(node_name)
    
    # 创建执行日志
    log_entry = create_node_log(
        node_name=node_name,
        action="开始数据预处理",
        step_count=step_count,
        input=user_input
    )
    
    # 模拟数据处理
    time.sleep(0.2)
    processed_data = f"预处理结果: {user_input.upper()}"
    
    log_entry["result"] = processed_data
    log_entry["status"] = "completed"
    
    return {
        "current_node": node_name,
        "node_display_name": config["display_name"],
        "node_description": config["description"],
        "step_count": step_count,
        "execution_log": [log_entry]
    }

def ai_analyzer_node(state: NodeTrackingState) -> NodeTrackingState:
    """
    AI分析节点
    学习要点：LLM调用、节点状态跟踪
    """
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    node_name = "ai_analyzer"
    
    # 获取节点配置
    config = get_node_config(node_name)
    
    # 创建执行日志
    log_entry = create_node_log(
        node_name=node_name,
        action="开始AI分析",
        step_count=step_count,
        input=user_input
    )
    
    # 使用LLM进行分析
    prompt = f"""
请分析用户输入: "{user_input}"
提供简要的分析结果。
"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    analysis_result = response.content
    
    log_entry["result"] = analysis_result
    log_entry["status"] = "completed"
    
    return {
        "current_node": node_name,
        "node_display_name": config["display_name"],
        "node_description": config["description"],
        "step_count": step_count,
        "execution_log": [log_entry]
    }

def recommendation_engine_node(state: NodeTrackingState) -> NodeTrackingState:
    """
    推荐引擎节点
    学习要点：动态节点名称、状态传递
    """
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    node_name = "recommendation_engine"
    
    # 获取节点配置
    config = get_node_config(node_name)
    
    # 创建执行日志
    log_entry = create_node_log(
        node_name=node_name,
        action="开始生成推荐",
        step_count=step_count,
        input=user_input
    )
    
    # 模拟推荐生成
    time.sleep(0.1)
    recommendation = f"基于 '{user_input}' 的推荐: 建议深入学习相关技术"
    
    log_entry["result"] = recommendation
    log_entry["status"] = "completed"
    
    return {
        "current_node": node_name,
        "node_display_name": config["display_name"],
        "node_description": config["description"],
        "step_count": step_count,
        "execution_log": [log_entry]
    }

def response_generator_node(state: NodeTrackingState) -> NodeTrackingState:
    """
    响应生成器节点
    学习要点：最终状态整合、节点名称展示
    """
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    node_name = "response_generator"
    
    # 获取节点配置
    config = get_node_config(node_name)
    
    # 创建执行日志
    log_entry = create_node_log(
        node_name=node_name,
        action="开始生成最终响应",
        step_count=step_count,
        input=user_input
    )
    
    # 生成最终响应
    final_response = f"""
🎉 处理完成！

用户输入: {user_input}
处理步骤: {step_count} 步
当前节点: {config["display_name"]}

感谢您的使用！
"""
    
    log_entry["result"] = final_response
    log_entry["status"] = "completed"
    
    return {
        "current_node": node_name,
        "node_display_name": config["display_name"],
        "node_description": config["description"],
        "step_count": step_count,
        "execution_log": [log_entry]
    }

def create_node_tracking_workflow():
    """创建节点跟踪工作流"""
    workflow = StateGraph(NodeTrackingState)
    
    # 添加节点
    workflow.add_node("data_processor", data_processor_node)
    workflow.add_node("ai_analyzer", ai_analyzer_node)
    workflow.add_node("recommendation_engine", recommendation_engine_node)
    workflow.add_node("response_generator", response_generator_node)
    
    # 设置流程
    workflow.set_entry_point("data_processor")
    workflow.add_edge("data_processor", "ai_analyzer")
    workflow.add_edge("ai_analyzer", "recommendation_engine")
    workflow.add_edge("recommendation_engine", "response_generator")
    workflow.add_edge("response_generator", END)
    
    return workflow

# ===== FastAPI 应用与 WebSocket/SSE 流式接口 =====
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LangGraph Streaming API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 在应用启动时创建一次工作流，避免重复构建
from langgraph.checkpoint.memory import MemorySaver
_memory_checkpointer = MemorySaver()
# 以带检查点的形式编译
graph_app = create_node_tracking_workflow().compile(checkpointer=_memory_checkpointer)

# ====== 引入中断所需类型 ======
from typing import List, Literal
from langgraph.types import Command, interrupt

# ====== 基于 08_interrupt_人工_demo.py 的中断工作流定义 ======
class InterruptState(TypedDict):
    """
    中断工作流的状态定义
    
    状态字段说明：
    - user_input: 用户输入内容
    - processed_result: 处理后的结果
    - steps: 执行步骤列表（使用operator.add进行累积）
    - decision: 决策结果（通过/拒绝/待处理）
    - tools_log: 工具调用日志列表（使用operator.add进行累积）
    - current_node: 当前执行的节点名称
    """
    user_input: str
    processed_result: str
    steps: Annotated[List[str], operator.add]
    decision: str
    tools_log: Annotated[List[dict], operator.add]
    current_node: str

def _create_interrupt_workflow():
    """
    创建支持中断功能的工作流
    
    工作流特点：
    1. 支持人工干预节点，可以在执行过程中暂停等待用户输入
    2. 包含决策节点，根据用户反馈决定后续流程
    3. 支持工具调用，包含合规检查、数据获取、摘要生成等
    4. 支持多种执行路径：通过、拒绝、待处理
    
    工作流节点：
    - process_input: 处理输入节点
    - human_interaction: 人工交互节点（中断点）
    - decision: 决策节点
    - approve: 批准处理节点
    - reject: 拒绝处理节点
    - finalize: 最终处理节点
    """
    # ===== 模拟工具（同步调用） =====
    def tool_check_compliance(text: str) -> dict:
        start_ts = time.time()
        time.sleep(0.05)
        ok = "违规" not in text
        return {
            "tool": "check_compliance",
            "duration_ms": int((time.time() - start_ts) * 1000),
            "status": "ok",
            "output": {"is_compliant": ok}
        }

    def tool_fetch_external_data(query: str) -> dict:
        start_ts = time.time()
        time.sleep(0.08)
        return {
            "tool": "fetch_external_data",
            "duration_ms": int((time.time() - start_ts) * 1000),
            "status": "ok",
            "output": {"query": query, "data": ["item-a", "item-b"]}
        }

    def tool_generate_summary(payload: dict) -> dict:
        start_ts = time.time()
        time.sleep(0.04)
        summary = f"共 {len(str(payload))} 字符的摘要"
        return {
            "tool": "generate_summary",
            "duration_ms": int((time.time() - start_ts) * 1000),
            "status": "ok",
            "output": {"summary": summary}
        }
    def process_input_node(state: InterruptState) -> InterruptState:
        user_input = state.get("user_input", "")
        return {
            "user_input": user_input,
            "steps": ["process_input"],
            "current_node": "process_input",
        }

    def human_interaction_node(state: InterruptState) -> InterruptState:
        """
        人工交互节点 - 工作流的中断点
        
        功能说明：
        1. 这是工作流的中断点，会暂停执行等待人工干预
        2. 向用户展示当前状态和可选项
        3. 等待用户提供反馈后继续执行
        
        中断数据包含：
        - message: 提示信息
        - current_input: 当前用户输入
        - options: 可选择的选项列表
        
        返回值：
        - 用户反馈将作为新的user_input继续后续流程
        """
        # 构建中断数据，包含提示信息和可选项
        interrupt_data = {
            "message": "请提供反馈信息",
            "current_input": state.get("user_input", ""),
            "options": ["通过", "拒绝", "需要更多信息"],
        }
        # 调用interrupt函数，暂停工作流等待用户输入
        user_feedback = interrupt(interrupt_data)
        return {
            "user_input": user_feedback,        # 用户反馈作为新的输入
            "steps": ["human_interaction"],     # 记录执行步骤
            "current_node": "human_interaction", # 当前节点
        }

    def decision_node(state: InterruptState) -> Command[Literal["approve", "reject", "finalize"]]:
        """
        决策节点 - 根据用户反馈决定后续流程
        
        功能说明：
        1. 分析用户反馈内容，判断用户意图
        2. 根据意图选择不同的执行路径
        3. 使用Command对象控制工作流的跳转
        
        决策逻辑：
        - 包含"通过"、"同意"等关键词 -> 跳转到approve节点
        - 包含"拒绝"、"不同意"等关键词 -> 跳转到reject节点
        - 其他情况 -> 跳转到finalize节点（待处理）
        
        返回值：
        - Command对象，包含状态更新和跳转目标
        """
        # 获取用户输入并转换为小写，便于关键词匹配
        user_input = state.get("user_input", "").lower()
        
        # 判断用户意图并设置跳转目标
        if any(k in user_input for k in ["通过", "同意", "approve", "yes", "1"]):
            goto = "approve"      # 跳转到批准节点
            decision = "approved" # 决策结果：已批准
        elif any(k in user_input for k in ["拒绝", "不同意", "reject", "no", "2"]):
            goto = "reject"       # 跳转到拒绝节点
            decision = "rejected" # 决策结果：已拒绝
        else:
            goto = "finalize"     # 跳转到最终处理节点
            decision = "pending"  # 决策结果：待处理
        
        # 返回Command对象，包含状态更新和跳转目标
        return Command(update={
            "user_input": user_input,    # 更新用户输入
            "steps": ["decision"],       # 记录执行步骤
            "decision": decision,        # 记录决策结果
            "current_node": "decision",  # 当前节点
        }, goto=goto)

    def approve_node(state: InterruptState) -> InterruptState:
        """
        批准处理节点 - 执行完整的处理流程
        
        功能说明：
        1. 当用户选择"通过"时，执行此节点
        2. 顺序调用多个工具进行完整处理
        3. 记录所有工具调用的日志
        4. 生成最终的处理结果
        
        工具调用流程：
        1. 合规检查工具 - 检查内容是否符合规范
        2. 外部数据获取工具 - 获取相关的外部数据
        3. 摘要生成工具 - 基于输入和外部数据生成摘要
        
        返回值：
        - 包含处理结果、执行步骤、工具日志和当前节点信息
        """
        user_input = state.get("user_input", "")
        tools_logs: List[dict] = []  # 工具调用日志列表
        
        # 顺序调用模拟工具，记录每个工具的调用结果
        log1 = tool_check_compliance(user_input)      # 合规检查
        tools_logs.append(log1)
        log2 = tool_fetch_external_data(user_input)   # 获取外部数据
        tools_logs.append(log2)
        log3 = tool_generate_summary({"input": user_input, "ext": log2.get("output")})  # 生成摘要
        tools_logs.append(log3)

        # 生成最终处理结果，包含摘要信息
        processed = f"✅ 已批准: {user_input} | 摘要: {log3['output'].get('summary')}"
        return {
            "processed_result": processed,           # 处理结果
            "steps": ["approve", "tools_called"],   # 执行步骤
            "tools_log": tools_logs,                # 工具调用日志
            "current_node": "approve",              # 当前节点
        }

    def reject_node(state: InterruptState) -> InterruptState:
        user_input = state.get("user_input", "")
        return {
            "processed_result": f"❌ 已拒绝: {user_input}",
            "steps": ["reject"],
            "current_node": "reject",
        }

    def finalize_node(state: InterruptState) -> InterruptState:
        user_input = state.get("user_input", "")
        processed_result = f"⏳ 待处理: {user_input}"
        return {
            "processed_result": processed_result,
            "steps": ["finalize"],
            "current_node": "finalize",
        }

    builder = StateGraph(InterruptState)
    builder.add_node("process_input", process_input_node)
    builder.add_node("human_interaction", human_interaction_node)
    builder.add_node("decision", decision_node)
    builder.add_node("approve", approve_node)
    builder.add_node("reject", reject_node)
    builder.add_node("finalize", finalize_node)

    builder.add_edge(START, "process_input")
    builder.add_edge("process_input", "human_interaction")
    builder.add_edge("human_interaction", "decision")
    builder.add_edge("approve", END)
    builder.add_edge("reject", END)
    builder.add_edge("finalize", END)

    return builder

# 以同一个 checkpointer 编译可跨消息恢复
interrupt_graph_app = _create_interrupt_workflow().compile(checkpointer=_memory_checkpointer)

ALLOWED_STREAM_MODES = {"updates", "values", "messages", "debug"}

def _safe_serialize(obj):
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        if isinstance(obj, dict):
            return {k: _safe_serialize(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_safe_serialize(v) for v in obj]
        return str(obj)

def _format_sse(data: dict, event: str = "message") -> str:
    payload = {"event": event, "data": _safe_serialize(data)}
    return json.dumps(payload, ensure_ascii=False) + "\n"

def _parse_stream_modes(mode_param):
    if not mode_param:
        return ["updates"], []
    raw_list = []
    if isinstance(mode_param, str):
        raw_list = [p.strip() for p in mode_param.replace("|", ",").split(",") if p.strip()]
    elif isinstance(mode_param, (list, tuple, set)):
        for item in mode_param:
            if isinstance(item, str):
                raw_list.extend([p.strip() for p in item.replace("|", ",").split(",") if p.strip()])
    # 去重并校验
    uniq = []
    for m in raw_list:
        if m not in uniq:
            uniq.append(m)
    valid = [m for m in uniq if m in ALLOWED_STREAM_MODES]
    invalid = [m for m in uniq if m not in ALLOWED_STREAM_MODES]
    if not valid:
        valid = ["updates"]
    return valid, invalid

def _normalize_content(content):
    """将复杂 message content 规整为字符串，避免不可序列化/不可哈希对象向下游传播。"""
    try:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, (int, float, bool)):
            return str(content)
        # LangChain 常见：list[dict|str|obj]
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    # 优先提取 text 字段
                    txt = item.get("text") or item.get("content")
                    if isinstance(txt, str):
                        parts.append(txt)
                    else:
                        parts.append(json.dumps(_safe_serialize(item), ensure_ascii=False))
                else:
                    # 兜底为字符串
                    parts.append(str(item))
            return "".join(parts)
        if isinstance(content, dict):
            # 尝试提取 text，否则整体序列化
            txt = content.get("text") or content.get("content")
            if isinstance(txt, str):
                return txt
            return json.dumps(_safe_serialize(content), ensure_ascii=False)
        # 对象：尝试取 .text/.value/.content 等
        for attr in ("text", "value", "content"):
            if hasattr(content, attr):
                val = getattr(content, attr)
                return _normalize_content(val)
        return str(content)
    except Exception:
        return str(content)

def _extract_message_list(value):
    messages = []
    src = None
    if isinstance(value, dict) and "messages" in value:
        src = value["messages"]
    elif isinstance(value, list):
        src = value
    else:
        src = [value]
    for m in src:
        role = getattr(m, "type", None) or getattr(m, "role", None)
        content = getattr(m, "content", None)
        if isinstance(m, dict):
            role = m.get("type") or m.get("role") or role
            content = m.get("content") or content
        content = _normalize_content(content)
        messages.append({"role": role or "unknown", "content": content})
    return messages

def _iter_node_items(chunk):
    """兼容性迭代：将 chunk 统一为 (node_name, node_value) 序列。
    支持 dict、(node, value) 元组、[(node,value), ...] 列表、或其它类型。
    """
    if isinstance(chunk, dict):
        for k, v in chunk.items():
            yield k, v
        return
    if isinstance(chunk, tuple):
        if len(chunk) == 2:
            yield chunk[0], chunk[1]
            return
    if isinstance(chunk, list):
        for item in chunk:
            if isinstance(item, tuple) and len(item) == 2:
                yield item[0], item[1]
            elif isinstance(item, dict):
                for k, v in item.items():
                    yield k, v
            else:
                yield "unknown", item
        return
    # 其它未知类型，作为单个值输出
    yield "unknown", chunk

def _format_tuple_messages_chunk(msg_obj, meta: dict) -> dict:
    """将 (MessageChunk/Message, meta) 规范化为统一负载。"""
    node_name = meta.get("langgraph_node") or "unknown"
    cfg = get_node_config(str(node_name))
    content = _normalize_content(getattr(msg_obj, "content", msg_obj))
    role = getattr(msg_obj, "type", None) or getattr(msg_obj, "role", None) or "assistant"
    payload = {
        "node": node_name,
        "display_name": cfg["display_name"],
        "description": cfg["description"],
        "step": meta.get("langgraph_step"),
        "path": meta.get("langgraph_path"),
        "triggers": meta.get("langgraph_triggers"),
        "provider": meta.get("ls_provider"),
        "model": meta.get("ls_model_name"),
        "message": {
            "role": role,
            "content": content
        }
    }
    return payload

def _node_sse_generator(user_input: str, stream_mode = "updates", thread_id: str | None = None, checkpoint: str | None = None, replay_history: bool = True):
    modes, invalid = _parse_stream_modes(stream_mode)
    if invalid:
        yield _format_sse({"warning": "invalid_modes", "ignored": invalid, "allowed": sorted(list(ALLOWED_STREAM_MODES))}, event="warning")
    inputs = {
        "user_input": user_input,
        "execution_log": [],
        "step_count": 0
    }
    # 透传会话与断点配置
    stream_kwargs = {}
    cfg = {}
    configurable = {}
    if thread_id:
        configurable["thread_id"] = thread_id
    if checkpoint:
        # 同步传递两种常见键，便于不同版本兼容
        configurable["checkpoint"] = checkpoint
        configurable["checkpoint_id"] = checkpoint
    if configurable:
        cfg["configurable"] = configurable
    if cfg:
        stream_kwargs["config"] = cfg
        
    logger.info(f"stream_kwargs: {stream_kwargs}")

    # 按需回放历史：将已有 execution_log 以独立的 history 事件输出

    if replay_history and stream_kwargs.get("config"):
        try:
            snapshot = graph_app.get_state(stream_kwargs["config"])
            logger.info(f"history snapshot: {snapshot}")
            if snapshot and hasattr(snapshot, "values") and isinstance(snapshot.values, dict):
                prev_logs = snapshot.values.get("execution_log")
                if isinstance(prev_logs, list):
                    for hist in prev_logs:
                        node = hist.get("node", "unknown")
                        cfg_node = get_node_config(str(node))
                        out = {
                            "step": hist.get("step"),
                            "node": node,
                            "display_name": cfg_node["display_name"],
                            "description": cfg_node["description"],
                            "timestamp": hist.get("timestamp"),
                            "action": hist.get("action"),
                            "result": (hist.get("result")[:500] + "...") if isinstance(hist.get("result"), str) and len(hist.get("result")) > 500 else hist.get("result"),
                            "thread_id": thread_id,
                            "checkpoint": checkpoint
                        }
                        yield _format_sse(out, event="history")
        except Exception as _e:
            # 历史回放失败忽略
            pass

    try:
        for mode in modes:
            # 每个模式的起始事件
            yield _format_sse({"mode": mode, "status": "start", "thread_id": thread_id, "checkpoint": checkpoint}, event="mode_start")
            if mode == "updates":
                for chunk in graph_app.stream(inputs, stream_mode=mode, **stream_kwargs):
                    for key, value in chunk.items():
                        if isinstance(value, dict) and "current_node" in value:
                            node_name = value["current_node"]
                            display_name = value.get("node_display_name", node_name)
                            description = value.get("node_description", "")
                            step_count = value.get("step_count", 0)
                            payload = {
                                "step": step_count,
                                "node": node_name,
                                "display_name": display_name,
                                "description": description,
                                "thread_id": thread_id,
                                "checkpoint": checkpoint
                            }
                            if "execution_log" in value:
                                for log in value["execution_log"]:
                                    if log.get("node") == node_name:
                                        result = log.get("result")
                                        if isinstance(result, str) and len(result) > 500:
                                            result = result[:500] + "..."
                                        payload["log"] = {
                                            "timestamp": log.get("timestamp"),
                                            "action": log.get("action"),
                                            "result": result
                                        }
                                        break
                            yield _format_sse(payload, event="node")
            # elif mode == "messages":
            #     for chunk in graph_app.stream(inputs, stream_mode=mode, **stream_kwargs):
            #         logger.info(f"chunk: {chunk}")
            #         # 优先处理 (msg, meta) 元组
            #         if isinstance(chunk, tuple) and len(chunk) == 2 and isinstance(chunk[1], dict):
            #             payload = _format_tuple_messages_chunk(chunk[0], chunk[1])
            #             yield _format_sse(payload, event="node")
            #             continue
            #         # 处理列表：可能包含多个 (msg, meta)
            #         if isinstance(chunk, list):
            #             for item in chunk:
            #                 if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], dict):
            #                     payload = _format_tuple_messages_chunk(item[0], item[1])
            #                     yield _format_sse(payload, event="node")
            #                 else:
            #                     # 回退到通用解析
            #                     for node_name, node_value in _iter_node_items(item):
            #                         derived_name = node_name if isinstance(node_name, str) else (
            #                             node_value.get("langgraph_node") if isinstance(node_value, dict) else "unknown"
            #                         )
            #                         cfg = get_node_config(str(derived_name))
            #                         messages = _extract_message_list(node_value)
            #                         logger.info(f"messages: {messages}")
            #                         logger.info(f"cfg: {cfg}")
            #                         payload = {
            #                             "node": derived_name,
            #                             "display_name": cfg["display_name"],
            #                             "description": cfg["description"],
            #                             "messages": messages,
            #                             "thread_id": thread_id,
            #                             "checkpoint": checkpoint
            #                         }
            #                         yield _format_sse(payload, event="node")
            #             continue
            #         # 其它情况：使用通用解析
            #         for node_name, node_value in _iter_node_items(chunk):
            #             derived_name = node_name if isinstance(node_name, str) else (
            #                 node_value.get("langgraph_node") if isinstance(node_value, dict) else "unknown"
            #             )
            #             cfg = get_node_config(str(derived_name))
            #             messages = _extract_message_list(node_value)
            #             logger.info(f"messages: {messages}")
            #             logger.info(f"cfg: {cfg}")
            #             payload = {
            #                 "node": derived_name,
            #                 "display_name": cfg["display_name"],
            #                 "description": cfg["description"],
            #                 "messages": messages,
            #                 "thread_id": thread_id,
            #                 "checkpoint": checkpoint
            #             }
            #             yield _format_sse(payload, event="node")
            else:
                for chunk in graph_app.stream(inputs, stream_mode=mode, **stream_kwargs):
                    yield _format_sse({"chunk": chunk, "thread_id": thread_id, "checkpoint": checkpoint}, event=mode)
            # 每个模式的结束事件
            yield _format_sse({"mode": mode, "status": "completed", "thread_id": thread_id, "checkpoint": checkpoint}, event="mode_end")
        yield _format_sse({"status": "completed", "thread_id": thread_id, "checkpoint": checkpoint}, event="end")
    except Exception as e:
        yield _format_sse({"status": "error", "message": str(e)}, event="error")




def _node_sse_generator_interrupt(user_input: str, stream_mode = "updates", thread_id: str | None = None, checkpoint: str | None = None, replay_history: bool = True, resume: str | None = None):
    """
    中断工作流的 SSE 事件生成器
    
    功能说明：
    1. 支持工作流中断和人工干预机制
    2. 支持断点续传，可以从中断点恢复执行
    3. 支持历史记录回放，显示之前的执行步骤
    4. 支持工具调用结果的详细输出
    5. 支持调试模式，提供详细的执行信息
    
    参数说明：
    - user_input: 用户输入内容
    - stream_mode: 流式模式（updates/debug等）
    - thread_id: 会话ID，用于状态持久化
    - checkpoint: 检查点ID，用于断点续传
    - replay_history: 是否回放历史记录
    - resume: 恢复数据，用于从中断点继续执行
    
    返回事件：
    - history: 历史记录回放
    - mode_start/mode_end: 模式开始/结束
    - debug: 调试信息（执行前后状态）
    - interrupt: 工作流中断，等待人工干预
    - tool: 工具调用结果
    - result: 最终处理结果
    - error: 错误信息
    - end: 流程结束
    """
    # 构建配置对象，用于状态持久化和断点续传
    cfg = {}
    configurable = {}
    if thread_id:
        configurable["thread_id"] = thread_id  # 会话ID，用于区分不同的执行会话
    if checkpoint:
        configurable["checkpoint"] = checkpoint      # 检查点ID
        configurable["checkpoint_id"] = checkpoint   # 兼容性：同时设置两种键名
    if configurable:
        cfg["configurable"] = configurable

    # 历史记录回放：如果启用且存在配置，则输出已保存的执行步骤和结果
    if replay_history and cfg.get("configurable"):
        try:
            # 获取当前会话的状态快照
            snapshot = interrupt_graph_app.get_state(cfg)
            if snapshot and hasattr(snapshot, "values") and isinstance(snapshot.values, dict):
                steps = snapshot.values.get("steps") or []           # 已执行的步骤列表
                processed = snapshot.values.get("processed_result")  # 已处理的结果
                yield _format_sse({
                    "history_steps": steps,        # 历史步骤
                    "processed_result": processed, # 历史结果
                    "thread_id": thread_id,        # 会话ID
                    "checkpoint": checkpoint,      # 检查点ID
                }, event="history")
        except Exception:
            # 历史回放失败，忽略错误继续执行
            pass

    # 发送模式开始事件
    try:
        yield _format_sse({
            "mode": stream_mode or "updates",  # 当前流式模式
            "status": "start",                 # 状态：开始
            "thread_id": thread_id,            # 会话ID
            "checkpoint": checkpoint,          # 检查点ID
        }, event="mode_start")
    except Exception:
        pass

    try:
        # 调试模式：发送执行前的状态信息
        if (stream_mode or "updates") == "debug":
            yield _format_sse({
                "phase": "before_invoke",      # 阶段：执行前
                "intent": "resume" if (resume is not None and resume != "") else "initial",  # 意图：恢复或初始执行
                "config": cfg,                 # 配置信息
                "thread_id": thread_id,        # 会话ID
                "checkpoint": checkpoint,      # 检查点ID
            }, event="debug")
        
        # 根据是否有恢复数据决定执行方式
        if resume is not None and resume != "":
            # 恢复执行：从中断点继续
            result = interrupt_graph_app.invoke(Command(resume=resume), config=cfg)
        else:
            # 初次执行：创建新的输入状态
            inputs = {
                "user_input": user_input,      # 用户输入
                "processed_result": "",        # 处理结果（初始为空）
                "steps": [],                   # 执行步骤（初始为空）
                "decision": "",                # 决策结果（初始为空）
            }
            result = interrupt_graph_app.invoke(inputs, config=cfg)

        # 检查是否发生中断
        if isinstance(result, dict) and "__interrupt__" in result:
            # 工作流被中断，需要人工干预
            payload = result["__interrupt__"]  # 中断数据
            yield _format_sse({
                "type": "interrupt",           # 类型：中断
                "node": "human_interaction",   # 中断节点：人工交互
                "data": _safe_serialize(payload),  # 中断数据（安全序列化）
                "thread_id": thread_id,        # 会话ID
                "checkpoint": checkpoint       # 检查点ID
            }, event="interrupt")
            return  # 中断后直接返回，等待客户端发送恢复数据

        # 提取最终结果信息
        steps = result.get("steps") if isinstance(result, dict) else None           # 执行步骤
        processed = result.get("processed_result") if isinstance(result, dict) else None  # 处理结果
        decision = result.get("decision") if isinstance(result, dict) else None     # 决策结果
        
        # 调试模式：发送执行后的状态信息
        yield _format_sse({
            "phase": "after_invoke",           # 阶段：执行后
            "steps": steps,                    # 执行步骤
            "decision": decision,              # 决策结果
            "has_tools_log": bool(isinstance(result, dict) and result.get("tools_log")),  # 是否有工具日志
            "node": result.get("current_node") if isinstance(result, dict) else None,     # 当前节点
            "thread_id": thread_id,            # 会话ID
            "checkpoint": checkpoint           # 检查点ID
        }, event="debug")
        
        # 输出工具调用明细：逐条输出每个工具的调用结果
        if isinstance(result, dict):
            tools_log = result.get("tools_log")
            if isinstance(tools_log, list):
                for t in tools_log:
                    yield _format_sse({
                        "type": "tool",                    # 类型：工具调用
                        "node": result.get("current_node"), # 调用工具所在的节点
                        "tool": t.get("tool"),             # 工具名称
                        "duration_ms": t.get("duration_ms"), # 执行时长（毫秒）
                        "status": t.get("status"),         # 执行状态
                        "data": _safe_serialize(t.get("output")),  # 工具输出数据
                        "thread_id": thread_id,            # 会话ID
                        "checkpoint": checkpoint,          # 检查点ID
                    }, event="tool")
        
        # 发送最终处理结果
        yield _format_sse({
            "status": "ok",                    # 状态：成功
            "steps": steps,                    # 执行步骤
            "processed_result": processed,     # 处理结果
            "decision": decision,              # 决策结果
            "node": result.get("current_node") if isinstance(result, dict) else None,  # 当前节点
            "thread_id": thread_id,            # 会话ID
            "checkpoint": checkpoint,          # 检查点ID
        }, event="result")
        
        # 发送流程结束事件
        yield _format_sse({"status": "completed", "thread_id": thread_id, "checkpoint": checkpoint}, event="end")
        
    except Exception as e:
        # 发生错误，发送错误信息
        yield _format_sse({"status": "error", "message": str(e)}, event="error")
    finally:
        # 确保发送模式结束事件
        try:
            yield _format_sse({
                "mode": stream_mode or "updates",  # 当前流式模式
                "status": "completed",             # 状态：完成
                "thread_id": thread_id,            # 会话ID
                "checkpoint": checkpoint,          # 检查点ID
            }, event="mode_end")
        except Exception:
            # 发送模式结束事件失败，忽略
            pass


# 已移除 HTTP 接口，仅保留 WebSocket 端点

# ===== 新增：WebSocket 端点 =====
@app.websocket("/ws")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                message_text = await websocket.receive_text()
            except WebSocketDisconnect:
                break
            except Exception:
                # 未能解析消息，发送错误并继续
                await websocket.send_text(_format_sse({"status": "error", "message": "invalid message"}, event="error"))
                continue
            try:
                body = json.loads(message_text) if message_text else {}
            except Exception:
                body = {}
            user_input = body.get("user_input") or ""
            stream_mode = body.get("stream_mode") or "updates"
            thread_id = body.get("thread_id")
            checkpoint = body.get("checkpoint")
            replay_history = bool(body.get("replay_history", False))
            if not user_input:
                await websocket.send_text(_format_sse({"status": "error", "message": "missing user_input"}, event="error"))
                continue
            # 将生成的事件通过 WebSocket 逐条发送（文本帧）
            for line in _node_sse_generator(
                user_input,
                stream_mode=stream_mode,
                thread_id=thread_id,
                checkpoint=checkpoint,
                replay_history=replay_history,
            ):
                await websocket.send_text(line)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(_format_sse({"status": "error", "message": str(e)}, event="error"))
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass



# ===== 支持中断功能的 WebSocket 端点 =====
@app.websocket("/ws_interrupt")
async def websocket_stream_interrupt(websocket: WebSocket):
    """
    支持中断功能的 WebSocket 流式接口
    
    功能特点：
    1. 支持工作流中断和人工干预
    2. 支持断点续传和状态恢复
    3. 支持历史记录回放
    4. 支持多种流式模式
    
    消息格式：
    - 初始请求：{"user_input": "用户输入", "thread_id": "会话ID", "checkpoint": "检查点ID"}
    - 恢复请求：{"resume": "恢复数据", "thread_id": "会话ID", "checkpoint": "检查点ID"}
    
    返回事件类型：
    - history: 历史记录回放
    - mode_start/mode_end: 模式开始/结束
    - interrupt: 工作流中断，等待人工干预
    - debug: 调试信息
    - tool: 工具调用结果
    - result: 最终处理结果
    - error: 错误信息
    - end: 流程结束
    """
    # 接受 WebSocket 连接
    await websocket.accept()
    
    try:
        # 持续监听客户端消息
        while True:
            try:
                # 接收客户端发送的文本消息
                message_text = await websocket.receive_text()
            except WebSocketDisconnect:
                # 客户端主动断开连接，退出循环
                break
            except Exception:
                # 消息接收失败，发送错误信息并继续监听
                await websocket.send_text(_format_sse({"status": "error", "message": "invalid message"}, event="error"))
                continue
            
            try:
                # 解析 JSON 格式的消息体
                body = json.loads(message_text) if message_text else {}
            except Exception:
                # JSON 解析失败，使用空字典作为默认值
                body = {}
            
            # 提取请求参数
            user_input = body.get("user_input") or ""           # 用户输入内容
            stream_mode = body.get("stream_mode") or "updates"  # 流式模式（默认updates）
            thread_id = body.get("thread_id")                   # 会话ID，用于状态持久化
            checkpoint = body.get("checkpoint")                 # 检查点ID，用于断点续传
            replay_history = bool(body.get("replay_history", False))  # 是否回放历史记录
            resume = body.get("resume")                         # 恢复数据，用于从中断点继续执行
            
            # 参数验证：必须提供用户输入或恢复数据
            if not user_input and not resume:
                await websocket.send_text(_format_sse({"status": "error", "message": "missing user_input or resume"}, event="error"))
                continue
            
            # 调用中断工作流生成器，逐条发送流式事件
            for line in _node_sse_generator_interrupt(
                user_input,                    # 用户输入
                stream_mode=stream_mode,       # 流式模式
                thread_id=thread_id,           # 会话ID
                checkpoint=checkpoint,         # 检查点ID
                replay_history=replay_history, # 历史回放
                resume=resume,                 # 恢复数据
            ):
                # 将每个事件通过 WebSocket 发送给客户端
                await websocket.send_text(line)
                
    except WebSocketDisconnect:
        # 客户端断开连接，正常退出
        pass
    except Exception as e:
        # 发生未预期错误，尝试发送错误信息给客户端
        try:
            await websocket.send_text(_format_sse({"status": "error", "message": str(e)}, event="error"))
        except Exception:
            # 发送错误信息也失败，忽略
            pass
    finally:
        # 确保 WebSocket 连接被正确关闭
        try:
            await websocket.close()
        except Exception:
            # 关闭连接失败，忽略
            pass




if __name__ == "__main__":
    # 默认启动 FastAPI 服务（使用导入字符串以启用 reload/workers）
    # todo cd langgraph_demo/study 
    import uvicorn
    uvicorn.run("11_stream_fastapi_ws_interrupt:app", host="0.0.0.0", port=8000, reload=False)
    
    print("\n✅ 节点名称自定义示例完成！")
    print("\n📚 学习要点总结:")
    print("1. 节点名称配置: 支持中文、emoji和描述")
    print("2. 状态跟踪: 实时监控当前执行的节点")
    print("3. 显示名称: 用户友好的节点展示")
    print("4. 配置管理: 统一的节点配置字典")
    print("5. 动态获取: 根据节点名获取配置信息")
    print("6. 执行日志: 详细的节点执行记录") 