from core.logging_config import setup_logging, get_logger,logger # 使用绝对导入
# 初始化日志
# logger = setup_logging()

from textwrap import dedent
from typing import Dict, Iterator, Optional
import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.utils.pprint import pprint_run_response
from agno.workflow import RunEvent, RunResponse, Workflow
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

# 确保可以导入config模块
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))
import config  # 使用绝对导入
from config import model_config_manager  # 导入模型配置管理器
from core.utils import search_web_news, search_web_images

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
        response_model=Topic_list,
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
You are an expert in report writing, and are good at writing up to 3 chapter names based on the report topic.
# Requirement: 
# Return only chapter names list, no other text
# Must use Chinese to answer
                        """
        ),
        # markdown=True,  # 启用Markdown格式输出
        show_tool_calls=True,
    )

    # Search Agent: Handles intelligent web searching and source gathering
    searcher_news: Agent = Agent(
        stream=False,
        # save_response_to_file="1.md",
        # response_model=search_news_result,
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
        tools=[
            # ReasoningTools(add_instructions=True),  # 添加推理工具，并包含指令
            # search_web_images,
            search_web_news,
        ],
        system_message_role="system",
        create_default_system_message=False,
        system_message=dedent(
            """
你是一名数据收集专家，擅长通过网络搜索新闻
# 步骤如下：
## 1. 必须调用 [search_web_news] 工具搜索相关新闻，至少 10 条
                        """
        ),
        # markdown=True,  # 启用Markdown格式输出
        show_tool_calls=True,
    )

    searcher_images: Agent = Agent(
        stream=False,
        # save_response_to_file="1.md",
        # response_model=search_images_result,
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
## 1. 必须调用 [search_web_images] 工具搜索相关图片，至少 10 条
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
        save_response_to_file="1.md",
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
1. Content Strategy 📝
- Write a compelling title
- Write an engaging introduction
- Build an engaging content structure
- Add relevant subheadings
2. Writing Excellence ✍️
- Strike a balance between professionalism and readability
- Use clear, engaging language
- Naturally incorporate statistics
3. Source Integration 🔍
- Add citations after subsections, using markdown format![Title](url)
- Insert images in the appropriate subsections, using markdown format![Image](image)
- Keep facts accurate
4. Digital Optimization 💻
- Build an easy-to-navigate structure
- Include shareable bullet points
- Optimize for SEO
- Add engaging subheadings
        """),
        expected_output=dedent("""\
        # {Viral-Worthy Headline}

        ## Introduction
        {Engaging hook and context}

        ## {Compelling Section 1}
        {Key insights and analysis}
        {Expert quotes and statistics}
       {Properly attributed sources with links}\
        ## {Engaging Section 2}
        {Deeper exploration}
        {Real-world examples}
      {Properly attributed sources with links}\
        ## {Practical Section 3}
        {Actionable insights}
        {Expert recommendations}
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
    ) -> Iterator[RunResponse]:
        logger.info(f"Generating a blog post on: {topic}")

        # Use the cached blog post if use_cache is True
        if use_cached_report:
            cached_report_post = self.get_cached_report_post(topic)
            if cached_report_post:
                yield RunResponse(
                    content=cached_report_post, event=RunEvent.workflow_completed
                )
                return

        # 生成章节列表
        yield from self.chapter.run(topic, stream=True)
        chapter_list = self.chapter.run_response.content
        logger.info(f"chapter_list:{chapter_list}")
        # print(dir(chapter_list))
        # 搜索章节 搜索引擎新闻与图片列表
        search_news_dict = {}
        search_image_dict = {}
        news_list = []
        image_list = []
        for chapter in chapter_list.topic_list[0:1]:
            # print(chapter)
            yield from self.searcher_news.run(chapter, stream=True)
            yield from self.searcher_images.run(chapter, stream=True)

            search_result_news = self.searcher_news.run_response.content
            search_result_image = self.searcher_images.run_response.content

            news_list.extend(search_result_news)
            image_list.extend(search_result_image)

        logger.info(f"news_list:{news_list}")
        logger.info(f"image_list:{image_list}")
        logger.info(dir(news_list[0]))
        logger.info(type(news_list[0]))

        # 去重url
        for news in news_list:
            search_news_dict.setdefault(news.url,news)
        for image in image_list:
            search_image_dict.setdefault(image.image_src,image)
 
        news_list = []
        image_list = []
        for news in search_news_dict.values():
            news_list.append(asdict(news))
        for image in search_image_dict.values():
            image_list.append(asdict(image))

        logger.info(f"news_list:{news_list}")
        logger.info(f"image_list:{image_list}")

        # # Scrape the search results
        # scraped_articles: Dict[str, ScrapedArticle] = self.scrape_articles(
        #     topic, search_results, use_scrape_cache
        # )

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


# Run the workflow if the script is executed directly
if __name__ == "__main__":
    import random

    from rich.prompt import Prompt

    # Fun example prompts to showcase the generator's versatility
    # example_prompts = [
    #     "Why Cats Secretly Run the Internet",
    #     "The Science Behind Why Pizza Tastes Better at 2 AM",
    #     "Time Travelers' Guide to Modern Social Media",
    #     "How Rubber Ducks Revolutionized Software Development",
    #     "The Secret Society of Office Plants: A Survival Guide",
    #     "Why Dogs Think We're Bad at Smelling Things",
    #     "The Underground Economy of Coffee Shop WiFi Passwords",
    #     "A Historical Analysis of Dad Jokes Through the Ages",
    # ]

    # # Get topic from user
    # topic = Prompt.ask(
    #     "[bold]Enter a blog post topic[/bold] (or press Enter for a random example)\n✨",
    #     default=random.choice(example_prompts),
    # )

    # Convert the topic to a URL-safe string for use in session_id
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

    # Execute the workflow with caching enabled
    # Returns an iterator of RunResponse objects containing the generated conte
    blog_post: Iterator[RunResponse] = generate_report_post.run(
        topic=topic,
        use_search_cache=True,
        use_scrape_cache=True,
        use_cached_report=True,
    )

    # Print the response
    pprint_run_response(blog_post, markdown=True)
