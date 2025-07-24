"""Utility functions for the multi-agent report generation system.
多智能体报告生成系统的工具函数。
"""

import logging
import os
from urllib.parse import urljoin
from typing import Any, Dict, List, Optional, Sequence
import requests
import pandas as pd
import asyncio
import aiohttp

from .models import SearchResultNews, SearchResultImage, ImageAnalysis, TableData
from .logging_config import get_logger
from . import config
# 获取日志记录器
logger = get_logger(__name__, "Utils")
# logger.info(f"Utils logger initialized")
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
def search_bochai(chapter: str, count: int = 20) -> List[SearchResultNews|SearchResultImage]:
    """
    Performs a search using the Bochai AI Search API.

    Args:
        chapter: The search query chapter.
        count: The number of results to return.

    Returns:
        A list of SearchResult objects.
    """
    if not config.BOCHAI_API_URL:
        logger.error("BOCHAI_API_URL未配置。")
        return []
    logger.info(f"正在使用Bochai搜索: {chapter}")
    logger.info(f"Bochai API URL: {config.BOCHAI_API_URL}")

    try:
        request_body = {
            "query": chapter,
            "count": count,
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
        return [*news_data, *image_data]
    except Exception as e:
        logger.error(f"Bochai搜索失败: {e}")
        return []


def _sync_crawl_url(url: str) -> Optional[str]:
    """
    同步爬取URL内容，兼容原有crawl_url逻辑。
    """
    try:
        response = requests.get("https://r.jina.ai/" + url, timeout=60)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"crawl_url请求失败，URL: {url}，错误: {e}")
        return None

async def _async_crawl_url(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get("https://r.jina.ai/" + url, timeout=60) as response:
            if response.status == 200:
                content = await response.text()
                print(444444,content)
                return content
            else:
                logger.error(f"crawl_url请求失败，URL: {url}，状态码: {response.status}")
                return None
    except Exception as e:
        logger.error(f"crawl_url请求失败，URL: {url}，错误: {e}")
        return None

async def _batch_crawl_urls(urls: list[str]) -> list[Optional[str]]:
    async with aiohttp.ClientSession() as session:
        tasks = [_async_crawl_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def search_searxng_news(keyword: str ) -> List[SearchResultNews]:
    """
    Performs a search using the SearXNG Search API.
    Args:
        keyword: The search query keyword.
    Returns:
        A list of SearchResult objects.
    """
    page: int = 1
    language: str = "zh-CN"
    categories: str = "general"
    if categories not in ["general", "images"]:
        logger.warning(f"无效的类别 '{categories}'，默认使用 'general'")
        categories = "general"
    if not config.SEARXNG_API_URL:
        logger.error("SEARXNG_API_URL未配置。")
        return []
    logger.info(f"正在使用SearXNG搜索: {keyword}")
    try:
        request_body = {
            "q": keyword,
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
        items = response.get("results", [])

        skip_domains = ["zhihu.com"]  # 这里填你要跳过的域名
        urls = []
        skip_flags = []
        for item in items:
            url = item.get("url", "")
            if any(domain in url for domain in skip_domains):
                urls.append(None)  # 占位，后面直接用summary
                skip_flags.append(True)
            else:
                urls.append(url)
                skip_flags.append(False)
        # 并发爬取内容（只爬取未跳过的url）
        try:
            crawl_urls = [u for u in urls if u]
            crawl_contents = asyncio.run(_batch_crawl_urls(crawl_urls))
        except Exception as e:
            logger.error(f"批量爬取失败，降级为同步: {e}")
            crawl_contents = [_sync_crawl_url(u) for u in crawl_urls]
        # 合并内容，跳过的用None
        contents = []
        crawl_idx = 0
        for is_skip, url in zip(skip_flags, urls):
            if is_skip:
                contents.append(None)
            else:
                contents.append(crawl_contents[crawl_idx])
                crawl_idx += 1
        results = []
        for item, content, is_skip in zip(items, contents, skip_flags):
            if is_skip:
                logger.info(f"跳过域名: {item.get('url', '')}，content将使用原始summary: {item.get('content', '')}")
            results.append(
                SearchResultNews(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", "") if is_skip or not content else content,
                )
            )
        logger.info(f"SearXNG搜索结果: {results}")
        return results
    except Exception as e:
        logger.error(f"SearXNG搜索失败: {e}")
        return []

def search_searxng_images(keyword: str) -> List[SearchResultImage]:
    """
    Performs a search using the SearXNG Search API.

    Args:
        keyword: The search query keyword.

    Returns:
        A list of SearchResult objects.
    """
    page: int = 2
    language: str = "zh-CN"
    categories: str = "images"

    if categories not in ["general", "images"]:
        logger.warning(f"无效的类别 '{categories}'，默认使用 'general'")
        categories = "general"

    if not config.SEARXNG_API_URL:
        logger.error("SEARXNG_API_URL未配置。")
        return []
    logger.info(f"正在使用SearXNG搜索: {keyword}")
    try:
        request_body = {
            "q": keyword,
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

        results = []
        for item in response.get("results", []):
            desc = parse_image_url(item.get("img_src", ""))
            if desc:
                results.append(SearchResultImage(image_src=item.get("img_src", ""), description=desc.description))

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
    logger.info(f"model_config: {model_config}")
    if not model_config:
        logger.warning("QWEN_VL_API_KEY未设置。跳过图像分析。")
        return None
        
    logger.info(f"正在分析图像: {image_url}")
    # headers = {"Authorization": f"Bearer {model_config.api_key}"}
    try:
        response = _make_api_request(
            urljoin(model_config.base_url, "/chat/completions"),  # type: ignore[attr-defined]
            method="POST", 
            # headers=headers, 
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
                                "text": "你是一名专业的图片分析师，擅长解析图片中的内容与文字。 要求： 1.有非文字，则简述图片的内容 2. 图片中没有图像只有文字，则返回`无效图片`"
                            }
                        ]
                    }
                ]
            }
        )
     
        msg = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        if msg == "无效图片" or msg == "" or "无效图片" in msg :
            return None
        else:
            return ImageAnalysis(image_src=image_url, description=msg)
    except Exception as e:
        logger.error(f"Image analysis for {image_url} failed: {e}")
        return None


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


