"""
LangGraph Swarm 简化示例

本示例演示了 LangGraph Swarm 的核心概念，展示如何构建多智能体协作系统。

核心概念演示：
1. 多个智能体的定义 - 如何创建不同职责的智能体
2. 智能体之间的切换 - 如何使用 handoff 工具实现智能体切换
3. 状态管理 - 如何使用检查点保存器管理会话状态
4. 流式输出 - 如何实时观察智能体的执行过程

架构特点：
- 模块化设计：每个智能体专注于特定任务
- 灵活切换：智能体之间可以无缝切换
- 状态保持：会话状态在切换过程中得到保持
- 可扩展性：易于添加新的智能体和功能
"""

# 系统相关导入
import os
import uuid
import sys

# LangChain 相关导入
from langchain_openai import ChatOpenAI  # OpenAI 语言模型

# LangGraph 相关导入
from langgraph.checkpoint.memory import InMemorySaver  # 内存检查点保存器
from langgraph.prebuilt import create_react_agent      # 预构建的 ReAct 智能体

# LangGraph Swarm 相关导入
from langgraph_swarm import create_handoff_tool, create_swarm  # Swarm 核心功能

# 配置相关导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 设置 OpenAI API 环境变量
os.environ["OPENAI_API_BASE"] = config.base_url  # API 基础URL
os.environ["OPENAI_API_KEY"] = config.api_key    # API 密钥
MODEL_NAME = config.model                        # 模型名称

# 初始化语言模型
# 使用 ChatOpenAI 作为所有智能体的基础模型
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,  # 较低的温度确保输出的一致性和可预测性
    max_tokens=1000   # 限制输出长度，避免过长响应
)

# ==================== 工具函数定义 ====================
# 这些工具函数将被智能体调用来执行具体的任务

def add_numbers(a: int, b: int) -> int:
    """
    加法运算工具
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        两个数字的和
    """
    return a + b

def multiply_numbers(a: int, b: int) -> int:
    """
    乘法运算工具
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        两个数字的积
    """
    return a * b

def get_weather(location: str) -> str:
    """
    获取天气信息工具
    
    Args:
        location: 城市名称
        
    Returns:
        该城市的天气信息
    """
    if location == "北京":
        return "北京今天天气晴朗，温度 25°C"
    elif location == "上海":
        return "上海今天多云，温度 28°C"
    else:
        return f"{location}的天气信息暂时不可用"

# ==================== 智能体切换工具定义 ====================
# Handoff 工具允许智能体之间进行切换，实现协作

# 创建智能体切换工具
# 这些工具允许智能体将控制权转移给其他智能体
transfer_to_math_agent = create_handoff_tool(
    agent_name="math_agent",  # 目标智能体名称
    description="切换到数学智能体，可以进行数学计算。"  # 工具描述，用于模型理解何时使用
)

transfer_to_weather_agent = create_handoff_tool(
    agent_name="weather_agent",  # 目标智能体名称
    description="切换到天气智能体，可以查询天气信息。"  # 工具描述
)

transfer_to_assistant_agent = create_handoff_tool(
    agent_name="assistant_agent",  # 目标智能体名称
    description="切换到主助手智能体，可以处理一般查询。"  # 工具描述
)

# ==================== 智能体定义 ====================
# 定义不同的智能体，每个智能体都有特定的职责和工具

# 主助手智能体 - 作为系统的入口点和协调者
assistant_agent = create_react_agent(
    llm,  # 使用统一的语言模型
    tools=[
        transfer_to_math_agent,    # 可以切换到数学智能体
        transfer_to_weather_agent  # 可以切换到天气智能体
    ],
    prompt="""你是一个智能助手，专门帮助用户解决问题。
    
    你的职责包括：
    1. 理解用户的需求
    2. 根据需求切换到相应的专业智能体
    3. 提供一般性的帮助和建议
    
    当用户需要数学计算时，请切换到 math_agent
    当用户需要查询天气时，请切换到 weather_agent
    
    请始终保持友好和专业的服务态度。""",
    name="assistant_agent"  # 智能体名称，用于识别和切换
)

# 数学智能体 - 专门处理数学计算任务
math_agent = create_react_agent(
    llm,  # 使用统一的语言模型
    tools=[
        add_numbers,                # 加法运算工具
        multiply_numbers,           # 乘法运算工具
        transfer_to_weather_agent,  # 可以切换到天气智能体
        transfer_to_assistant_agent # 可以切换回主助手
    ],
    prompt="""你是一个专业的数学智能体。
    
    你的职责包括：
    1. 进行数学计算
    2. 提供数学相关建议
    3. 解释计算过程
    
    当用户完成数学计算后，可以建议他们查询天气。
    如果需要切换到其他智能体，请使用相应的切换工具。
    
    请提供准确和详细的数学计算。""",
    name="math_agent"  # 智能体名称
)

# 天气智能体 - 专门处理天气查询任务
weather_agent = create_react_agent(
    llm,  # 使用统一的语言模型
    tools=[
        get_weather,                # 天气查询工具
        transfer_to_math_agent,     # 可以切换到数学智能体
        transfer_to_assistant_agent # 可以切换回主助手
    ],
    prompt="""你是一个专业的天气智能体。
    
    你的职责包括：
    1. 查询天气信息
    2. 提供天气相关建议
    3. 解释天气数据
    
    当用户完成天气查询后，可以建议他们进行数学计算。
    如果需要切换到其他智能体，请使用相应的切换工具。
    
    请提供准确和有用的天气信息。""",
    name="weather_agent"  # 智能体名称
)

# ==================== Swarm 构建 ====================
# 将多个智能体组合成一个协作系统

def create_simple_swarm():
    """
    创建简单的 Swarm 系统
    
    这个函数将多个智能体组合成一个协作系统，实现智能体之间的切换和状态管理。
    
    Returns:
        编译后的 Swarm 应用程序
    """
    print("正在创建简单 Swarm 系统...")
    
    # 创建 Swarm - 将多个智能体组合在一起
    swarm = create_swarm(
        agents=[
            assistant_agent,  # 主助手智能体
            math_agent,       # 数学智能体
            weather_agent     # 天气智能体
        ],
        default_active_agent="assistant_agent"  # 默认从主助手开始，作为系统入口点
    )
    
    # 设置检查点保存器 - 用于管理会话状态
    # InMemorySaver 将状态保存在内存中，支持会话的持久化
    checkpointer = InMemorySaver()
    
    # 编译 Swarm - 生成可执行的应用程序
    # 编译过程会建立智能体之间的连接和切换机制
    app = swarm.compile(checkpointer=checkpointer)
    
    print("Swarm 系统创建完成！")
    return app

# ==================== 流式输出工具 ====================
# 用于实时观察智能体的执行过程和状态变化

def print_stream(stream):
    """
    打印流式输出
    
    这个函数用于实时观察智能体的执行过程，包括：
    - 智能体的切换过程
    - 工具调用的结果
    - 状态更新信息
    
    Args:
        stream: 流式输出对象，包含智能体执行的实时信息
    """
    for ns, update in stream:
        # 打印命名空间信息，表示当前执行的智能体
        print(f"\n=== 命名空间: {ns} ===")
        
        # 遍历所有节点的更新信息
        for node, node_updates in update.items():
            if node_updates is None:
                continue

            # 处理不同类型的更新格式
            if isinstance(node_updates, (dict, tuple)):
                node_updates_list = [node_updates]
            elif isinstance(node_updates, list):
                node_updates_list = node_updates
            else:
                continue

            # 处理每个节点的更新
            for node_updates in node_updates_list:
                print(f"\n--- 节点: {node} ---")
                
                # 如果是元组类型，直接打印
                if isinstance(node_updates, tuple):
                    print(node_updates)
                    continue
                    
                # 查找消息键，用于提取智能体的响应消息
                messages_key = next(
                    (k for k in node_updates.keys() if "messages" in k), None
                )
                
                if messages_key is not None:
                    # 打印最后一条消息，通常是智能体的响应
                    last_message = node_updates[messages_key][-1]
                    print(f"消息: {last_message.content}")
                else:
                    # 打印其他类型的更新信息
                    print(f"更新: {node_updates}")

        # 分隔符，用于区分不同的执行步骤
        print("\n" + "="*50 + "\n")

# ==================== 演示函数 ====================
# 展示 Swarm 系统的各种功能和特性



def demo_agent_interaction():
    """
    演示智能体交互
    
    这个函数展示了智能体之间的交互过程，包括：
    - 多轮对话中的智能体切换
    - 状态在切换过程中的保持
    - 智能体之间的协作
    """
    print("\n=== 智能体交互演示 ===")
    print("=" * 40)
    
    # 创建 Swarm 应用程序
    app = create_simple_swarm()
    
    # 生成唯一的会话ID，用于标识这次交互会话
    thread_id = str(uuid.uuid4())
    config_dict = {
        "configurable": {
            "thread_id": thread_id  # 会话ID，确保状态在交互过程中得到保持
        }
    }
    
    print(f"会话ID: {thread_id}")
    
    # 定义交互场景，展示智能体之间的切换和协作
    scenarios = [
        "我想计算 8 × 9",           # 场景1: 数学计算
        "现在我想知道上海的天气",    # 场景2: 天气查询
        "再帮我计算 100 ÷ 5",       # 场景3: 再次数学计算
        "回到主助手"                # 场景4: 返回主助手
    ]
    
    # 逐个执行场景，观察智能体的切换过程
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n场景 {i}: {scenario}")
        print("-" * 30)
        
        # 使用流式输出观察每个场景的执行过程
        print_stream(
            app.stream(
                {
                    "messages": [
                        {"role": "user", "content": scenario}
                    ]
                },
                config_dict,  # 使用相同的配置，保持会话状态
                subgraphs=True  # 显示详细的执行过程
            )
        )

def main():
    """
    主函数
    
    程序的入口点，负责：
    1. 显示程序标题
    2. 调用演示函数
    3. 处理异常情况
    """
    print("LangGraph Swarm 简化示例")
    print("=" * 50)
    
    try:
        # 演示智能体交互 - 展示智能体之间的协作过程
        demo_agent_interaction()
        
    except Exception as e:
        # 异常处理，确保程序不会因为错误而崩溃
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()  # 打印详细的错误堆栈信息

if __name__ == "__main__":
    main() 