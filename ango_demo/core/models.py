"""Data models for the multi-agent report generation system.
多智能体报告生成系统的数据模型。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class SearchResultNews:
    """新闻搜索结果模型"""
    title: str
    url: str
    summary: str


@dataclass
class SearchResultImage:
    """图片搜索结果模型"""
    image_src: str


@dataclass
class ImageAnalysis:
    """图片分析结果模型"""
    image_src: str
    id: str = ""
    object: str = ""
    created: int = 0
    model: str = ""
    choices: List[Dict[str, Any]] = field(default_factory=list)
    description: str = ""
    
    @property
    def content(self) -> str:
        """获取分析内容"""
        if self.choices and len(self.choices) > 0:
            choice = self.choices[0]
            if 'message' in choice and 'content' in choice['message']:
                return choice['message']['content']
        return self.description or "无法解析图片内容"


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