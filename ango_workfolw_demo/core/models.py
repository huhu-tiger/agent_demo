"""Data models for the multi-agent report generation system.
多智能体报告生成系统的数据模型。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any






@dataclass
class ImageAnalysis:
    """图片分析结果模型"""
    image_src: str
    description: str = ""
    
    # @property
    # def content(self) -> str:
    #     """获取分析内容"""
    #     if self.choices and len(self.choices) > 0:
    #         choice = self.choices[0]
    #         if 'message' in choice and 'content' in choice['message']:
    #             return choice['message']['content']
    #     return self.description or "无法解析图片内容"


@dataclass
class TableData:
    """表格数据模型"""
    title: str
    markdown_content: str
    reasoning_summary: str = ""


@dataclass
class ReportRequest:
    """报告请求模型"""
    topic: str
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportResponse:
    """报告响应模型"""
    report_markdown: str
    message: str
    execution_time: float
    agent_logs: List[str] = field(default_factory=list) 


from pydantic import BaseModel, Field


class SearchResultNews(BaseModel):
    """新闻搜索结果模型"""
    title: str = Field(..., description="新闻标题")
    url: str = Field(..., description="新闻URL")
    summary: Optional[str] = Field(
        ..., description="Summary of the article if available."
    )


class SearchResultImage(BaseModel):
    """图片搜索结果模型"""
    image_src: str = Field(..., description="图片URL")
    description: Optional[str] = Field(
        default="", description="图片描述"
    )

class search_news_result(BaseModel):
    """表示搜索新闻的结果"""


    search_result_news: List[SearchResultNews] = Field(
        default_factory=list, description="Search result news"
    )


class search_images_result(BaseModel):
    """表示搜索图片的结果"""

    search_result_image: List[SearchResultImage] = Field(
        default_factory=list, description="Search result image"
    )

class ChapterReport(BaseModel):
    # report_markdown: str = Field(
    #     ..., description="Report Content in Markdown format"
    # )
    search_result_image: List[SearchResultImage] = Field(
        ..., description="Search result image"
    )
    search_result_news: List[SearchResultNews] = Field(
        ..., description="Search result news"
    )
    # message: str = Field(
    #     ..., description="reasoning message"
    # )


class Keyword_list(BaseModel):
    keyword_list: List[str] = Field(
        ..., description="Topic list"
    )

if __name__ == "__main__":
    test_ChapterReport=TopicReport(
        report_markdown="# 111",
        search_result_image=[SearchResultImage(image_src="test", description="test")],
        search_result_news=[SearchResultNews(title="test", url="test", summary="test")],
        message="test"
    )
    print(test_ChapterReport)
    print(test_ChapterReport.model_dump_json())
    print(test_ChapterReport.model_dump())

    