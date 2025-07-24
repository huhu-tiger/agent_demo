"""
Pydantic models for the multi-agent research report generation system.
多智能体研究报告生成系统的 Pydantic 数据模型。
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchResultNews(BaseModel):
    """
    Represents a single search result item.
    """
    title: str = Field(description="标题")
    url: str = Field(description="访问链接")
    content: Optional[str] = Field(None, description="内容")



class search_news_result(BaseModel):
    """表示搜索新闻的结果"""
    search_result_news: List[SearchResultNews] = Field(
        default_factory=list, description="新闻列表"
    )

class SearchResultImage(BaseModel):
    """
    Represents a single search result item.
    表示单个搜索结果项。
    """
    image_src: str = Field(description="图片访问链接")


class ImageAnalysis(BaseModel):
    """
    Represents the analysis of an image.
    表示对图像的分析结果。
    """
    image_src: str = Field(description="图像的原始URL")
    description: str = Field(description="描述图像的文本")
    # tags: List[str] = Field(default_factory=list, description="Relevant tags for the image. 图像的相关标签。")


class TableData(BaseModel):
    """
    Represents a data table, likely for financial or statistical data.
    表示数据表格，通常用于财务或统计数据。
    """
    title: str = Field(description="Title of the table. 表格的标题。")
    markdown_content: str = Field(description="The table formatted in Markdown. 使用Markdown格式的表格内容。")
    reasoning_summary: str = Field(description="Summary of how the table data was inferred or calculated. 表格数据如何推断或计算的摘要说明。") 