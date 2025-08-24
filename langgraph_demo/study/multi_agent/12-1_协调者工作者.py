"""
LangGraph Orchestrator-Worker 模式示例

这个示例展示了如何使用LangGraph实现协调者-工作者模式：
- 协调者(orchestrator): 负责规划和分配任务
- 工作者(worker): 执行具体的任务
- 合成器(synthesizer): 整合所有工作者的结果

主要特点：
1. 使用Send API进行动态任务分配
2. 并行执行多个工作者任务
3. 状态管理和结果聚合
"""

import operator
from typing import Annotated, TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 获取日志器
logger = config.logger

# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 初始化LLM模型
# 初始化语言模型
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,  # 较低的温度确保输出的一致性
    max_tokens=1000   # 限制输出长度
)

# 定义报告章节的结构化输出模式
class Section(BaseModel):
    name: str = Field(description="章节名称")
    description: str = Field(description="章节内容描述")

class Sections(BaseModel):
    sections: List[Section] = Field(description="报告的所有章节")

# 为LLM添加结构化输出能力
planner = llm.with_structured_output(Sections)

# 定义图状态
class State(TypedDict):
    topic: str  # 报告主题
    sections: List[Section]  # 报告章节列表
    completed_sections: Annotated[List[str], operator.add]  # 所有工作者并行写入此键
    final_report: str  # 最终报告

# 定义工作者状态
class WorkerState(TypedDict):
    section: Section
    completed_sections: Annotated[List[str], operator.add]

def orchestrator(state: State):
    """协调者：生成报告计划"""
    print(f"🎯 协调者正在为主题 '{state['topic']}' 制定计划...")
    
    # 生成报告章节计划
    report_sections = planner.invoke([
        SystemMessage(content="你是一个专业的报告规划专家。请为给定的主题生成一个详细的报告大纲，包含3-5个章节。每个章节都应该有明确的名称和描述。"),
        HumanMessage(content=f"请为主题 '{state['topic']}' 制定一个详细的报告大纲。")
    ])
    
    print(f"📋 已生成 {len(report_sections.sections)} 个章节的计划")
    return {"sections": report_sections.sections}

def llm_call(state: WorkerState):
    """工作者：撰写报告章节"""
    section = state['section']
    print(f"📝 工作者正在撰写章节: {section.name}")
    
    # 生成章节内容
    section_content = llm.invoke([
        SystemMessage(content="你是一个专业的报告撰写专家。请根据提供的章节名称和描述撰写详细的内容。使用markdown格式，内容要专业、详细且有条理。"),
        HumanMessage(content=f"请撰写章节 '{section.name}' 的内容。\n章节描述: {section.description}\n\n请提供详细、专业的内容。")
    ])
    
    print(f"✅ 章节 '{section.name}' 撰写完成")
    return {"completed_sections": [section_content.content]}

def synthesizer(state: State):
    """合成器：整合完整报告"""
    print("🔗 合成器正在整合所有章节...")
    
    # 获取所有完成的章节
    completed_sections = state["completed_sections"]
    
    # 格式化章节内容
    completed_report_sections = "\n\n---\n\n".join(completed_sections)
    
    # 添加报告标题和总结
    final_report = f"# {state['topic']}\n\n{completed_report_sections}\n\n---\n\n## 报告总结\n\n本报告涵盖了关于 {state['topic']} 的全面分析，包含 {len(completed_sections)} 个主要章节。"
    
    print("🎉 报告整合完成！")
    return {"final_report": final_report}

def assign_workers(state: State):
    """分配工作者：为每个章节创建并行工作者"""
    print(f"🚀 正在为 {len(state['sections'])} 个章节分配工作者...")
    
    # 使用Send API为每个章节创建并行工作者
    # todo workstats 与stats 转换
    return [Send("llm_call", {"section": s}) for s in state["sections"]]

def should_continue(state: State):
    """判断是否继续执行"""
    # 如果所有章节都完成了，继续到合成器
    if len(state.get("completed_sections", [])) == len(state.get("sections", [])):
        return "synthesizer"
    return "llm_call"

# 构建工作流
def build_orchestrator_worker_graph():
    """构建协调者-工作者图"""
    print("🏗️ 正在构建协调者-工作者图...")
    
    # 创建状态图
    orchestrator_worker_builder = StateGraph(State)
    
    # 添加节点
    orchestrator_worker_builder.add_node("orchestrator", orchestrator)
    orchestrator_worker_builder.add_node("llm_call", llm_call)
    orchestrator_worker_builder.add_node("synthesizer", synthesizer)
    
    # 添加边连接节点
    orchestrator_worker_builder.add_edge(START, "orchestrator")
    orchestrator_worker_builder.add_conditional_edges(
        "orchestrator", 
        assign_workers, 
        ["llm_call"]
    )
    orchestrator_worker_builder.add_edge("llm_call", "synthesizer")
    orchestrator_worker_builder.add_edge("synthesizer", END)
    
    # 编译图
    graph = orchestrator_worker_builder.compile()
    print("✅ 图构建完成！")
    
    return graph


def run_simple_example():
    """运行简化示例（不使用流式输出）"""
    print("=" * 60)
    print("🚀 LangGraph 协调者-工作者模式简化示例")
    print("=" * 60)
    
    # 构建图
    graph = build_orchestrator_worker_graph()
    
    # 定义报告主题
    topic = "可持续发展与环境保护"
    
    print(f"\n📋 开始生成关于 '{topic}' 的报告...")
    
    # 执行图
    try:
        final_state = graph.invoke({"topic": topic})
        
        print("\n" + "=" * 60)
        print("📄 最终报告")
        print("=" * 60)
        print(final_state["final_report"])
        
        return final_state
        
    except Exception as e:
        print(f"❌ 执行过程中出现错误: {e}")
        return None

if __name__ == "__main__":
    # 运行示例
    # 注意：需要设置有效的OpenAI API密钥
    print("⚠️  请确保已设置有效的OpenAI API密钥")
    print("   可以通过设置环境变量 OPENAI_API_KEY 或修改代码中的API密钥")
    
    # 运行简化示例
    result = run_simple_example()
    
    if result:
        print("\n✅ 示例执行成功！")
    else:
        print("\n❌ 示例执行失败，请检查API密钥配置")
