"""
FastAPI server to expose the multi-agent system functionality.
FastAPI 服务器，用于暴露多智能体系统功能。
"""

import os
import logging
import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import dotenv

# 加载.env文件中的环境变量
dotenv.load_dotenv()
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .agents import OrchestratorAgent
from . import config  # Load environment variables from .env
from .logging_config import setup_logging, get_logger
from .config import model_config_manager

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Research Report Generator",
    description="An API to trigger a multi-agent system for generating research reports.",
    version="10.0",
)

# 添加CORS中间件，支持前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置日志
setup_logging(log_to_file=True)  # 确保日志写入文件
logger = get_logger(__name__, "Server")
logger.info("服务器启动中...")

# --- Load LLM Configurations ---
# We expect the OAI_CONFIG_LIST environment variable to be set, pointing to the config file.


orchestrator = OrchestratorAgent(config_list=model_config_manager.models)


# --- API Request and Response Models ---
class ReportRequest(BaseModel):
    """Request model for generating a report."""
    topic: str
    filters: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    """Response model containing the generated report."""
    report_markdown: str
    message: str
    execution_time: float
    agent_logs: List[str] = []


class AgentLogResponse(BaseModel):
    """Response model for agent logs."""
    logs: List[str]
    status: str


# --- API Endpoints ---
@app.post("/generate_report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Endpoint to generate a research report.

    This endpoint triggers the OrchestratorAgent to start the multi-agent
    workflow. The process is synchronous and will wait for the report
    to be completed.
    """
    logger.info(f"收到生成报告请求，主题: {request.topic}")
    if not orchestrator:
        logger.error("协调器未初始化，缺少LLM配置")
        raise HTTPException(
            status_code=503,
            detail="Orchestrator is not initialized due to missing LLM config.",
        )

    try:
        # 记录开始时间
        logger.info(f"开始为主题 '{request.topic}' 生成报告...")
        start_time = time.time()
        
        # 调用orchestrator.run()并await结果
        report_content = await orchestrator.run(
            topic=request.topic, filters=request.filters
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        logger.info(f"报告生成完成，用时: {execution_time:.2f}秒")
        
        if "No report generated." in report_content:
            logger.warning(f"工作流完成，但未生成明确的报告")
            return ReportResponse(
                report_markdown=report_content,
                message="Workflow completed, but no definitive report was generated.",
                execution_time=execution_time,
                agent_logs=[]
            )

        logger.info(f"成功生成报告，长度: {len(report_content)} 字符")
        return ReportResponse(
            report_markdown=report_content,
            message="Report generated successfully.",
            execution_time=execution_time,
            agent_logs=[]
        )
    except Exception as e:
        logger.exception(f"报告生成过程中发生错误，主题: {request.topic}")
        raise HTTPException(
            status_code=500, detail=f"An internal error occurred: {e}"
        )


@app.get("/agent_logs", response_model=AgentLogResponse)
async def get_agent_logs():
    """
    获取智能体执行日志，用于前端右侧对话框显示
    """
    try:
        # 这里可以从日志文件或内存中获取最新的智能体日志
        # 暂时返回模拟数据
        logs = [
            "PlanningAgent: 开始分析主题...",
            "SearchAgent_BC: 正在使用博查API搜索相关信息...",
            "SearchAgent_SX: 正在使用SearXNG搜索图片...",
            "VisionAgent: 正在分析图片内容...",
            "TableReasonerAgent: 正在处理数据并生成表格...",
            "ReportWriterAgent: 正在整合信息并生成最终报告..."
        ]
        
        return AgentLogResponse(
            logs=logs,
            status="success"
        )
    except Exception as e:
        logger.error(f"获取智能体日志失败: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get agent logs: {e}"
        )


@app.get("/health")
def health_check():
    """Health check endpoint to verify that the server is running."""
    return {"status": "ok"}


@app.get("/models")
def get_available_models():
    """
    模型列表
    """
    return {
        "available_models": model_config_manager.get_available_models(),
        "default_model": model_config_manager.get_default_model()
    }


if __name__ == "__main__":
    import uvicorn

    # 添加启动信息日志
    logger.info("=== 多智能体研究报告生成系统服务器 ===")
    logger.info(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"配置的模型数量: {len(model_config_manager.models)}")
    logger.info(f"服务器将在 0.0.0.0:8000 上运行")
    
    # This allows running the server directly for testing
    # Production deployments should use a proper ASGI server like Gunicorn + Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
