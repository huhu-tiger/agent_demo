# LangMem 长上下文管理示例

这个示例展示了如何使用LangMem的摘要功能来管理长对话上下文，解决LLM应用中的上下文窗口限制问题。

## 🎯 功能特性

### 1. **基础摘要功能**
- 使用 `summarize_messages` 函数自动摘要长对话
- 智能token管理，避免超出上下文窗口
- 运行摘要跟踪，避免重复摘要

### 2. **高级摘要功能**
- 使用 `SummarizationNode` 作为独立的图节点
- 更精细的摘要控制
- 与LangGraph深度集成

### 3. **多线程记忆隔离**
- 不同对话线程的摘要独立管理
- 线程间记忆隔离
- 支持多用户场景

## 🏗️ 架构设计

```
用户消息 → LangGraph → SummarizationNode → LLM → 响应
                ↓
            检查点保存器 → 运行摘要存储
```

## 📋 核心组件

### LongContextChatbot
- 基础摘要聊天机器人
- 自动token计数和摘要触发
- 运行摘要状态管理

### AdvancedSummarizationDemo
- 高级摘要演示
- 使用SummarizationNode
- 更复杂的图结构

## 🔧 配置参数

```python
# 摘要配置
max_tokens=512,              # 最大总token数
max_tokens_before_summary=256,  # 触发摘要的token阈值
max_summary_tokens=128,      # 摘要最大token数
```

## 🚀 使用方法

### 1. 安装依赖
```bash
pip install -r langmem_summarization_requirements.txt
```

### 2. 设置环境变量
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 3. 运行示例
```bash
python 15_langmem_summarization_demo.py
```

## 📊 演示内容

### 基础摘要演示
- 模拟20轮长对话
- 自动触发摘要机制
- 展示摘要效果

### 高级摘要演示
- 使用SummarizationNode
- 15轮技术对话
- 独立摘要节点处理

### 记忆集成演示
- 多线程对话管理
- 线程间摘要隔离
- 摘要对比分析

## 💡 关键概念

### RunningSummary
- 跟踪对话摘要状态
- 避免重复摘要
- 维护对话连续性

### Token管理
- 智能token计数
- 动态摘要触发
- 上下文窗口优化

### 线程隔离
- 独立对话上下文
- 摘要状态分离
- 多用户支持

## 🔍 技术细节

### 摘要触发条件
1. 消息token数超过 `max_tokens_before_summary`
2. 总token数超过 `max_tokens`
3. 运行摘要存在且需要更新

### 摘要策略
- 保留最近的对话内容
- 摘要早期对话历史
- 维护关键信息完整性

### 性能优化
- 避免不必要的摘要
- 缓存运行摘要
- 智能token计算

## 🎯 应用场景

### 1. 长对话聊天机器人
- 客服系统
- 教育助手
- 技术支持

### 2. 多轮对话应用
- 会议记录
- 访谈系统
- 咨询平台

### 3. 文档处理
- 长文档问答
- 报告分析
- 合同审查

## 📈 优势

1. **上下文管理**: 自动处理长对话上下文
2. **性能优化**: 减少token消耗和API成本
3. **用户体验**: 保持对话连贯性
4. **可扩展性**: 支持多线程和多用户
5. **灵活性**: 可配置的摘要参数

## 🔧 自定义配置

```python
# 自定义摘要参数
summarization_config = {
    "max_tokens": 1024,
    "max_tokens_before_summary": 512,
    "max_summary_tokens": 256
}

# 自定义模型配置
model_config = ModelConfig(
    model_provider="openai",
    model_name="gpt-4",
    base_url="https://api.openai.com/v1"
)
```

## 🐛 故障排除

### 常见问题
1. **摘要不触发**: 检查token阈值配置
2. **摘要质量差**: 调整摘要模型参数
3. **内存泄漏**: 定期清理检查点数据

### 调试技巧
- 启用详细日志
- 监控token使用情况
- 检查摘要内容质量

## 📚 相关资源

- [LangMem官方文档](https://github.com/langchain-ai/langmem)
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [摘要最佳实践](https://github.com/langchain-ai/langmem/blob/main/docs/docs/guides/summarization.md) 