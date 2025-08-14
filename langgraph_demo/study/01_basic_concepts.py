# -*- coding: utf-8 -*-
"""
LangGraph 基础概念示例
学习要点：状态管理、节点定义、边连接

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
from typing import TypedDict, List
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# LangChain 组件
from langchain_core.messages import HumanMessage, AIMessage

# 可视化组件
try:
    import matplotlib.pyplot as plt
    import networkx as nx
    from IPython.display import display, Image
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("警告: 可视化组件未安装，请运行: pip install matplotlib networkx ipython")

# 导入可视化工具
from visualization_utils import visualize_workflow, show_simple_graph


import config
# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url  # 自定义模型地址
os.environ["OPENAI_API_KEY"] = config.api_key  # 自定义模型密钥
MODEL_NAME = config.model  # 自定义模型名称

# 获取日志器
logger = config.logger

# ============================================================================
# 基础状态定义
# ============================================================================

class BasicState(TypedDict):
    """基础状态定义 - 包含消息历史和用户输入"""
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    response: str
    step_count: int

# ============================================================================
# 基础节点定义
# ============================================================================

def input_processor(state: BasicState) -> BasicState:
    """
    输入处理节点 - 处理用户输入
    学习要点：节点函数的基本结构
    """
    logger.info("🔄 输入处理节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info(f"state: {state}")
    user_input = state["user_input"]
    step_count = state.get("step_count", 0) + 1
    
    # 简单的输入处理逻辑
    processed_input = f"已处理: {user_input}"
    
    return {
        "user_input": processed_input,
        "step_count": step_count,
        "messages": [HumanMessage(content=processed_input)]
    }

def response_generator(state: BasicState) -> BasicState:
    """
    响应生成节点 - 生成智能体响应
    学习要点：状态更新和消息处理
    """
    logger.info("🤖 响应生成节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    processed_input = state["user_input"]
    step_count = state["step_count"]
    
    # 生成响应
    response = f"步骤 {step_count}: 我收到了您的消息 '{processed_input}'。这是一个基础响应示例。"
    
    return {
        "response": response,
        "messages": [AIMessage(content=response)]
    }

def message_logger(state: BasicState) -> BasicState:
    """
    消息记录节点 - 记录处理过程
    学习要点：状态读取和日志记录
    """
    logger.info("📝 消息记录节点正在工作...")
    logger.info(f"使用模型: {MODEL_NAME}")
    
    messages = state["messages"]
    response = state["response"]
    step_count = state["step_count"]
    
    # 记录处理信息
    log_message = f"处理完成 - 步骤: {step_count}, 消息数量: {len(messages)}"
    logger.info(log_message)
    
    return {
        "response": f"{response}\n\n{log_message}"
    }

# ============================================================================
# 工作流构建
# ============================================================================

def create_basic_workflow():
    """
    创建基础工作流
    学习要点：StateGraph 的创建和配置
    """
    logger.info("\n" + "="*60)
    logger.info("🚀 基础概念工作流")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info("="*60)
    
    # 1. 创建状态图
    workflow = StateGraph(BasicState)
    
    # 2. 添加节点
    workflow.add_node("input_processor", input_processor)
    workflow.add_node("response_generator", response_generator)
    workflow.add_node("message_logger", message_logger)
    
    # 3. 设置入口点
    workflow.set_entry_point("input_processor")
    
    # 4. 添加边（顺序执行）
    workflow.add_edge("input_processor", "response_generator")
    workflow.add_edge("response_generator", "message_logger")
    workflow.add_edge("message_logger", END)
    
    # 5. 编译工作流
    graph = workflow.compile()
    
    return graph, workflow

# ============================================================================
# 测试函数
# ============================================================================

def show_workflow_graph(workflow, title="工作流图"):
    """
    显示工作流图
    学习要点：工作流的可视化
    """
    logger.info(f"📊 显示{title}")
    
    try:
        # 方法1: 使用 LangGraph 内置的可视化
        logger.info("方法1: LangGraph 内置可视化")
        graph_drawable = workflow.get_graph()
        
        # 生成 Mermaid 图
        mermaid_code = graph_drawable.draw_mermaid()
        logger.info("Mermaid 代码:")
        logger.info(mermaid_code)
        
        # 保存为图片
        try:
            png_image = graph_drawable.draw_mermaid_png()
            with open("workflow_graph.png", "wb") as f:
                f.write(png_image)
            logger.info("✅ 工作流图已保存为 workflow_graph.png")
        except Exception as e:
            logger.warning(f"无法生成PNG图片: {e}")
        
        # 保存为SVG
        try:
            svg_image = graph_drawable.draw_mermaid_svg()
            with open("workflow_graph.svg", "w", encoding="utf-8") as f:
                f.write(svg_image)
            logger.info("✅ 工作流图已保存为 workflow_graph.svg")
        except Exception as e:
            logger.warning(f"无法生成SVG图片: {e}")
            
    except Exception as e:
        logger.error(f"LangGraph 可视化失败: {e}")
    
    # 方法2: 使用 NetworkX 自定义可视化
    try:
        logger.info("方法2: NetworkX 自定义可视化")
        create_custom_graph(workflow, title)
    except Exception as e:
        logger.error(f"NetworkX 可视化失败: {e}")

def create_custom_graph(workflow, title):
    """
    使用 NetworkX 创建自定义工作流图
    """
    # 创建有向图
    G = nx.DiGraph()
    
    # 获取工作流信息
    try:
        # 尝试获取节点信息
        nodes = workflow.nodes
        edges = workflow.edges
        
        # 添加节点
        for node_name in nodes:
            G.add_node(node_name, label=node_name)
        
        # 添加边
        for edge in edges:
            if hasattr(edge, 'from_node') and hasattr(edge, 'to_node'):
                G.add_edge(edge.from_node, edge.to_node)
            elif isinstance(edge, tuple) and len(edge) == 2:
                G.add_edge(edge[0], edge[1])
        
        # 添加开始和结束节点
        G.add_node("START", label="START")
        G.add_node("END", label="END")
        
        # 添加从开始到入口点的边
        entry_point = workflow.entry_point
        if entry_point:
            G.add_edge("START", entry_point)
        
        # 添加从结束节点到END的边（如果有的话）
        # 这里需要根据实际的工作流结构来添加
        
    except Exception as e:
        logger.warning(f"无法获取工作流结构: {e}")
        # 使用默认结构
        G.add_node("input_processor", label="输入处理")
        G.add_node("response_generator", label="响应生成")
        G.add_node("message_logger", label="消息记录")
        G.add_edge("START", "input_processor")
        G.add_edge("input_processor", "response_generator")
        G.add_edge("response_generator", "message_logger")
        G.add_edge("message_logger", "END")
    
    # 绘制图
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # 绘制节点
    nx.draw_networkx_nodes(G, pos, 
                          node_color='lightblue', 
                          node_size=3000,
                          alpha=0.8)
    
    # 绘制边
    nx.draw_networkx_edges(G, pos, 
                          edge_color='gray',
                          arrows=True,
                          arrowsize=20,
                          arrowstyle='->')
    
    # 绘制标签
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    # 添加边标签
    edge_labels = {}
    for edge in G.edges():
        edge_labels[edge] = f"{edge[0]} → {edge[1]}"
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8)
    
    plt.title(f"{title} - 节点和边的连接关系", fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(f"{title.replace(' ', '_')}_custom.png", dpi=300, bbox_inches='tight')
    logger.info(f"✅ 自定义工作流图已保存为 {title.replace(' ', '_')}_custom.png")
    
    # 显示图
    plt.show()

def test_basic_concepts():
    """测试基础概念"""
    logger.info("🎓 测试 LangGraph 基础概念")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 创建工作流
    graph, workflow = create_basic_workflow()
    
    # 显示工作流图
    if VISUALIZATION_AVAILABLE:
        logger.info("🎨 显示工作流图")
        visualize_workflow(workflow, "基础概念工作流")
    else:
        logger.warning("可视化组件未安装，跳过图形显示")
        show_simple_graph(workflow, "基础概念工作流")
    
    # 测试输入
    test_inputs = [
        "你好，我想学习 LangGraph",
        "请解释一下状态管理的概念",
        "节点和边有什么区别？"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        logger.info(f"\n--- 测试 {i} ---")
        logger.info(f"输入: {test_input}")
        
        try:
            result = graph.invoke({"user_input": test_input})
            logger.info(f"输出: {result['response']}")
            logger.info(f"步骤数: {result['step_count']}")
            logger.info(f"消息数: {len(result['messages'])}")
        except Exception as e:
            logger.error(f"错误: {e}")

if __name__ == "__main__":
    test_basic_concepts() 