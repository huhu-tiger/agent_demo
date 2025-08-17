# -*- coding: utf-8 -*-
"""
LangGraph Command 真实中断示例
学习要点：Command 对象的使用方式和应用场景

Command 是 LangGraph 中的一个核心概念，用于：
1. 状态更新和控制流：同时更新状态并决定下一个节点
2. 中断和恢复：暂停执行等待用户输入
3. 工具调用：返回工具执行结果并更新状态
4. 子图导航：在嵌套图中进行跳转

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import uuid
from typing import TypedDict, List, Literal
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END  # 状态图、开始/结束节点
from langgraph.types import Command, interrupt      # Command 对象和中断功能
from langgraph.checkpoint.memory import InMemorySaver  # 内存检查点保存器

import config  # 配置文件

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url  # 设置 API 基础地址
os.environ["OPENAI_API_KEY"] = config.api_key    # 设置 API 密钥
MODEL_NAME = config.model                         # 获取模型名称

# 获取日志器
logger = config.logger  # 用于记录执行过程和调试信息

# ============================================================================
# 完整中断恢复演示
# ============================================================================

class InterruptState(TypedDict):
    """
    中断状态定义
    
    用于演示完整的中断和恢复功能：
    - 暂停执行等待用户输入：使用 interrupt() 函数
    - 使用 Command 恢复执行：使用 Command(resume=...) 恢复
    - 使用 Command 动态路由：使用 Command(goto=...) 根据用户反馈决定流程
    """
    user_input: str      # 用户输入，在中断时收集，恢复时使用
    processed_result: str # 处理结果，最终输出的内容
    steps: List[str]     # 执行步骤，记录工作流的执行历史
    decision: str        # 决策结果，由 decision 节点设置

def get_user_input(prompt: str, options: List[str] = None) -> str:
    """
    获取用户输入
    
    Args:
        prompt: 提示信息
        options: 可选选项列表
    
    Returns:
        用户输入的字符串
    """
    print(f"\n{'='*50}")
    print(f"🤖 系统提示: {prompt}")
    
    if options:
        print("📋 可选选项:")
        for i, option in enumerate(options, 1):
            print(f"   {i}. {option}")
        print("💡 您也可以输入自定义内容")
    
    print(f"{'='*50}")
    
    while True:
        try:
            user_input = input("👤 请输入您的反馈: ").strip()
            if user_input:
                return user_input
            else:
                print("❌ 输入不能为空，请重新输入")
        except KeyboardInterrupt:
            print("\n⚠️ 检测到 Ctrl+C，程序退出")
            exit(0)
        except EOFError:
            print("\n⚠️ 检测到 EOF，程序退出")
            exit(0)

def demo_complete_interrupt_resume():
    """
    演示完整的中断和恢复功能
    
    展示如何使用 interrupt 暂停执行，
    然后使用 Command 恢复执行和动态路由
    """
    logger.info("\n" + "="*60)
    logger.info("🔄 完整中断恢复演示")
    logger.info("interrupt + Command(resume) + Command(goto)")
    logger.info("特点：人工干预、暂停恢复、动态路由")
    logger.info("="*60)
    
    def process_input_node(state: InterruptState) -> InterruptState:
        """处理输入节点"""
        logger.info("🔧 处理输入节点: 处理用户输入")
        user_input = state.get("user_input", "")
        logger.info(f"   📥 用户输入: {user_input}")
        
        return {
            "user_input": user_input,
            "steps": ["process_input"]
        }
    
    def human_interaction_node(state: InterruptState) -> InterruptState:
        """
        人工交互节点
        
        使用 interrupt 暂停执行，等待用户输入
        """
        logger.info("🔧 人工交互节点: 等待用户输入")
        
        # 使用 interrupt 暂停执行
        interrupt_data = {
            "message": "请提供反馈信息",
            "current_input": state.get("user_input", ""),
            "options": ["通过", "拒绝", "需要更多信息"]
        }
        
        logger.info(f"   ⏸️ 中断执行，等待用户输入: {interrupt_data}")
        
        # 调用 interrupt 函数 - 这里会真正暂停执行
        user_feedback = interrupt(interrupt_data)
        
        logger.info(f"   📥 收到用户反馈: {user_feedback}")
        
        return {
            "user_input": user_feedback,
            "steps": ["human_interaction"]
        }
    
    def decision_node(state: InterruptState) -> Command[Literal["approve", "reject", "finalize"]]:
        """
        决策节点：使用 Command 进行动态路由
        
        根据用户反馈内容决定下一步流程
        """
        logger.info("🔧 决策节点: 基于用户反馈进行路由")
        user_input = state.get("user_input", "").lower()
        
        # 根据用户反馈内容决定路由
        if any(keyword in user_input for keyword in ["通过", "同意", "approve", "yes", "1"]):
            goto = "approve"
            decision = "approved"
        elif any(keyword in user_input for keyword in ["拒绝", "不同意", "reject", "no", "2"]):
            goto = "reject"
            decision = "rejected"
        else:
            goto = "finalize"
            decision = "pending"
        
        logger.info(f"   🎯 决策结果: {decision} -> 跳转到: {goto}")
        
        # 使用 Command 进行动态路由和状态更新
        return Command(
            update={
                "user_input": user_input,
                "steps": ["decision"],
                "decision": decision
            },
            goto=goto
        )
    
    def approve_node(state: InterruptState) -> InterruptState:
        """批准节点"""
        logger.info("🔧 批准节点: 处理批准流程")
        user_input = state.get("user_input", "")
        
        return {
            "processed_result": f"✅ 已批准: {user_input}",
            "steps": ["approve"]
        }
    
    def reject_node(state: InterruptState) -> InterruptState:
        """拒绝节点"""
        logger.info("🔧 拒绝节点: 处理拒绝流程")
        user_input = state.get("user_input", "")
        
        return {
            "processed_result": f"❌ 已拒绝: {user_input}",
            "steps": ["reject"]
        }
    
    def finalize_node(state: InterruptState) -> InterruptState:
        """完成节点"""
        logger.info("🔧 完成节点: 处理最终结果")
        user_input = state.get("user_input", "")
        processed_result = f"⏳ 待处理: {user_input}"
        
        logger.info(f"   📤 处理结果: {processed_result}")
        
        return {
            "processed_result": processed_result,
            "steps": ["finalize"]
        }
    
    # 构建工作流
    logger.info("📋 构建完整中断恢复工作流...")
    logger.info("   - 工作流结构: START -> process_input -> human_interaction -> decision -> [approve/reject/finalize] -> END")
    
    builder = StateGraph(InterruptState)
    
    # 添加节点
    builder.add_node("process_input", process_input_node)
    builder.add_node("human_interaction", human_interaction_node)
    builder.add_node("decision", decision_node)
    builder.add_node("approve", approve_node)
    builder.add_node("reject", reject_node)
    builder.add_node("finalize", finalize_node)
    
    # 设置边
    builder.add_edge(START, "process_input")
    builder.add_edge("process_input", "human_interaction")
    builder.add_edge("human_interaction", "decision")
    builder.add_edge("approve", END)
    builder.add_edge("reject", END)
    builder.add_edge("finalize", END)
    
    # 编译图（添加 checkpointer）
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    logger.info("✅ 完整中断恢复工作流编译完成")
    
    # 执行工作流
    logger.info("\n🚀 执行完整中断恢复工作流...")
    
    try:
        # 创建唯一的线程 ID
        thread_id = str(uuid.uuid4())
        logger.info(f"📋 线程 ID: {thread_id}")
        
        # 初始状态
        initial_state = {
            "user_input": "测试申请内容",
            "processed_result": "",
            "steps": [],
            "decision": ""
        }
        
        logger.info(f"📋 初始状态: {initial_state}")
        
        # 第一次执行 - 会在这里中断
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            result = graph.invoke(initial_state, config=config)
            logger.info("✅ 工作流执行完成（无中断）")
            logger.info(f"📊 最终结果: {result}")
            
        except Exception as e:
            logger.info(f"🔍 捕获异常: {type(e).__name__}: {str(e)}")
            
            # 检查是否包含中断信息
            if hasattr(e, '__interrupt__') or '__interrupt__' in str(e):
                logger.info("⏸️ 检测到中断")
                logger.info("💡 现在可以恢复执行")
                
                # 获取用户真实输入
                user_feedback = get_user_input(
                    "请对申请内容提供反馈",
                    ["通过", "拒绝", "需要更多信息"]
                )
                
                logger.info(f"🔄 用户输入: {user_feedback}")
                
                try:
                    # 使用 Command(resume=...) 恢复执行
                    resume_command = Command(resume=user_feedback)
                    logger.info(f"📝 恢复命令: {resume_command}")
                    
                    # 恢复执行
                    result = graph.invoke(resume_command, config=config)
                    
                    logger.info(f"✅ 恢复执行完成")
                    logger.info(f"📊 最终结果: {result}")
                    logger.info(f"🎯 执行路径: {' -> '.join(result['steps'])}")
                    logger.info(f"📤 处理结果: {result['processed_result']}")
                    
                except Exception as resume_error:
                    logger.error(f"恢复执行时出错: {resume_error}")
            else:
                logger.error(f"执行工作流时出错: {e}")
                
    except Exception as e:
        logger.error(f"执行工作流时出错: {e}")

# ============================================================================
# 主测试函数
# ============================================================================

def test_commands():
    """
    测试 Command 功能的主函数
    
    演示真实的中断和恢复场景中的 Command 使用：
    - 使用 interrupt() 暂停执行
    - 使用 Command(resume) 恢复执行
    - 使用 Command(goto) 进行动态路由
    - 支持人工干预和外部输入
    
    学习要点：
    - Command 是 LangGraph 中控制流和状态管理的核心
    - 支持动态路由、人工干预、外部输入
    - 适用于构建需要人工干预的 AI 工作流和代理系统
    """
    logger.info("🎯 测试 LangGraph Command 真实中断功能")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    logger.info("📚 学习目标：掌握 Command 在真实中断恢复场景中的使用")
    
    # 演示完整中断恢复
    logger.info("\n" + "="*60)
    logger.info("📖 完整中断恢复演示")
    logger.info("学习要点：完整中断 + 恢复执行 + 动态路由")
    demo_complete_interrupt_resume()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 Command 真实中断演示完成！")
    logger.info("📋 总结：Command 是 LangGraph 中实现复杂控制流的关键")
    logger.info("🔗 相关概念：状态管理、动态路由、人工干预、中断恢复、checkpointer")
    logger.info("="*60)

if __name__ == "__main__":
    test_commands() 