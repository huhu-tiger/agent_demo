# ReAct智能体演示

这是一个基于ReAct（Reasoning and Acting）方式的智能体实现，具备工具调用能力，仅使用OpenAI库进行模型调用。

## 功能特点

- **ReAct架构**: 实现了思考(Thought) → 行动(Action) → 观察(Observation)的循环
- **工具调用**: 支持动态添加和执行各种工具
- **对话历史**: 维护完整的对话上下文
- **安全计算**: 内置安全的数学计算工具
- **模型问答处理**: 自动识别并处理模型相关问题

## 内置工具

1. **get_current_time**: 获取当前时间
2. **calculate**: 计算数学表达式（支持基本运算）
3. **get_weather**: 获取天气信息（模拟数据）
4. **search_web**: 搜索网络信息（模拟数据）

## 安装和配置

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 设置OpenAI API密钥：
```bash
export OPENAI_API_KEY="your-api-key-here"
```

或者在代码中直接设置：
```python
openai.api_key = "your-api-key-here"
```

## 使用方法

运行主程序：
```bash
python demo.py
```

## 示例对话

```
用户输入: 计算 15 * 8 + 20
AI响应: 
Thought: 用户需要计算数学表达式，我应该使用calculate工具
Action: calculate
Action Input: {"expression": "15 * 8 + 20"}
工具结果: 工具 calculate 执行成功: 15 * 8 + 20 = 140
Thought: 我已经获得了计算结果，可以给出最终答案
Final Answer: 15 * 8 + 20 = 140

智能体回答: 15 * 8 + 20 = 140
```

## 自定义工具

您可以通过继承`Tool`类来添加自定义工具：

```python
def my_custom_tool(param1: str, param2: int):
    """自定义工具函数"""
    return f"处理结果: {param1} - {param2}"

agent.add_tool(Tool(
    name="my_custom_tool",
    description="自定义工具描述",
    function=my_custom_tool,
    parameters={"param1": "字符串参数", "param2": "整数参数"}
))
```

## ReAct流程说明

1. **Thought**: 智能体分析当前情况，决定需要采取的行动
2. **Action**: 选择要使用的工具
3. **Action Input**: 提供工具的输入参数（JSON格式）
4. **Observation**: 获取工具执行结果
5. **循环**: 根据需要重复上述步骤
6. **Final Answer**: 基于所有观察结果给出最终答案

## 注意事项

- 确保OpenAI API密钥有效且有足够的配额
- 工具函数应该是安全的，避免执行危险操作
- 数学计算工具只允许基本运算，确保安全性
- 程序会自动识别模型相关问题并给出标准回答

## 扩展建议

- 集成真实的天气API
- 添加更多计算工具
- 实现文件操作工具
- 添加网络请求工具
- 实现更复杂的推理链 