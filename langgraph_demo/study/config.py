import os 
import logging
from typing import Optional, Dict, Any
model="Qwen3-235B-A22B-Instruct-2507"
# model="Qwen3-235B"
base_url="http://39.155.179.5:8002/v1"
api_key= "xxx"



v3_model = "deepseek-v3"
v3_base_url = "http://61.49.53.5:30002/v1"
v3_api_key = ""


# model_client_vl = OpenAIChatCompletionClient(
#     model="Qwen2.5-VL-7B-Instruct",
#     base_url="http://39.155.179.4:9116/v1",
#     api_key="",
#     model_info={
#         "vision": True,
#         "function_calling": True,
#         "json_output": True,
#         "family": ModelFamily.UNKNOWN,
#         "structured_output": True,
#     },
# )



modelscope_qwen_model="qwen-plus-latest"
modelscope_qwen_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
modelscope_qwen_api_key="sk-b5e591f6a4354b34bf34b26afc20969e"

def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志格式 - 添加文件名显示
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(f"{log_dir}/langgraph_demo.log", encoding='utf-8'),
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
        embedding_model: str = "text-embedding-3-small",
        embedding_provider: str = "openai",
        embedding_base_url: Optional[str] = None,
        embedding_api_key: Optional[str] = None,
        embedding_dimensions: Optional[int] = None
    ):
        """
        初始化模型配置
        
        Args:
            model_name: 聊天模型名称
            model_provider: 聊天模型提供商
            base_url: 聊天模型API基础URL
            api_key: API密钥
            embedding_model: 嵌入模型名称
            embedding_provider: 嵌入模型提供商
            embedding_base_url: 嵌入模型API基础URL
            embedding_api_key: 嵌入模型API密钥
            embedding_dimensions: 嵌入模型维度（可选，如果不提供则自动检测）
        """
        self.model_name = model_name
        self.model_provider = model_provider
        self.base_url = base_url
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.embedding_provider = embedding_provider
        self.embedding_base_url = embedding_base_url
        self.embedding_api_key = embedding_api_key
        self.embedding_dimensions = embedding_dimensions
    
    def get_chat_model_config(self) -> Dict[str, Any]:
        """获取聊天模型配置"""
        config = {}
        
        # 设置API密钥
        if self.api_key:
            config["api_key"] = self.api_key
        
        # 设置基础URL（如果提供）
        if self.base_url:
            config["base_url"] = self.base_url
        
        return config
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """获取嵌入模型配置"""
        config = {}
        
        # 设置API密钥
        if self.embedding_api_key:
            config["api_key"] = self.embedding_api_key
        
        # 设置基础URL（如果提供）
        if self.embedding_base_url:
            config["base_url"] = self.embedding_base_url
        
        return config
    
    def get_embedding_dimensions(self) -> int:
        """获取嵌入模型维度"""
        if self.embedding_dimensions is not None:
            return self.embedding_dimensions
        
        # 自动检测维度
        return self._auto_detect_embedding_dimensions()
    
    def _auto_detect_embedding_dimensions(self) -> int:
        """自动检测嵌入模型维度"""
        # 常见嵌入模型的维度映射
        embedding_dims = {
            # OpenAI 模型
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            
            # Qwen 模型
            "Qwen3-Embedding-8B": 2048,
            "text-embedding-v1": 1536,
            
            # 其他模型
            "nomic-embed-text": 768,
            "embedding-2": 1024,
            "Qwen3-Embedding-8B" : 4096,
            # 默认维度（如果模型不在列表中）
            "default": 1536
        }
        
        # 查找模型对应的维度
        for model_name, dims in embedding_dims.items():
            if model_name.lower() in self.embedding_model.lower():
                return dims
        
        # 如果找不到匹配的模型，返回默认维度
        print(f"⚠️  警告: 未找到模型 '{self.embedding_model}' 的维度配置，使用默认维度 1536")
        return embedding_dims["default"]



# 创建自定义配置
custom_config = ModelConfig(
    model_name="Qwen3-235B-A22B-Instruct-2507",
    model_provider="openai",
    base_url="http://39.155.179.5:8002/v1",  # 可以修改为其他端点
    api_key="sk-1234567890",
    embedding_model="Qwen3-Embedding-8B",
    embedding_provider="openai",
    embedding_base_url="http://10.20.201.212:8013/v1",
    embedding_api_key="sk-1234567890",
    embedding_dimensions=4096  # Qwen3-Embedding-8B的维度
)