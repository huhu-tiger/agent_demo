"""Utility functions for the multi-agent report generation system.
多智能体报告生成系统的工具函数。
"""

import logging
import os
import sys
from urllib.parse import urljoin
from typing import Any, Dict, List, Optional, Sequence
import requests
from pathlib import Path
import pandas as pd
# 确保可以导入config模块
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))


from .models import SearchResultNews, SearchResultImage, ImageAnalysis, TableData
from .logging_config import get_logger

import config

from agno.agent import Agent
from agno.tools import tool
from typing import Any, Callable, Dict


# 获取日志记录器
logger = get_logger(__name__, "Utils")
logger.info(f"Utils logger initialized")
# --- API Configuration is now managed in core/config.py ---


def _make_api_request(
    url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, **kwargs
) -> Dict[str, Any]:
    """
    A robust function to make API requests with retry logic.

    Args:
        url: The API endpoint URL.
        method: HTTP method (GET, POST, etc.).
        headers: Request headers.
        **kwargs: Additional arguments for the requests call (e.g., json, params).

    Returns:
        The JSON response from the API.
    
    Raises:
        requests.exceptions.HTTPError: If the request fails after all retries.
    """
    try:
        response = requests.request(method, url, headers=headers, timeout=60, **kwargs)
        response.raise_for_status()
        logger.info(f"API请求成功，URL: {url}，参数: {kwargs}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求失败，URL: {url}，错误: {e}")
        raise

def extract_bocah_data(response)->tuple[List[SearchResultNews], List[SearchResultImage]]:
    """
    从bocah API返回数据中提取新闻和图片信息
    
    Args:
        response (dict): bocah API的响应数据
        
    Returns:
        tuple: (news_data, image_data) - 新闻数据列表和图片数据列表
    """
    news_data_result = []
    image_data_result = []
    logger.info(f"提取博查数据: {response}")
    try:
        if response and isinstance(response, dict) and "data" in response:
            # 提取新闻数据
            if "webPages" in response["data"] and "value" in response["data"]["webPages"]:
                news_data = response["data"]["webPages"]["value"]
                news_data_result = [
                    SearchResultNews(
                        title=item.get("name", ""),
                        url=item.get("url", ""),
                        summary=item.get("summary", ""),
                    )
                    for item in news_data
                ]
            
            # 提取图片数据
            if "images" in response["data"] and response["data"]["images"] is not None:
                image_data = response["data"]["images"]["value"]
                image_data_result = [
                    SearchResultImage(
                        image_src=item.get("contentUrl", "")
                    )
                    for item in image_data
                ]
    except Exception as e:
        import traceback
        logger.error(f"提取博查数据失败: {e}\n{traceback.format_exc()}")
    return news_data_result, image_data_result 



def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Hook function that wraps the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result


@tool(
    name="通过搜索引擎搜索图片",                # Custom name for the tool (otherwise the function name is used)
    # description="通过博查搜索引擎搜索新闻和图片,count为搜索结果的数量",  # Custom description (otherwise the function docstring is used)
    show_result=True,                               # Show result after function call
    stop_after_tool_call=False,                      # Return the result immediately after the tool call and stop the agent
    tool_hooks=[logger_hook],                       # Hook to run before and after execution
    requires_confirmation=False,                     # Requires user confirmation before execution
    # cache_results=True,                             # Enable caching of results
    # cache_dir="/tmp/agno_cache",                    # Custom cache directory
    # cache_ttl=3600                                  # Cache TTL in seconds (1 hour)
)
def search_web_images(chapter: str, images_num: int=10) -> List[SearchResultImage]:
    """
    使用搜索引擎搜索图片的工具函数

    Args:
        chapter:搜索主题的关键词
        images_num:搜索的图片,不少于20条

    Returns:
        新闻和图片的列表
    """
    # bochai_result = []
    # bochai_result = search_bochai(chapter, num)
    # print(f"bochai_result: {bochai_result}")
    # searxng_result_general = search_searxng(chapter=chapter, page=1, language="zh-CN", categories="general")
    logger.info(f"search_web_images: {chapter}, images_num:{images_num}")
    result = []
    searxng_result_images = search_searxng(chapter=chapter, page=2, language="zh-CN", categories="images")
    logger.info(f"searxng_result_images: {searxng_result_images}")
    for image in searxng_result_images:
        image_analysis = parse_image_url(image.image_src)
        logger.info(f"image_analysis: {image_analysis}")
        if "无效" in image_analysis.description:
            continue
        result.append(SearchResultImage(image_src=image.image_src,description=image_analysis.description,title="图片"))
    logger.info(f"search_web_images result: {result}")
    return result


@tool(
    name="通过搜索引擎搜索新闻文字",                # Custom name for the tool (otherwise the function name is used)
    # description="通过博查搜索引擎搜索新闻和图片,count为搜索结果的数量",  # Custom description (otherwise the function docstring is used)
    show_result=True,                               # Show result after function call
    stop_after_tool_call=False,                      # Return the result immediately after the tool call and stop the agent
    tool_hooks=[logger_hook],                       # Hook to run before and after execution
    requires_confirmation=False,                     # Requires user confirmation before execution
    # cache_results=True,                             # Enable caching of results
    # cache_dir="/tmp/agno_cache",                    # Custom cache directory
    # cache_ttl=3600                                  # Cache TTL in seconds (1 hour)
)
def search_web_news(chapter: str, news_num: int=10) -> List[SearchResultNews]:
    """
    使用搜索引擎搜索新闻文字的工具函数

    Args:
        chapter:搜索主题的关键词
        news_num:搜索的数量,不少于20条

    Returns:
        新闻和图片的列表
    """
    bochai_result = []
    bochai_result = search_bochai(chapter, news_num,news=True,images=False)
    # print(f"bochai_result: {bochai_result}")
    searxng_result_general = search_searxng(chapter=chapter, page=1, language="zh-CN", categories="general")
    # searxng_result_images = search_searxng(chapter=chapter, page=1, language="zh-CN", categories="images")

    return [*bochai_result, *searxng_result_general]


def search_bochai(chapter: str, result: int=20,news:bool=True,images:bool=False) -> List[SearchResultNews]:
    """
    使用博查搜索引擎搜索新闻和图片的工具函数

    Args:
        chapter: 搜索主题的关键词
        result: 搜索返回的结果的数量

    Returns:
        新闻和图片的列表
    """
    if not config.BOCHAI_API_URL:
        logger.error("BOCHAI_API_URL未配置。")
        return []
    logger.info(f"正在使用Bochai搜索: {chapter}")
    logger.info(f"Bochai API URL: {config.BOCHAI_API_URL}")

    try:
        request_body = {
            "query": chapter,
            "count": result,
            "freshness": "noLimit",
            "summary": True
        }
        # 构造请求头，加入 Bearer 身份认证
        headers: Dict[str, str] | None = None
        if config.BOCHAI_API_KEY:
            headers = {"Authorization": f"Bearer {config.BOCHAI_API_KEY}"}

        # 发送请求至 Bochai API
        response = _make_api_request(
            config.BOCHAI_API_URL,
            method="POST",
            headers=headers,
            json=request_body,
        )

        logger.info(f"Bochai Body: {request_body}")

        # 解析返回结果
        news_data, image_data = extract_bocah_data(response)
        return [*news_data]
    except Exception as e:
        logger.error(f"Bochai搜索失败: {e}")
        return []


def search_searxng(chapter: str, page: int = 1, language: str = "zh-CN", categories: str = "general") -> List[SearchResultNews|SearchResultImage]:
    """
    Performs a search using the SearXNG Search API.

    Args:
        chapter: The search query chapter.
        page: The page number for pagination,
        language: The language for search results, defaults to zh-CN.
        categories: The search category, either "general" or "images".

    Returns:
        A list of SearchResult objects.
    """
    if categories not in ["general", "images"]:
        logger.warning(f"无效的类别 '{categories}'，默认使用 'general'")
        categories = "general"

    if not config.SEARXNG_API_URL:
        logger.error("SEARXNG_API_URL未配置。")
        return []
    logger.info(f"正在使用SearXNG搜索: {chapter}")
    try:
        request_body = {
            "q": chapter,
            "format": "json",
            "pageno": page,
            "language": language,
            "categories": categories
        }
        response = _make_api_request(
        config.SEARXNG_API_URL, 
        params=request_body
        )
        logger.info(f"SearXNG Body: {request_body}")
        # Adapt the response structure to SearchResult model
        if categories == "general":
            results = [
                SearchResultNews(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    summary=item.get("content", ""),
                )
                for item in response.get("results", [])
            ]
        elif categories == "images":
            results = [
                SearchResultImage(
                    image_src=item.get("img_src", "")
                )
                for item in response.get("results", [])
            ]
        return list(results)
    except Exception as e:
        logger.error(f"SearXNG搜索失败: {e}")
        return []


def parse_image_url(image_url: str) -> Optional[ImageAnalysis]:
    """
    Analyzes an image from a URL using the Vision API.

    Args:
        image_url: The URL of the image to analyze.

    Returns:
        An ImageAnalysis object or None if analysis fails.
    """

    model_config = config.model_config_manager.get_model_config("qwen-vl")
    if not model_config:
        logger.warning("QWEN_VL_API_KEY未设置。跳过图像分析。")
        return None
        
    logger.info(f"正在分析图像: {image_url}")
    # headers = {"Authorization": f"Bearer {model_config.api_key}"}
    try:
        response = _make_api_request(
            url=model_config.url+"/chat/completions",  # type: ignore[attr-defined]
            method="POST", 
            # headers=headers, 
            json={
                "model": model_config.model_name,
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            },
                            {
                                "type": "text",
                                "text": "你是一名专业的图片分析师，擅长解析图片中的内容与文字。 要求： 1.有非文字，则简述图片的内容 2. 图片中没有图像只有文字，则返回`无效图片`"
                            }
                        ]
                    }
                ]
            }
        )
        if response.get("choices", [{}])[0].get("message", {}).get("content", ""):
            return ImageAnalysis(image_src=image_url, description=response.get("choices", [{}])[0].get("message", {}).get("content", ""))
        else:
            return ImageAnalysis(image_src=image_url, description="无效图片")
    except Exception as e:
        logger.error(f"Image analysis for {image_url} failed: {e}")
        return ImageAnalysis(
            image_src=image_url,
            description="无效图片",
        )


def perform_table_reasoning(data_snippets: List[str]) -> List[TableData]:
    """
    Performs reasoning on data snippets to generate tables.
    This is a placeholder for a more complex implementation.

    Args:
        data_snippets: A list of text snippets containing data.

    Returns:
        A list of TableData objects.
    """
    logger.info("Performing table reasoning...")
    # This is a mock implementation. A real implementation would use a powerful
    # model to parse snippets, identify data, and create/extend tables.
    if not data_snippets:
        return []

    # Example: Simple aggregation of numbers found in text
    all_text = " ".join(data_snippets)
    # A real implementation would involve complex NLP and pandas logic
    df = pd.DataFrame({
        "Year": [2023, 2024],
        "Investment (Billion USD)": [685, 910]
    })
    df["YoY Growth (%)"] = df["Investment (Billion USD)"].pct_change() * 100
    
    table_md = df.to_markdown(index=False) or ""
    
    return [
        TableData(
            title="Global AI Investment Growth",
            markdown_content=table_md,
            reasoning_summary="Extracted investment figures and calculated year-over-year growth.",
        )
    ]


def save_report_to_file(report_markdown: str, filename: str = "report.md") -> str:
    """将生成的Markdown报告保存到本地文件。

    Args:
        report_markdown: Markdown格式的报告内容。
        filename: 保存的文件名，默认为 report.md。

    Returns:
        保存成功后返回确认消息。
    """
    logger.info(f"保存报告到文件: {filename}")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_markdown)
        logger.info("报告保存成功")
        # return f"Report saved to {filename}"
        return f"报告保存完成 to {filename}"
    except Exception as e:
        logger.error(f"保存报告文件失败: {e}")
        return f"Failed to save report: {e}"


