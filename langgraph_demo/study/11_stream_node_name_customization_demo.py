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

# 添加当前目录到路径
sys.path.append('.')

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import config

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
    time.sleep(0.3)
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
    
    return workflow.compile()

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
    # 显示节点配置
    show_node_configurations()
    
    # 演示自定义节点名称
    # demonstrate_custom_node_names()
    
    # 测试节点名称跟踪
    test_node_name_tracking()
    
    print("\n✅ 节点名称自定义示例完成！")
    print("\n📚 学习要点总结:")
    print("1. 节点名称配置: 支持中文、emoji和描述")
    print("2. 状态跟踪: 实时监控当前执行的节点")
    print("3. 显示名称: 用户友好的节点展示")
    print("4. 配置管理: 统一的节点配置字典")
    print("5. 动态获取: 根据节点名获取配置信息")
    print("6. 执行日志: 详细的节点执行记录") 