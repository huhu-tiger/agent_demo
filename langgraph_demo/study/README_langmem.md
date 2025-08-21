# LangMem 示例

这个目录包含了LangMem（LangChain Memory）的示例代码，展示了如何使用LangMem进行长期记忆管理。

## 什么是LangMem？

LangMem是LangChain生态系统中用于长期记忆管理的库，它提供了：

- **记忆存储**: 使用向量数据库存储和检索记忆
- **记忆工具**: 为智能体提供记忆管理能力
- **记忆提取**: 从对话中自动提取结构化记忆
- **提示词优化**: 基于对话历史优化提示词
- **多用户支持**: 支持多用户记忆隔离

## 文件说明

### 1. `langmem_demo.py` - 完整功能演示
包含LangMem的所有核心功能：
- 基本记忆管理（添加、搜索、列出）
- 记忆提取
- 提示词优化
- 多线程记忆隔离

### 2. `simple_langmem_demo.py` - 简化演示
专注于核心功能：
- 基本记忆操作
- 多用户记忆隔离

### 3. `langmem_requirements.txt` - 依赖文件
安装所需的Python包。

## 安装和设置

### 1. 安装依赖
```bash
pip install -r langmem_requirements.txt
```

### 2. 设置环境变量
```bash
# OpenAI API密钥（用于嵌入）
export OPENAI_API_KEY="your_openai_api_key"

# Anthropic API密钥（用于对话模型）
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

## 使用方法

### 运行简化演示
```bash
python simple_langmem_demo.py
```

### 运行完整演示
```bash
python langmem_demo.py
```

## 核心功能示例

### 1. 创建带记忆的智能体
```python
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langmem import create_manage_memory_tool, create_search_memory_tool

# 设置存储
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)

# 创建工具
memory_tools = [
    create_manage_memory_tool(namespace=("memories",), store=store),
    create_search_memory_tool(namespace=("memories",), store=store),
]

# 创建智能体
agent = create_react_agent(
    "anthropic:claude-3-5-sonnet-latest", 
    tools=memory_tools, 
    store=store
)
```

### 2. 添加记忆
```python
response = agent.invoke({
    "messages": [{"role": "user", "content": "记住我喜欢Python编程"}]
})
```

### 3. 搜索记忆
```python
results = store.search(("memories",), query="编程", limit=5)
for item in results:
    print(item.value.get('content', ''))
```

### 4. 多用户记忆隔离
```python
# 用户A
config_a = {"configurable": {"thread_id": "user-a"}}
agent.invoke({
    "messages": [{"role": "user", "content": "我叫Alice"}]
}, config=config_a)

# 用户B
config_b = {"configurable": {"thread_id": "user-b"}}
agent.invoke({
    "messages": [{"role": "user", "content": "我叫Bob"}]
}, config=config_b)
```

## 主要特性

### 1. 记忆管理
- **添加记忆**: 智能体可以记住用户信息
- **搜索记忆**: 基于语义相似度搜索相关记忆
- **记忆隔离**: 不同用户/线程的记忆相互隔离

### 2. 记忆提取
```python
from langmem import create_memory_store_manager

manager = create_memory_store_manager(
    "anthropic:claude-3-5-sonnet-latest",
    namespace=("memories",),
)

conversation = [
    {"role": "user", "content": "我叫张三，25岁"},
    {"role": "assistant", "content": "很高兴认识你！"}
]

memories = manager.invoke({"messages": conversation})
```

### 3. 提示词优化
```python
from langmem import create_prompt_optimizer

optimizer = create_prompt_optimizer(
    "anthropic:claude-3-5-sonnet-latest",
    kind="metaprompt"
)

updated_prompt = optimizer.invoke({
    "trajectories": conversation_trajectories,
    "prompt": "你是一个有用的AI助手"
})
```

## 最佳实践

### 1. 命名空间管理
- 使用有意义的命名空间组织记忆
- 支持动态命名空间（如用户ID）
- 考虑记忆的访问权限

### 2. 记忆质量
- 提取结构化的记忆信息
- 定期清理过时或错误的记忆
- 使用适当的相似度阈值

### 3. 性能优化
- 在生产环境中使用持久化存储
- 合理设置搜索限制
- 考虑记忆的过期策略

## 故障排除

### 常见问题

1. **API密钥错误**
   - 确保设置了正确的环境变量
   - 检查API密钥的有效性

2. **依赖安装失败**
   - 使用虚拟环境
   - 检查Python版本兼容性

3. **记忆搜索无结果**
   - 检查命名空间是否正确
   - 确认记忆已成功添加
   - 调整搜索查询

### 调试技巧

1. 启用详细日志
2. 检查存储状态
3. 验证工具配置

## 扩展阅读

- [LangMem官方文档](https://langchain-ai.github.io/langmem/)
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [LangChain文档](https://python.langchain.com/)

## 贡献

欢迎提交Issue和Pull Request来改进这些示例！ 