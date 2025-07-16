"""Core components for the multi-agent research report generation system."""

import logging
import os
from typing import Any, Dict, List, Optional

from autogen import (
    Agent,
    AssistantAgent,
    UserProxyAgent,
    GroupChat,
    GroupChatManager,
    config_list_from_json,
)
from pydantic import BaseModel, Field

from .utils import (
    search_bochai,
    search_searxng,
    parse_image_url,
    perform_table_reasoning,
    write_markdown_report,
)

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(agent)s | %(message)s",
)
logger = logging.getLogger(__name__)


# --- Data Models ---
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


# --- Agent Definitions ---
class OrchestratorAgent:
    """
    The main agent responsible for orchestrating the report generation process.
    It decomposes the task, manages other agents, and aggregates the final report.
    """

    def __init__(self, config_list: List[Dict[str, Any]]):
        """Initializes the OrchestratorAgent."""
        self.config_list = config_list
        self.user_proxy = UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
        )

        # Specialist Agents
        self.search_agent_bc = AssistantAgent(
            name="SearchAgent_BC",
            system_message="You are a search specialist. Use the provided search_bochai tool to find relevant news and information.",
            llm_config={"config_list": self._get_llm_config("deepseek-v3")},
        )
        self.search_agent_sx = AssistantAgent(
            name="SearchAgent_SX",
            system_message="You are a search specialist. Use the provided search_searxng tool to find relevant news and information.",
            llm_config={"config_list": self._get_llm_config("deepseek-v3")},
        )
        self.vision_agent = AssistantAgent(
            name="VisionAgent",
            system_message="You are a vision specialist. Use the parse_image_url tool to analyze images and generate captions.",
            llm_config={"config_list": self._get_llm_config("deepseek-r1")},
        )
        self.table_reasoner_agent = AssistantAgent(
            name="TableReasonerAgent",
            system_message="You are a data analysis specialist. Use the perform_table_reasoning tool to analyze data and create Markdown tables.",
            llm_config={"config_list": self._get_llm_config("deepseek-r1")},
        )
        self.report_writer_agent = AssistantAgent(
            name="ReportWriterAgent",
            system_message="You are a professional report writer. Use the provided information to compose a comprehensive Markdown report.",
            llm_config={"config_list": self._get_llm_config("deepseek-r1")},
        )

        # Register tools
        self.user_proxy.register_function(
            function_map={
                "search_bochai": search_bochai,
                "search_searxng": search_searxng,
                "parse_image_url": parse_image_url,
                "perform_table_reasoning": perform_table_reasoning,
                "write_markdown_report": write_markdown_report,
            }
        )

    def _get_llm_config(self, model_name: str) -> List[Dict[str, Any]]:
        """Filters the config list for a specific model."""
        return [config for config in self.config_list if config.get("model") == model_name]

    def run(self, topic: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        Runs the entire report generation workflow.

        Args:
            topic: The main topic for the research report.
            filters: Optional filters for the search (e.g., date range).

        Returns:
            The generated Markdown report as a string.
        """
        groupchat = GroupChat(
            agents=[
                self.user_proxy,
                self.search_agent_bc,
                self.search_agent_sx,
                self.vision_agent,
                self.table_reasoner_agent,
                self.report_writer_agent,
            ],
            messages=[],
            max_round=15,
        )
        
        manager_llm_config = self._get_llm_config("qwen-plus")
        if not manager_llm_config:
            raise ValueError("Configuration for qwen-plus model not found for the manager.")

        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=manager_llm_config[0],
            # The system message defines the high-level workflow
            system_message=(
                "You are the orchestrator. Your job is to manage a team of specialists to produce a research report. "
                f"The topic is: '{topic}'.\n\n"
                "1.  **Search**: First, instruct both `SearchAgent_BC` and `SearchAgent_SX` to search for this topic. "
                "Wait for their results.\n"
                "2.  **Analyze**: Once you have the search results, delegate tasks. "
                "   - Send all image URLs to `VisionAgent` for analysis. "
                "   - Send relevant data snippets to `TableReasonerAgent` to create tables. "
                "3.  **Synthesize**: After receiving the analyses from the Vision and Table agents, "
                "   gather all information (search results, image captions, tables) and pass it to the `ReportWriterAgent`.\n"
                "4.  **Finalize**: Instruct the `ReportWriterAgent` to write the final Markdown report. "
                "Once the report is ready, output it and terminate the process by saying 'TERMINATE'."
            )
        )

        # Initiate the chat
        self.user_proxy.initiate_chat(
            manager,
            message=f"Please generate a research report on the topic: {topic}",
        )

        # The final report should be in the last message from the ReportWriterAgent or the manager
        final_report = "No report generated."
        for msg in reversed(groupchat.messages):
            if msg["name"] == "ReportWriterAgent" and "report.md" in msg["content"]:
                final_report = msg["content"]
                break
        
        return final_report
