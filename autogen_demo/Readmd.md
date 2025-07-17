# 多智能体研究报告生成系统

基于AutoGen框架的智能报告生成平台，支持多源数据检索、图片分析、表格推理等功能。

## 功能特性

- 🤖 **多智能体协作**：基于AutoGen框架，多个专业智能体分工协作
- 🔍 **多源数据检索**：支持博查API、SearXNG等多种搜索源
- 🖼️ **图片智能分析**：自动分析图片内容并生成描述
- 📊 **表格数据推理**：从文本中提取数据并生成结构化表格
- 📝 **Markdown报告生成**：统一输出格式，支持进一步编辑
- 🎨 **双栏界面设计**：左侧报告生成，右侧实时日志显示

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio前端    │    │   FastAPI后端   │    │   多智能体系统   │
│                 │    │                 │    │                 │
│ • 双栏布局      │◄──►│ • RESTful API   │◄──►│ • 搜索智能体    │
│ • 实时日志      │    │ • 模型管理      │    │ • 视觉智能体    │
│ • 报告下载      │    │ • 任务调度      │    │ • 表格推理智能体 │
└─────────────────┘    └─────────────────┘    │ • 报告撰写智能体 │
                                              └─────────────────┘
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd autogen_demo

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2 环境配置

复制环境变量模板并配置：

```bash
cp env_template.env .env
```

编辑 `.env` 文件，配置各模型的API密钥：

```env
# 模型配置
QWEN_PLUS_API_KEY=your_qwen_plus_api_key_here
QWEN_PLUS_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_PLUS_MODEL=qwen-plus-latest

DEEPSEEK_V3_API_KEY=your_deepseek_v3_api_key_here
DEEPSEEK_V3SE_URL=http://your_deepseek_server:302v1
DEEPSEEK_V3_MODEL=deepseek-v3

# 外部API配置
BOCHAI_API_URL=your_bochai_api_url_here
BOCHAI_API_KEY=your_bochai_api_key_here
SEARXNG_API_URL=your_searxng_api_url_here
VISION_API_URL=your_vision_api_url_here

# 系统配置
DEFAULT_MODEL=qwen-plus
LOG_LEVEL=INFO
```

### 3启动服务

#### 启动后端API服务

```bash
# 启动FastAPI后端服务
python -m core.server
```

服务将在 `http://localhost:800 启动

#### 启动前端界面

```bash
# 启动Gradio前端界面
python ui/gradio_app.py
```

界面将在 `http://localhost:7860 启动

###4. 使用系统1. 打开浏览器访问 `http://localhost:78602在左侧输入报告主题，例如：人工智能在金融领域的应用"3. 可选择添加过滤条件（JSON格式）
4. 点击🚀 生成报告"按钮
5. 在右侧查看智能体执行日志6报告生成完成后可下载Markdown文件

## API接口

### 生成报告

```http
POST /generate_report
Content-Type: application/json[object Object]   topic": "人工智能在金融领域的应用",filters: {       date_range:224124-12,
       sources": ["news",reports]    }
}
```

响应：

```json
[object Object]  report_markdown:# 研究报告内容...",
    messageReport generated successfully.",
    execution_time":4523
  agent_logs:PlanningAgent: 开始分析主题...]
}
```

### 获取智能体日志

```http
GET /agent_logs
```

### 获取可用模型

```http
GET /models
```

### 健康检查

```http
GET /health
```

## 智能体说明

系统包含以下专业智能体：

- **PlanningAgent**: 任务规划和协调
- **SearchAgent_BC**: 使用博查API搜索新闻和信息
- **SearchAgent_SX**: 使用SearXNG搜索新闻和图片
- **VisionAgent**: 分析图片内容并生成描述
- **TableReasonerAgent**: 从文本中提取数据并生成表格
- **ReportWriterAgent**: 整合所有信息并生成最终报告

## 配置说明

### 模型配置

每个模型都有独立的环境变量配置：

- `QWEN_PLUS_*`: 通义千问Plus模型
- `DEEPSEEK_V3_*`: DeepSeek V3模型
- `DEEPSEEK_R1_*`: DeepSeek R1模型
- `OPENAI_*`: OpenAI GPT模型
- `CLAUDE_*`: Claude模型

### 系统配置

- `DEFAULT_MODEL`: 默认使用的模型
- `MODEL_SELECTION_STRATEGY`: 模型选择策略
- `MAX_CONCURRENT_REQUESTS`: 最大并发请求数
- `REQUEST_TIMEOUT`: 请求超时时间
- `MAX_RETRIES`: 重试次数

## 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t autogen-demo .

# 运行容器
docker run -p 8000:800-p 7860:7860-env-file .env autogen-demo
```

### Kubernetes部署

```bash
# 应用Kubernetes配置
kubectl apply -f deploy/k8.yaml
```

## 开发指南

### 项目结构

```
autogen_demo/
├── core/                   # 核心模块
│   ├── agents.py          # 智能体定义
│   ├── config.py          # 配置管理
│   ├── models.py          # 数据模型
│   ├── server.py          # FastAPI服务
│   ├── utils.py           # 工具函数
│   └── logging_config.py  # 日志配置
├── ui/                    # 前端界面
│   └── gradio_app.py      # Gradio应用
├── tools/                 # 工具和测试
├── logs/                  # 日志文件
├── deploy/                # 部署配置
├── .env                   # 环境变量
├── env_template.env       # 环境变量模板
└── requirements.txt       # 依赖列表
```

### 添加新模型

1 在 `.env` 文件中添加新模型的环境变量2 在 `core/config.py` 的 `ModelConfigManager` 中添加模型配置
3. 重启服务

### 添加新智能体
1 在 `core/agents.py` 中定义新的智能体类
2`OrchestratorAgent` 中初始化并添加到群聊3. 更新系统消息以包含新智能体的职责

## 故障排除

### 常见问题

1**API密钥错误**: 检查 `.env` 文件中的API密钥配置2. **模型连接失败**: 确认模型服务地址和端口正确3. **前端无法连接后端**: 检查CORS配置和端口设置4. **报告生成超时**: 增加 `REQUEST_TIMEOUT` 配置值

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 贡献指南

1 Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -mAdd some AmazingFeature`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: your-email@example.com

---

**注意**: 请确保在使用前正确配置所有必要的API密钥和环境变量。
