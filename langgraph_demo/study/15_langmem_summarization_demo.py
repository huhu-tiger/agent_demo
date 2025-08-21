from typing import Any, TypedDict, List
import uuid

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI

from langchain_core.messages import AnyMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from langmem.short_term import SummarizationNode, RunningSummary


def add_message_ids(messages: List[BaseMessage]) -> List[BaseMessage]:
    """为消息添加ID字段"""
    for message in messages:
        if not hasattr(message, 'id') or message.id is None:
            message.id = str(uuid.uuid4())
    return messages


class ChildChatOpenAI(ChatOpenAI):
    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        """
        自定义token计算方法，支持多种模型
        优先使用OpenAI的tiktoken，失败时使用字符估算
        """
        try:
            # 尝试使用OpenAI的tiktoken
            model, encoding = self._get_encoding_model()
            if model.startswith("cl100k_base"):
                # 调用祖父类的函数
                return super(BaseChatOpenAI, self).get_num_tokens_from_messages(messages)
            else:
                return super().get_num_tokens_from_messages(messages)
        except Exception as e:
            # 如果tiktoken失败，使用字符估算
            try:
                contents = []
                for m in messages:
                    if hasattr(m, "content"):
                        content = getattr(m, "content")
                        if isinstance(content, str):
                            contents.append(content)
                        elif isinstance(content, list):
                            # 处理多模态内容
                            for item in content:
                                if hasattr(item, "text"):
                                    contents.append(getattr(item, "text"))
                                elif isinstance(item, dict) and "text" in item:
                                    contents.append(item["text"])
                        else:
                            contents.append(str(content))
                    elif isinstance(m, dict) and "content" in m:
                        contents.append(str(m["content"]))
                    else:
                        contents.append(str(m))
                
                text = " ".join(contents)
                # 粗略估算：约每4字符≈1token（适用于中文和英文混合）
                estimated_tokens = max(1, len(text) // 4)
                print(f"⚠️  使用字符估算token数量: {estimated_tokens} (文本长度: {len(text)})")
                return estimated_tokens
            except Exception as fallback_error:
                print(f"❌ Token计算完全失败，使用默认值1: {fallback_error}")
                return 1


def print_messages_summary(messages: List[BaseMessage], title: str = "消息内容"):
    """打印消息内容的摘要信息"""
    print(f"\n📋 {title}:")
    print("-" * 50)
    
    total_chars = 0
    total_messages = len(messages)
    
    for i, message in enumerate(messages, 1):
        if hasattr(message, "content"):
            content = message.content
            if isinstance(content, str):
                chars = len(content)
                total_chars += chars
                # 截断显示长内容
                display_content = content[:100] + "..." if len(content) > 100 else content
                print(f"消息{i} ({chars}字符): {display_content}")
            elif isinstance(content, list):
                # 处理多模态内容
                for j, item in enumerate(content):
                    if hasattr(item, "text"):
                        text = item.text
                        chars = len(text)
                        total_chars += chars
                        display_text = text[:100] + "..." if len(text) > 100 else text
                        print(f"消息{i}-{j+1} ({chars}字符): {display_text}")
            else:
                content_str = str(content)
                chars = len(content_str)
                total_chars += chars
                display_content = content_str[:100] + "..." if len(content_str) > 100 else content_str
                print(f"消息{i} ({chars}字符): {display_content}")
        elif isinstance(message, dict) and "content" in message:
            content = message["content"]
            chars = len(content)
            total_chars += chars
            display_content = content[:100] + "..." if len(content) > 100 else content
            print(f"消息{i} ({chars}字符): {display_content}")
        else:
            print(f"消息{i}: 无法解析内容")
    
    print(f"\n📊 统计信息:")
    print(f"   消息数量: {total_messages}")
    print(f"   总字符数: {total_chars}")
    print(f"   平均字符数: {total_chars // total_messages if total_messages > 0 else 0}")
    print("-" * 50)


import config
import os
# 自定义模型配置
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 获取日志器
logger = config.logger


def search(query: str):
    """Search the web."""
    if "weather" in query.lower():
        return "The weather is sunny in New York, with a high of 104 degrees."
    elif "broadway" in query.lower():
        return "Hamilton is always on!"
    else:
        raise "Not enough information"

tools = [search]

# 初始化模型 - 支持自定义模型
def create_llm(model_name=None, temperature=0.1):
    """
    创建LLM实例，支持自定义模型
    """
    if model_name is None:
        model_name = MODEL_NAME
    
    return ChildChatOpenAI(
        model=model_name,
        temperature=temperature,
        streaming=False
    )

# 默认模型实例
model = create_llm()
summarization_model = model.bind(max_tokens=128)

# 创建安全的token计数器
def safe_token_counter(messages: List[BaseMessage]) -> int:
    """
    安全的token计数器，使用自定义的ChildChatOpenAI
    """
    try:
        return model.get_num_tokens_from_messages(messages)
    except Exception as e:
        print(f"⚠️  Token计数器异常，使用字符估算: {e}")
        # 字符估算回退
        try:
            contents = []
            for m in messages:
                if hasattr(m, "content"):
                    content = getattr(m, "content")
                    if isinstance(content, str):
                        contents.append(content)
                    else:
                        contents.append(str(content))
                elif isinstance(m, dict) and "content" in m:
                    contents.append(str(m["content"]))
                else:
                    contents.append(str(m))
            
            text = " ".join(contents)
            return max(1, len(text) // 4)
        except Exception:
            return 1

summarization_node = SummarizationNode(
    token_counter=safe_token_counter,
    model=summarization_model,
    max_tokens=256,
    max_tokens_before_summary=1024,
    max_summary_tokens=128,
)

class State(MessagesState):
    context: dict[str, Any]

class LLMInputState(TypedDict):
    summarized_messages: list[AnyMessage]
    context: dict[str, Any]

def call_model(state: LLMInputState):
    # 为消息添加ID
    summarized_messages = add_message_ids(state["summarized_messages"])
    
    # 打印摘要后的消息内容
    print_messages_summary(summarized_messages, "摘要后的消息内容")
    
    response = model.bind_tools(tools).invoke(summarized_messages)
    return {"messages": [response]}

# Define a router that determines whether to execute tools or exit
def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return END
    else:
        return "tools"

checkpointer = InMemorySaver()
builder = StateGraph(State)
builder.add_node("summarize_node", summarization_node)
builder.add_node("call_model", call_model)
builder.add_node("tools", ToolNode(tools))
builder.set_entry_point("summarize_node")
builder.add_edge("summarize_node", "call_model")
builder.add_conditional_edges("call_model", should_continue, path_map=["tools", END])
builder.add_edge("tools", "summarize_node")  
graph = builder.compile(checkpointer=checkpointer)

# 测试token计算功能
def test_token_counter():
    """测试token计算功能"""
    print("🧪 测试自定义token计算功能")
    print("-" * 40)
    
    from langchain_core.messages import HumanMessage, SystemMessage
    
    test_messages = [
        SystemMessage(content="你是一个有用的助手"),
        HumanMessage(content="你好，请介绍一下自己"),
        HumanMessage(content="什么是人工智能？"),
        HumanMessage(content="机器学习的发展历程如何？")
    ]
    
    # 为测试消息添加ID
    test_messages = add_message_ids(test_messages)
    
    try:
        # 测试自定义token计数器
        token_count = safe_token_counter(test_messages)
        print(f"✅ Token计算成功: {token_count}")
        
        # 测试模型直接调用
        model_token_count = model.get_num_tokens_from_messages(test_messages)
        print(f"✅ 模型Token计算成功: {model_token_count}")
        
        return True
    except Exception as e:
        print(f"❌ Token计算测试失败: {e}")
        return False

# 主函数
def main():
    """主函数"""
    print("🚀 LangMem 长上下文管理演示 (自定义Token计算)")
    print("=" * 60)
    
    # 测试token计算
    if test_token_counter():
        print("\n✅ Token计算功能正常，开始演示")
        
        # Invoke the graph
        config = {"configurable": {"thread_id": "1"}}
        
        print("\n💬 开始对话演示:")
        print("=" * 60)
        
        # 创建长对话消息来触发摘要
        long_conversation = [
            "你好，我想了解一下人工智能的发展历史。人工智能这个概念最早是在什么时候提出的？",
            "能详细说说机器学习的发展阶段吗？从最早的符号主义到现在的深度学习，每个阶段都有什么特点？",
            "深度学习是什么时候兴起的？为什么深度学习在2010年代突然变得这么重要？",
            "神经网络的历史可以追溯到什么时候？最早的神经网络模型是什么样的？",
            "能讲讲图灵测试吗？这个测试是如何判断一个机器是否具有智能的？",
            "什么是专家系统？专家系统在人工智能发展史上扮演了什么角色？",
            "自然语言处理的发展历程是怎样的？从最早的规则方法到现在的大语言模型，经历了哪些重要阶段？",
            "计算机视觉的发展历史如何？从最早的图像处理到现在的高级视觉理解，有哪些关键技术突破？",
            "强化学习是什么时候提出的？强化学习与其他机器学习方法有什么不同？",
            "能详细解释一下监督学习和无监督学习的区别吗？它们各自适用于什么场景？"
        ]
        
        for i, message in enumerate(long_conversation, 1):
            print(f"\n🔄 第{i}轮对话:")
            print("=" * 50)
            
            # 打印原始消息
            print(f"用户输入: {message}")
            
            # 获取当前状态中的消息
            current_state = checkpointer.get(config)
            if current_state and "messages" in current_state:
                current_messages = current_state["messages"]
                print_messages_summary(current_messages, f"当前对话历史 (第{i}轮前)")
            
            # 调用图
            response = graph.invoke({"messages": message}, config=config)
            
            # 打印响应
            result = response["messages"][-1].content
            print(f"\n🤖 助手回复: {result}")
            
            # 每3轮检查一次摘要状态
            if i % 3 == 0:
                print(f"\n📝 第{i}轮后的摘要状态:")
                state = checkpointer.get(config)
                if state and "summary" in state:
                    summary = state["summary"]
                    if summary and hasattr(summary, 'summary'):
                        print(f"运行摘要: {summary.summary}")
                        print(f"摘要字符数: {len(summary.summary)}")
                else:
                    print("暂无摘要")
            
            print("\n" + "="*50)
        
        print("\n✅ 演示完成！")
    else:
        print("\n❌ Token计算功能异常，无法继续演示")

if __name__ == "__main__":
    main()