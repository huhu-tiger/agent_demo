# -*- coding: utf-8 -*-
"""
LangGraph 多智能体协作示例
学习要点：复杂状态管理、智能体协作、结果整合

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
from typing import TypedDict, List, Dict
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# LangChain 组件
from langchain_core.messages import HumanMessage, AIMessage

import config

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger

# ============================================================================
# 协作状态定义
# ============================================================================

class CollaborationState(TypedDict):
    """协作状态 - 多个智能体共享的复杂状态"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    research_result: str
    analysis_result: str
    planning_result: str
    execution_result: str
    final_report: str
    collaboration_log: List[str]
    agent_performance: Dict[str, str]

# ============================================================================
# 专业智能体定义
# ============================================================================

def researcher_agent(state: CollaborationState) -> CollaborationState:
    """
    研究员智能体 - 负责信息收集和研究
    学习要点：信息收集和整理
    """
    logger.info("🔬 研究员智能体正在收集信息...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    collaboration_log = state.get("collaboration_log", [])
    collaboration_log.append("研究员开始工作")
    
    # 模拟研究过程
    research_result = f"关于 '{user_input}' 的研究发现：\n\n"
    research_result += "📊 数据收集：\n"
    research_result += "• 收集了相关文献和资料\n"
    research_result += "• 分析了市场趋势和用户需求\n"
    research_result += "• 整理了技术发展现状\n\n"
    
    research_result += "📈 关键发现：\n"
    research_result += "• 这是一个热门话题，关注度持续上升\n"
    research_result += "• 存在多种技术路线和解决方案\n"
    research_result += "• 用户需求多样化，需要个性化方案\n"
    research_result += "• 技术发展迅速，需要持续跟踪\n\n"
    
    research_result += "🎯 研究结论：\n"
    research_result += "• 具有很高的商业价值和技术价值\n"
    research_result += "• 建议深入分析和规划\n"
    research_result += "• 需要多角度考虑实施策略"
    
    collaboration_log.append("研究员完成信息收集")
    
    logger.info("研究员智能体工作完成")
    
    return {
        "research_result": research_result,
        "collaboration_log": collaboration_log,
        "agent_performance": {"researcher": "优秀"},
        "messages": [AIMessage(content=f"研究完成：已收集关于 '{user_input}' 的详细信息")]
    }

def analyst_agent(state: CollaborationState) -> CollaborationState:
    """
    分析师智能体 - 负责数据分析和洞察
    学习要点：数据分析和洞察生成
    """
    logger.info("📊 分析师智能体正在分析数据...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    research_result = state["research_result"]
    collaboration_log = state["collaboration_log"]
    collaboration_log.append("分析师开始工作")
    
    # 基于研究结果进行分析
    analysis_result = f"基于研究结果的数据分析：\n\n"
    analysis_result += "📋 信息质量评估：\n"
    analysis_result += "• 信息可信度：高 (95%)\n"
    analysis_result += "• 数据完整性：良好 (85%)\n"
    analysis_result += "• 时效性：优秀 (90%)\n\n"
    
    analysis_result += "🔍 深度分析：\n"
    analysis_result += "• 市场机会：存在显著的市场空白\n"
    analysis_result += "• 技术可行性：技术成熟度较高\n"
    analysis_result += "• 风险评估：中等风险，可控\n"
    analysis_result += "• 竞争优势：具有差异化优势\n\n"
    
    analysis_result += "💡 关键洞察：\n"
    analysis_result += "• 建议采用渐进式实施策略\n"
    analysis_result += "• 重点关注用户体验优化\n"
    analysis_result += "• 建立持续改进机制\n"
    analysis_result += "• 加强技术团队建设"
    
    collaboration_log.append("分析师完成数据分析")
    
    logger.info("分析师智能体工作完成")
    
    return {
        "analysis_result": analysis_result,
        "collaboration_log": collaboration_log,
        "agent_performance": {"analyst": "优秀"},
        "messages": [AIMessage(content="分析完成：已生成深度洞察和建议")]
    }

def planner_agent(state: CollaborationState) -> CollaborationState:
    """
    规划师智能体 - 负责制定实施计划
    学习要点：计划制定和策略规划
    """
    logger.info("📋 规划师智能体正在制定计划...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    research_result = state["research_result"]
    analysis_result = state["analysis_result"]
    collaboration_log = state["collaboration_log"]
    collaboration_log.append("规划师开始工作")
    
    # 制定实施计划
    planning_result = f"基于研究和分析的实施计划：\n\n"
    planning_result += "🎯 目标设定：\n"
    planning_result += "• 短期目标：建立基础框架和团队\n"
    planning_result += "• 中期目标：完成核心功能开发\n"
    planning_result += "• 长期目标：实现全面部署和优化\n\n"
    
    planning_result += "📅 时间规划：\n"
    planning_result += "• 第1阶段：需求分析和设计 (2周)\n"
    planning_result += "• 第2阶段：核心开发 (4周)\n"
    planning_result += "• 第3阶段：测试和优化 (2周)\n"
    planning_result += "• 第4阶段：部署和监控 (1周)\n\n"
    
    planning_result += "👥 资源配置：\n"
    planning_result += "• 技术团队：3-5人\n"
    planning_result += "• 项目管理：1人\n"
    planning_result += "• 质量保证：1人\n"
    planning_result += "• 运维支持：1人\n\n"
    
    planning_result += "⚠️ 风险控制：\n"
    planning_result += "• 技术风险：建立技术评审机制\n"
    planning_result += "• 进度风险：设置里程碑检查点\n"
    planning_result += "• 质量风险：实施持续集成和测试\n"
    planning_result += "• 人员风险：建立知识共享机制"
    
    collaboration_log.append("规划师完成计划制定")
    
    logger.info("规划师智能体工作完成")
    
    return {
        "planning_result": planning_result,
        "collaboration_log": collaboration_log,
        "agent_performance": {"planner": "优秀"},
        "messages": [AIMessage(content="规划完成：已制定详细的实施计划")]
    }

def executor_agent(state: CollaborationState) -> CollaborationState:
    """
    执行者智能体 - 负责实施和监控
    学习要点：执行监控和结果验证
    """
    logger.info("⚡ 执行者智能体正在实施计划...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    planning_result = state["planning_result"]
    collaboration_log = state["collaboration_log"]
    collaboration_log.append("执行者开始工作")
    
    # 模拟执行过程
    execution_result = f"计划执行状态和结果：\n\n"
    execution_result += "🚀 执行进度：\n"
    execution_result += "• 第1阶段：已完成 (100%)\n"
    execution_result += "• 第2阶段：进行中 (60%)\n"
    execution_result += "• 第3阶段：待开始 (0%)\n"
    execution_result += "• 第4阶段：待开始 (0%)\n\n"
    
    execution_result += "✅ 已完成工作：\n"
    execution_result += "• 需求分析文档已编写完成\n"
    execution_result += "• 系统架构设计已确定\n"
    execution_result += "• 核心模块开发进行中\n"
    execution_result += "• 测试用例设计完成\n\n"
    
    execution_result += "📊 关键指标：\n"
    execution_result += "• 代码质量：优秀 (95分)\n"
    execution_result += "• 测试覆盖率：良好 (85%)\n"
    execution_result += "• 进度符合率：优秀 (95%)\n"
    execution_result += "• 团队满意度：优秀 (90分)\n\n"
    
    execution_result += "🔧 下一步行动：\n"
    execution_result += "• 完成核心功能开发\n"
    execution_result += "• 开始系统集成测试\n"
    execution_result += "• 准备用户验收测试\n"
    execution_result += "• 部署环境准备"
    
    collaboration_log.append("执行者完成实施监控")
    
    logger.info("执行者智能体工作完成")
    
    return {
        "execution_result": execution_result,
        "collaboration_log": collaboration_log,
        "agent_performance": {"executor": "优秀"},
        "messages": [AIMessage(content="执行完成：计划实施进展顺利")]
    }

def coordinator_agent(state: CollaborationState) -> CollaborationState:
    """
    协调员智能体 - 整合所有结果生成最终报告
    学习要点：结果整合和报告生成
    """
    logger.info("🎯 协调员智能体正在整合结果...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    user_input = state["user_input"]
    research_result = state["research_result"]
    analysis_result = state["analysis_result"]
    planning_result = state["planning_result"]
    execution_result = state["execution_result"]
    collaboration_log = state["collaboration_log"]
    agent_performance = state["agent_performance"]
    
    collaboration_log.append("协调员开始整合")
    
    # 生成综合报告
    final_report = f"关于 '{user_input}' 的综合协作报告\n"
    final_report += "=" * 50 + "\n\n"
    
    final_report += "📋 项目概述：\n"
    final_report += f"• 项目主题：{user_input}\n"
    final_report += f"• 协作智能体：{len(agent_performance)} 个\n"
    final_report += f"• 协作步骤：{len(collaboration_log)} 步\n"
    final_report += f"• 完成时间：模拟完成\n\n"
    
    final_report += "🔬 研究阶段：\n"
    final_report += research_result + "\n\n"
    
    final_report += "📊 分析阶段：\n"
    final_report += analysis_result + "\n\n"
    
    final_report += "📋 规划阶段：\n"
    final_report += planning_result + "\n\n"
    
    final_report += "⚡ 执行阶段：\n"
    final_report += execution_result + "\n\n"
    
    final_report += "👥 团队表现：\n"
    for agent, performance in agent_performance.items():
        final_report += f"• {agent}: {performance}\n"
    
    final_report += "\n🎯 总结建议：\n"
    final_report += "• 项目具有很高的实施价值\n"
    final_report += "• 建议按照规划逐步推进\n"
    final_report += "• 重点关注质量控制和风险管理\n"
    final_report += "• 建立持续改进和反馈机制"
    
    collaboration_log.append("协调员完成整合")
    
    logger.info("协调员智能体工作完成")
    
    return {
        "final_report": final_report,
        "collaboration_log": collaboration_log,
        "agent_performance": agent_performance,
        "messages": [AIMessage(content="协作完成：已生成综合报告")]
    }

# ============================================================================
# 工作流构建
# ============================================================================

def create_collaboration_workflow():
    """
    创建多智能体协作工作流
    学习要点：复杂工作流的构建
    """
    logger.info("\n" + "="*60)
    logger.info("🤝 多智能体协作工作流")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(CollaborationState)
    
    # 2. 添加节点
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("executor", executor_agent)
    workflow.add_node("coordinator", coordinator_agent)
    
    # 3. 设置入口点
    workflow.set_entry_point("researcher")
    
    # 4. 添加边（顺序协作）
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "coordinator")
    workflow.add_edge("coordinator", END)
    
    # 5. 编译工作流
    graph = workflow.compile()
    
    return graph

# ============================================================================
# 测试函数
# ============================================================================

def test_multi_agent_collaboration():
    """测试多智能体协作"""
    logger.info("🤝 测试 LangGraph 多智能体协作")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 创建工作流
    graph = create_collaboration_workflow()
    
    # 测试输入
    test_inputs = [
        "开发一个智能客服系统",
        "设计一个电商推荐算法",
        "构建一个数据分析平台",
        "创建一个在线教育系统"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        logger.info(f"\n--- 测试 {i} ---")
        logger.info(f"项目主题: {test_input}")
        
        try:
            result = graph.invoke({"user_input": test_input})
            logger.info(f"协作步骤: {len(result['collaboration_log'])} 步")
            logger.info(f"智能体表现: {result['agent_performance']}")
            logger.info(f"最终报告长度: {len(result['final_report'])} 字符")
            logger.info("协作完成！")
        except Exception as e:
            logger.error(f"错误: {e}")

if __name__ == "__main__":
    test_multi_agent_collaboration() 