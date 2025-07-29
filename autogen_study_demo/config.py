from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily

model="Qwen3-235B-A22B-Instruct-2507"
base_url="http://39.155.179.5:57887/v1"
api_key= ""
model_info={
    "vision": False,
    "function_calling": True,
    "json_output": True,
    "family": ModelFamily.UNKNOWN,
    "structured_output": True,
}

model_client = OpenAIChatCompletionClient(
    model=model,
    base_url=base_url,
    api_key=api_key,
    model_info=model_info,
    timeout=120
)


model_client_v3 = OpenAIChatCompletionClient(
    model="deepseek-v3",
    base_url="http://39.155.179.5:57885/v1",
    api_key="",
    model_info={
        "vision": False,
        "function_calling": False,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
    },
)

model_client_vl = OpenAIChatCompletionClient(
    model="Qwen2.5-VL-7B-Instruct",
    base_url="http://39.155.179.4:9116/v1",
    api_key="",
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
    },
)


model_client_vl_plus = OpenAIChatCompletionClient(
    model="qwen-vl-plus-2025-01-25",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-b5e591f6a4354b34bf34b26afc20969e",
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
    },
)

model_client_qwen_plus = OpenAIChatCompletionClient(
    model="qwen-plus-latest",
    # base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    base_url="http://39.155.179.5:57888/compatible-mode/v1",
    api_key="sk-b5e591f6a4354b34bf34b26afc20969e",
    model_info={
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": True,
    },
)