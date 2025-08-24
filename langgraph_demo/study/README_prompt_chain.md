# LangGraph Prompt Chain 示例

本示例展示了如何使用LangGraph实现各种类型的提示链工作流，从简单的线性链到复杂的条件路由和迭代优化。

## 📁 文件结构

```
study/
├── 10-1_提示链.py          # 主要的提示链示例文件
├── config.py              # 配置文件
└── README_prompt_chain.md # 本文件
```

## 🚀 示例概览

### 1. 简单提示链 (Functional API)

**特点：**
- 使用`@task`和`@entrypoint`装饰器
- 线性执行流程
- 条件分支（质量检查）

**核心组件：**
- `generate_joke()`: 生成初始笑话
- `improve_joke()`: 改进笑话
- `polish_joke()`: 润色笑话
- `check_punchline()`: 质量检查

**适用场景：**
- 内容生成和优化
- 简单的多步骤处理
- 质量控制和改进

### 2. 复杂提示链 (StateGraph API)

**特点：**
- 使用StateGraph构建复杂工作流
- 状态管理和条件路由
- 迭代优化和质量评估

**核心组件：**
- `generate_initial_content()`: 生成初始内容
- `evaluate_quality()`: 评估质量
- `improve_content()`: 改进内容
- `polish_content()`: 润色内容
- `should_continue()`: 条件路由

**适用场景：**
- 复杂的内容创作流程
- 需要质量评估的系统
- 多轮迭代优化

### 3. 迭代优化提示链

**特点：**
- 基于反馈的迭代优化
- 结构化质量评估
- 自动停止条件

**核心组件：**
- `generate_content()`: 生成内容
- `evaluate_content()`: 评估内容
- 循环优化直到达到目标质量

**适用场景：**
- 内容质量优化
- 基于反馈的学习
- 自动化内容改进

### 4. 并行提示链

**特点：**
- 并行执行多个任务
- 结果聚合
- 提高执行效率

**核心组件：**
- `generate_story()`: 生成故事
- `generate_poem()`: 生成诗歌
- `generate_essay()`: 生成文章
- `combine_content()`: 组合结果

**适用场景：**
- 多类型内容生成
- 提高处理效率
- 内容多样化

## 🛠️ 安装和配置

### 1. 安装依赖

```bash
pip install langgraph langchain-openai langchain-core
```

### 2. 配置API密钥

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

或在代码中设置：

```python
import os
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
```

## 📖 使用方法

### 运行示例

```bash
python 10-1_提示链.py
```

### 选择运行模式

运行后会显示菜单，可以选择：

1. **简单提示链示例** - 基础的笑话生成和优化
2. **复杂提示链示例** - 状态图方式的内容创作
3. **迭代优化示例** - 基于反馈的迭代优化
4. **并行提示链示例** - 并行内容生成
5. **流式输出示例** - 实时查看执行过程
6. **运行所有示例** - 依次运行所有示例
7. **退出**

## 🔧 核心概念

### 1. Functional API

使用装饰器定义任务和工作流：

```python
@task
def my_task(input_data):
    # 任务逻辑
    return result

@entrypoint()
def my_workflow(input_data):
    result = my_task(input_data).result()
    return result
```

### 2. StateGraph API

使用图结构定义复杂工作流：

```python
workflow = StateGraph(State)
workflow.add_node("node_name", node_function)
workflow.add_edge(START, "node_name")
workflow.add_edge("node_name", END)
chain = workflow.compile()
```

### 3. 条件路由

根据状态决定下一步：

```python
def should_continue(state):
    if condition:
        return "next_node"
    else:
        return "end_node"

workflow.add_conditional_edges(
    "current_node",
    should_continue,
    {"next_node": "next_node", "end_node": END}
)
```

### 4. 流式输出

实时查看执行过程：

```python
for step in workflow.stream(input_data, stream_mode="updates"):
    print(step)
```

## 🎯 最佳实践

### 1. 任务设计

- 每个任务应该有明确的职责
- 使用有意义的函数名和注释
- 处理异常情况

### 2. 状态管理

- 使用`TypedDict`定义清晰的状态结构
- 避免在状态中存储过大的数据
- 合理使用状态更新

### 3. 条件路由

- 使用清晰的条件逻辑
- 避免无限循环
- 提供合理的默认路径

### 4. 错误处理

- 在关键节点添加异常处理
- 提供有意义的错误信息
- 考虑重试机制

## 🔍 调试技巧

### 1. 流式输出

使用`stream()`方法查看执行过程：

```python
for chunk in workflow.stream(input_data):
    print(chunk)
```

### 2. 状态检查

在节点中添加状态打印：

```python
def my_node(state):
    print(f"当前状态: {state}")
    # 处理逻辑
```

### 3. 图可视化

使用LangSmith查看图结构：

```python
workflow.get_graph().draw_mermaid_png()
```

## 📚 扩展阅读

- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [Functional API指南](https://langchain-ai.github.io/langgraph/docs/concepts/functional_api/)
- [StateGraph API指南](https://langchain-ai.github.io/langgraph/docs/how-tos/graph-api/)
- [提示链最佳实践](https://langchain-ai.github.io/langgraph/docs/tutorials/workflows/)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这些示例！

## 📄 许可证

本项目采用MIT许可证。 