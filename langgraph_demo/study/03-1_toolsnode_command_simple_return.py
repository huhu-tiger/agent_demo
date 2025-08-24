"""
简化版本 - 不使用 Command 对象，直接返回结果
"""

from typing import Annotated, Dict, Any
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
import config
import os 

# 获取日志器用于调试和监控
logger = config.logger

# 设置 OpenAI API 环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 初始化语言模型
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,
    max_tokens=1000
)

# 模拟用户数据库
USER_DATA = {
    "user_123": {
        "name": "张三",
        "email": "zhangsan@example.com",
        "role": "开发者",
        "location": "北京"
    }
}

class State(AgentState):
    user_info: Dict[str, Any]

def get_user_info(user_id: str) -> Dict[str, Any]:
    """获取用户信息"""
    return USER_DATA.get(user_id, {"name": "未知用户", "email": "unknown@example.com","role":"未知角色","location":"未知位置"})

@tool
def lookup_user_info(config: RunnableConfig) -> str:
    """
    查找用户信息以更好地协助用户回答问题。
    当用户询问关于他们自己的信息时，请使用此工具。
    此工具会返回用户的姓名、邮箱、角色和位置等信息。
    """
    logger.info(f"=== lookup_user_info 被调用 ===")
    logger.info(f"config: {config}")
    
    # 从配置中获取用户ID
    user_id = config.get("configurable", {}).get("user_id")
    logger.info(f"user_id: {user_id}")
    
    if user_id is None:
        return "错误：请提供有效的用户ID"
    if user_id not in USER_DATA:
        return f"错误：用户 '{user_id}' 不存在"
    
    user_info = get_user_info(user_id)
    logger.info(f"user_info: {user_info}")
    
    # 直接返回用户信息字符串
    return f"用户信息：姓名={user_info['name']}，角色={user_info['role']}，位置={user_info['location']}，邮箱={user_info['email']}"

def agent_node(state: State) -> State:
    """智能体节点"""
    messages = state.get("messages", [])
    userinfo = state.get("user_info", {})
    
    # 构建系统提示
    if userinfo:
        system_message = f"你是一个助手，用户信息如下：{userinfo['name']}，用户位置：{userinfo['location']}"
    else:
        system_message = """你是一个助手。当用户询问关于他们自己的信息时，请使用 lookup_user_info 工具来获取用户信息。
        这个工具可以帮助你了解用户的姓名、位置、角色等信息，以便更好地回答用户的问题。"""
    
    logger.info(f"系统提示: {system_message}")
    
    # 将工具绑定到语言模型
    model_with_tools = llm.bind_tools([lookup_user_info])
    
    # 调用模型
    response = model_with_tools.invoke([SystemMessage(content=system_message)] + messages)
    
    logger.info(f"模型响应: {response}")
    logger.info(f"是否有工具调用: {hasattr(response, 'tool_calls') and response.tool_calls}")
    if hasattr(response, 'tool_calls') and response.tool_calls:
        logger.info(f"工具调用详情: {response.tool_calls}")
    
    return {"messages": [response]}

def should_use_tools(state: State) -> str:
    """条件路由函数"""
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    logger.info(f"检查是否需要工具调用，最后消息: {last_message}")
    logger.info(f"是否有工具调用: {hasattr(last_message, 'tool_calls') and last_message.tool_calls}")
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        logger.info("决定使用工具")
        return "tools"
    
    logger.info("决定结束执行")
    return "end"

def demo_lookup_user_info():
    """演示 lookup_user_info 工具"""
    print("=== lookup_user_info 工具演示（简化版本）===")
    
    # 创建 ToolNode
    tool_node = ToolNode([lookup_user_info])
    graph = StateGraph(State)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges(
        "agent",
        should_use_tools,
        {
            "tools": "tools",
            "end": END
        }
    )
    agent = graph.compile()
    
    print("测试问题: 我是谁，我在哪儿")
    print("-" * 30)
    
    try:
        for chunk in agent.stream(
            {"messages": [HumanMessage("我是谁，我在哪儿")]},
            {"configurable": {"user_id": "user_123"}}
        ):
            print(f"状态更新: {chunk}")
    except Exception as e:
        print(f"执行出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("LangGraph ToolNode 简化版本（不使用 Command）")
    print("=" * 50)
    
    demo_lookup_user_info()

if __name__ == "__main__":
    main() 