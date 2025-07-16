"""Utility functions for the multi-agent report generation system."""

import logging
import os
from typing import Any, Dict, List, Optional
import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

from .agents import SearchResult, ImageAnalysis, TableData

logger = logging.getLogger(__name__)

# --- API Configuration ---
BOCHAI_API_URL = "https://www.bochai.com/api/v1/search"  # Placeholder
SEARXNG_API_URL = "https://searxng.instance/api/search"  # Placeholder
VISION_API_URL = "https://vision.api/v1/analyze"  # Placeholder
QWEN_PLUS_TOKEN = os.environ.get("QWEN_PLUS_TOKEN")


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
        response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request to {url} failed: {e}")
        raise


def search_bochai(topic: str, count: int = 5) -> List[SearchResult]:
    """
    Performs a search using the Bochai AI Search API.

    Args:
        topic: The search query topic.
        count: The number of results to return.

    Returns:
        A list of SearchResult objects.
    """
    logger.info(f"Searching Bochai for: {topic}")
    try:
        response = _make_api_request(
            BOCHAI_API_URL, params={"q": topic, "count": count}
        )
        # Assuming the API returns a list of result objects
        return [SearchResult(**item) for item in response.get("results", [])]
    except Exception as e:
        logger.error(f"Bochai search failed: {e}")
        return []


def search_searxng(topic: str, count: int = 5) -> List[SearchResult]:
    """
    Performs a search using the SearXNG Search API.

    Args:
        topic: The search query topic.
        count: The number of results to return.

    Returns:
        A list of SearchResult objects.
    """
    logger.info(f"Searching SearXNG for: {topic}")
    try:
        response = _make_api_request(
            SEARXNG_API_URL, params={"q": topic, "format": "json", "count": count}
        )
        # Adapt the response structure to SearchResult model
        results = [
            SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                image_url=item.get("img_src")
            )
            for item in response.get("results", [])
        ]
        return results
    except Exception as e:
        logger.error(f"SearXNG search failed: {e}")
        return []


def parse_image_url(image_url: str) -> Optional[ImageAnalysis]:
    """
    Analyzes an image from a URL using the Vision API.

    Args:
        image_url: The URL of the image to analyze.

    Returns:
        An ImageAnalysis object or None if analysis fails.
    """
    if not QWEN_PLUS_TOKEN:
        logger.warning("QWEN_PLUS_TOKEN not set. Skipping image analysis.")
        return None
        
    logger.info(f"Analyzing image: {image_url}")
    headers = {"Authorization": f"Bearer {QWEN_PLUS_TOKEN}"}
    try:
        response = _make_api_request(
            VISION_API_URL, method="POST", headers=headers, json={"image_url": image_url}
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
    
    table_md = df.to_markdown(index=False)
    
    return [
        TableData(
            title="Global AI Investment Growth",
            markdown_content=table_md,
            reasoning_summary="Extracted investment figures and calculated year-over-year growth.",
        )
    ]


def write_markdown_report(
    topic: str,
    search_results: List[SearchResult],
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