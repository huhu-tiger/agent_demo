# LangGraph 工作流可视化指南

## 📊 概述

本指南介绍如何在 LangGraph 中显示和可视化工作流图，帮助您理解节点和边的连接关系。

## 🎯 可视化方法

### 方法1: LangGraph 内置可视化

LangGraph 提供了内置的可视化功能，可以生成 Mermaid 图和图片文件。

```python
from visualization_utils import show_simple_graph

# 显示工作流图
show_simple_graph(workflow, "我的工作流")
```

**输出文件：**
- `工作流名_builtin.md` - Mermaid 代码
- `工作流名_builtin.png` - PNG 图片
- `工作流名_builtin.svg` - SVG 图片

### 方法2: NetworkX 自定义可视化

使用 NetworkX 创建自定义的工作流图，提供更丰富的视觉效果。

```python
from visualization_utils import visualize_workflow

# 显示所有可视化方法
visualize_workflow(workflow, "我的工作流")
```

**输出文件：**
- `工作流名_custom.png` - 自定义 PNG 图片

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install matplotlib networkx ipython
```

### 2. 在代码中使用

```python
# 导入可视化工具
from visualization_utils import visualize_workflow

# 创建工作流
workflow = StateGraph(MyState)
workflow.add_node("node_a", node_a)
workflow.add_node("node_b", node_b)
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

# 显示工作流图
visualize_workflow(workflow, "我的工作流")
```

### 3. 查看结果

运行代码后，您将看到：
- 控制台输出：工作流信息和可视化过程
- 生成的文件：各种格式的工作流图

## 📋 可视化内容

### 工作流信息
- 节点数量和列表
- 边数量
- 入口点
- 条件边信息

### 图形显示
- 节点：用不同颜色区分类型
  - 绿色：开始节点
  - 蓝色：处理节点
  - 红色：结束节点
- 边：显示节点间的连接关系
- 条件：条件边上显示路由条件

## 🎨 自定义选项

### 修改节点颜色
```python
# 在 visualization_utils.py 中修改
node_colors = {
    'start': 'lightgreen',
    'node': 'lightblue', 
    'end': 'lightcoral'
}
```

### 修改图片大小
```python
plt.figure(figsize=(14, 10))  # 宽度, 高度
```

### 修改保存格式
```python
plt.savefig("workflow.png", dpi=300, bbox_inches='tight')
```

## 🔧 故障排除

### 问题1: 可视化组件未安装
```
警告: 可视化组件未安装，请运行: pip install matplotlib networkx ipython
```

**解决方案：**
```bash
pip install matplotlib networkx ipython
```

### 问题2: 无法生成图片
```
无法生成PNG图片: [错误信息]
```

**可能原因：**
- 缺少图形后端
- 权限问题
- 路径问题

**解决方案：**
```python
# 设置 matplotlib 后端
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
```

### 问题3: 中文显示问题
```
中文标签显示为方块
```

**解决方案：**
```python
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
```

## 📝 示例代码

### 基础示例
```python
from langgraph.graph import StateGraph, END
from visualization_utils import visualize_workflow

# 定义状态
class MyState(TypedDict):
    messages: List[Any]
    user_input: str

# 定义节点
def node_a(state: MyState) -> MyState:
    return {"response": "节点A处理完成"}

def node_b(state: MyState) -> MyState:
    return {"response": "节点B处理完成"}

# 创建工作流
workflow = StateGraph(MyState)
workflow.add_node("node_a", node_a)
workflow.add_node("node_b", node_b)
workflow.set_entry_point("node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

# 可视化
visualize_workflow(workflow, "基础工作流示例")
```

### 条件边示例
```python
def route_condition(state: MyState) -> str:
    if "a" in state["user_input"]:
        return "route_to_a"
    else:
        return "route_to_b"

workflow.add_conditional_edges(
    "decision_node",
    route_condition,
    {
        "route_to_a": "node_a",
        "route_to_b": "node_b"
    }
)
```

## 🎯 最佳实践

### 1. 清晰的节点命名
```python
# ✅ 好的命名
workflow.add_node("input_processor", input_processor)
workflow.add_node("data_validator", data_validator)

# ❌ 不好的命名
workflow.add_node("node1", node1)
workflow.add_node("func2", func2)
```

### 2. 模块化设计
```python
# 将相关功能分组
workflow.add_edge("input_validation", "data_processing")
workflow.add_edge("data_processing", "result_generation")
```

### 3. 添加注释
```python
# 在可视化时添加说明
visualize_workflow(workflow, "数据处理工作流 - 包含验证、处理和输出")
```

### 4. 定期更新
```python
# 在工作流修改后重新生成可视化
visualize_workflow(updated_workflow, "更新后的工作流")
```

## 📚 相关资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [Matplotlib 文档](https://matplotlib.org/)
- [NetworkX 文档](https://networkx.org/)
- [Mermaid 语法](https://mermaid.js.org/)

---

**总结**: 工作流可视化是理解和调试 LangGraph 应用的重要工具。通过本指南，您可以轻松地为任何工作流生成清晰的可视化图表。 