# -*- coding: utf-8 -*-
"""
LangGraph MapReduce 示例
学习要点：MapReduce 模式的创建和使用

MapReduce 是一种编程模型，用于大规模数据集的并行处理：
- Map 阶段：将输入数据分解为多个独立的子任务，并行处理
- Reduce 阶段：将 Map 阶段的结果合并，产生最终输出

本示例演示了：
1. 基础 MapReduce 模式：笑话生成和选择
2. 高级 MapReduce 模式：文档处理流水线
3. 可视化工作流程图

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import operator
from typing import TypedDict, List
from typing_extensions import Annotated

# LangGraph 核心组件
from langgraph.graph import StateGraph, START, END  # 状态图、开始/结束节点
from langgraph.graph.message import add_messages    # 消息合并器
from langgraph.types import Send                    # 发送类型，用于条件边

# LangChain 组件
from langchain_core.messages import HumanMessage, AIMessage  # 消息类型
from langchain_core.runnables import RunnablePassthrough, RunnableLambda  # 可运行组件

import config  # 配置文件

# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url  # 设置 API 基础地址
os.environ["OPENAI_API_KEY"] = config.api_key    # 设置 API 密钥
MODEL_NAME = config.model                         # 获取模型名称

# 获取日志器
logger = config.logger  # 用于记录执行过程和调试信息

# ============================================================================
# 状态定义
# ============================================================================

class MapReduceState(TypedDict):
    """
    MapReduce 状态定义
    
    使用 TypedDict 定义工作流的状态结构，确保类型安全
    """
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]  # 消息列表，使用 add_messages 合并器
    topic: str                                                          # 用户输入的主题
    subjects: List[str]                                                 # 生成的主题列表（Map 阶段输入）
    jokes: Annotated[List[str], operator.add]                          # 笑话列表，使用 operator.add 合并器（并行结果）
    best_selected_joke: str                                             # 选择的最佳笑话（Reduce 阶段输出）
    execution_history: Annotated[List[str], operator.add]              # 执行历史，记录每个节点的执行情况

# ============================================================================
# Map 阶段节点
# ============================================================================

def generate_topics(state: MapReduceState) -> MapReduceState:
    """
    生成主题列表 - Map 阶段的输入节点
    
    根据用户输入的主题，生成多个子主题，为后续的并行处理做准备
    这是 MapReduce 模式中的"数据准备"阶段
    
    Args:
        state: 当前工作流状态
        
    Returns:
        更新后的状态，包含生成的主题列表
    """
    logger.info("🎯 生成主题列表...")
    
    # 从状态中获取用户输入的主题，默认为"动物"
    user_input = state.get("topic", "动物")
    # 为每个主题生成3个子主题，用于并行处理
    subjects = [f"{user_input}_主题1", f"{user_input}_主题2", f"{user_input}_主题3"]
    
    logger.info(f"生成的主题: {subjects}")
    
    # 返回更新后的状态
    return {
        "subjects": subjects,                    # 生成的主题列表
        "execution_history": ["generate_topics"] # 记录执行历史
    }

def generate_joke(state: MapReduceState) -> MapReduceState:
    """
    为单个主题生成笑话 - Map 阶段节点
    
    这是 MapReduce 模式中的 Map 阶段，每个主题会并行执行此函数
    在实际应用中，这里通常会调用 LLM 来生成内容
    
    Args:
        state: 当前工作流状态，包含要处理的主题
        
    Returns:
        更新后的状态，包含生成的笑话
    """
    logger.info("😄 为单个主题生成笑话...")
    
    # 从状态中获取要处理的主题
    subject = state.get("subject", "未知主题")
    
    # 预定义的笑话映射表（模拟 LLM 生成的结果）
    # 在实际应用中，这里会调用 LLM API
    joke_map = {
        "动物_主题1": "为什么动物不喜欢数学？因为它们不会数数！",
        "动物_主题2": "什么动物最喜欢音乐？海豚，因为它们总是唱高音！",
        "动物_主题3": "为什么熊猫总是黑眼圈？因为它们熬夜看竹子！",
        "科技_主题1": "为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 == Dec 25！",
        "科技_主题2": "什么是最快的编程语言？闪电，因为它有 C++！",
        "科技_主题3": "为什么程序员不喜欢户外活动？因为他们害怕遇到 bug！",
        "食物_主题1": "什么食物最聪明？面包，因为它有面包屑！",
        "食物_主题2": "为什么披萨总是迟到？因为它被切成了片！",
        "食物_主题3": "什么水果最害羞？草莓，因为它总是脸红！"
    }
    
    # 根据主题获取对应的笑话，如果没有则使用默认笑话
    joke = joke_map.get(subject, f"关于{subject}的笑话：这是一个默认笑话！")
    
    logger.info(f"为 {subject} 生成笑话: {joke}")
    
    # 返回更新后的状态
    return {
        "jokes": [joke],                           # 生成的笑话（列表形式，会被 reducer 合并）
        "execution_history": [f"generate_joke_{subject}"]  # 记录执行历史
    }

# ============================================================================
# Reduce 阶段节点
# ============================================================================

def select_best_joke(state: MapReduceState) -> MapReduceState:
    """
    选择最佳笑话 - Reduce 阶段节点
    
    这是 MapReduce 模式中的 Reduce 阶段，将所有并行生成的笑话合并并选择最佳结果
    在实际应用中，这里可能会使用更复杂的评分算法或 LLM 来评估质量
    
    Args:
        state: 当前工作流状态，包含所有生成的笑话
        
    Returns:
        更新后的状态，包含选择的最佳笑话
    """
    logger.info("🏆 选择最佳笑话...")
    
    # 从状态中获取所有生成的笑话（已经通过 reducer 合并）
    jokes = state.get("jokes", [])
    
    if not jokes:
        # 如果没有笑话，返回默认消息
        best_joke = "没有找到任何笑话"
    else:
        # 简单的选择逻辑：选择最长的笑话作为最佳笑话
        # 在实际应用中，这里可能会使用 LLM 来评估笑话质量
        best_joke = max(jokes, key=len)
    
    logger.info(f"选择的最佳笑话: {best_joke}")
    
    # 返回更新后的状态
    return {
        "best_selected_joke": best_joke,        # 选择的最佳笑话
        "execution_history": ["select_best_joke"]  # 记录执行历史
    }

# ============================================================================
# 条件路由函数
# ============================================================================

def continue_to_jokes(state: MapReduceState) -> List[Send]:
    """
    条件路由函数：为每个主题创建笑话生成任务
    
    这是 MapReduce 模式中的关键函数，它实现了"扇出"（fan-out）功能
    将单个输入分解为多个并行任务，每个任务处理一个主题
    
    Args:
        state: 当前工作流状态，包含要处理的主题列表
        
    Returns:
        Send 对象列表，每个对象代表一个并行任务
    """
    # 从状态中获取主题列表
    subjects = state.get("subjects", [])
    logger.info(f"🎭 为 {len(subjects)} 个主题创建笑话生成任务")
    
    # 为每个主题创建一个 Send 任务，实现并行处理
    # Send("generate_joke", {"subject": subject}) 表示：
    # - 发送到 "generate_joke" 节点
    # - 传递参数 {"subject": subject}
    return [Send("generate_joke", {"subject": subject}) for subject in subjects]

# ============================================================================
# MapReduce 演示
# ============================================================================

def demo_mapreduce():
    """
    演示基础 MapReduce 模式
    
    工作流程：
    1. 数据准备：根据用户输入生成多个主题
    2. Map 阶段：为每个主题并行生成笑话
    3. Reduce 阶段：选择最佳笑话作为最终结果
    
    这是 MapReduce 模式的经典实现，展示了如何将复杂任务分解为并行子任务
    """
    logger.info("\n" + "="*60)
    logger.info("🔄 MapReduce 模式演示")
    logger.info("Map 阶段：为每个主题生成笑话")
    logger.info("Reduce 阶段：选择最佳笑话")
    logger.info("="*60)
    
    # 创建状态图，定义工作流的状态结构
    workflow = StateGraph(MapReduceState)
    
    # 添加工作流节点
    workflow.add_node("generate_topics", generate_topics)      # 数据准备节点
    workflow.add_node("generate_joke", generate_joke)          # Map 阶段节点（并行执行）
    workflow.add_node("select_best_joke", select_best_joke)    # Reduce 阶段节点
    
    # 设置工作流的入口点
    workflow.set_entry_point("generate_topics")
    
    # 添加条件边：实现 Map 阶段的并行处理
    # 从 generate_topics 节点开始，根据 continue_to_jokes 函数的返回值
    # 为每个主题创建一个并行的 generate_joke 任务
    workflow.add_conditional_edges(
        "generate_topics",      # 源节点
        continue_to_jokes,      # 条件路由函数，使用send 创建并行任务
        ["generate_joke"]       # 目标节点列表
    )
    
    # 添加边：实现 Reduce 阶段的聚合
    # 所有并行的 generate_joke 任务完成后，都会流向 select_best_joke
    workflow.add_edge("generate_joke", "select_best_joke")
    # 最终结果输出
    workflow.add_edge("select_best_joke", END)
    
    # 编译工作流图，生成可执行的工作流
    graph = workflow.compile()
    
    # 可视化工作流程图
    from show_graph import show_workflow_graph
    
    # 生成工作流图的 PNG 格式，用于文档和演示
    # 可以根据需要选择不同的格式：
    # - formats=['md']: 只生成 Markdown 文件
    # - formats=['mmd']: 只生成 Mermaid 代码文件  
    # - formats=['png']: 只生成 PNG 图片
    # - formats=['png', 'md', 'mmd']: 生成多种格式
    show_workflow_graph(graph, "MapReduce工作流", logger, "MapReduce 模式演示", formats=['png'])
    # 测试工作流：使用不同的主题进行演示
    test_topics = ["动物", "科技", "食物"]
    
    for topic in test_topics:
        logger.info(f"\n🧪 测试主题: {topic}")
        
        try:
            # 调用工作流，传入主题参数
            # config 参数用于区分不同的执行线程，便于调试和日志追踪
            result = graph.invoke(
                {"topic": topic},  # 输入参数：用户选择的主题
                config={"configurable": {"thread_id": f"mapreduce_{topic}"}}  # 线程配置
            )
            
            # 输出执行结果
            logger.info(f"执行历史: {' → '.join(result['execution_history'])}")  # 显示执行路径
            logger.info(f"生成的笑话数量: {len(result['jokes'])}")              # 显示生成的笑话数量
            logger.info(f"最佳笑话: {result['best_selected_joke']}")           # 显示最终结果
            
        except Exception as e:
            logger.error(f"执行工作流时出错: {e}")

# ============================================================================
# 高级 MapReduce 演示（使用 Runnable）
# ============================================================================

def demo_advanced_mapreduce():
    """
    演示高级 MapReduce 模式（使用 LangChain Runnable）
    
    这个示例展示了如何使用 LangChain 的 Runnable 组件构建更复杂的 MapReduce 流水线
    相比基础版本，这里使用了：
    - RunnablePassthrough: 用于数据传递和转换
    - RunnableLambda: 用于自定义处理逻辑
    - 链式调用: 将多个处理步骤组合成流水线
    
    这种模式更适合处理复杂的文档处理、数据分析等任务
    """
    logger.info("\n" + "="*60)
    logger.info("🚀 高级 MapReduce 模式演示")
    logger.info("使用 RunnablePassthrough 和 RunnableLambda")
    
    # 模拟文档数据 - 在实际应用中，这些可能是从数据库或文件系统读取的文档
    documents = [
        {"id": 1, "content": "人工智能正在改变世界"},
        {"id": 2, "content": "机器学习是AI的核心技术"},
        {"id": 3, "content": "深度学习在图像识别方面表现出色"}
    ]
    
    def get_content(state):
        """
        提取文档内容 - Map 阶段的数据准备
        
        从输入状态中提取文档内容，为后续处理做准备
        这相当于 MapReduce 中的"数据提取"步骤
        
        Args:
            state: 包含文档列表的状态
            
        Returns:
            文档内容列表，每个元素包含 content 字段
        """
        docs = state.get("documents", [])
        return [{"content": doc["content"]} for doc in docs]
    
    def process_content(content_list):
        """
        处理内容 - Map 阶段的核心处理逻辑
        
        模拟 LLM 调用，对每个文档内容进行处理
        在实际应用中，这里会调用真实的 LLM API 进行文本分析、摘要生成等
        
        Args:
            content_list: 文档内容列表
            
        Returns:
            处理后的结果列表，包含原始内容、处理结果和摘要
        """
        processed = []
        for content_item in content_list:
            content = content_item["content"]
            # 模拟 LLM 处理：添加处理标记和生成摘要
            processed.append({
                "original": content,                    # 原始内容
                "processed": f"已处理: {content}",      # 处理后的内容
                "summary": f"摘要: {content[:10]}..."   # 生成的摘要
            })
        return processed
    
    def reduce_results(combined):
        """
        合并处理结果 - Reduce 阶段
        
        将 Map 阶段的处理结果与原始文档信息合并，生成最终输出
        这相当于 MapReduce 中的"结果聚合"步骤
        
        Args:
            combined: 包含处理结果和原始文档的合并状态
            
        Returns:
            最终结果列表，包含完整的文档处理信息
        """
        processed_results = combined.get("processed_results", [])
        documents = combined.get("documents", [])
        
        # 将处理结果与原始文档信息合并
        return {
            "final_results": [
                {
                    "id": doc["id"],                    # 文档ID
                    "original": doc["content"],          # 原始内容
                    "processed": result["processed"],    # 处理后的内容
                    "summary": result["summary"]         # 生成的摘要
                }
                for doc, result in zip(documents, processed_results)
            ]
        }
    
    # 创建 MapReduce 处理链
    # RunnablePassthrough.assign() 用于在传递数据的同时添加新的字段
    map_step = RunnablePassthrough.assign(
        processed_results=get_content | RunnableLambda(process_content)  # Map 阶段：提取内容并处理
    )
    
    # 将 Map 阶段和 Reduce 阶段组合成完整的处理链
    map_reduce_chain = map_step | reduce_results
    
    # 执行 MapReduce 处理链
    try:
        # 调用处理链，传入文档数据
        result = map_reduce_chain.invoke({"documents": documents})
        
        # 输出处理结果
        logger.info("📄 文档处理结果:")
        for item in result["final_results"]:
            logger.info(f"ID: {item['id']}")                    # 文档ID
            logger.info(f"原文: {item['original']}")            # 原始内容
            logger.info(f"处理: {item['processed']}")           # 处理后的内容
            logger.info(f"摘要: {item['summary']}")             # 生成的摘要
            logger.info("---")                                  # 分隔线
            
    except Exception as e:
        logger.error(f"执行高级 MapReduce 时出错: {e}")

# ============================================================================
# 主测试函数
# ============================================================================

def test_mapreduce():
    """
    测试 MapReduce 模式的主函数
    
    这个函数演示了两种不同的 MapReduce 实现方式：
    1. 基础 MapReduce：使用 LangGraph 的状态图和条件边
    2. 高级 MapReduce：使用 LangChain 的 Runnable 组件
    
    两种方式各有优势：
    - 基础版本：更适合复杂的工作流控制和状态管理
    - 高级版本：更适合简单的数据处理流水线
    """
    logger.info("🎯 测试 LangGraph MapReduce 模式")
    logger.info(f"模型配置: {MODEL_NAME}")
    logger.info(f"API 地址: {os.environ.get('OPENAI_API_BASE', '默认地址')}")
    
    # 演示基础 MapReduce 模式（笑话生成和选择）
    demo_mapreduce()
    
    # 演示高级 MapReduce 模式（文档处理流水线）
    print("="*60 + "LangChain MapReduce" + "="*60)
    # demo_advanced_mapreduce()
    
    logger.info("\n" + "="*60)
    logger.info("🎉 MapReduce 演示完成！")
    logger.info("="*60)

if __name__ == "__main__":
    test_mapreduce() 