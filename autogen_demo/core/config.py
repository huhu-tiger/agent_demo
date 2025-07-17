"""
Configuration loader for the multi-agent system.

This module loads environment variables from a .env file, performs necessary
substitutions, and makes them available as Python variables or sets them
back into the environment for other libraries like autogen to use.
"""
from dotenv import load_dotenv
import os
import string
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
# Load environment variables from .env file
load_dotenv()

# 设置日志
logger = logging.getLogger(__name__)



class ModelConfigManager:
    """
    模型配置管理器
    """
    def __init__(self):
        self.models: Dict[str, OpenAIChatCompletionClient] = {}
        self._load_model_configs()

    def _load_model_configs(self) -> None:
        """
        从环境变量加载所有模型配置
        """
        # Qwen Plus 配置
        if os.getenv("QWEN_PLUS_API_KEY"):
            self.models["qwen-plus"] = OpenAIChatCompletionClient(
                model=os.getenv("QWEN_PLUS_MODEL", "qwen-plus-latest"),
                base_url=os.getenv("QWEN_PLUS_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                api_key=os.getenv("QWEN_PLUS_API_KEY") or "",
                model_info={
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": ModelFamily.UNKNOWN,
                    "structured_output": True,
                },
            )
            logger.info("已加载 Qwen Plus 模型配置")

        # qwen-235B-A22B
        if os.getenv("QWEN_MOE_API_KEY"):
            self.models["Qwen3-235B"] = OpenAIChatCompletionClient(
                model=os.getenv("QWEN_MOE_MODEL", "Qwen3-235B"),
                base_url=os.getenv("QWEN_MOE_BASE_URL",""),
                api_key=os.getenv("QWEN_MOE_API_KEY") or "",
                model_info={
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": ModelFamily.UNKNOWN,
                    "structured_output": True,
                },
            )
            logger.info("已加载 Qwen Plus 模型配置")
        # Qwen VL 配置
        if os.getenv("QWEN_VL_API_KEY"):
            self.models["qwen-vl"] = OpenAIChatCompletionClient(
                model=os.getenv("QWEN_VL_MODEL", "Qwen2.5-VL-7B-Instruct"),
                base_url=os.getenv("QWEN_VL_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                api_key=os.getenv("QWEN_VL_API_KEY") or "",
                model_info={
                    "vision": True,
                    "function_calling": False,
                    "json_output": True,
                    "family": ModelFamily.UNKNOWN,
                    "structured_output": True,
                },
            )
            logger.info("已加载 Qwen Plus 模型配置")
        # DeepSeek V3
        if os.getenv("DEEPSEEK_V3_API_KEY"):
            self.models["deepseek-v3"] = OpenAIChatCompletionClient(
                model=os.getenv("DEEPSEEK_V3_MODEL", "deepseek-v3"),
                base_url=os.getenv("DEEPSEEK_V3_BASE_URL", "http://61.49.53.5:30002/v1"),
                api_key=os.getenv("DEEPSEEK_V3_API_KEY") or "",
                model_info={
                    "vision": False,
                    "function_calling": False,
                    "json_output": True,
                    "family": ModelFamily.UNKNOWN,
                    "structured_output": True,
                },
            )
            logger.info("已加载 DeepSeek V3 模型配置")

        # DeepSeek R1
        if os.getenv("DEEPSEEK_R1_API_KEY"):
            self.models["deepseek-r1"] = OpenAIChatCompletionClient(
                model=os.getenv("DEEPSEEK_R1_MODEL", "deepseek-r1"),
                base_url=os.getenv("DEEPSEEK_R1_BASE_URL", "http://61.49.53.5:30001/v1"),
                api_key=os.getenv("DEEPSEEK_R1_API_KEY") or "",
                model_info={
                    "vision": False,
                    "function_calling": False,
                    "json_output": True,
                    "family": ModelFamily.R1,
                    "structured_output": True,
                },
            )
            logger.info("已加载 DeepSeek R1 模型配置")


    def get_model_config(self, model_name: str) -> Optional[OpenAIChatCompletionClient]:
        """
        指定模型的配置
        """
        return self.models.get(model_name)

    def get_available_models(self) -> List[str]:
        """
        可用的模型名称
        """
        return list(self.models.keys())

    def get_default_model(self) -> Optional[str]:
        """
        取默认模型名称
        """
        default_model = os.getenv("DEFAULT_MODEL", "qwen-plus")
        if default_model in self.models:
            return default_model
        elif self.models:
            return list(self.models.keys())[0]
        return None


# 创建全局模型配置管理器实例
model_config_manager = ModelConfigManager()

# --- API Configurations ---
BOCHAI_API_URL = os.getenv("BOCHAI_API_URL")
BOCHAI_API_KEY = os.getenv("BOCHAI_API_KEY")

SEARXNG_API_URL = os.getenv("SEARXNG_API_URL")

VISION_API_URL = os.getenv("VISION_API_URL")

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- 系统配置 ---
DEFAULT_MODEL = model_config_manager.get_default_model()
MODEL_SELECTION_STRATEGY = os.getenv("MODEL_SELECTION_STRATEGY", "cost_optimized")
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# 打印配置信息
logger.info(f"已加载 {len(model_config_manager.models)} 个模型配置")
logger.info(f"默认模型: {DEFAULT_MODEL}")
logger.info(f"可用模型: {model_config_manager.get_available_models()}")
logger.info(f"日志级别: {LOG_LEVEL}")

