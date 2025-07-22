from tkinter import NO
from core.logging_config import setup_logging, get_logger,logger # 使用绝对导入
# 初始化日志
# logger = setup_logging()
from agno.playground import Playground
from textwrap import dedent
from typing import Dict, Iterator, Optional
import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.utils.pprint import pprint_run_response
from agno.workflow import RunEvent, RunResponse, Workflow
from agno.run.response import RunResponse, RunResponseEvent, RunResponseContentEvent, RunEvent
from pydantic import BaseModel, Field
from agno.agent import Agent  # 导入Agno框架的Agent类
from agno.models.deepseek import DeepSeek  # 导入DeepSeek模型
from agno.models.openai import OpenAIChat
from agno.models.deepseek import DeepSeek
from textwrap import dedent
from dataclasses import asdict
import sys
from pathlib import Path
from core.models import *
from fastapi.middleware.cors import CORSMiddleware
# 确保可以导入config模块
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))
import config  # 使用绝对导入
from config import model_config_manager  # 导入模型配置管理器
from core.utils import search_web_news, search_web_images, parse_image_url

logger.info(model_config_manager.models)
# 导入日志模块

import time

md_file = f"{int(time.time())}.md"
print(md_file)


model_name = "Qwen3-235B"
reasoning_model_name = "deepseek-r1"


class ReportPostGenerator(Workflow):
    """Advanced workflow for producing professional research reports with proper research and citations."""

    description: str = dedent(
        """\
    Intelligent research report generator to create engaging, well-researched content.
    This workflow coordinates multiple AI agents to research, analyze, and create engaging research reports that combine journalistic rigor with compelling storytelling.
    The system excels at creating content that is informative and optimized for digital consumption.
        """
    )

    chapter: Agent = Agent(
        stream=True,
        # save_response_to_file="1.md",
        response_model=Keyword_list,
        # 配置DeepSeek模型，使用配置文件中的模型参数
        # model=DeepSeek(
        #     id=model_config_manager.models["deepseek-r1"].model_name,  # 模型ID
        #     name=model_config_manager.models["deepseek-r1"].model_name,  # 模型名称
        #     api_key=model_config_manager.models["deepseek-r1"].api_key,  # API密钥
        #     base_url=model_config_manager.models["deepseek-r1"].url  # API基础URL
        # ),
        description=dedent(
            """\
生成报告章节列表的agent
"""
        ),
        model=OpenAIChat(
            id=model_config_manager.models[model_name].model_name,  # 模型ID
            name=model_config_manager.models[model_name].model_name,  # 模型名称
            api_key=model_config_manager.models[model_name].api_key,  # API密钥
            base_url=model_config_manager.models[model_name].url,  # API基础URL
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        reasoning_model=DeepSeek(
            id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
            name=model_config_manager.models[
                reasoning_model_name
            ].model_name,  # 模型名称
            api_key=model_config_manager.models[
                reasoning_model_name
            ].api_key,  # API密钥
            base_url=model_config_manager.models[
                reasoning_model_name
            ].url,  # API基础URL
        ),
        # 配置代理的工具
        system_message_role="system",
        create_default_system_message=False,
        system_message=dedent(
            """
You are an expert in web search and are good at writing up to three web search keywords based on the topic.
# Requirements:
# Only return the keyword list, no other text
# Answers must be written in Chinese
                        """
        ),
        # markdown=True,  # 启用Markdown格式输出
        show_tool_calls=True,
    )

    # Search Agent: Handles intelligent web searching and source gathering
    searcher_news: Agent = Agent(
        stream=False,
        debug_mode=True,
        tool_call_limit=1,
        # save_response_to_file="1.md",
        response_model=search_news_result,
        # structured_outputs=True,
        # 配置DeepSeek模型，使用配置文件中的模型参数
        # model=DeepSeek(
        #     id=model_config_manager.models["deepseek-r1"].model_name,  # 模型ID
        #     name=model_config_manager.models["deepseek-r1"].model_name,  # 模型名称
        #     api_key=model_config_manager.models["deepseek-r1"].api_key,  # API密钥
        #     base_url=model_config_manager.models["deepseek-r1"].url  # API基础URL
        # ),
        description=dedent(
            """\
收集网络新闻的agent
"""
        ),
        parser_model=OpenAIChat(
            id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
            name=model_config_manager.models[reasoning_model_name].model_name,  # 模型名称
            api_key=model_config_manager.models[reasoning_model_name].api_key,  # API密钥
            base_url=model_config_manager.models[reasoning_model_name].url,  # API基础URL
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        model=OpenAIChat(
            id=model_config_manager.models[model_name].model_name,  # 模型ID
            name=model_config_manager.models[model_name].model_name,  # 模型名称
            api_key=model_config_manager.models[model_name].api_key,  # API密钥
            base_url=model_config_manager.models[model_name].url,  # API基础URL
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        # reasoning_model=DeepSeek(
        #     id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
        #     name=model_config_manager.models[
        #         reasoning_model_name
        #     ].model_name,  # 模型名称
        #     api_key=model_config_manager.models[
        #         reasoning_model_name
        #     ].api_key,  # API密钥
        #     base_url=model_config_manager.models[
        #         reasoning_model_name
        #     ].url,  # API基础URL
        # ),
        # 配置代理的工具
        tools=[
            # ReasoningTools(add_instructions=True),  # 添加推理工具，并包含指令
            # search_web_images,
            search_web_news,
        ],
        # tool_choice="auto",  
        system_message_role="system",
        create_default_system_message=True,
        system_message=dedent("""
你是一名数据收集专家，擅长调用search_web_news工具收集新闻
"""
        ),
        instructions=dedent("""\
    1. 搜索相关新闻，至少 10 条
    2. 不需要生成任何内容，只需要返回搜索结果

        """),
        # markdown=True,  # 启用Markdown格式输出
        show_tool_calls=True,
    )

    searcher_images: Agent = Agent(
        stream=False,
        # save_response_to_file="1.md",
        response_model=search_images_result,
        # 配置DeepSeek模型，使用配置文件中的模型参数
        # model=DeepSeek(
        #     id=model_config_manager.models["deepseek-r1"].model_name,  # 模型ID
        #     name=model_config_manager.models["deepseek-r1"].model_name,  # 模型名称
        #     api_key=model_config_manager.models["deepseek-r1"].api_key,  # API密钥
        #     base_url=model_config_manager.models["deepseek-r1"].url  # API基础URL
        # ),
        description=dedent(
            """\
收集网络图片的agent
"""
        ),
        model=OpenAIChat(
            id=model_config_manager.models[model_name].model_name,  # 模型ID
            name=model_config_manager.models[model_name].model_name,  # 模型名称
            api_key=model_config_manager.models[model_name].api_key,  # API密钥
            base_url=model_config_manager.models[model_name].url,  # API基础URL
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        parser_model=OpenAIChat(
            id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
            name=model_config_manager.models[reasoning_model_name].model_name,  # 模型名称
            api_key=model_config_manager.models[reasoning_model_name].api_key,  # API密钥
            base_url=model_config_manager.models[reasoning_model_name].url,  # API基础URL
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        # reasoning_model=DeepSeek(
        #     id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
        #     name=model_config_manager.models[
        #         reasoning_model_name
        #     ].model_name,  # 模型名称
        #     api_key=model_config_manager.models[
        #         reasoning_model_name
        #     ].api_key,  # API密钥
        #     base_url=model_config_manager.models[
        #         reasoning_model_name
        #     ].url,  # API基础URL
        # ),
        # 配置代理的工具
        # tool_choice="auto",  # 强制模型调用一个工具
        tools=[
            # ReasoningTools(add_instructions=True),  # 添加推理工具，并包含指令
            # search_web_images,
            search_web_images,
        ],
        system_message_role="system",
        create_default_system_message=False,
        system_message=dedent(
            """
你是一名数据收集专家，擅长通过网络搜索图片
# 步骤如下：
## 1. 不考虑任何因素，必须调用 [search_web_images] 工具搜索相关图片，至少 10 条
## 2. 不需要生成任何内容，只需要返回搜索结果

                        """
        ),
        # markdown=True,  # 启用Markdown格式输出
        show_tool_calls=True,
    )

    image_analysis: Agent = Agent(
        stream=False,
        # save_response_to_file="1.md",
        response_model=search_images_result,
        # 配置DeepSeek模型，使用配置文件中的模型参数
        # model=DeepSeek(
        #     id=model_config_manager.models["deepseek-r1"].model_name,  # 模型ID
        #     name=model_config_manager.models["deepseek-r1"].model_name,  # 模型名称
        #     api_key=model_config_manager.models["deepseek-r1"].api_key,  # API密钥
        #     base_url=model_config_manager.models["deepseek-r1"].url  # API基础URL
        # ),
        description=dedent(
            """\
图片分析工具
"""
        ),
        model=OpenAIChat(
            id=model_config_manager.models[model_name].model_name,  # 模型ID
            name=model_config_manager.models[model_name].model_name,  # 模型名称
            api_key=model_config_manager.models[model_name].api_key,  # API密钥
            base_url=model_config_manager.models[model_name].url,  # API基础URL
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        parser_model=OpenAIChat(
            id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
            name=model_config_manager.models[reasoning_model_name].model_name,  # 模型名称
            api_key=model_config_manager.models[reasoning_model_name].api_key,  # API密钥
            base_url=model_config_manager.models[reasoning_model_name].url,  # API基础URL
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        # reasoning_model=DeepSeek(
        #     id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
        #     name=model_config_manager.models[
        #         reasoning_model_name
        #     ].model_name,  # 模型名称
        #     api_key=model_config_manager.models[
        #         reasoning_model_name
        #     ].api_key,  # API密钥
        #     base_url=model_config_manager.models[
        #         reasoning_model_name
        #     ].url,  # API基础URL
        # ),
        # 配置代理的工具
        # tool_choice="auto",  # 强制模型调用一个工具
        tools=[
            # ReasoningTools(add_instructions=True),  # 添加推理工具，并包含指令
            # search_web_images,
            parse_image_url,
        ],
        system_message_role="system",
        create_default_system_message=False,
        system_message=dedent(
            """
你是一名图片分析专家，擅长通过图片分析，获取图片的详细信息
# 步骤如下：
## 1. 不考虑任何因素，必须调用 [parse_image_url] 工具分析图片

                        """
        ),
        # markdown=True,  # 启用Markdown格式输出
        show_tool_calls=True,
    )
    

    # Content Scraper: Extracts and processes article content
    # article_scraper: Agent = Agent(
    #     model=OpenAIChat(
    #         id=model_config_manager.models[model_name].model_name,  # 模型ID
    #         name=model_config_manager.models[model_name].model_name,  # 模型名称
    #         api_key=model_config_manager.models[model_name].api_key,  # API密钥
    #         base_url=model_config_manager.models[model_name].url,  # API基础URL
    #         role_map={
    #             "system": "system",
    #             "user": "user",
    #             "assistant": "assistant",
    #             "tool": "tool",
    #             "model": "assistant"
    #             }
    #     ),
    #     reasoning_model=DeepSeek(
    #         id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
    #         name=model_config_manager.models[reasoning_model_name].model_name,  # 模型名称
    #         api_key=model_config_manager.models[reasoning_model_name].api_key,  # API密钥
    #         base_url=model_config_manager.models[reasoning_model_name].url  # API基础URL
    #     ),
    #     tools=[Newspaper4kTools()],
    #     description=dedent("""\
    #     You are ContentBot-X, a specialist in extracting and processing digital content
    #     for blog creation. Your expertise includes:

    #     - Efficient content extraction
    #     - Smart formatting and structuring
    #     - Key information identification
    #     - Quote and statistic preservation
    #     - Maintaining source attribution\
    #     """),
    #     instructions=dedent("""\
    #     1. Content Extraction 📑
    #        - Extract content from the article
    #        - Preserve important quotes and statistics
    #        - Maintain proper attribution
    #        - Handle paywalls gracefully
    #     2. Content Processing 🔄
    #        - Format text in clean markdown
    #        - Preserve key information
    #        - Structure content logically
    #     3. Quality Control ✅
    #        - Verify content relevance
    #        - Ensure accurate extraction
    #        - Maintain readability\
    #     """),
    #     response_model=ScrapedArticle,
    #     structured_outputs=True,
    # )

    # Content Writer Agent: Crafts engaging blog posts from research
    writer: Agent = Agent(
        # save_response_to_file="1.md",
        model=OpenAIChat(
            id=model_config_manager.models[model_name].model_name,  # 模型ID
            name=model_config_manager.models[model_name].model_name,  # 模型名称
            api_key=model_config_manager.models[model_name].api_key,  # API密钥
            base_url=model_config_manager.models[model_name].url,  # API基础URL
            max_tokens=10000,
            role_map={
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            },
        ),
        # reasoning_model=DeepSeek(
        #     id=model_config_manager.models[reasoning_model_name].model_name,  # 模型ID
        #     name=model_config_manager.models[
        #         reasoning_model_name
        #     ].model_name,  # 模型名称
        #     api_key=model_config_manager.models[
        #         reasoning_model_name
        #     ].api_key,  # API密钥
        #     base_url=model_config_manager.models[
        #         reasoning_model_name
        #     ].url,  # API基础URL
        # ),
        description=dedent("""\
You are Research Report Writing-X, an elite content creator who combines excellent journalism skills with market analysis expertise. Your strengths include:

- Craft viral headlines
- Write engaging introductions
- Build content for digital consumption
- Seamlessly integrate research findings
- Optimize for SEO while maintaining quality
- Write shareable conclusions
        """),
        instructions=dedent("""\
All chart data must come from the provided data
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

5. **Digital Optimization 💻**  
Ensuring your content is optimized for digital consumption, especially when using data-driven insights,

        """),
        expected_output=dedent("""\
        # {Viral-Worthy Headline}

        ## Introduction
        {Engaging hook and context}

        ## {Compelling Section 1}
        {Key insights and analysis}
       {Properly image sources with links}\
        {Expert quotes and statistics}
       {Properly attributed sources with links}\
        ## {Engaging Section 2}
        {Deeper exploration}
        {Real-world examples}
       {Properly image sources with links}\
       {Properly attributed sources with links}\
        ## {Practical Section 3}
        {Actionable insights}
        {Expert recommendations}
       {Properly image sources with links}\
       {Properly attributed sources with links}\
        ## Key Takeaways
        - {Shareable insight 1}
        - {Practical takeaway 2}
        - {Notable finding 3}
        """),
        markdown=True,
    )

    def run(
        self,
        topic: str,
        use_search_cache: bool = True,
        use_scrape_cache: bool = True,
        use_cached_report: bool = True,
    ) -> Iterator[RunResponseEvent]:
        logger.info(f"Generating a blog post on: {topic}")

        # Use the cached blog post if use_cache is True
        if use_cached_report:
            cached_report_post = self.get_cached_report_post(topic)
            if cached_report_post:
                yield RunResponseContentEvent(
                    content=cached_report_post, event=RunEvent.run_response_content
                )
                return

        # 生成章节列表
        last_event = None

        for event in self.chapter.run(topic, stream=True):
            yield event
            last_event = event

        if last_event:
            if isinstance(last_event.content, dict):
                # 使用Pydantic的model_validate方法将Any类型转换为Keyword_list
                Keyword_list_result: Keyword_list|None = Keyword_list.model_validate(last_event.content)
            else:
                Keyword_list_result = last_event.content


        logger.info(f"Keyword_list_result:{Keyword_list_result}")
        logger.info(type(Keyword_list_result))
        # print(dir(chapter_list))
        # 搜索章节 搜索引擎新闻与图片列表
        search_news_dict = {}
        search_image_dict = {}
        news_list = []
        image_list = []
        if Keyword_list_result:
            for chapter in Keyword_list_result.keyword_list[0:1]:
                logger.info(f"chapter:{chapter}")
                self.searcher_news.run(chapter, stream=False)
                self.searcher_images.run(chapter, stream=False)

                search_result_news : search_news_result|None = search_news_result.model_validate(self.searcher_news.run_response.content)
                search_result_image : search_images_result|None = search_images_result.model_validate(self.searcher_images.run_response.content)
                logger.info(type(search_result_news))
                logger.info(type(search_result_image))
                logger.info(f"search_result_news:{search_result_news}")
                logger.info(f"search_result_image:{search_result_image}")
                news_list.extend(search_result_news.search_result_news)
                image_list.extend(search_result_image.search_result_image)



        logger.info(f"news_list:{news_list}")
        logger.info(f"image_list:{image_list}")
        logger.info(dir(news_list[0]))

        # 去重url
        # 使用字典推导式直接完成去重和转换
        unique_news = {news.url: news.model_dump() for news in news_list}
        unique_images = {image.image_src: image.model_dump() for image in image_list}

        # 直接获取字典值列表
        news_list = list(unique_news.values())
        image_list = list(unique_images.values())

        logger.info(f"去重后news_list数量:{len(news_list)}")
        logger.info(f"去重后image_list数量:{len(image_list)}")

        logger.info(f"news_list:{news_list}")
        logger.info(f"image_list:{image_list}")

        # 分析图片
        search_result_image : search_images_result|None = search_images_result.model_validate(self.image_analysis.run_response.content)
        image_list = list(search_result_image.search_result_image)

        # Prepare the input for the writer
        writer_input = {
            "topic": topic,
            "articles": {"news":news_list,"images":image_list},
        }
        logger.info(f"writer_input:{writer_input}")
        # # Run the writer and yield the response
        yield from self.writer.run(json.dumps(writer_input, indent=4), stream=True)
        
        report_markdown = self.writer.run_response.content
         # 以 UTF-8 编码写入文件
        with open("2.md", "w", encoding="utf-8") as f:
            f.write(report_markdown)
        # Save the blog post in the cache
        # self.add_report_post_to_cache(topic, self.writer.run_response.content)

    # 提取缓存中的最终报告
    def get_cached_report_post(self, topic: str) -> Optional[str]:
        logger.info("Checking if cached report post exists")

        return self.session_state.get("report_posts", {}).get(topic)

    # 保存最终报告至缓存
    def add_report_post_to_cache(self, topic: str, report_content: str):
        logger.info(f"Saving report post for topic: {topic}")
        self.session_state.setdefault("report_posts", {})
        self.session_state["report_posts"][topic] = report_content

    # def get_cached_search_results(self, topic: str) -> Optional[SearchResults]:
    #     logger.info("Checking if cached search results exist")
    #     search_results = self.session_state.get("search_results", {}).get(topic)
    #     return (
    #         SearchResults.model_validate(search_results)
    #         if search_results and isinstance(search_results, dict)
    #         else search_results
    #     )

    # def add_search_results_to_cache(self, topic: str, search_results: SearchResults):
    #     logger.info(f"Saving search results for topic: {topic}")
    #     self.session_state.setdefault("search_results", {})
    #     self.session_state["search_results"][topic] = search_results

    # def get_cached_scraped_articles(
    #     self, topic: str
    # ) -> Optional[Dict[str, ScrapedArticle]]:
    #     logger.info("Checking if cached scraped articles exist")
    #     scraped_articles = self.session_state.get("scraped_articles", {}).get(topic)
    #     return (
    #         ScrapedArticle.model_validate(scraped_articles)
    #         if scraped_articles and isinstance(scraped_articles, dict)
    #         else scraped_articles
    #     )

    # def add_scraped_articles_to_cache(
    #     self, topic: str, scraped_articles: Dict[str, ScrapedArticle]
    # ):
    #     logger.info(f"Saving scraped articles for topic: {topic}")
    #     self.session_state.setdefault("scraped_articles", {})
    #     self.session_state["scraped_articles"][topic] = scraped_articles

    # def get_search_results(
    #     self, topic: str, use_search_cache: bool, num_attempts: int = 3
    # ) -> Optional[SearchResults]:
    #     # Get cached search_results from the session state if use_search_cache is True
    #     if use_search_cache:
    #         try:
    #             search_results_from_cache = self.get_cached_search_results(topic)
    #             if search_results_from_cache is not None:
    #                 search_results = SearchResults.model_validate(
    #                     search_results_from_cache
    #                 )
    #                 logger.info(
    #                     f"Found {len(search_results.articles)} articles in cache."
    #                 )
    #                 return search_results
    #         except Exception as e:
    #             logger.warning(f"Could not read search results from cache: {e}")

    #     # If there are no cached search_results, use the searcher to find the latest articles
    #     for attempt in range(num_attempts):
    #         try:
    #             searcher_response: RunResponse = self.searcher.run(topic)
    #             if (
    #                 searcher_response is not None
    #                 and searcher_response.content is not None
    #                 and isinstance(searcher_response.content, SearchResults)
    #             ):
    #                 article_count = len(searcher_response.content.articles)
    #                 logger.info(
    #                     f"Found {article_count} articles on attempt {attempt + 1}"
    #                 )
    #                 # Cache the search results
    #                 self.add_search_results_to_cache(topic, searcher_response.content)
    #                 return searcher_response.content
    #             else:
    #                 logger.warning(
    #                     f"Attempt {attempt + 1}/{num_attempts} failed: Invalid response type"
    #                 )
    #         except Exception as e:
    #             logger.warning(f"Attempt {attempt + 1}/{num_attempts} failed: {str(e)}")

    #     logger.error(f"Failed to get search results after {num_attempts} attempts")
    #     return None

    # def scrape_articles(
    #     self, topic: str, search_results: SearchResults, use_scrape_cache: bool
    # ) -> Dict[str, ScrapedArticle]:
    #     scraped_articles: Dict[str, ScrapedArticle] = {}

    #     # Get cached scraped_articles from the session state if use_scrape_cache is True
    #     if use_scrape_cache:
    #         try:
    #             scraped_articles_from_cache = self.get_cached_scraped_articles(topic)
    #             if scraped_articles_from_cache is not None:
    #                 scraped_articles = scraped_articles_from_cache
    #                 logger.info(
    #                     f"Found {len(scraped_articles)} scraped articles in cache."
    #                 )
    #                 return scraped_articles
    #         except Exception as e:
    #             logger.warning(f"Could not read scraped articles from cache: {e}")

    #     # Scrape the articles that are not in the cache
    #     for article in search_results.articles:
    #         if article.url in scraped_articles:
    #             logger.info(f"Found scraped article in cache: {article.url}")
    #             continue

    #         article_scraper_response: RunResponse = self.article_scraper.run(
    #             article.url
    #         )
    #         if (
    #             article_scraper_response is not None
    #             and article_scraper_response.content is not None
    #             and isinstance(article_scraper_response.content, ScrapedArticle)
    #         ):
    #             scraped_articles[article_scraper_response.content.url] = (
    #                 article_scraper_response.content
    #             )
    #             logger.info(f"Scraped article: {article_scraper_response.content.url}")

    #     # Save the scraped articles in the session state
    #     self.add_scraped_articles_to_cache(topic, scraped_articles)
    #     return scraped_articles
topic = "芯片产业"
url_safe_topic = topic.lower().replace(" ", "-")

# Initialize the blog post generator workflow
# - Creates a unique session ID based on the topic
# - Sets up SQLite storage for caching results
generate_report_post = ReportPostGenerator(
    session_id=f"generate-blog-post-on-{url_safe_topic}",
    # storage=SqliteStorage(
    #     table_name="generate_report_post_workflows",
    #     db_file="tmp/agno_workflows.db",
    # ),
    debug_mode=True,
)

from agno.tools import tool
# 1. 封装工作流为工具
@tool(name="generate_report", description="生成专业报告")
def generate_report_tool(topic: str) -> Iterator[str]:
    # 这里直接流式返回 markdown 内容
    for event in generate_report_post.run(topic=topic, use_search_cache=True, use_scrape_cache=True, use_cached_report=True):
        # 只返回最终内容事件
        if hasattr(event, "content") and event.content:
            yield event.content

# 2. 创建 workflow_agent，并注册工具
workflow_agent = Agent(
    name="Workflow Agent",
    model=OpenAIChat(
        id=model_config_manager.models[model_name].model_name,  # 模型ID
        name=model_config_manager.models[model_name].model_name,  # 模型名称
        api_key=model_config_manager.models[model_name].api_key,  # API密钥
        base_url=model_config_manager.models[model_name].url,  # API基础URL
        max_tokens=10000,
        role_map={
            "system": "system",
            "user": "user",
            "assistant": "assistant",
            "tool": "tool",
            "model": "assistant",
        },
    ),
    tools=[generate_report_tool],  # 注册工作流工具
    instructions=["你是一个工作流专家，请根据用户的需求，使用工具生成专业报告,报告完整的返回,不要有任何的解释"],
    # storage=SqliteStorage(table_name="finance_agent"),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
)

from datetime import datetime
# 示例tool，流式返回字符串
@tool(name="getCurrentTime", description="获取当前时间")
def get_current_time_tool(query: str="")->str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# demo agent，注册该tool
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

demo_agent = Agent(
    stream=True,
    name="Demo Agent",
    model=OpenAIChat(
        id=model_config_manager.models[model_name].model_name,  # 模型ID
        name=model_config_manager.models[model_name].model_name,  # 模型名称
        api_key=model_config_manager.models[model_name].api_key,  # API密钥
        base_url=model_config_manager.models[model_name].url,  # API基础URL
        role_map={
            "system": "system",
            "user": "user",
            "assistant": "assistant",
            "tool": "tool",
            "model": "assistant",
        },
    ),
    tools=[get_current_time_tool],

    instructions=["你可以调用 getCurrentTime 工具来获取当前时间。"],
    # add_datetime_to_instructions=True,
    markdown=True,
)

# 注册到playground
playground = Playground(agents=[workflow_agent])
app = playground.get_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 保留原有的 main 入口
if __name__ == "__main__":
    playground.serve("demo1_ui:app", host="0.0.0.0", reload=True)

# Run the workflow if the script is executed directly
# if __name__ == "__main__":
#     import random

#     from rich.prompt import Prompt


#     blog_post: Iterator[RunResponseEvent] = generate_report_post.run(
#         topic=topic,
#         use_search_cache=True,
#         use_scrape_cache=True,
#         use_cached_report=True,
#     )

#     # Print the response
#     pprint_run_response(blog_post, markdown=True)
    
