"""
Pydantic models for the multi-agent research report generation system.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Represents a single search result item."""
    title: str = Field(description="Title of the news article or report.")
    url: str = Field(description="Direct URL to the content.")
    snippet: str = Field(description="A brief summary or snippet of the content.")
    image_url: Optional[str] = Field(None, description="URL of a relevant image.")


class ImageAnalysis(BaseModel):
    """Represents the analysis of an image."""
    original_url: str = Field(description="The original URL of the image.")
    caption: str = Field(description="A generated caption describing the image.")
    tags: List[str] = Field(default_factory=list, description="Relevant tags for the image.")


class TableData(BaseModel):
    """Represents a data table, likely for financial or statistical data."""
    title: str = Field(description="Title of the table.")
    markdown_content: str = Field(description="The table formatted in Markdown.")
    reasoning_summary: str = Field(description="Summary of how the table data was inferred or calculated.") 