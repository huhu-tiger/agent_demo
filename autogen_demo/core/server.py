"""
FastAPI server to expose the multi-agent system functionality.
FastAPI 服务器，用于暴露多智能体系统功能。
"""

import os
import logging
import json
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import dotenv

# 加载.env文件中的环境变量
dotenv.load_dotenv()

from .agents import OrchestratorAgent
from . import config  # Load environment variables from .env
from .logging_config import setup_logging, get_logger

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Research Report Generator",
    description="An API to trigger a multi-agent system for generating research reports.",
    version="1.0.0",
)

# 设置日志
setup_logging(log_to_file=True)  # 确保日志写入文件
logger = get_logger(__name__, "Server")
logger.info("服务器启动中...")

# --- Load LLM Configurations ---
# We expect the OAI_CONFIG_LIST environment variable to be set, pointing to the config file.
try:
    # 从环境变量中加载 JSON 格式的配置列表
    try:
        # 尝试从环境变量中读取OAI_CONFIG_LIST
        oai_config_str = os.environ.get("OAI_CONFIG_LIST")
        if oai_config_str:
            # 如果环境变量存在，尝试解析JSON
            config_list = json.loads(oai_config_str)
            logger.info("从环境变量OAI_CONFIG_LIST成功加载配置")
        else:
            # 如果环境变量不存在，设置为None
            logger.warning("环境变量OAI_CONFIG_LIST未设置")
            config_list = None
    except json.JSONDecodeError as e:
        logger.warning(f"无法解析OAI_CONFIG_LIST环境变量中的JSON: {e}")
        config_list = None
    
    # 如果配置列表为空或需要修改，可以手动创建
    if not config_list:
        logger.info("创建手动配置列表")
        # 为模型添加价格信息和其他必要的配置
        enhanced_config = []
        
        # 添加 qwen-plus 配置
        qwen_config = {
            "model": "qwen-plus",
            "api_key": os.environ.get("QWEN_PLUS_API_KEY", ""),
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_type": "open_ai",
            "price": [0.001, 0.002]  # 示例价格 [prompt_price_per_1k, completion_token_price_per_1k]
        }
        enhanced_config.append(qwen_config)
        
        # 添加 deepseek-v3 配置
        deepseek_v3_config = {
            "model": "deepseek-v3",
            "api_key": os.environ.get("DEEPSEEK_V3_API_KEY", ""),
            "base_url": "http://61.49.53.5:30002/v1",
            "api_type": "open_ai",
            "price": [0.001, 0.002]  # 示例价格
        }
        enhanced_config.append(deepseek_v3_config)
        
        # 添加 deepseek-r1 配置
        deepseek_r1_config = {
            "model": "deepseek-r1",
            "api_key": os.environ.get("DEEPSEEK_R1_API_KEY", ""),
            "base_url": "http://61.49.53.5:30001/v1",
            "api_type": "open_ai",
            "price": [0.001, 0.002]  # 示例价格
        }
        enhanced_config.append(deepseek_r1_config)
        
        # 使用增强的配置
        config_list = enhanced_config
        
        # 更新环境变量以便其他组件使用
        os.environ["OAI_CONFIG_LIST"] = json.dumps(config_list)
    
    logger.info(f"加载了 {len(config_list)} 个 LLM 配置")
    logger.debug(f"配置列表: {json.dumps(config_list, indent=2)}")
except ValueError as e:
    logger.error(
        f"OAI_CONFIG_LIST 环境变量未设置或无效: {str(e)}. "
        "请确保它包含有效的 JSON 配置。"
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
    logger.info(f"收到生成报告请求，主题: {request.topic}")
    if not orchestrator:
        logger.error("协调器未初始化，缺少LLM配置")
        raise HTTPException(
            status_code=503,
            detail="Orchestrator is not initialized due to missing LLM config.",
        )

    try:
        # The run method is synchronous in this example.
        # For production, you might want to make this an async background task.
        logger.info(f"开始为主题 '{request.topic}' 生成报告...")
        start_time = time.time()
        report_content = orchestrator.run(
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
            )

        logger.info(f"成功生成报告，长度: {len(report_content)} 字符")
        return ReportResponse(
            report_markdown=report_content,
            message="Report generated successfully.",
        )
    except Exception as e:
        logger.exception(f"报告生成过程中发生错误，主题: {request.topic}")
        raise HTTPException(
            status_code=500, detail=f"An internal error occurred: {e}"
        )


@app.get("/health")
def health_check():
    """Health check endpoint to verify that the server is running."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    # 添加启动信息日志
    logger.info("=== 多智能体研究报告生成系统服务器 ===")
    logger.info(f"启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"配置的模型数量: {len(config_list)}")
    logger.info(f"服务器将在 0.0.0.0:8000 上运行")
    
    # This allows running the server directly for testing
    # Production deployments should use a proper ASGI server like Gunicorn + Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
