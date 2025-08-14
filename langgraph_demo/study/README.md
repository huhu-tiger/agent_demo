# LangGraph 智能体学习示例

## 📚 概述

本示例基于 Context7 提供的 LangGraph 官方文档，为您提供一个全面的 LangGraph 学习教程。通过四个渐进式的示例，您将学习到 LangGraph 的核心概念和实际应用。

## 🎯 学习目标

通过本示例，您将掌握：

1. **状态管理 (State)** - 理解如何在智能体间共享数据
2. **节点定义 (Nodes)** - 学习如何创建智能体节点
3. **边连接 (Edges)** - 掌握工作流的连接方式
4. **条件路由 (Conditional Edges)** - 实现智能决策逻辑
5. **多智能体协作** - 构建复杂的协作系统
6. **工具使用** - 增强智能体能力

## 🏗️ 项目结构

```
langgraph_demo/study/
├── config.py                           # 配置文件（模型配置、日志配置）
├── 01_basic_concepts.py                # 基础概念示例
├── 02_conditional_routing.py           # 条件路由示例
├── 03_tools_integration.py             # 工具集成示例
├── 04_multi_agent_collaboration.py     # 多智能体协作示例
├── 05_advanced_features.py             # 高级特性示例
├── run_all_examples.py                 # 主运行文件
├── requirements.txt                    # 依赖管理
├── README.md                          # 说明文档
└── logs/                              # 日志目录（自动创建）
    └── langgraph_demo.log             # 运行日志
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置环境变量

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 运行示例

```bash
# 运行所有示例
python run_all_examples.py all

# 显示所有可用示例
python run_all_examples.py list

# 运行特定示例
python run_all_examples.py "基础概念"

# 交互式运行
python run_all_examples.py interactive

# 直接运行单个示例文件
python 01_basic_concepts.py
python 02_conditional_routing.py
python 03_tools_integration.py
python 04_multi_agent_collaboration.py
python 05_advanced_features.py
```

## 📖 详细说明

### 配置文件 (config.py)

**功能：**
- 模型配置：自定义模型地址、API密钥、模型名称
- 日志配置：自动创建日志目录，同时输出到文件和控制台
- 统一配置管理：所有示例共享配置

**配置示例：**
```python
# 模型配置
base_url = "http://localhost:11434/v1"  # 自定义模型地址
api_key = "ollama"  # 自定义模型密钥
model = "qwen2.5:7b"  # 自定义模型名称
```

### 第一部分：基础概念示例 (01_basic_concepts.py)

**概念学习：**
- `StateGraph` - 状态图的基础创建
- `TypedDict` - 状态类型定义
- `add_node()` - 添加节点
- `set_entry_point()` - 设置入口点
- `add_edge()` - 添加边
- `compile()` - 编译工作流

**代码示例：**
```python
class BasicState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    response: str

def basic_agent(state: BasicState) -> BasicState:
    # 简单的智能体逻辑
    user_input = state["user_input"]
    response = f"我收到了您的消息：'{user_input}'"
    return {"response": response, "messages": [AIMessage(content=response)]}

# 创建工作流
workflow = StateGraph(BasicState)
workflow.add_node("basic_agent", basic_agent)
workflow.set_entry_point("basic_agent")
workflow.add_edge("basic_agent", END)
graph = workflow.compile()
```

### 第二部分：条件路由示例 (02_conditional_routing.py)

**概念学习：**
- `add_conditional_edges()` - 条件边
- 路由函数 - 根据状态决定下一步
- 多节点协作 - 不同智能体处理不同任务

**核心特性：**
- 智能决策：根据用户输入自动选择处理方式
- 多路径：支持计算、搜索、聊天等多种处理路径
- 状态传递：决策结果在节点间传递

**工作流程：**
```
用户输入 → 决策智能体 → 路由函数 → 专业智能体 → 输出结果
```

### 第三部分：工具集成示例 (03_tools_integration.py)

**概念学习：**
- `@tool` 装饰器 - 定义工具
- 工具集成 - 将外部功能集成到智能体
- 状态扩展 - 工具结果的状态管理

**工具示例：**
```python
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    weather_data = {
        "北京": "晴天，温度 25°C，空气质量良好",
        "上海": "多云，温度 28°C，空气质量一般"
    }
    return weather_data.get(city, f"抱歉，没有找到 {city} 的天气信息")
```

### 第四部分：多智能体协作示例 (04_multi_agent_collaboration.py)

**概念学习：**
- 复杂状态管理 - 多个智能体共享状态
- 顺序执行 - 智能体间的协作流程
- 结果整合 - 多智能体结果的综合处理

**协作流程：**
```
研究员智能体 → 分析师智能体 → 协调员智能体 → 最终报告
```

## 🔧 核心概念详解

### 1. 状态 (State)

状态是 LangGraph 中最重要的概念，它定义了智能体间共享的数据结构：

```python
class MyState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], add_messages]
    user_input: str
    # 其他状态字段...
```

**关键点：**
- 使用 `TypedDict` 定义状态结构
- `Annotated` 用于特殊字段（如消息列表）
- 状态在节点间自动传递和更新

### 2. 节点 (Nodes)

节点是工作流中的处理单元，通常是 Python 函数：

```python
def my_agent(state: MyState) -> MyState:
    # 处理逻辑
    return {"updated_field": "new_value"}
```

**节点特点：**
- 接收当前状态作为输入
- 返回状态更新字典
- 可以包含复杂的处理逻辑

### 3. 边 (Edges)

边定义了节点间的连接关系：

```python
# 直接边
workflow.add_edge("node1", "node2")

# 条件边
workflow.add_conditional_edges(
    "decision_node",
    route_function,
    {"option1": "node1", "option2": "node2"}
)
```

### 4. 条件路由

条件路由允许根据状态动态选择下一个节点：

```python
def route_function(state: MyState) -> str:
    if state["condition"] == "option1":
        return "node1"
    else:
        return "node2"
```

### 第五部分：高级特性示例 (05_advanced_features.py)

**概念学习：**
- 记忆管理 - 对话历史和上下文维护
- 检查点 - 状态保存和恢复
- 并行处理 - 多任务并发执行
- 错误处理 - 异常处理和恢复机制

**高级功能：**
- 会话管理：自动生成会话ID
- 并行执行：多个处理器同时工作
- 错误恢复：自动处理异常情况
- 状态持久化：支持检查点保存

## 🎮 交互式演示

运行示例后，您可以选择不同的工作流进行交互式测试：

1. **基础概念** - 状态管理、节点定义、边连接
2. **条件路由** - 智能决策、动态路由、多路径处理
3. **工具集成** - 工具定义、工具调用、能力增强
4. **多智能体协作** - 复杂协作、结果整合、团队工作
5. **高级特性** - 记忆管理、并行处理、错误处理

## 🔍 调试和监控

示例中包含了详细的日志信息：

```python
logger.info("🤖 基础智能体正在处理...")
logger.info(f"输入：{user_input}")
logger.info(f"输出：{result['response']}")
```

**日志特性：**
- 自动创建日志目录和文件
- 同时输出到控制台和文件
- 包含时间戳和日志级别
- 支持错误日志记录

## 📈 扩展建议

### 1. 添加更多工具
```python
@tool
def search_web(query: str) -> str:
    """网络搜索工具"""
    pass

@tool
def send_email(to: str, subject: str, content: str) -> str:
    """邮件发送工具"""
    pass
```

### 2. 集成 LLM
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")

def llm_agent(state: MyState) -> MyState:
    response = llm.invoke(state["user_input"])
    return {"response": response.content}
```

### 3. 添加记忆功能
```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
workflow = StateGraph(MyState, checkpointer=checkpointer)
```

### 4. 错误处理
```python
def robust_agent(state: MyState) -> MyState:
    try:
        # 处理逻辑
        return {"result": "success"}
    except Exception as e:
        return {"error": str(e), "result": "failure"}
```

## 🎓 学习路径

1. **初学者**：从基础工作流开始，理解状态和节点的概念
2. **进阶者**：学习条件路由，掌握动态决策
3. **高级用户**：探索工具集成和多智能体协作
4. **专家级**：结合 LangSmith 进行调试和优化

## 📚 相关资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangChain 文档](https://python.langchain.com/)
- [Context7 文档](https://context7.com/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个学习示例！

## 📄 许可证

MIT License

---

**祝您学习愉快！** 🎉 