#!/usr/bin/env python3
"""
模型配置文件
提供各种预设的模型配置
"""

import os
from typing import Dict, Any
from langgraph_demo.study.langgraph_inmemory_demo import ModelConfig


class ModelConfigs:
    """模型配置集合"""
    
    @staticmethod
    def get_openai_configs() -> Dict[str, ModelConfig]:
        """获取OpenAI相关配置"""
        api_key = os.environ.get("OPENAI_API_KEY")
        
        return {
            "gpt-4o-mini": ModelConfig(
                model_name="gpt-4o-mini",
                model_provider="openai",
                api_key=api_key,
                embedding_model="text-embedding-3-small",
                embedding_provider="openai"
            ),
            "gpt-4o": ModelConfig(
                model_name="gpt-4o",
                model_provider="openai",
                api_key=api_key,
                embedding_model="text-embedding-3-small",
                embedding_provider="openai"
            ),
            "gpt-3.5-turbo": ModelConfig(
                model_name="gpt-3.5-turbo",
                model_provider="openai",
                api_key=api_key,
                embedding_model="text-embedding-ada-002",
                embedding_provider="openai"
            ),
            "gpt-4-turbo": ModelConfig(
                model_name="gpt-4-turbo-preview",
                model_provider="openai",
                api_key=api_key,
                embedding_model="text-embedding-3-small",
                embedding_provider="openai"
            )
        }
    
    @staticmethod
    def get_azure_configs() -> Dict[str, ModelConfig]:
        """获取Azure OpenAI配置"""
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        
        if not api_key or not endpoint:
            print("⚠️  请设置 AZURE_OPENAI_API_KEY 和 AZURE_OPENAI_ENDPOINT 环境变量")
            return {}
        
        return {
            "azure-gpt-4": ModelConfig(
                model_name="gpt-4",
                model_provider="azure",
                base_url=endpoint,
                api_key=api_key,
                embedding_model="text-embedding-ada-002",
                embedding_provider="azure",
                embedding_base_url=endpoint
            ),
            "azure-gpt-35-turbo": ModelConfig(
                model_name="gpt-35-turbo",
                model_provider="azure",
                base_url=endpoint,
                api_key=api_key,
                embedding_model="text-embedding-ada-002",
                embedding_provider="azure",
                embedding_base_url=endpoint
            )
        }
    
    @staticmethod
    def get_anthropic_configs() -> Dict[str, ModelConfig]:
        """获取Anthropic配置"""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not api_key:
            print("⚠️  请设置 ANTHROPIC_API_KEY 环境变量")
            return {}
        
        return {
            "claude-3-opus": ModelConfig(
                model_name="claude-3-opus-20240229",
                model_provider="anthropic",
                api_key=api_key,
                embedding_model="text-embedding-3-small",
                embedding_provider="openai"  # Anthropic没有嵌入模型，使用OpenAI
            ),
            "claude-3-sonnet": ModelConfig(
                model_name="claude-3-sonnet-20240229",
                model_provider="anthropic",
                api_key=api_key,
                embedding_model="text-embedding-3-small",
                embedding_provider="openai"
            ),
            "claude-3-haiku": ModelConfig(
                model_name="claude-3-haiku-20240307",
                model_provider="anthropic",
                api_key=api_key,
                embedding_model="text-embedding-3-small",
                embedding_provider="openai"
            )
        }
    
    @staticmethod
    def get_local_configs() -> Dict[str, ModelConfig]:
        """获取本地模型配置"""
        return {
            "ollama-llama2": ModelConfig(
                model_name="llama2",
                model_provider="ollama",
                base_url="http://localhost:11434",
                embedding_model="nomic-embed-text",
                embedding_provider="ollama",
                embedding_base_url="http://localhost:11434"
            ),
            "ollama-mistral": ModelConfig(
                model_name="mistral",
                model_provider="ollama",
                base_url="http://localhost:11434",
                embedding_model="nomic-embed-text",
                embedding_provider="ollama",
                embedding_base_url="http://localhost:11434"
            ),
            "ollama-codellama": ModelConfig(
                model_name="codellama",
                model_provider="ollama",
                base_url="http://localhost:11434",
                embedding_model="nomic-embed-text",
                embedding_provider="ollama",
                embedding_base_url="http://localhost:11434"
            )
        }
    
    @staticmethod
    def get_custom_configs() -> Dict[str, ModelConfig]:
        """获取自定义配置"""
        return {
            "dashscope-qwen": ModelConfig(
                model_name="qwen-turbo",
                model_provider="dashscope",
                base_url="https://dashscope.aliyuncs.com/api/v1",
                api_key=os.environ.get("DASHSCOPE_API_KEY"),
                embedding_model="text-embedding-v1",
                embedding_provider="dashscope",
                embedding_base_url="https://dashscope.aliyuncs.com/api/v1"
            ),
            "zhipu-glm": ModelConfig(
                model_name="glm-4",
                model_provider="zhipuai",
                api_key=os.environ.get("ZHIPU_API_KEY"),
                embedding_model="embedding-2",
                embedding_provider="zhipuai"
            )
        }
    
    @staticmethod
    def get_all_configs() -> Dict[str, ModelConfig]:
        """获取所有配置"""
        all_configs = {}
        
        # 合并所有配置
        all_configs.update(ModelConfigs.get_openai_configs())
        all_configs.update(ModelConfigs.get_azure_configs())
        all_configs.update(ModelConfigs.get_anthropic_configs())
        all_configs.update(ModelConfigs.get_local_configs())
        all_configs.update(ModelConfigs.get_custom_configs())
        
        return all_configs
    
    @staticmethod
    def list_available_configs():
        """列出所有可用的配置"""
        print("📋 可用的模型配置:")
        print("=" * 50)
        
        configs = ModelConfigs.get_all_configs()
        
        for name, config in configs.items():
            print(f"\n🔧 {name}:")
            print(f"   聊天模型: {config.model_provider}:{config.model_name}")
            print(f"   嵌入模型: {config.embedding_provider}:{config.embedding_model}")
            if config.base_url:
                print(f"   聊天API地址: {config.base_url}")
            if config.embedding_base_url:
                print(f"   嵌入API地址: {config.embedding_base_url}")
    
    @staticmethod
    def get_config_by_name(name: str) -> ModelConfig:
        """根据名称获取配置"""
        configs = ModelConfigs.get_all_configs()
        
        if name not in configs:
            available = list(configs.keys())
            raise ValueError(f"配置 '{name}' 不存在。可用配置: {available}")
        
        return configs[name]


def create_custom_config(
    model_name: str,
    model_provider: str,
    base_url: str = None,
    api_key: str = None,
    embedding_model: str = "text-embedding-3-small",
    embedding_provider: str = "openai",
    embedding_base_url: str = None,
    embedding_api_key: str = None
) -> ModelConfig:
    """
    创建自定义配置
    
    Args:
        model_name: 聊天模型名称
        model_provider: 聊天模型提供商
        base_url: 聊天模型API基础URL
        api_key: API密钥
        embedding_model: 嵌入模型名称
        embedding_provider: 嵌入模型提供商
        embedding_base_url: 嵌入模型API基础URL
        embedding_api_key: 嵌入模型API密钥
        
    Returns:
        ModelConfig对象
    """
    return ModelConfig(
        model_name=model_name,
        model_provider=model_provider,
        base_url=base_url,
        api_key=api_key,
        embedding_model=embedding_model,
        embedding_provider=embedding_provider,
        embedding_base_url=embedding_base_url,
        embedding_api_key=embedding_api_key
    )


if __name__ == "__main__":
    # 列出所有可用配置
    ModelConfigs.list_available_configs()
    
    print("\n" + "=" * 50)
    print("💡 使用示例:")
    print("from model_configs import ModelConfigs")
    print("config = ModelConfigs.get_config_by_name('gpt-4o-mini')")
    print("demo = LangGraphMemoryDemo(model_config=config)") 