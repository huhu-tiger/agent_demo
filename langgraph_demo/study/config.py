import os 
import logging

# model="Qwen3-235B-A22B-Instruct-2507"
model="Qwen3-235B"
base_url="http://39.155.179.5:8002/v1"
api_key= ""



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
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
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