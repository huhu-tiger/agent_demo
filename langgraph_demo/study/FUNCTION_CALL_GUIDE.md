# LangGraph Function Call 使用指南

## 📊 概述

本指南介绍如何在 LangGraph 中使用 Function Call 方式来调用工具，实现智能的工具选择和自动执行。

## 🎯 Function Call 的优势

### 传统方式 vs Function Call

#### 传统方式（关键词匹配）
```python
# 需要手动编写规则
if "天气" in user_input:
    selected_tools.append("get_weather")
elif "计算" in user_input:
    selected_tools.append("calculate_math")
```

#### Function Call 方式
```python
# 大模型自动分析用户意图
agent = create_openai_functions_agent(llm, tools, prompt)
result = agent_executor.invoke({"input": user_input})
```

### 主要优势
- ✅ **智能理解**：大模型自动分析用户意图
- ✅ **自动参数提取**：从自然语言中提取工具参数
- ✅ **多工具支持**：支持复杂的多工具组合
- ✅ **错误处理**：内置错误处理和备用方案
- ✅ **可扩展性**：易于添加新工具

## 🚀 快速开始

### 1. 定义工具

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 工具实现
    return f"{city}天气信息"

@tool
def calculate_math(expression: str) -> str:
    """计算数学表达式"""
    # 工具实现
    return f"计算结果: {eval(expression)}"
```

### 2. 创建工具列表

```python
tools = [get_weather, calculate_math, search_web, translate_text]
```

### 3. 创建 Function Call 代理

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def create_function_call_agent():
    # 系统提示
    system_prompt = """你是一个智能助手，可以根据用户的需求选择合适的工具来帮助用户。

可用工具：
- get_weather: 查询指定城市的天气信息
- calculate_math: 计算数学表达式
- search_web: 搜索网络信息
- translate_text: 翻译文本

请根据用户的问题，选择合适的工具来帮助用户。
"""

    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 创建代理
    agent = create_openai_functions_agent(llm, tools, prompt)
    return agent
```

### 4. 执行代理

```python
# 创建代理执行器
agent = create_function_call_agent()
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

# 执行
result = agent_executor.invoke({"input": "查询北京的天气怎么样"})
print(result["output"])
```

## 📋 在 LangGraph 中使用

### 1. 工具选择节点

```python
def tool_selector(state: ToolState) -> ToolState:
    """使用 function call 方式选择工具"""
    user_input = state["user_input"]
    
    try:
        # 创建代理
        agent = create_function_call_agent()
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
        
        # 执行代理
        result = agent_executor.invoke({"input": user_input})
        
        return {
            "selected_tools": ["function_call_agent"],
            "agent_result": result.get("output", ""),
            "messages": [AIMessage(content=result.get("output", "处理完成"))]
        }
        
    except Exception as e:
        # 备用方案
        return {
            "selected_tools": ["ask_llm"],
            "agent_result": f"处理失败: {str(e)}",
            "messages": [AIMessage(content=f"处理失败: {str(e)}")]
        }
```

### 2. 工具执行节点

```python
def tool_executor(state: ToolState) -> ToolState:
    """执行工具"""
    user_input = state["user_input"]
    selected_tools = state["selected_tools"]
    agent_result = state.get("agent_result", "")
    
    if "function_call_agent" in selected_tools:
        # 使用 function call 结果
        tool_results = [agent_result]
    else:
        # 使用传统方式
        tool_results = []
        # ... 传统工具执行逻辑
    
    return {
        "tool_results": tool_results,
        "messages": [AIMessage(content="工具执行完成")]
    }
```

### 3. 响应合成节点

```python
def response_synthesizer(state: ToolState) -> ToolState:
    """合成最终响应"""
    user_input = state["user_input"]
    selected_tools = state["selected_tools"]
    agent_result = state.get("agent_result", "")
    
    if "function_call_agent" in selected_tools:
        # 直接使用代理结果
        final_response = agent_result
    else:
        # 使用传统方式合成
        final_response = f"根据您的需求 '{user_input}'，我为您提供了以下信息：..."
    
    return {
        "final_response": final_response,
        "messages": [AIMessage(content=final_response)]
    }
```

## 🛠️ 工具定义最佳实践

### 1. 清晰的工具描述

```python
@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息
    
    Args:
        city: 城市名称，如"北京"、"上海"
        
    Returns:
        天气信息字符串，包含温度、天气状况等
    """
    # 工具实现
```

### 2. 参数类型注解

```python
@tool
def calculate_math(expression: str) -> str:
    """计算数学表达式"""
    # 使用类型注解帮助大模型理解参数类型
```

### 3. 错误处理

```python
@tool
def search_web(query: str) -> str:
    """网络搜索工具"""
    try:
        # 搜索逻辑
        return search_results
    except Exception as e:
        return f"搜索失败: {str(e)}"
```

## 🔧 故障排除

### 常见问题

#### 1. 提示模板变量错误
```
Input to ChatPromptTemplate is missing variables {'chat_history'}
```

**解决方案**：
```python
# 移除不需要的变量
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
```

#### 2. 工具调用失败
```
Function call 代理执行失败
```

**解决方案**：
- 检查工具定义是否正确
- 确保工具参数类型匹配
- 添加备用方案

#### 3. 模型无法选择工具
```
模型没有明确选择工具
```

**解决方案**：
- 优化系统提示
- 提供更清晰的工具描述
- 添加示例

### 调试技巧

#### 1. 启用详细日志
```python
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

#### 2. 检查工具列表
```python
print("可用工具:", [tool.name for tool in tools])
```

#### 3. 测试单个工具
```python
result = get_weather("北京")
print(f"工具测试结果: {result}")
```

## 📝 示例代码

### 完整示例

```python
# 1. 导入必要的库
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 2. 定义工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}天气信息"

# 3. 创建工具列表
tools = [get_weather, calculate_math, search_web]

# 4. 创建代理
def create_function_call_agent():
    system_prompt = """你是一个智能助手，可以根据用户的需求选择合适的工具来帮助用户。"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_functions_agent(llm, tools, prompt)
    return agent

# 5. 执行
agent = create_function_call_agent()
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
result = agent_executor.invoke({"input": "查询北京的天气"})
print(result["output"])
```

## 🎯 最佳实践

### 1. 工具设计
- 保持工具功能单一
- 提供清晰的参数说明
- 实现适当的错误处理

### 2. 系统提示
- 明确描述每个工具的功能
- 提供使用示例
- 说明工具选择规则

### 3. 错误处理
- 实现备用方案
- 记录详细日志
- 提供用户友好的错误信息

### 4. 性能优化
- 避免不必要的工具调用
- 缓存常用结果
- 优化提示模板

## 📚 相关资源

- [LangChain Agents 文档](https://python.langchain.com/docs/modules/agents/)
- [Function Calling 指南](https://python.langchain.com/docs/modules/agents/agent_types/openai_functions_agent)
- [工具定义最佳实践](https://python.langchain.com/docs/modules/agents/tools/)

---

**总结**: Function Call 方式提供了更智能、更灵活的工具调用机制，通过大模型自动分析用户意图并选择合适的工具，大大提升了系统的智能性和用户体验。 