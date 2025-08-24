"""
LangGraph 复杂提示链示例

这个示例展示了如何使用LangGraph的StateGraph API实现复杂的提示链工作流。

主要特点：
- 使用StateGraph构建复杂工作流
- 状态管理和条件路由
- 迭代优化和质量评估
- 结构化输出和反馈
- 自动质量控制和改进
"""

import os
import sys
import time
import uuid
from typing import TypedDict, List, Literal, Optional
from typing_extensions import Annotated
import operator

# 添加路径以导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 导入必要的库
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key

# 初始化语言模型
llm = ChatOpenAI(
    model=config.model,
    temperature=0.1,
    max_tokens=1000
)

# ===== 1. 复杂提示链示例 (StateGraph API) =====



# 定义状态
class PromptChainState(TypedDict):
    topic: str
    original_content: str
    improved_content: str
    polished_content: str
    quality_score: float
    iteration_count: int
    final_result: str

# 定义结构化输出模式
class QualityFeedback(BaseModel):
    score: float = Field(description="质量评分 (0-10)")
    feedback: str = Field(description="改进建议")
    needs_improvement: bool = Field(description="是否需要进一步改进")

# 为LLM添加结构化输出能力
quality_evaluator = llm.with_structured_output(QualityFeedback)

def generate_initial_content(state: PromptChainState) -> PromptChainState:
    """生成初始内容"""
    topic = state["topic"]
    print(f"🎯 为话题 '{topic}' 生成初始内容...")
    
    response = llm.invoke([
        SystemMessage(content="你是一个专业的内容创作者。请根据给定话题创作高质量的内容。"),
        HumanMessage(content=f"请为话题 '{topic}' 创作一段有趣、有深度的内容。")
    ])
    
    return {"original_content": response.content}

def evaluate_quality(state: PromptChainState) -> PromptChainState:
    """评估内容质量"""
    content = state["original_content"]
    print("🔍 评估内容质量...")
    
    feedback = quality_evaluator.invoke([
        SystemMessage(content="你是一个专业的内容评估专家。请评估以下内容的质量并提供改进建议。"),
        HumanMessage(content=f"请评估以下内容：\n\n{content}")
    ])
    
    return {
        "quality_score": feedback.score,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def improve_content(state: PromptChainState) -> PromptChainState:
    """改进内容"""
    content = state["original_content"]
    print("✨ 改进内容...")
    
    response = llm.invoke([
        SystemMessage(content="你是一个专业的内容编辑。请根据反馈改进内容。"),
        HumanMessage(content=f"请改进以下内容：\n\n{content}")
    ])
    
    return {"improved_content": response.content}

def polish_content(state: PromptChainState) -> PromptChainState:
    """润色内容"""
    content = state.get("improved_content", state["original_content"])
    print("💎 润色内容...")
    
    response = llm.invoke([
        SystemMessage(content="你是一个专业的文案润色专家。请对内容进行最终润色。"),
        HumanMessage(content=f"请润色以下内容：\n\n{content}")
    ])
    
    return {"polished_content": response.content}

def should_continue(state: PromptChainState) -> Literal["improve", "polish", "end"]:
    """决定是否继续改进"""
    score = state.get("quality_score", 0)
    iteration = state.get("iteration_count", 0)
    
    print(f"📊 当前质量评分: {score}, 迭代次数: {iteration}")
    
    if score >= 8.0:
        return "polish"
    elif iteration < 3:
        return "improve"
    else:
        return "end"

def finalize_result(state: PromptChainState) -> PromptChainState:
    """最终化结果"""
    final_content = state.get("polished_content", state.get("improved_content", state["original_content"]))
    print("🎉 最终化结果...")
    
    return {"final_result": final_content}

def build_complex_prompt_chain():
    """构建复杂提示链图"""
    print("🏗️ 构建复杂提示链图...")
    
    # 创建状态图
    workflow = StateGraph(PromptChainState)
    
    # 添加节点
    workflow.add_node("generate_initial", generate_initial_content)
    workflow.add_node("evaluate_quality", evaluate_quality)
    workflow.add_node("improve_content", improve_content)
    workflow.add_node("polish_content", polish_content)
    workflow.add_node("finalize_result", finalize_result)
    
    # 添加边
    workflow.add_edge(START, "generate_initial")
    workflow.add_edge("generate_initial", "evaluate_quality")
    workflow.add_conditional_edges(
        "evaluate_quality",
        should_continue,
        {
            "improve": "improve_content",
            "polish": "polish_content",
            "end": "finalize_result"
        }
    )
    workflow.add_edge("improve_content", "evaluate_quality")
    workflow.add_edge("polish_content", "finalize_result")
    workflow.add_edge("finalize_result", END)
    
    # 编译图
    chain = workflow.compile()
    print("✅ 复杂提示链图构建完成！")
    
    return chain



# ===== 2. 运行示例函数 =====

def run_complex_example():
    """运行复杂提示链示例"""
    print("=" * 60)
    print("🚀 复杂提示链示例")
    print("=" * 60)
    
    # 构建图
    chain = build_complex_prompt_chain()
    
    # 执行
    topic = "可持续发展"
    state = chain.invoke({"topic": topic})
    
    print(f"\n🎉 最终结果:")
    print(f"原始内容: {state['original_content']}")
    print(f"质量评分: {state['quality_score']}")
    print(f"迭代次数: {state['iteration_count']}")
    print(f"最终结果: {state['final_result']}")

def main():
    """主函数"""
    print("🎭 LangGraph Prompt Chain 示例")
    print("=" * 60)
    
    # 检查API密钥
    if config.api_key == "your-openai-api-key":
        print("⚠️  请设置有效的OpenAI API密钥")
        print("   可以通过环境变量 OPENAI_API_KEY 设置")
        return
    
    # 直接运行复杂提示链示例
    print("\n🚀 运行复杂提示链示例...")
    run_complex_example()

if __name__ == "__main__":
    main()
