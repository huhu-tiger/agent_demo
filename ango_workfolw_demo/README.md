# Ango Demo

这是一个使用Agno框架的演示程序，展示了如何利用大语言模型和各种工具生成关于NVDA（NVIDIA）的报告。

## 功能特点

- 支持多种大语言模型（DeepSeek, Qwen等）
- 集成了推理工具和Yahoo Finance数据工具
- 可以生成格式化的Markdown报告
- 支持流式输出和中间步骤展示

## 环境设置

### 安装依赖

```bash
pip install agno yfinance pandas requests
```

### 配置模型参数

你可以通过环境变量或直接修改`config.py`来配置模型参数：

通过环境变量（推荐）：

```bash
# Qwen 3 模型配置
export QWEN_MOE_BASE_URL="http://your-qwen-server:port"
export QWEN_MOE_API_KEY="your_api_key_here"
export QWEN_MOE_MODEL="Qwen3-235B"

# DeepSeek 模型配置
export DEEPSEEK_R1_BASE_URL="http://your-deepseek-server:port"
export DEEPSEEK_R1_API_KEY="your_api_key_here"
export DEEPSEEK_R1_MODEL="deepseek-r1"
```

或者直接编辑`config.py`中的默认值。

## 运行演示

```bash
# 确保你在项目根目录
cd ango_demo

# 运行演示程序
python demo.py
```

## 切换模型

你可以修改`demo.py`中的模型配置部分来切换使用不同的模型：

```python
# 使用DeepSeek模型
model=DeepSeek(
    id=model_config_manager.models["deepseek-r1"].model_name,
    name=model_config_manager.models["deepseek-r1"].model_name,
    api_key=model_config_manager.models["deepseek-r1"].api_key,
    base_url=model_config_manager.models["deepseek-r1"].url
)

# 或使用OpenAI兼容API的Qwen模型
model=OpenAIChat(
    id=model_config_manager.models["Qwen3-235B"].model_name,
    name=model_config_manager.models["Qwen3-235B"].model_name,
    api_key=model_config_manager.models["Qwen3-235B"].api_key,
    base_url=model_config_manager.models["Qwen3-235B"].url
)
```

## 项目结构

```
ango_demo/
├── config.py         # 模型配置管理
├── demo.py           # 主演示程序
└── README.md         # 本文件
```

## 注意事项

- 确保你有正确的API密钥和服务器地址
- 如果使用本地部署的模型，确保模型服务已经启动
- 报告生成可能需要一些时间，取决于模型的响应速度和网络状态 