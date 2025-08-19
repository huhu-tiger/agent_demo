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
from fastapi import FastAPI, Body, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect

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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/stream")
def stream_post(body: dict = Body(...)):
    user_input = body.get("user_input") or ""
    stream_mode = body.get("stream_mode") or "updates"
    thread_id = body.get("thread_id")
    checkpoint = body.get("checkpoint")
    replay_history = bool(body.get("replay_history", False))
    if not user_input:
        def _err():
            yield _format_sse({"status": "error", "message": "missing user_input"}, event="error")
        return StreamingResponse(_err(), media_type="text/event-stream")
    return StreamingResponse(_node_sse_generator(user_input, stream_mode=stream_mode, thread_id=thread_id, checkpoint=checkpoint, replay_history=replay_history), media_type="text/event-stream")

@app.get("/stream")
def stream_get(
    user_input: str = Query(..., description="用户输入"),
    stream_mode: str = Query("updates", description="流模式：可用 updates,values,messages,debug；支持用逗号/竖线组合"),
    thread_id: str | None = Query(None, description="会话线程ID，用于持久化与断点续作"),
    checkpoint: str | None = Query(None, description="断点ID/名称，用于从指定断点恢复"),
    replay_history: bool = Query(False, description="是否在开始时回放历史 execution_log")
):
    return StreamingResponse(_node_sse_generator(user_input, stream_mode=stream_mode, thread_id=thread_id, checkpoint=checkpoint, replay_history=replay_history), media_type="text/event-stream")

@app.get("/history")
def history(
    thread_id: str = Query(..., description="会话线程ID"),
    checkpoint: str | None = Query(None, description="可选的断点ID/名称")
):
    def _history_sse_generator():
        # 读取状态快照
        config = {"configurable": {"thread_id": thread_id}}
        if checkpoint:
            config["configurable"]["checkpoint_id"] = checkpoint
            config["configurable"]["checkpoint"] = checkpoint
        logger.info(f"history config: {config}")
        try:
            snapshot = graph_app.get_state(config=config)
            logger.info(f"history snapshot: {snapshot}")
            # 开始事件
            yield _format_sse({"status": "start", "thread_id": thread_id, "checkpoint": checkpoint}, event="history_start")
            store = None
            if snapshot is not None:
                if hasattr(snapshot, "values"):
                    store = snapshot.values
                elif hasattr(snapshot, "value"):
                    store = snapshot.value
            prev_logs = store.get("execution_log") if isinstance(store, dict) else None
            if isinstance(prev_logs, list) and prev_logs:
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
            else:
                yield _format_sse({"thread_id": thread_id, "checkpoint": checkpoint, "history": []}, event="history_empty")
            # 结束事件
            yield _format_sse({"status": "completed", "thread_id": thread_id, "checkpoint": checkpoint}, event="end")
        except Exception as e:
            yield _format_sse({"status": "error", "message": str(e)}, event="error")

    return StreamingResponse(_history_sse_generator(), media_type="text/event-stream")

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

def test_node_name_tracking():
    """测试节点名称跟踪功能"""
    print("🚀 节点名称跟踪测试")
    print("=" * 60)
    
    # 创建工作流
    graph = create_node_tracking_workflow()
    
    # 测试输入
    user_input = "我想学习Python编程"
    
    print(f"📝 输入: {user_input}")
    print("-" * 40)
    
    # 准备输入状态
    inputs = {
        "user_input": user_input,
        "execution_log": [],
        "step_count": 0
    }
    
    print("🔍 节点执行跟踪:")
    print("-" * 40)
    
    try:
        # 使用 updates 模式跟踪节点执行
        for chunk in graph.stream(inputs, stream_mode="updates"):
            # 提取节点信息
            for key, value in chunk.items():
                if isinstance(value, dict) and "current_node" in value:
                    node_name = value["current_node"]
                    display_name = value.get("node_display_name", node_name)
                    description = value.get("node_description", "")
                    step_count = value.get("step_count", 0)
                    
                    print(f"📍 步骤 {step_count}: {display_name}")
                    print(f"   📋 描述: {description}")
                    print(f"   🔧 节点名: {node_name}")
                    
                    # 显示节点执行日志
                    if "execution_log" in value:
                        for log in value["execution_log"]:
                            if log.get("node") == node_name:
                                print(f"   ⏰ 时间: {log.get('timestamp', 'N/A')}")
                                print(f"   🎯 动作: {log.get('action', 'N/A')}")
                                if "result" in log:
                                    result = log["result"]
                                    if len(result) > 80:
                                        result = result[:80] + "..."
                                    print(f"   📊 结果: {result}")
                                print()
                    
    except Exception as e:
        print(f"❌ 错误: {e}")

def show_node_configurations():
    """显示节点配置"""
    print("\n🎨 节点配置展示")
    print("=" * 60)
    
    print("可用节点配置:")
    for node_name, config in NODE_CONFIGS.items():
        print(f"\n{config['emoji']} {config['display_name']}")
        print(f"   节点名: {node_name}")
        print(f"   描述: {config['description']}")
    
    print("\n配置特点:")
    print("✅ 支持中文显示名称")
    print("✅ 支持emoji表情符号")
    print("✅ 详细的节点描述")
    print("✅ 统一的配置管理")
    print("✅ 动态节点信息获取")

def demonstrate_custom_node_names():
    """演示自定义节点名称功能"""
    print("\n🎯 自定义节点名称演示")
    print("=" * 60)
    
    # 创建工作流
    graph = create_node_tracking_workflow()
    
    # 测试输入
    test_inputs = [
        "如何学习机器学习",
        "推荐一些编程书籍",
        "Python有什么优势"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n📝 测试 {i}: {user_input}")
        print("-" * 40)
        
        # 准备输入状态
        inputs = {
            "user_input": user_input,
            "execution_log": [],
            "step_count": 0
        }
        
        try:
            # 执行工作流并跟踪节点
            node_execution_order = []
            
            for chunk in graph.stream(inputs, stream_mode="updates"):
                for key, value in chunk.items():
                    if isinstance(value, dict) and "current_node" in value:
                        node_name = value["current_node"]
                        display_name = value.get("node_display_name", node_name)
                        step_count = value.get("step_count", 0)
                        
                        if step_count not in [log["step"] for log in node_execution_order]:
                            node_execution_order.append({
                                "step": step_count,
                                "node": node_name,
                                "display_name": display_name
                            })
            
            # 显示执行顺序
            print("执行顺序:")
            for execution in node_execution_order:
                print(f"  {execution['step']}. {execution['display_name']}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    # 默认启动 FastAPI 服务（使用导入字符串以启用 reload/workers）
    # todo cd langgraph_demo/study 
    import uvicorn
    uvicorn.run("11_stream_fastapi_ws:app", host="0.0.0.0", port=8000, reload=True)
    
    print("\n✅ 节点名称自定义示例完成！")
    print("\n📚 学习要点总结:")
    print("1. 节点名称配置: 支持中文、emoji和描述")
    print("2. 状态跟踪: 实时监控当前执行的节点")
    print("3. 显示名称: 用户友好的节点展示")
    print("4. 配置管理: 统一的节点配置字典")
    print("5. 动态获取: 根据节点名获取配置信息")
    print("6. 执行日志: 详细的节点执行记录") 