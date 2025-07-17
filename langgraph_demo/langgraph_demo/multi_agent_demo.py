"""langgraph_demo.multi_agent_demo

一个使用 LangGraph 构建的多智能体 Demo：
1. ResearchAgent 负责根据用户查询进行资料收集（调用 LLM 进行搜索模拟）。
2. SummaryAgent 负责对 ResearchAgent 的结果进行总结。

支持本地模型（Ollama）、云端模型（OpenAI）和DeepSeek模型（VLLM部署）。

运行方式：
$ python -m langgraph_demo.multi_agent_demo "你的问题"
"""
from __future__ import annotations

import os
import sys
from typing import Dict, Any, TypedDict, Optional, cast

from dotenv import load_dotenv
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# -----------------------------------------------------------------------------
# 环境变量加载
# -----------------------------------------------------------------------------
load_dotenv()
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_R1_BASE_URL")

# -----------------------------------------------------------------------------
# 状态类型定义
# -----------------------------------------------------------------------------
class AgentState(TypedDict):
    """Agent状态类型定义"""
    query: str
    research_notes: Optional[str]
    summary: Optional[str]

# -----------------------------------------------------------------------------
# LLM 初始化 - 支持本地和云端模型
# -----------------------------------------------------------------------------

def get_llm(model_type: str = "local", model_name: str = "qwen"):
    """
    获取LLM实例
    
    Args:
        model_type: "local", "openai" 或 "deepseek-vllm" 
        model_name: 模型名称
            - 本地模型: "qwen2.5:7b", "llama3.1:8b", "gemma2:9b" 等
            - OpenAI模型: "gpt-3.5-turbo", "gpt-4" 等
            - DeepSeek模型: 对应的模型名称
    """

    if model_type.lower() == "deepseek-vllm":
        try:
            # 使用VLLM部署的DeepSeek模型（通过OpenAI兼容API）
            return ChatOpenAI(
                model=model_name, 
                temperature=0.7,
                base_url=DEEPSEEK_BASE_URL,
                api_key="dummy-key"  # OpenAI兼容API通常需要任意API密钥
            )
        except Exception as e:
            print(f"DeepSeek-VLLM模型连接失败: {e}")
            print("请确保已正确启动VLLM服务")
            print("启动示例: python -m vllm.entrypoints.openai.api_server --model deepseek-coder")
            sys.exit(1)
    else:
        raise ValueError("model_type 必须是 'local', 'openai' 或 'deepseek-vllm'")

# 默认使用本地模型，可通过环境变量或命令行参数修改
DEFAULT_MODEL_TYPE = os.getenv("MODEL_TYPE", "local")
DEFAULT_MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")

# 初始化两个LLM实例（可以混合使用本地和云端模型）
llm_research = get_llm(DEFAULT_MODEL_TYPE, DEFAULT_MODEL_NAME)
llm_summary = get_llm(DEFAULT_MODEL_TYPE, DEFAULT_MODEL_NAME)

# -----------------------------------------------------------------------------
# Prompt 模版
# -----------------------------------------------------------------------------
research_prompt = ChatPromptTemplate.from_template(
    """
    你是一名研究专家，需要收集关于 "{query}" 的资料、研究现状、关键论文与结论。
    输出应采用 markdown 列表，每个要点不超过 3 行。
    """
)
summary_prompt = ChatPromptTemplate.from_template(
    """
    你是一名写作助理，需要基于以下研究资料写出 3 段文字的摘要，每段 2~3 句：

    === 研究资料开始 ===
    {research_notes}
    === 研究资料结束 ===
    """
)

# -----------------------------------------------------------------------------
# 节点定义
# -----------------------------------------------------------------------------

def research_node(state: AgentState) -> AgentState:
    """Research Agent 节点，输入 state，其中包含 'query'。输出附加 'research_notes'。"""
    query: str = state["query"]
    
    # 构造 prompt 并调用 LLM
    chain = research_prompt | llm_research
    response = chain.invoke({"query": query})
    
    # 获取响应文本
    research_notes = str(response.content if hasattr(response, 'content') else response)
    
    # 打印日志
    print("\n====== Research Agent ======")
    print(research_notes)
    print("===========================\n")
    
    # 返回新 state
    return cast(AgentState, {
        "query": query, 
        "research_notes": research_notes, 
        "summary": None
    })


def summary_node(state: AgentState) -> AgentState:
    """Summary Agent 节点，输入 state，其中包含 'research_notes'。输出附加 'summary'。"""
    query: str = state["query"]
    research_notes: Optional[str] = state["research_notes"]
    
    if not research_notes:
        research_notes = "未找到研究资料"
    
    # 构造 prompt 并调用 LLM
    chain = summary_prompt | llm_summary
    response = chain.invoke({"research_notes": research_notes})
    
    # 获取响应文本
    summary = str(response.content if hasattr(response, 'content') else response)
    
    # 打印日志
    print("\n====== Summary Agent ======")
    print(summary)
    print("==========================\n")
    
    # 返回新 state
    return cast(AgentState, {
        "query": query, 
        "research_notes": research_notes, 
        "summary": summary
    })

# -----------------------------------------------------------------------------
# 流程图构建
# -----------------------------------------------------------------------------

def build_graph():
    """构建工作流程图并返回编译后的图"""
    # 创建带有状态模式的图
    graph = StateGraph(AgentState)
    
    # 添加节点
    graph.add_node("research", research_node)
    graph.add_node("summary", summary_node)

    # research → summary → END
    graph.add_edge("research", "summary")
    graph.add_edge("summary", END)

    graph.set_entry_point("research")
    # 返回编译后的图
    return graph.compile()

# -----------------------------------------------------------------------------
# 命令行接口
# -----------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("请在命令行参数中提供查询问题，例如：\npython -m langgraph_demo.multi_agent_demo \"量子计算的发展现状？\"")
        print("\n环境变量配置:")
        print("- MODEL_TYPE: local、openai 或 deepseek-vllm (默认: local)")
        print("- MODEL_NAME: 模型名称 (默认: qwen2.5:7b)")
        print("- OPENAI_API_KEY: OpenAI API密钥 (仅当MODEL_TYPE=openai时需要)")
        print("- DEEPSEEK_R1_BASE_URL: DeepSeek VLLM API地址 (仅当MODEL_TYPE=deepseek-vllm时需要)")
        sys.exit(1)

    query = sys.argv[1]

    # 显示当前使用的模型配置
    print(f"使用模型类型: {DEFAULT_MODEL_TYPE}")
    print(f"使用模型名称: {DEFAULT_MODEL_NAME}")
    print(f"查询问题: {query}\n")

    workflow = build_graph()
    initial_state = cast(AgentState, {"query": query, "research_notes": None, "summary": None})
    final_state = workflow.invoke(initial_state)

    print("\n================ 最终摘要 ================")
    print(final_state["summary"])
    print("========================================\n")


if __name__ == "__main__":
    main() 