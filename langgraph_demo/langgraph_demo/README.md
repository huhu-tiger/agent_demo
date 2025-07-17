# LangGraph 多智能体 Demo

本示例展示如何使用 **LangGraph** 构建一个简单的多智能体工作流（Research → Summary），并提供完整的环境创建与运行步骤。

**支持本地模型（Ollama）和云端模型（OpenAI）**

## 1. 环境准备

1. 建议使用 **Python 3.10+**。
2. 创建虚拟环境（任选其一）：
   ```bash
   # venv 示例
   python -m venv venv
   # 或者 Conda 示例
   conda create -n langgraph_demo python=3.10 -y
   ```
3. 激活环境：
   ```bash
   # venv (Windows Powershell)
   .\venv\Scripts\Activate.ps1
   # conda
   conda activate langgraph_demo
   ```
4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 2. 模型配置

### 2.1 本地模型（推荐）

1. 安装 Ollama：
   - 访问 [https://ollama.ai/](https://ollama.ai/) 下载安装
   - 或使用命令行：`curl -fsSL https://ollama.ai/install.sh | sh`

2. 下载模型：
   ```bash
   # 下载通义千问模型（推荐）
   ollama pull qwen2.5:7b
   
   # 或下载其他模型
   ollama pull llama3.1:8b
   ollama pull gemma2:9b
   ```

3. 启动 Ollama 服务：
   ```bash
   ollama serve
   ```

### 2.2 云端模型（备选）

在项目根目录创建 `.env` 文件：
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL_TYPE=openai
MODEL_NAME=gpt-3.5-turbo
```

## 3. 运行 Demo

### 3.1 使用本地模型（默认）
```bash
python -m langgraph_demo.multi_agent_demo "给我一份关于量子计算现状的调研报告，并生成摘要。"
```

### 3.2 使用云端模型
```bash
# 方法1：设置环境变量
set MODEL_TYPE=openai
set MODEL_NAME=gpt-3.5-turbo
python -m langgraph_demo.multi_agent_demo "你的问题"

# 方法2：在.env文件中配置
# MODEL_TYPE=openai
# MODEL_NAME=gpt-3.5-turbo
```

### 3.3 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MODEL_TYPE` | `local` | `local` 或 `openai` |
| `MODEL_NAME` | `qwen2.5:7b` | 模型名称 |
| `OPENAI_API_KEY` | - | OpenAI API密钥（仅云端模型需要） |

## 4. 关于本地模型

**本地模型不需要Function Call功能**，只需要支持基本的文本生成即可。本Demo使用的Prompt都是简单的文本生成任务，适合大多数开源模型。

推荐的本地模型：
- `qwen2.5:7b` - 通义千问，中文效果好
- `llama3.1:8b` - Meta开源模型
- `gemma2:9b` - Google开源模型

## 5. 目录结构
```
langgraph_demo/
├── README.md
├── requirements.txt
└── multi_agent_demo.py
```

## 6. 参考
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/docs) 