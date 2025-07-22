import asyncio
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from textwrap import dedent
from pathlib import Path
import sys
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))
from core.config import model_config_manager
load_dotenv()
client = model_config_manager.models["Qwen3-235B-A22B-Instruct-2507"]
from core.utils import search_searxng
from core.models import SearchResultNews, search_news_result



web_search_news_agent = FunctionTool(
    search_searxng,
    description="在网络中搜索关键字查找相关信息",
    strict=True
)

agent = AssistantAgent(
    name="web_search_news_agent",
    model_client=client,
    tools=[web_search_news_agent],
    system_message=dedent("""
    你是一名旅游顾问，帮助用户查找度假目的地。
    你必须调用工具 [search_searxng] 获取数据，并且最终回复内容必须严格输出如下 JSON 格式：
{
  "search_result_news": [
    {"title": "...", "url": "...", "summary": "..."},
    ...
  ]
}
不要输出任何解释性文字。
    """),
    reflect_on_tool_use=True,
    output_content_type=search_news_result

)


async def main():
    response = await agent.on_messages(
        [TextMessage(content="芯片产业", source="user")],
        cancellation_token=CancellationToken(),
    )
    print(000000)
    print(response.inner_messages)
    print(11111)
    print(response.chat_message)
    msg = response.chat_message
    print(type(response.chat_message.content))

    print(response.chat_message.content)
asyncio.run(main())