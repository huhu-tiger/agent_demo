"""Utility functions for the multi-agent report generation system.
多智能体报告生成系统的工具函数。
"""

import logging
import os
from typing import Any, Dict, List, Optional
import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import SearchResultNews, SearchResultImage, ImageAnalysis, TableData
from . import config
from .logging_config import get_logger

# 获取日志记录器
logger = get_logger(__name__, "Utils")
logger.info(f"Utils logger initialized")
# --- API Configuration is now managed in core/config.py ---


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
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
        if "images" in response["data"] and "value" in response["data"]["images"]:
            image_data = response["data"]["images"]["value"]
            image_data_result = [
                SearchResultImage(
                    image_src=item.get("contentUrl", "")
                )
                for item in image_data
            ]
    
    return news_data_result, image_data_result 
def search_bochai(topic: str, count: int = 5) -> List[SearchResultNews|SearchResultImage]:
    """
    Performs a search using the Bochai AI Search API.

    Args:
        topic: The search query topic.
        count: The number of results to return.

    Returns:
        A list of SearchResult objects.
    """
    if not config.BOCHAI_URL:
        logger.error("BOCHAI_API_URL未配置。")
        return []
    logger.info(f"正在使用Bochai搜索: {topic}")
    logger.info(f"Bochai API URL: {config.BOCHAI_URL}")

    try:
        request_body = {
            "query": topic,
            "count": count,
            "freshness": "noLimit",
            "summary": True
        }
        response = _make_api_request(
            config.BOCHAI_URL, 
            method="POST", 
            json=request_body
        )
        logger.info(f"Bochai Body: {request_body}")
        news_data, image_data = extract_bocah_data(response)
        return [*news_data, *image_data]
    except Exception as e:
        logger.error(f"Bochai搜索失败: {e}")
        return []


def search_searxng(topic: str, page: int = 1, language: str = "zh-CN", categories: str = "general") -> List[SearchResultNews|SearchResultImage]:
    """
    Performs a search using the SearXNG Search API.

    Args:
        topic: The search query topic.
        page: The page number for pagination.
        language: The language for search results, defaults to zh-CN.
        categories: The search category, either "general" or "images".

    Returns:
        A list of SearchResult objects.
    """
    if categories not in ["general", "images"]:
        logger.warning(f"无效的类别 '{categories}'，默认使用 'general'")
        categories = "general"

    if not config.SEARXNG_URL:
        logger.error("SEARXNG_API_URL未配置。")
        return []
    logger.info(f"正在使用SearXNG搜索: {topic}")
    try:
        request_body = {
            "q": topic,
            "format": "json",
            "pageno": page,
            "language": language,
            "categories": categories
        }
        response = _make_api_request(
        config.SEARXNG_URL, 
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
        return results
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
    if not config.VISION_URL:
        logger.error("VISION_API_URL未配置。跳过图像分析。")
        return None
    if not config.QWEN_TOKEN:
        logger.warning("QWEN_PLUS_TOKEN未设置。跳过图像分析。")
        return None
        
    logger.info(f"正在分析图像: {image_url}")
    headers = {"Authorization": f"Bearer {config.QWEN_TOKEN}"}
    try:
        response = _make_api_request(
            config.VISION_URL, 
            method="POST", 
            headers=headers, 
            json={
                "model": "Qwen2.5-VL-7B-Instruct",
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
                                "text": "请分析这张图片并提供详细描述"
                            }
                        ]
                    }
                ]
            }
        )
        return ImageAnalysis(original_url=image_url, **response)
    except Exception as e:
        logger.error(f"Image analysis for {image_url} failed: {e}")
        return ImageAnalysis(
            original_url=image_url,
            caption=f"Image at {image_url} (analysis failed)",
            tags=["error"],
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


def write_markdown_report(
    topic: str,
    search_results: List[SearchResultNews|SearchResultImage],
    image_analyses: List[ImageAnalysis],
    tables: List[TableData],
) -> str:
    """
    Composes the final Markdown report from all gathered assets.

    Args:
        topic: The central topic of the report.
        search_results: A list of search results.
        image_analyses: A list of image analysis results.
        tables: A list of generated tables.

    Returns:
        A string containing the final Markdown report.
    """
    logger.info("Writing final Markdown report...")
    report_parts = [f"# Research Report: {topic}\n"]

    report_parts.append("## 1. Key Findings from Web Search\n")
    for i, res in enumerate(search_results, 1):
        report_parts.append(f"### {res.title}")
        report_parts.append(f"> {res.snippet}")
        report_parts.append(f"\nSource: [{res.url}]({res.url})\n")

    if image_analyses:
        report_parts.append("## 2. Image Analysis\n")
        for img in image_analyses:
            report_parts.append(f"![{img.caption}]({img.original_url})")
            report_parts.append(f"*Fig. {img.tags[0] if img.tags else 'Analyzed Image'}: {img.caption}*")
            report_parts.append("\n")

    if tables:
        report_parts.append("## 3. Data and Tables\n")
        for table in tables:
            report_parts.append(f"### {table.title}")
            report_parts.append(table.markdown_content)
            report_parts.append(f"\n*{table.reasoning_summary}*\n")
            
    report_parts.append("\n---\n*This report was auto-generated by a multi-agent system.*")
    
    return "\n".join(report_parts)


