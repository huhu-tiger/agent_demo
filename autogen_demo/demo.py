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
client = model_config_manager.models["qwen-plus"]
from core.utils import search_searxng_news,search_searxng_images
from core.models import SearchResultNews, search_news_result
from core.logging_config import logger


# web_search_news_agent = FunctionTool(
#     search_searxng_news,
#     description="在网络中搜索关键字查找相关新闻",
#     # strict=True
# )

search_news_agent = AssistantAgent(
    name="web_search_news_agent",
    model_client=client,
    tools=[search_searxng_news],
    system_message=dedent("""
你是一名新闻编辑，根据用户输入的关键字，在网络中搜索相关新闻，并根据搜索结果编写一篇新闻报道。
    要求如下:
    1. 小节后面必须要有引用链接，markdown格式 ![title][url]
    2. 客观，新闻的语气，不要有任何主观评价
    3. 不少于8000字
    """),
    reflect_on_tool_use=True,
    # output_content_type=search_news_result
)

search_images_agent = AssistantAgent(
    name="generate_report_agent",
    model_client=client,
    tools=[search_searxng_images],
    system_message=dedent("""
你是一名研究报告编辑专家，根据新闻内容，编写一篇研究报告
    要求如下:
All chart data must come from the provided data
Keep news quote link in markdown format ![title][url]
-----------------------------------------------

1. **Content Strategy 📝**  
Creating content that is not only informative but backed by data analysis ensures high credibility and relevance. Below are steps to create compelling content with data-driven insights, including tables for better data presentation.

- **Craft a Captivating Title**  
    - Use a title that highlights the data-driven nature of your article, such as "Analyzing Market Trends in 2025: A Data-Driven Approach". This will instantly communicate that the content is based on data insights.
    - Include numbers or key findings in the title to attract attention and provide an indication of the article's depth.

- **Write an Engaging Introduction**  
    - Begin with a summary of the key findings derived from data analysis.  
    - Offer a preview of the insights the reader can expect, making sure to frame it as an analysis or study based on real-world data.

- **Build a Structured Content Layout**  
    - Organize your content to logically follow the data analysis process, from data collection to results.  
    - Include key data tables in each section to showcase the progression of the analysis.

- **Add Relevant Subheadings**  
    - Subheadings should clearly reflect the sections where you discuss specific data points. For example:  
      - "Data Collection and Methodology"  
      - "Analysis of Market Trends"  
      - "Key Insights and Recommendations"

2. **Writing Excellence ✍️**  
Writing data-driven content requires clear communication and readability, while ensuring the accuracy of statistical and analytical findings. Here’s how to balance professionalism and readability:

- **Balance Professionalism with Readability**  
    - Use professional language but keep it simple enough for the average reader to follow. Avoid excessive jargon or overly technical terms.  
    - Ensure your explanation of statistical concepts or data trends is accessible.

- **Use Clear and Engaging Language**  
    - When presenting data, explain what the numbers mean in layman's terms, and provide context for your audience.  
    - Use descriptive language to convey why a specific data point matters and how it impacts the overall picture.

- **Naturally Incorporate Statistics**  
    - Embed relevant statistics seamlessly into the narrative. Use them to back up claims, provide evidence, and offer context.  
    - Make sure each statistic is referenced properly with a citation to ensure the reader knows its source.

3. **Source Integration 🔍**  
Properly incorporating and citing sources is crucial for maintaining the credibility of your content. When presenting data in tables, ensure you include the following steps for source integration:

- **Add Citations After Subsections**  
    - Use citations in markdown format: `![Title](url)` to point out where the data originated.  
    - Ensure that each citation is relevant to the section and strengthens the credibility of the analysis.

- **Insert Images Appropriately**  
    - For any data visualization (charts, graphs, etc.), use markdown format to insert images directly: `![Image](image-url)`.  
    - Ensure that images are properly labeled with captions that explain the data being presented.

- **Ensure Accuracy of Facts**  
    - Always verify the data before including it in your content. Cross-check the figures, and ensure that any references to studies or databases are up-to-date and trustworthy.  
    - Cite each dataset or source clearly in the content, and provide background information on how the data was gathered.

4. **Data Presentation in Tables**  
To ensure the data in tables is both clear and valuable, consider the following structure:

- **Use Tables to Display Analyzed Data**  
    - Use tables to present statistical data or comparisons. Make sure each table is easy to read and breaks down complex data into manageable chunks.  
    - For example, you might present market trends or sales data across different years in a table format to help illustrate trends.

    Example Table (Data Analysis: Market Trends for 2025):

    | Year | Market Size (in $ billions) | Growth Rate (%) |
    |------|-----------------------------|-----------------|
    | 2021 | 150                         | 8.2             |
    | 2022 | 180                         | 10.4            |
    | 2023 | 200                         | 11.1            |
    | 2024 | 220                         | 9.5             |
    | 2025 | 250                         | 13.6            |

    **Analysis**:  
    - In the table above, we can clearly see the year-over-year market growth, which highlights the increasing demand in the sector. The table presents both the size and the growth rate, helping readers identify trends in the market.
    """),
    reflect_on_tool_use=True,
    # output_content_type=search_news_result
)


async def main():
    response = await search_news_agent.on_messages(
        [TextMessage(content="芯片产业", source="user")],
        cancellation_token=CancellationToken(),
    )
    print(000000)
    print(response.inner_messages)
    print(11111)
    print(response.chat_message)

    # msg = response.chat_message
    print(type(response.chat_message.content))

    print(response.chat_message.content)


    response = await search_images_agent.on_messages(
        [TextMessage(content=response.chat_message.content, source="user")],
        cancellation_token=CancellationToken(),
    )

    logger.info(response.chat_message.content)
    


asyncio.run(main())