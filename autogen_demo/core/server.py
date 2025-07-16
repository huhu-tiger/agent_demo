"""
FastAPI server to expose the multi-agent system functionality.
"""

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from autogen import config_list_from_json
from .agents import OrchestratorAgent

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Research Report Generator",
    description="An API to trigger a multi-agent system for generating research reports.",
    version="1.0.0",
)

logger = logging.getLogger(__name__)

# --- Load LLM Configurations ---
# We expect a OAI_CONFIG_LIST.json file in the root directory
# It should contain configurations for qwen-plus, deepseek-v3, and deepseek-r1
try:
    config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
except ValueError:
    logger.error(
        "OAI_CONFIG_LIST.json not found or is invalid. "
        "Please ensure the file exists and is correctly formatted."
    )
    config_list = []

# --- Initialize the Orchestrator ---
if not config_list:
    raise RuntimeError("LLM configuration is missing. The server cannot start.")

orchestrator = OrchestratorAgent(config_list=config_list)


# --- API Request and Response Models ---
class ReportRequest(BaseModel):
    """Request model for generating a report."""
    topic: str
    filters: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    """Response model containing the generated report."""
    report_markdown: str
    message: str


# --- API Endpoints ---
@app.post("/generate_report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Endpoint to generate a research report.

    This endpoint triggers the OrchestratorAgent to start the multi-agent
    workflow. The process is synchronous and will wait for the report
    to be completed.
    """
    logger.info(f"Received request to generate report for topic: {request.topic}")
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator is not initialized due to missing LLM config.",
        )

    try:
        # The run method is synchronous in this example.
        # For production, you might want to make this an async background task.
        report_content = orchestrator.run(
            topic=request.topic, filters=request.filters
        )
        
        if "No report generated." in report_content:
             return ReportResponse(
                report_markdown=report_content,
                message="Workflow completed, but no definitive report was generated.",
            )

        return ReportResponse(
            report_markdown=report_content,
            message="Report generated successfully.",
        )
    except Exception as e:
        logger.exception(f"An error occurred during report generation for topic: {request.topic}")
        raise HTTPException(
            status_code=500, detail=f"An internal error occurred: {e}"
        )


@app.get("/health")
def health_check():
    """Health check endpoint to verify that the server is running."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    # This allows running the server directly for testing
    # Production deployments should use a proper ASGI server like Gunicorn + Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
