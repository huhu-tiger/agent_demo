# -*- coding: utf-8 -*-
"""
LangGraph Gradio Demo 配置文件
"""

import os
import logging
from typing import Optional, Dict, Any

# 模型配置
model = "Qwen3-235B-A22B-Instruct-2507"
base_url = "http://39.155.179.5:8002/v1"
api_key = "xxx"

# DeepSeek V3 模型配置
v3_model = "deepseek-v3"
v3_base_url = "http://61.49.53.5:30002/v1"
v3_api_key = ""

# ModelScope 通义千问配置
modelscope_qwen_model = "qwen-plus-latest"
modelscope_qwen_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
modelscope_qwen_api_key = "sk-b5e591f6a4354b34bf34b26afc20969e"

def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(f"{log_dir}/langgraph_gradio_demo.log", encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    
    return logging.getLogger(__name__)

# 初始化日志
logger = setup_logging()

class ModelConfig:
    """模型配置类"""
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        model_provider: str = "openai",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        初始化模型配置
        
        Args:
            model_name: 聊天模型名称
            model_provider: 聊天模型提供商
            base_url: API基础URL
            api_key: API密钥
            temperature: 温度参数
            max_tokens: 最大token数
        """
        self.model_name = model_name
        self.model_provider = model_provider
        self.base_url = base_url
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        config = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # 设置API密钥
        if self.api_key:
            config["api_key"] = self.api_key
        
        # 设置基础URL（如果提供）
        if self.base_url:
            config["base_url"] = self.base_url
        
        return config

# 预设模型配置
DEFAULT_MODELS = {
    "Qwen3-235B": ModelConfig(
        model_name="Qwen3-235B-A22B-Instruct-2507",
        model_provider="openai",
        base_url="http://39.155.179.5:8002/v1",
        api_key="xxx",
        temperature=0.7,
        max_tokens=4096
    ),
    "DeepSeek-V3": ModelConfig(
        model_name="deepseek-v3",
        model_provider="openai",
        base_url="http://61.49.53.5:30002/v1",
        api_key="",
        temperature=0.7,
        max_tokens=4096
    ),
    "ModelScope-Qwen": ModelConfig(
        model_name="qwen-plus-latest",
        model_provider="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key="sk-b5e591f6a4354b34bf34b26afc20969e",
        temperature=0.7,
        max_tokens=4096
    )
}