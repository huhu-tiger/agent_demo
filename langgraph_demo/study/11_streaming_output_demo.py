# -*- coding: utf-8 -*-
"""
LangGraph 流式输出示例
学习要点：流式输出、状态跟踪、节点执行监控
"""

import os
import sys
import time
import json
from typing import TypedDict, Annotated
from typing_extensions import Annotated
import operator

# 添加当前目录到路径
sys.path.append('.')

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.config import get_stream_writer
import config

# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 初始化语言模型
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,
    max_tokens=1000
)

# 定义状态结构
class StreamingState(TypedDict):
    """流式输出状态定义"""
    user_input: str                    # 用户输入
    processed_input: str               # 处理后的输入
    analysis_result: str               # 分析结果
    recommendation: str                # 推荐结果
    final_response: str                # 最终响应
    execution_log: Annotated[list, operator.add]  # 执行日志
    step_count: int                    # 步骤计数
    current_node: str                  # 当前节点名称
    node_display_name: str             # 节点显示名称

# 定义工具
@tool
def analyze_user_input(text: str) -> str:
    """分析用户输入的工具"""
    writer = get_stream_writer()
    writer({"type": "progress", "message": f"开始分析用户输入: {text[:20]}..."})
    
    # 模拟分析过程
    time.sleep(0.1)
    writer({"type": "progress", "message": "正在识别用户意图..."})
    
    time.sleep(0.1)
    writer({"type": "progress", "message": "分析完成"})
    
    return f"分析结果: 用户输入包含 {len(text)} 个字符，主要意图是获取信息"

@tool
def generate_recommendation(topic: str) -> str:
    """生成推荐的工具"""
    writer = get_stream_writer()
    writer({"type": "progress", "message": f"正在为 '{topic}' 生成推荐..."})
    
    # 模拟推荐生成过程
    time.sleep(0.1)
    writer({"type": "progress", "message": "收集相关数据..."})
    
    time.sleep(0.1)
    writer({"type": "progress", "message": "生成个性化推荐..."})
    
    time.sleep(0.1)
    writer({"type": "progress", "message": "推荐生成完成"})
    
    return f"基于 '{topic}' 的推荐: 建议您深入了解相关技术，并实践应用"

# 定义节点函数
def input_processor(state: StreamingState) -> StreamingState:
    """
    输入处理节点
    学习要点：状态更新、日志记录、节点名称跟踪
    """
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    # 节点信息
    node_name = "input_processor"
    display_name = "📝 输入处理节点"
    
    # 记录节点开始执行
    log_entry = {
        "step": step_count,
        "node": node_name,
        "display_name": display_name,
        "action": "开始处理用户输入",
        "timestamp": time.strftime("%H:%M:%S"),
        "input": user_input
    }
    
    # 处理输入
    processed_input = f"处理后的输入: {user_input.upper()}"
    
    return {
        "processed_input": processed_input,
        "step_count": step_count,
        "current_node": node_name,
        "node_display_name": display_name,
        "execution_log": [log_entry]
    }

def analysis_node(state: StreamingState) -> StreamingState:
    """
    分析节点
    学习要点：工具调用、流式输出、节点名称跟踪
    """
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    # 节点信息
    node_name = "analysis_node"
    display_name = "🔍 智能分析节点"
    
    # 记录节点开始执行
    log_entry = {
        "step": step_count,
        "node": node_name,
        "display_name": display_name,
        "action": "开始分析用户输入",
        "timestamp": time.strftime("%H:%M:%S"),
        "input": user_input
    }
    
    # 调用分析工具
    analysis_result = analyze_user_input(user_input)
    
    # 记录分析完成
    log_entry["result"] = analysis_result
    log_entry["status"] = "completed"
    
    return {
        "analysis_result": analysis_result,
        "step_count": step_count,
        "current_node": node_name,
        "node_display_name": display_name,
        "execution_log": [log_entry]
    }

def recommendation_node(state: StreamingState) -> StreamingState:
    """
    推荐生成节点
    学习要点：LLM调用、状态传递、节点名称跟踪
    """
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    # 节点信息
    node_name = "recommendation_node"
    display_name = "💡 AI推荐节点"
    
    # 记录节点开始执行
    log_entry = {
        "step": step_count,
        "node": node_name,
        "display_name": display_name,
        "action": "开始生成推荐",
        "timestamp": time.strftime("%H:%M:%S"),
        "input": user_input
    }
    
    # 使用LLM生成推荐
    prompt = f"""
基于用户输入: "{user_input}"
请生成一个有用的推荐或建议。
"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    recommendation = response.content
    
    # 记录推荐完成
    log_entry["result"] = recommendation
    log_entry["status"] = "completed"
    
    return {
        "recommendation": recommendation,
        "step_count": step_count,
        "current_node": node_name,
        "node_display_name": display_name,
        "execution_log": [log_entry]
    }

def response_synthesizer(state: StreamingState) -> StreamingState:
    """
    响应合成节点
    学习要点：状态整合、最终输出、节点名称跟踪
    """
    user_input = state["user_input"]
    analysis_result = state.get("analysis_result", "")
    recommendation = state.get("recommendation", "")
    step_count = state.get("step_count", 0) + 1
    
    # 节点信息
    node_name = "response_synthesizer"
    display_name = "🎯 响应合成节点"
    
    # 记录节点开始执行
    log_entry = {
        "step": step_count,
        "node": node_name,
        "display_name": display_name,
        "action": "开始合成最终响应",
        "timestamp": time.strftime("%H:%M:%S"),
        "input": user_input
    }
    
    # 合成最终响应
    final_response = f"""
基于您的输入: "{user_input}"

{analysis_result}

{recommendation}

感谢您的使用！
"""
    
    # 记录合成完成
    log_entry["result"] = final_response
    log_entry["status"] = "completed"
    
    return {
        "final_response": final_response,
        "step_count": step_count,
        "current_node": node_name,
        "node_display_name": display_name,
        "execution_log": [log_entry]
    }

def create_streaming_workflow():
    """
    创建流式输出工作流
    学习要点：图构建、节点连接
    """
    # 创建状态图
    workflow = StateGraph(StreamingState)
    
    # 添加节点
    workflow.add_node("input_processor", input_processor)
    workflow.add_node("analysis_node", analysis_node)
    workflow.add_node("recommendation_node", recommendation_node)
    workflow.add_node("response_synthesizer", response_synthesizer)
    
    # 设置入口点
    workflow.set_entry_point("input_processor")
    
    # 添加边
    workflow.add_edge("input_processor", "analysis_node")
    workflow.add_edge("analysis_node", "recommendation_node")
    workflow.add_edge("recommendation_node", "response_synthesizer")
    workflow.add_edge("response_synthesizer", END)
    
    # 编译工作流
    return workflow.compile()

def test_streaming_modes():
    """
    测试不同的流式输出模式
    学习要点：流式输出模式、状态监控
    """
    print("🚀 LangGraph 流式输出示例")
    print("=" * 60)
    
    # 创建工作流
    graph = create_streaming_workflow()
    
    # 测试输入
    test_inputs = [
        # "我想学习Python编程",
        # "如何提高代码质量",
        "推荐一些AI学习资源"
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
        
        # 测试不同的流式模式
        test_modes = [
            ("values", "完整状态值"),
            # ("updates", "状态更新"),
            # ("custom", "自定义数据"),
            # ("debug", "调试信息")
        ]
        
        for mode, description in test_modes:
            print(f"\n🔍 模式: {description} ({mode})")
            print("-" * 30)
            
            try:
                # 执行流式输出
                for chunk in graph.stream(inputs, stream_mode=mode):
                    if mode == "values":
                        # 完整状态值模式
                        print(f"完整状态: {json.dumps(chunk, ensure_ascii=False, indent=2)}")
                    elif mode == "updates":
                        # 状态更新模式
                        print(f"状态更新: {json.dumps(chunk, ensure_ascii=False, indent=2)}")
                    elif mode == "custom":
                        # 自定义数据模式
                        print(f"自定义数据: {json.dumps(chunk, ensure_ascii=False, indent=2)}")
                    elif mode == "debug":
                        # 调试模式
                        print(f"调试信息: {json.dumps(chunk, ensure_ascii=False, indent=2)}")
                    
                    print()  # 空行分隔
                    
            except Exception as e:
                print(f"❌ 错误: {e}")

def test_multi_mode_streaming():
    """
    测试多模式流式输出
    学习要点：同时监控多种输出类型
    """
    print("\n🎯 多模式流式输出测试")
    print("=" * 60)
    
    # 创建工作流
    graph = create_streaming_workflow()
    
    # 测试输入
    user_input = "请帮我分析一下机器学习的发展趋势"
    
    print(f"📝 输入: {user_input}")
    print("-" * 40)
    
    # 准备输入状态
    inputs = {
        "user_input": user_input,
        "execution_log": [],
        "step_count": 0
    }
    
    try:
        # 同时使用多种流式模式
        for mode, chunk in graph.stream(
            inputs, 
            stream_mode=["updates", "custom"]
        ):
            print(f"📊 模式: {mode}")
            print(f"📦 数据: {json.dumps(chunk, ensure_ascii=False, indent=2)}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ 错误: {e}")

def test_node_filtering():
    """
    测试节点过滤
    学习要点：特定节点的输出监控
    """
    print("\n🎯 节点过滤测试")
    print("=" * 60)
    
    # 创建工作流
    graph = create_streaming_workflow()
    
    # 测试输入
    user_input = "我想了解深度学习"
    
    print(f"📝 输入: {user_input}")
    print("-" * 40)
    
    # 准备输入状态
    inputs = {
        "user_input": user_input,
        "execution_log": [],
        "step_count": 0
    }
    
    try:
        # 只监控特定节点的输出
        target_nodes = ["analysis_node", "recommendation_node"]
        
        for chunk in graph.stream(inputs, stream_mode="updates"):
            # 检查是否是目标节点的输出
            for node_name in target_nodes:
                if node_name in chunk:
                    print(f"🎯 目标节点 {node_name} 输出:")
                    print(f"📦 数据: {json.dumps(chunk[node_name], ensure_ascii=False, indent=2)}")
                    print("-" * 30)
                    
    except Exception as e:
        print(f"❌ 错误: {e}")

def show_workflow_structure():
    """
    显示工作流结构
    学习要点：图结构可视化
    """
    print("\n🏗️ 工作流结构")
    print("=" * 60)
    
    # 创建工作流
    graph = create_streaming_workflow()
    
    print("节点列表:")
    print("- input_processor: 📝 输入处理节点")
    print("- analysis_node: 🔍 智能分析节点")
    print("- recommendation_node: 💡 AI推荐节点")
    print("- response_synthesizer: 🎯 响应合成节点")
    
    print("\n执行流程:")
    print("START → input_processor → analysis_node → recommendation_node → response_synthesizer → END")
    
    print("\n状态字段:")
    state_fields = [
        "user_input: 用户输入",
        "processed_input: 处理后的输入",
        "analysis_result: 分析结果",
        "recommendation: 推荐结果",
        "final_response: 最终响应",
        "execution_log: 执行日志",
        "step_count: 步骤计数",
        "current_node: 当前节点名称",
        "node_display_name: 节点显示名称"
    ]
    
    for field in state_fields:
        print(f"- {field}")

def test_node_name_tracking():
    """
    测试节点名称跟踪功能
    学习要点：节点名称监控、自定义显示名称
    """
    print("\n🎯 节点名称跟踪测试")
    print("=" * 60)
    
    # 创建工作流
    graph = create_streaming_workflow()
    
    # 测试输入
    user_input = "我想学习机器学习"
    
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
                    step_count = value.get("step_count", 0)
                    
                    print(f"📍 步骤 {step_count}: {display_name} ({node_name})")
                    
                    # 显示节点执行日志
                    if "execution_log" in value:
                        for log in value["execution_log"]:
                            if log.get("node") == node_name:
                                print(f"   ⏰ 时间: {log.get('timestamp', 'N/A')}")
                                print(f"   🎯 动作: {log.get('action', 'N/A')}")
                                if "result" in log:
                                    result = log["result"]
                                    if len(result) > 100:
                                        result = result[:100] + "..."
                                    print(f"   📊 结果: {result}")
                                print()
                    
    except Exception as e:
        print(f"❌ 错误: {e}")

def create_custom_node_names():
    """
    创建自定义节点名称的示例
    学习要点：节点名称自定义、显示名称配置
    """
    print("\n🎨 自定义节点名称示例")
    print("=" * 60)
    
    # 节点名称配置
    node_configs = {
        "input_processor": {
            "display_name": "🚀 数据预处理引擎",
            "description": "智能处理用户输入数据"
        },
        "analysis_node": {
            "display_name": "🧠 深度学习分析器",
            "description": "使用AI技术分析用户意图"
        },
        "recommendation_node": {
            "display_name": "🎯 智能推荐系统",
            "description": "基于AI生成个性化推荐"
        },
        "response_synthesizer": {
            "display_name": "✨ 响应生成器",
            "description": "整合所有结果生成最终响应"
        }
    }
    
    print("自定义节点配置:")
    for node_name, config in node_configs.items():
        print(f"- {node_name}: {config['display_name']}")
        print(f"  描述: {config['description']}")
    
    print("\n使用方法:")
    print("1. 在节点函数中设置 node_name 和 display_name")
    print("2. 在状态中跟踪 current_node 和 node_display_name")
    print("3. 在流式输出中监控节点执行过程")
    print("4. 可以根据需要动态修改显示名称")

if __name__ == "__main__":
    # 显示工作流结构
    show_workflow_structure()
    
    # 显示自定义节点名称示例
    # create_custom_node_names()
    
    # 测试节点名称跟踪功能
    # test_node_name_tracking()
    
    # 测试不同的流式输出模式
    # test_streaming_modes()
    
    # 测试多模式流式输出
    test_multi_mode_streaming()
    
    # 测试节点过滤
    # test_node_filtering()
    
    print("\n✅ 流式输出示例完成！")
    print("\n📚 学习要点总结:")
    print("1. 流式输出模式: values, updates, custom, debug")
    print("2. 状态跟踪: 监控节点执行和状态变化")
    print("3. 自定义输出: 使用 get_stream_writer() 发送自定义数据")
    print("4. 多模式监控: 同时使用多种流式模式")
    print("5. 节点过滤: 监控特定节点的输出")
    print("6. 节点名称跟踪: 返回当前节点名称和自定义显示名称")
    print("7. 自定义节点名称: 支持中文、emoji和描述性名称") 