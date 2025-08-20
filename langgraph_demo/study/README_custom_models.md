# LangGraph InMemoryStore 自定义模型配置指南

本指南详细说明如何在LangGraph InMemoryStore中使用自定义模型配置，包括不同的模型提供商、API端点和配置选项。

## 🚀 功能特性

### 🔧 模型配置支持
- **多提供商支持**: OpenAI、Azure OpenAI、Anthropic、本地模型等
- **自定义API端点**: 支持自定义API地址和端口
- **混合配置**: 可以为聊天模型和嵌入模型使用不同的提供商
- **灵活配置**: 支持环境变量和代码配置

### 📋 支持的模型提供商

| 提供商 | 聊天模型 | 嵌入模型 | 配置方式 |
|--------|----------|----------|----------|
| OpenAI | ✅ | ✅ | API密钥 |
| Azure OpenAI | ✅ | ✅ | API密钥 + 端点 |
| Anthropic | ✅ | ❌ | API密钥 |
| Ollama (本地) | ✅ | ✅ | 本地服务 |
| DashScope | ✅ | ✅ | API密钥 |
| 智谱AI | ✅ | ✅ | API密钥 |

## 📦 安装依赖

```bash
pip install langgraph langchain-openai langchain-anthropic langchain-community requests
```

## 🔑 环境变量配置

### OpenAI
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Azure OpenAI
```bash
export AZURE_OPENAI_API_KEY="your-azure-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

### Anthropic
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 其他提供商
```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
export ZHIPU_API_KEY="your-zhipu-api-key"
```

## 🎯 使用方法

### 1. 基本使用

```python
from langgraph_demo.study.langgraph_inmemory_demo import LangGraphMemoryDemo, ModelConfig

# 使用默认配置
demo = LangGraphMemoryDemo()

# 使用自定义配置
config = ModelConfig(
    model_name="gpt-4o-mini",
    model_provider="openai",
    base_url="https://api.openai.com/v1",
    api_key="your-api-key"
)
demo = LangGraphMemoryDemo(model_config=config)
```

### 2. 使用预设配置

```python
from langgraph_demo.study.model_configs import ModelConfigs

# 获取所有可用配置
configs = ModelConfigs.get_all_configs()

# 使用特定配置
config = ModelConfigs.get_config_by_name("gpt-4o-mini")
demo = LangGraphMemoryDemo(model_config=config)
```

### 3. 创建自定义配置

```python
from langgraph_demo.study.model_configs import create_custom_config

# 创建自定义配置
config = create_custom_config(
    model_name="gpt-3.5-turbo",
    model_provider="openai",
    base_url="https://your-custom-endpoint.com/v1",
    api_key="your-api-key",
    embedding_model="text-embedding-ada-002",
    embedding_provider="openai"
)

demo = LangGraphMemoryDemo(model_config=config)
```

## 🔧 配置示例

### OpenAI 模型

```python
# GPT-4o-mini (默认)
config = ModelConfig(
    model_name="gpt-4o-mini",
    model_provider="openai",
    api_key=os.environ.get("OPENAI_API_KEY")
)

# GPT-3.5-turbo
config = ModelConfig(
    model_name="gpt-3.5-turbo",
    model_provider="openai",
    api_key=os.environ.get("OPENAI_API_KEY")
)
```

### Azure OpenAI

```python
config = ModelConfig(
    model_name="gpt-4",
    model_provider="azure",
    base_url="https://your-resource.openai.azure.com/",
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    embedding_model="text-embedding-ada-002",
    embedding_provider="azure",
    embedding_base_url="https://your-resource.openai.azure.com/"
)
```

### Anthropic Claude

```python
config = ModelConfig(
    model_name="claude-3-sonnet-20240229",
    model_provider="anthropic",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    embedding_model="text-embedding-3-small",
    embedding_provider="openai"  # Anthropic没有嵌入模型，使用OpenAI
)
```

### 本地模型 (Ollama)

```python
config = ModelConfig(
    model_name="llama2",
    model_provider="ollama",
    base_url="http://localhost:11434",
    embedding_model="nomic-embed-text",
    embedding_provider="ollama",
    embedding_base_url="http://localhost:11434"
)
```

### 混合配置

```python
# 使用OpenAI聊天模型 + 本地嵌入模型
config = ModelConfig(
    model_name="gpt-4o-mini",
    model_provider="openai",
    api_key=os.environ.get("OPENAI_API_KEY"),
    embedding_model="nomic-embed-text",
    embedding_provider="ollama",
    embedding_base_url="http://localhost:11434"
)
```

## 🧪 测试配置

### 运行完整示例

```bash
python langgraph_demo/study/custom_model_example.py
```

### 查看可用配置

```bash
python langgraph_demo/study/model_configs.py
```

### 测试特定配置

```python
from langgraph_demo.study.custom_model_example import example_1_openai_models

# 测试OpenAI模型
example_1_openai_models()
```

## 📊 配置管理

### ModelConfig 类属性

| 属性 | 类型 | 描述 |
|------|------|------|
| `model_name` | str | 聊天模型名称 |
| `model_provider` | str | 聊天模型提供商 |
| `base_url` | str | 聊天模型API基础URL |
| `api_key` | str | API密钥 |
| `embedding_model` | str | 嵌入模型名称 |
| `embedding_provider` | str | 嵌入模型提供商 |
| `embedding_base_url` | str | 嵌入模型API基础URL |
| `embedding_api_key` | str | 嵌入模型API密钥 |

### 预设配置列表

运行以下命令查看所有可用配置：

```python
from langgraph_demo.study.model_configs import ModelConfigs
ModelConfigs.list_available_configs()
```

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ❌ 请设置 OPENAI_API_KEY 环境变量
   ```
   解决：确保正确设置了相应的API密钥

2. **连接超时**
   ```
   ❌ 无法连接到Ollama服务
   ```
   解决：确保本地服务正在运行

3. **模型不存在**
   ```
   ❌ 配置 'xxx' 不存在
   ```
   解决：检查模型名称是否正确

4. **嵌入模型不匹配**
   ```
   ❌ 嵌入模型维度不匹配
   ```
   解决：确保嵌入模型维度与配置一致

### 调试技巧

1. **检查模型信息**
   ```python
   demo = LangGraphMemoryDemo(model_config=config)
   model_info = demo.get_model_info()
   print(model_info)
   ```

2. **测试连接**
   ```python
   # 测试API连接
   import requests
   response = requests.get("https://api.openai.com/v1/models", 
                          headers={"Authorization": f"Bearer {api_key}"})
   print(response.status_code)
   ```

3. **查看详细错误**
   ```python
   try:
       demo = LangGraphMemoryDemo(model_config=config)
   except Exception as e:
       print(f"详细错误: {e}")
       import traceback
       traceback.print_exc()
   ```

## 🚀 高级用法

### 动态配置切换

```python
def switch_model(demo, new_config):
    """动态切换模型配置"""
    demo.model_config = new_config
    # 重新初始化模型
    demo.llm = init_chat_model(f"{new_config.model_provider}:{new_config.model_name}")
    demo.embeddings = init_embeddings(f"{new_config.embedding_provider}:{new_config.embedding_model}")
```

### 配置验证

```python
def validate_config(config):
    """验证配置是否有效"""
    required_fields = ['model_name', 'model_provider']
    for field in required_fields:
        if not hasattr(config, field) or not getattr(config, field):
            raise ValueError(f"缺少必需字段: {field}")
    
    # 检查API密钥
    if not config.api_key:
        print("⚠️  警告: 未设置API密钥")
```

### 批量测试

```python
def test_all_configs():
    """测试所有配置"""
    configs = ModelConfigs.get_all_configs()
    results = {}
    
    for name, config in configs.items():
        try:
            demo = LangGraphMemoryDemo(model_config=config)
            demo.add_memory("测试", "test")
            results[name] = "✅ 成功"
        except Exception as e:
            results[name] = f"❌ 失败: {e}"
    
    return results
```

## 📝 最佳实践

1. **使用环境变量**: 避免在代码中硬编码API密钥
2. **配置验证**: 在使用前验证配置的有效性
3. **错误处理**: 添加适当的错误处理机制
4. **日志记录**: 记录模型切换和错误信息
5. **性能监控**: 监控不同模型的响应时间和成本

## 🤝 贡献

欢迎提交新的模型配置和示例！请确保：

1. 测试配置的有效性
2. 添加适当的文档
3. 包含错误处理
4. 遵循代码规范

## �� 许可证

MIT License 