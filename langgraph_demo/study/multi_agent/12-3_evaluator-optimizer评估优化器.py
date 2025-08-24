"""
LangGraph 笑话评估优化器示例

这个示例展示了如何使用LangGraph实现笑话评估优化器模式：
- 生成器：负责生成笑话
- 评估器：评估笑话质量并提供反馈
- 优化器：根据反馈改进笑话

主要特点：
- 使用StateGraph API构建工作流
- 结构化评估反馈
- 迭代优化直到达到目标质量
"""

import os
import sys
from typing import TypedDict, Literal

# 添加路径以导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 导入必要的库
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key

# 初始化语言模型
llm = ChatOpenAI(
    model=config.model,
    temperature=0.1,
    max_tokens=1000
)



# 定义状态
class JokeState(TypedDict):
    topic: str
    joke: str
    feedback: str
    funny_or_not: str
    iteration_count: int

# 定义结构化输出模式
class JokeFeedback(BaseModel):
    grade: Literal["funny", "not funny"] = Field(
        description="判断笑话是否有趣"
    )
    feedback: str = Field(
        description="如果笑话不够有趣，提供改进建议"
    )
    score: int = Field(
        description="笑话质量评分 (1-10)",
        ge=1,
        le=10
    )

# todo 为LLM添加结构化输出能力
joke_evaluator = llm.with_structured_output(JokeFeedback)

def generate_joke(state: JokeState) -> JokeState:
    """生成笑话"""
    topic = state["topic"]
    feedback = state.get("feedback", "")
    iteration = state.get("iteration_count", 0)
    
    print(f"🎭 第 {iteration + 1} 次尝试为话题 '{topic}' 生成笑话...")
    
    if feedback:
        prompt = f"请为话题 '{topic}' 写一个有趣的笑话，并考虑以下反馈：{feedback}"
    else:
        prompt = f"请为话题 '{topic}' 写一个有趣的笑话。"
    
    response = llm.invoke(prompt)
    
    return {
        "joke": response.content,
        "iteration_count": iteration + 1
    }

def evaluate_joke(state: JokeState) -> JokeState:
    """评估笑话"""
    joke = state["joke"]
    print(f"🔍 评估笑话: {joke[:50]}...")
    
    feedback = joke_evaluator.invoke([
        SystemMessage(content="你是一个专业的笑话评估专家。请评估以下笑话的质量，并提供具体的改进建议。"),
        HumanMessage(content=f"请评估这个笑话：\n\n{joke}")
    ])
    
    print(f"📊 评分: {feedback.score}/10, 等级: {feedback.grade}")
    
    return {
        "funny_or_not": feedback.grade,
        "feedback": feedback.feedback
    }

def route_joke(state: JokeState) -> Literal["Accepted", "Rejected + Feedback"]:
    """根据评估结果决定路由"""
    grade = state["funny_or_not"]
    score = state.get("score", 0)
    iteration = state.get("iteration_count", 0)
    
    print(f"🔄 路由决策: 等级={grade}, 评分={score}, 迭代={iteration}")
    
    # 如果笑话有趣或达到最大迭代次数，则接受
    if grade == "funny" or iteration >= 5:
        return "Accepted"
    else:
        return "Rejected + Feedback"

def build_joke_evaluator_optimizer():
    """构建笑话评估优化器图"""
    print("🏗️ 构建笑话评估优化器图...")
    
    # 创建状态图
    workflow = StateGraph(JokeState)
    
    # 添加节点
    workflow.add_node("generate_joke", generate_joke)
    workflow.add_node("evaluate_joke", evaluate_joke)
    
    # 添加边
    workflow.add_edge(START, "generate_joke")
    workflow.add_edge("generate_joke", "evaluate_joke")
    workflow.add_conditional_edges(
        "evaluate_joke",
        route_joke,
        {
            "Accepted": END,
            "Rejected + Feedback": "generate_joke"
        }
    )
    
    # 编译图
    chain = workflow.compile()
    print("✅ 笑话评估优化器图构建完成！")
    
    return chain



# ===== 2. 运行示例函数 =====

def run_joke_evaluator_optimizer():
    """运行笑话评估优化器示例"""
    print("=" * 60)
    print("🚀 笑话评估优化器示例")
    print("=" * 60)
    
    # 构建图
    chain = build_joke_evaluator_optimizer()
    
    # 执行
    topic = "人工智能"
    state = chain.invoke({"topic": topic})
    
    print(f"\n🎉 最终结果:")
    print(f"话题: {topic}")
    print(f"最终笑话: {state['joke']}")
    print(f"迭代次数: {state['iteration_count']}")
    print(f"最终评估: {state['funny_or_not']}")



def main():
    """主函数"""
    print("🎭 LangGraph 笑话评估优化器示例")
    print("=" * 60)
    
    # 检查API密钥
    if config.api_key == "your-openai-api-key":
        print("⚠️  请设置有效的OpenAI API密钥")
        print("   可以通过环境变量 OPENAI_API_KEY 设置")
        exit()
    
    # 直接运行笑话评估优化器示例
    print("\n🚀 运行笑话评估优化器示例...")
    run_joke_evaluator_optimizer()


if __name__ == "__main__":
    main()
