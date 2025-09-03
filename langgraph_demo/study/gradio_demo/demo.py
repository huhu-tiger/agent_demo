#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gradio LangGraph 智能对话界面
支持流式输出、可视化工作流图、节点执行监控的智能对话系统
"""

import gradio as gr
import asyncio
import logging
import time
import json
import os
import base64
from typing import List, Tuple, Optional, Union, TypedDict, Annotated, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import operator

# 添加系统路径以导入配置
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from langgraph.graph import StateGraph, START, END
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage
    from langchain_core.tools import tool
    from langgraph.config import get_stream_writer
    from langchain_core.runnables.graph import MermaidDrawMethod
    import config
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    print(f"LangGraph相关库未安装: {e}")

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 定义LangGraph状态结构
class ConversationState(TypedDict):
    """对话状态定义"""
    user_input: str                    # 用户输入
    processed_input: str               # 处理后的输入
    analysis_result: str               # 分析结果  
    ai_response: str                   # AI响应
    final_response: str                # 最终响应
    execution_log: Annotated[list, operator.add]  # 执行日志
    step_count: int                    # 步骤计数
    current_node: str                  # 当前节点名称
    node_display_name: str             # 节点显示名称
    conversation_history: Annotated[list, operator.add]  # 对话历史
    system_prompt: str                 # 系统提示

@dataclass
class ModelConfig:
    """模型配置类"""
    name: str
    model_name: str
    base_url: str
    api_key: str
    description: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096

@dataclass 
class ChatState:
    """聊天状态管理"""
    messages: List[Tuple[str, str]] = field(default_factory=list)
    current_model: Optional[str] = None
    workflow_graph: Optional[object] = None
    system_prompt: str = "你是一个有用的AI助手，请根据用户的问题提供准确、有帮助的回答。"
    execution_logs: List[Dict[str, Any]] = field(default_factory=list)
    workflow_diagram: str = ""

# 定义工具函数
@tool
def analyze_user_input(text: str) -> str:
    """分析用户输入的工具"""
    try:
        writer = get_stream_writer()
        writer({"type": "progress", "message": f"开始分析用户输入: {text[:50]}..."})
        
        time.sleep(0.5)  # 模拟分析过程
        writer({"type": "progress", "message": "正在识别用户意图..."})
        
        time.sleep(0.5)
        analysis = f"分析结果: 用户输入包含 {len(text)} 个字符，主要意图是获取信息或寻求帮助"
        writer({"type": "analysis_complete", "message": "分析完成", "result": analysis})
        
        return analysis
    except:
        return f"分析结果: 用户输入包含 {len(text)} 个字符，主要意图是获取信息或寻求帮助"

@tool
def search_knowledge(query: str) -> str:
    """知识搜索工具"""
    try:
        writer = get_stream_writer()
        writer({"type": "progress", "message": f"正在搜索知识: {query}..."})
        
        time.sleep(0.8)
        writer({"type": "progress", "message": "正在检索相关信息..."})
        
        time.sleep(0.5)
        result = f"搜索到与 '{query}' 相关的信息，建议您深入了解相关技术并实践应用。"
        writer({"type": "search_complete", "message": "搜索完成", "result": result})
        
        return result
    except:
        return f"搜索到与 '{query}' 相关的信息，建议您深入了解相关技术并实践应用。"

# 定义LangGraph节点函数
def input_processor(state: ConversationState) -> ConversationState:
    """输入处理节点"""
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    node_name = "input_processor"
    display_name = "📝 输入处理节点"
    
    log_entry = {
        "step": step_count,
        "node": node_name,
        "display_name": display_name,
        "action": "开始处理用户输入",
        "timestamp": time.strftime("%H:%M:%S"),
        "input": user_input,
        "status": "processing"
    }
    
    processed_input = f"处理后的输入: {user_input}"
    
    log_entry["result"] = processed_input
    log_entry["status"] = "completed"
    
    # 返回完整的状态
    return {
        "user_input": user_input,
        "processed_input": processed_input,
        "analysis_result": state.get("analysis_result", ""),
        "ai_response": state.get("ai_response", ""),
        "final_response": state.get("final_response", ""),
        "execution_log": state.get("execution_log", []) + [log_entry],
        "step_count": step_count,
        "current_node": node_name,
        "node_display_name": display_name,
        "conversation_history": state.get("conversation_history", []),
        "system_prompt": state.get("system_prompt", "")
    }

def analysis_node(state: ConversationState) -> ConversationState:
    """分析节点"""
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    node_name = "analysis_node"
    display_name = "🔍 智能分析节点"
    
    log_entry = {
        "step": step_count,
        "node": node_name,
        "display_name": display_name,
        "action": "开始分析用户输入",
        "timestamp": time.strftime("%H:%M:%S"),
        "input": user_input,
        "status": "processing"
    }
    
    # 调用分析工具
    analysis_result = analyze_user_input(user_input)
    
    log_entry["result"] = analysis_result
    log_entry["status"] = "completed"
    log_entry["tool_used"] = "analyze_user_input"
    
    # 返回完整的状态
    return {
        "user_input": user_input,
        "processed_input": state.get("processed_input", ""),
        "analysis_result": analysis_result,
        "ai_response": state.get("ai_response", ""),
        "final_response": state.get("final_response", ""),
        "execution_log": state.get("execution_log", []) + [log_entry],
        "step_count": step_count,
        "current_node": node_name,
        "node_display_name": display_name,
        "conversation_history": state.get("conversation_history", []),
        "system_prompt": state.get("system_prompt", "")
    }

def ai_response_node(state: ConversationState) -> ConversationState:
    """
AI响应生成节点
    """
    user_input = state["user_input"]
    analysis_result = state.get("analysis_result", "")
    system_prompt = state.get("system_prompt", "你是一个有用的AI助手")
    step_count = state.get("step_count", 0) + 1
    
    node_name = "ai_response_node"
    display_name = "🤖 AI响应生成节点"
    
    log_entry = {
        "step": step_count,
        "node": node_name,
        "display_name": display_name,
        "action": "开始生成AI响应",
        "timestamp": time.strftime("%H:%M:%S"),
        "input": user_input,
        "status": "processing"
    }
    
    try:
        if LANGGRAPH_AVAILABLE:
            # 初始化LLM
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            import config as local_config
            
            llm = ChatOpenAI(
                model=local_config.model,
                base_url=local_config.base_url,
                api_key=local_config.api_key,
                temperature=0.7
            )
            
            prompt = f"""
{system_prompt}

用户输入: {user_input}
分析结果: {analysis_result}

请提供有帮助的回答:
"""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            ai_response = response.content
            log_entry["tool_used"] = "ChatOpenAI"
        else:
            # 模拟响应
            ai_response = f"根据您的问题 '{user_input}'，我建议您可以尝试以下方法来解决或了解相关内容。如果您需要更详细的信息，请告诉我您的具体需求。"
            log_entry["tool_used"] = "simulated_response"
            
    except Exception as e:
        ai_response = f"抱歉，处理您的请求时出现错误: {str(e)}"
        log_entry["error"] = str(e)
    
    log_entry["result"] = ai_response
    log_entry["status"] = "completed"
    
    # 返回完整的状态
    return {
        "user_input": user_input,
        "processed_input": state.get("processed_input", ""),
        "analysis_result": analysis_result,
        "ai_response": ai_response,
        "final_response": state.get("final_response", ""),
        "execution_log": state.get("execution_log", []) + [log_entry],
        "step_count": step_count,
        "current_node": node_name,
        "node_display_name": display_name,
        "conversation_history": state.get("conversation_history", []),
        "system_prompt": system_prompt
    }

def response_finalizer(state: ConversationState) -> ConversationState:
    """响应终结器节点"""
    ai_response = state.get("ai_response", "")
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    node_name = "response_finalizer"
    display_name = "✅ 响应终结器"
    
    log_entry = {
        "step": step_count,
        "node": node_name,
        "display_name": display_name,
        "action": "终结响应处理",
        "timestamp": time.strftime("%H:%M:%S"),
        "input": ai_response,
        "status": "processing"
    }
    
    final_response = f"\n\n✨ **最终回答**: \n{ai_response}\n\n✅ 处理完成于 {time.strftime('%H:%M:%S')}"
    
    # 添加对话历史
    conversation_entry = {
        "user": user_input,
        "assistant": ai_response,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    log_entry["result"] = final_response
    log_entry["status"] = "completed"
    
    # 返回完整的状态
    return {
        "user_input": user_input,
        "processed_input": state.get("processed_input", ""),
        "analysis_result": state.get("analysis_result", ""),
        "ai_response": ai_response,
        "final_response": final_response,
        "execution_log": state.get("execution_log", []) + [log_entry],
        "step_count": step_count,
        "current_node": node_name,
        "node_display_name": display_name,
        "conversation_history": state.get("conversation_history", []) + [conversation_entry],
        "system_prompt": state.get("system_prompt", "")
    }
class LangGraphChatInterface:
    """LangGraph智能对话界面"""
    
    def __init__(self):
        self.chat_state = ChatState()
        self.models = self._load_model_configs()
        self.current_workflow = None
        self.workflow_diagram = ""
        
    def _load_model_configs(self) -> dict:
        """加载预设模型配置"""
        return {
            "Qwen3-235B": ModelConfig(
                name="Qwen3-235B",
                model_name="Qwen3-235B-A22B-Instruct-2507",
                base_url="http://39.155.179.5:8002/v1",
                api_key="xxx",
                description="通义千问3代235B参数模型",
                temperature=0.7
            ),
            "DeepSeek-V3": ModelConfig(
                name="DeepSeek-V3",
                model_name="deepseek-v3",
                base_url="http://61.49.53.5:30002/v1",
                api_key="",
                description="DeepSeek V3模型",
                temperature=0.7
            ),
            "ModelScope-Qwen": ModelConfig(
                name="ModelScope-Qwen",
                model_name="qwen-plus-latest",
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key="sk-b5e591f6a4354b34bf34b26afc20969e",
                description="阿里云ModelScope平台的通义千问",
                temperature=0.7
            )
        }
    
    def _create_workflow(self, model_config: ModelConfig, system_prompt: str):
        """创建 LangGraph 工作流"""
        if not LANGGRAPH_AVAILABLE:
            return None
            
        try:
            # 设置环境变量
            os.environ["OPENAI_API_BASE"] = model_config.base_url
            os.environ["OPENAI_API_KEY"] = model_config.api_key
            
            # 创建状态图
            workflow = StateGraph(ConversationState)
            
            # 添加节点
            workflow.add_node("input_processor", input_processor)
            workflow.add_node("analysis_node", analysis_node)
            workflow.add_node("ai_response_node", ai_response_node)
            workflow.add_node("response_finalizer", response_finalizer)
            
            # 设置边
            workflow.set_entry_point("input_processor")
            workflow.add_edge("input_processor", "analysis_node")
            workflow.add_edge("analysis_node", "ai_response_node")
            workflow.add_edge("ai_response_node", "response_finalizer")
            workflow.add_edge("response_finalizer", END)
            
            # 编译图
            graph = workflow.compile()
            
            logger.info(f"成功创建 LangGraph 工作流，使用模型: {model_config.name}")
            return graph
            
        except Exception as e:
            logger.error(f"创建 LangGraph 工作流失败: {e}")
            return None
    
    def _generate_workflow_diagram(self, workflow) -> str:
        """生成工作流图表"""
        if not workflow:
            return ""
            
        try:
            # 生成 Mermaid 图
            mermaid_code = workflow.get_graph().draw_mermaid()
            return mermaid_code
        except Exception as e:
            logger.error(f"生成工作流图表失败: {e}")
            return ""
    
    def select_model(self, model_name: str, system_prompt: str):
        """选择并初始化模型"""
        if model_name not in self.models:
            return f"❌ 未找到模型配置: {model_name}", [], gr.update(), "", ""
        
        model_config = self.models[model_name]
        self.chat_state.current_model = model_name
        self.chat_state.system_prompt = system_prompt or self.chat_state.system_prompt
        
        if LANGGRAPH_AVAILABLE:
            self.current_workflow = self._create_workflow(model_config, self.chat_state.system_prompt)
            if self.current_workflow:
                self.workflow_diagram = self._generate_workflow_diagram(self.current_workflow)
                status_msg = f"✅ 已成功加载模型: {model_config.name}\n📍 服务地址: {model_config.base_url}\n🎯 模型: {model_config.model_name}\n🛠️ 工作流: 已创建 4 个节点的 LangGraph 工作流"
            else:
                status_msg = f"❌ 模型加载失败: {model_config.name}"
                self.workflow_diagram = ""
        else:
            status_msg = f"⚠️ 模拟模式 - 已选择模型: {model_config.name}\n请安装LangGraph库以获得完整功能"
            self.workflow_diagram = ""
        
        # 清空聊天历史
        self.chat_state.messages = []
        self.chat_state.execution_logs = []
        
        return status_msg, [], gr.update(interactive=True), self.workflow_diagram, ""
    
    def add_custom_model(self, name: str, model_name: str, base_url: str, api_key: str, description: str):
        """添加自定义模型配置"""
        if not all([name, model_name, base_url]):
            return "❌ 请填写必要的模型信息（名称、模型名、服务地址）", gr.update()
        
        self.models[name] = ModelConfig(
            name=name,
            model_name=model_name,
            base_url=base_url,
            api_key=api_key or "",
            description=description or "自定义模型配置"
        )
        
        model_choices = list(self.models.keys())
        return f"✅ 已添加自定义模型: {name}", gr.update(choices=model_choices, value=name)
    def chat_response(self, message: str, history: List[Tuple[str, Optional[str]]]):
        """处理聊天响应"""
        if not message.strip():
            return history, "", ""
        
        if not self.chat_state.current_model:
            history.append((message, "❌ 请先选择一个模型配置"))
            return history, "", ""
        
        # 添加用户消息到历史（临时设为None，后续会更新）
        history.append((message, None))
        execution_log_text = ""
        
        try:
            if LANGGRAPH_AVAILABLE and self.current_workflow:
                # 使用LangGraph工作流处理
                initial_state = {
                    "user_input": message,
                    "system_prompt": self.chat_state.system_prompt,
                    "step_count": 0,
                    "execution_log": [],
                    "conversation_history": []
                }
                
                # 执行工作流
                execution_logs = []
                final_response = ""
                
                for chunk in self.current_workflow.stream(initial_state, stream_mode="values"):
                    if "current_node" in chunk:
                        node_info = {
                            "node": chunk.get("current_node", ""),
                            "display_name": chunk.get("node_display_name", ""),
                            "step": chunk.get("step_count", 0)
                        }
                        execution_logs.append(node_info)
                    
                    if "final_response" in chunk:
                        final_response = chunk["final_response"]
                    
                    if "execution_log" in chunk and chunk["execution_log"]:
                        for log in chunk["execution_log"]:
                            if log not in execution_logs:
                                execution_logs.append(log)
                
                # 格式化执行日志
                if execution_logs:
                    log_lines = ["🔄 **执行过程**:"]
                    for i, log in enumerate(execution_logs[-10:]):
                        if isinstance(log, dict):
                            display_name = log.get('display_name', log.get('node', ''))
                            timestamp = log.get('timestamp', '')
                            action = log.get('action', '')
                            status = log.get('status', '')
                            tool_used = log.get('tool_used', '')
                            
                            if display_name and timestamp:
                                status_icon = "✅" if status == "completed" else "⏳"
                                tool_info = f" [Tool: {tool_used}]" if tool_used else ""
                                log_lines.append(f"{i+1}. {status_icon} {display_name} - {action} ({timestamp}){tool_info}")
                    
                    execution_log_text = "\n".join(log_lines)
                
                # 提取最终响应
                if final_response:
                    # 清理格式化文本
                    clean_response = final_response.replace("✨ **最终回答**: \n", "").replace("\n\n✅ 处理完成于", "").strip()
                    # 查找最后一个时间戳
                    import re
                    time_pattern = r'\d{2}:\d{2}:\d{2}'
                    clean_response = re.sub(time_pattern + r'.*$', '', clean_response).strip()
                    response = clean_response
                else:
                    response = "抱歉，处理您的请求时未能获取到有效响应。"
                
            else:
                # 模拟响应
                response = self._simulate_langgraph_response(message)
                execution_log_text = self._simulate_execution_log()
            
            # 更新历史记录
            history[-1] = (message, response)
            
        except Exception as e:
            logger.error(f"聊天响应出错: {e}")
            history[-1] = (message, f"❌ 处理消息时出错: {str(e)}")
            execution_log_text = f"❌ 执行错误: {str(e)}"
        
        return history, "", execution_log_text
    
    def _simulate_langgraph_response(self, message: str) -> str:
        """模拟 LangGraph 响应"""
        responses = [
            f"根据您的问题 '{message}'，我的分析结果如下：",
            "这是一个模拟的 LangGraph 工作流响应。",
            "在真实环境中，这里会运行完整的 LangGraph 工作流。",
            "请安装 LangGraph 库以获得完整的智能对话功能。"
        ]
        return "\n\n".join(responses)
    
    def _simulate_execution_log(self) -> str:
        """模拟执行日志"""
        logs = [
            "🔄 **执行过程** (模拟模式):",
            "1. ✅ 📝 输入处理节点 - 开始处理用户输入 (12:34:56)",
            "2. ✅ 🔍 智能分析节点 - 开始分析用户输入 (12:34:57) [Tool: analyze_user_input]",
            "3. ✅ 🤖 AI响应生成节点 - 开始生成AI响应 (12:34:58) [Tool: ChatOpenAI]",
            "4. ✅ ✅ 响应终结器 - 终结响应处理 (12:34:59)",
            "",
            "⚠️ 注意: 当前为模拟模式，请安装 LangGraph 库以获得实际执行结果。"
        ]
        return "\n".join(logs)
    
    def clear_chat(self):
        """清空聊天记录"""
        self.chat_state.messages = []
        self.chat_state.execution_logs = []
        return [], ""
    
    def export_chat(self, history: List[Tuple[str, str]]):
        """导出聊天记录"""
        if not history:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"langgraph_chat_export_{timestamp}.json"
        
        export_data = {
            "timestamp": timestamp,
            "model": self.chat_state.current_model,
            "system_prompt": self.chat_state.system_prompt,
            "workflow_type": "LangGraph",
            "conversations": [{"user": user, "assistant": assistant} for user, assistant in history if user and assistant],
            "execution_logs": self.chat_state.execution_logs,
            "workflow_diagram": self.workflow_diagram
        }
        
        # 确保 logs 目录存在
        os.makedirs("logs", exist_ok=True)
        filepath = f"logs/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def create_interface(self):
        """创建 Gradio 界面"""
        with gr.Blocks(title="LangGraph 智能对话系统", theme=gr.themes.Soft()) as interface:
            gr.Markdown("""
            # 🤖 LangGraph 智能对话系统
            
            基于 LangGraph 框架的对话界面，支持可视化工作流、节点执行监控和实时日志
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("## ⚙️ 模型配置")
                    
                    # 模型选择
                    model_dropdown = gr.Dropdown(
                        choices=list(self.models.keys()),
                        label="选择预设模型",
                        value="",
                        interactive=True
                    )
                    
                    system_prompt = gr.Textbox(
                        label="系统提示词",
                        value=self.chat_state.system_prompt,
                        lines=3,
                        placeholder="定义AI助手的角色和行为..."
                    )
                    
                    select_btn = gr.Button("🚀 加载模型", variant="primary")
                    
                    status_display = gr.Textbox(
                        label="状态信息",
                        lines=6,
                        interactive=False
                    )
                    
                    # 自定义模型配置
                    with gr.Accordion("➕ 添加自定义模型", open=False):
                        custom_name = gr.Textbox(label="模型名称", placeholder="例如：My-GPT-4")
                        custom_model = gr.Textbox(label="模型ID", placeholder="例如：gpt-4-turbo")
                        custom_url = gr.Textbox(label="API地址", placeholder="例如：https://api.openai.com/v1")
                        custom_key = gr.Textbox(label="API密钥", type="password", placeholder="sk-...")
                        custom_desc = gr.Textbox(label="描述", placeholder="模型说明...")
                        
                        add_custom_btn = gr.Button("添加模型")
                    
                    # 工作流图显示
                    with gr.Accordion("🔄 LangGraph 工作流图", open=False):
                        workflow_diagram = gr.Code(
                            label="Mermaid 工作流图",
                            language="mermaid",
                            lines=15,
                            interactive=False
                        )
                
                with gr.Column(scale=2):
                    gr.Markdown("## 💬 对话区域")
                    
                    # 聊天界面
                    chatbot = gr.Chatbot(
                        height=400,
                        show_label=False,
                        avatar_images=("👤", "🤖"),
                        bubble_full_width=False
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder="输入您的问题...",
                            show_label=False,
                            scale=4,
                            interactive=False  # 初始状态不可用
                        )
                        send_btn = gr.Button("发送", variant="primary", interactive=False)
                    
                    # 执行日志
                    execution_log = gr.Textbox(
                        label="🔄 节点执行日志",
                        lines=8,
                        max_lines=15,
                        interactive=False,
                        placeholder="节点执行信息将在这里实时显示..."
                    )
                    
                    with gr.Row():
                        clear_btn = gr.Button("🗑️ 清空对话", variant="secondary")
                        export_btn = gr.Button("📤 导出对话", variant="secondary")
            
            # 事件绑定
            select_btn.click(
                fn=self.select_model,
                inputs=[model_dropdown, system_prompt],
                outputs=[status_display, chatbot, msg_input, workflow_diagram, execution_log]
            )
            
            add_custom_btn.click(
                fn=self.add_custom_model,
                inputs=[custom_name, custom_model, custom_url, custom_key, custom_desc],
                outputs=[status_display, model_dropdown]
            )
            
            # 聊天功能
            def submit_message(message, history):
                return self.chat_response(message, history)
            
            msg_input.submit(
                fn=submit_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input, execution_log]
            )
            
            send_btn.click(
                fn=submit_message,
                inputs=[msg_input, chatbot],
                outputs=[chatbot, msg_input, execution_log]
            )
            
            clear_btn.click(
                fn=self.clear_chat,
                outputs=[chatbot, execution_log]
            )
            
            export_btn.click(
                fn=self.export_chat,
                inputs=[chatbot],
                outputs=[gr.File()]
            )
            
            # 页脚信息
            gr.Markdown("""
            ---
            ### 📝 使用说明
            1. **选择模型**：从预设模型中选择或添加自定义模型配置
            2. **配置系统提示词**：定义AI助手的角色和行为方式
            3. **加载模型**：点击"加载模型"按钮初始化选定的模型，同时生成 LangGraph 工作流
            4. **查看工作流图**：展开"LangGraph 工作流图"可以查看 Mermaid 格式的工作流图表
            5. **开始对话**：在输入框中输入问题，按回车或点击发送
            6. **监控执行**：在"节点执行日志"区域实时查看各个节点的执行过程和工具调用情况
            7. **导出对话**：可以将对话记录和执行日志导出为JSON格式文件
            
            ### 🔄 LangGraph 工作流说明
            - **📝 输入处理节点**：处理和预处理用户输入
            - **🔍 智能分析节点**：使用工具分析用户意图和内容
            - **🤖 AI响应生成节点**：调用大语言模型生成智能回复
            - **✅ 响应终结器**：整理和输出最终回复
            
            ### ⚠️ 注意事项
            - 请确保网络连接正常，能够访问配置的API地址
            - API密钥请妥善保管，不要泄露给他人
            - 模型响应速度取决于网络条件和服务器性能
            - 执行日志显示 LangGraph 工作流中每个节点的执行情况
            """)
        
        return interface

def main():
    """主函数"""
    # 创建界面实例
    chat_interface = LangGraphChatInterface()
    
    # 创建并启动界面
    interface = chat_interface.create_interface()
    print(1)
    # 启动服务
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )

if __name__ == "__main__":
    main()