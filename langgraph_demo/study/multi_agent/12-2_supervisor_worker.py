"""
LangGraph Supervisor-Worker 模式示例 (使用 langgraph-supervisor 库)

这个示例展示了如何使用 langgraph-supervisor 库实现supervisor-worker模式：
- Supervisor: 中央协调者，负责决定调用哪个worker
- Worker Agents: 专门的智能体，执行特定任务
- 使用 create_supervisor 函数简化构建过程

主要特点：
1. 使用官方 langgraph-supervisor 库
2. 自动生成 handoff 工具
3. 简化的图构建过程
4. 更好的消息管理
"""
# todo https://github.com/langchain-ai/langgraph-supervisor-py
import os
import sys
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor, create_handoff_tool
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# 添加路径以导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key

# 初始化LLM模型
model = ChatOpenAI(
    model=config.model,
    temperature=0.1,
    max_tokens=1000
)

# 定义工具函数
@tool
def get_weather(location: str) -> str:
    """获取指定地点的天气信息"""
    weather_data = {
        "北京": "晴天，温度25°C，湿度60%",
        "上海": "多云，温度28°C，湿度70%",
        "广州": "雨天，温度30°C，湿度80%",
        "深圳": "晴天，温度29°C，湿度65%",
        "杭州": "多云，温度26°C，湿度65%",
        "成都": "阴天，温度24°C，湿度70%"
    }
    return weather_data.get(location, f"无法获取{location}的天气信息")

@tool
def calculate_math(expression: str) -> str:
    """计算数学表达式"""
    try:
        # 安全的数学表达式计算
        allowed_chars = set('0123456789+-*/(). ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"计算结果: {expression} = {result}"
        else:
            return "表达式包含不允许的字符"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def search_web(query: str) -> str:
    """搜索网络信息"""
    search_results = {
        "人工智能": "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。主要技术包括机器学习、深度学习、自然语言处理等。",
        "机器学习": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。主要算法包括监督学习、无监督学习、强化学习等。",
        "深度学习": "深度学习是机器学习的一个分支，使用多层神经网络来模拟人脑的学习过程。在图像识别、语音识别、自然语言处理等领域取得了突破性进展。",
        "自然语言处理": "自然语言处理是人工智能的一个重要分支，致力于让计算机理解、解释和生成人类语言。应用包括机器翻译、情感分析、问答系统等。",
        "计算机视觉": "计算机视觉是人工智能的一个分支，致力于让计算机理解和分析视觉信息。应用包括图像识别、目标检测、人脸识别等。"
    }
    return search_results.get(query, f"未找到关于'{query}'的相关信息")

@tool
def get_company_info(company: str) -> str:
    """获取公司信息"""
    company_data = {
        "苹果公司": "苹果公司（Apple Inc.）是一家总部位于美国加利福尼亚州的跨国科技公司，主要产品包括iPhone、iPad、Mac、Apple Watch等。",
        "谷歌": "谷歌（Google）是Alphabet公司的子公司，是全球最大的搜索引擎公司，主要业务包括搜索、广告、云计算、人工智能等。",
        "微软": "微软公司（Microsoft Corporation）是一家总部位于美国的跨国科技公司，主要产品包括Windows操作系统、Office办公软件、Azure云服务等。",
        "亚马逊": "亚马逊（Amazon）是全球最大的电子商务公司之一，业务涵盖电商、云计算、人工智能、物流等多个领域。",
        "特斯拉": "特斯拉（Tesla）是一家专注于电动汽车、能源存储和太阳能板的公司，致力于推动可持续能源的发展。"
    }
    return company_data.get(company, f"未找到关于'{company}'的公司信息")

# 创建专门的智能体
def create_research_agent():
    """创建研究智能体"""
    print("🔍 创建研究智能体...")
    research_tools = [search_web, get_company_info]
    return create_react_agent(
        model=model,
        tools=research_tools,
        name="research_expert",
        prompt="你是一个专业的研究助手，擅长信息搜索和知识查询。请帮助用户找到准确、详细的信息。"
    )

def create_math_agent():
    """创建数学智能体"""
    print("🧮 创建数学智能体...")
    math_tools = [calculate_math]
    return create_react_agent(
        model=model,
        tools=math_tools,
        name="math_expert",
        prompt="你是一个专业的数学助手，擅长各种数学计算和公式求解。请帮助用户解决数学问题，并解释计算过程。"
    )

def create_weather_agent():
    """创建天气智能体"""
    print("🌤️ 创建天气智能体...")
    weather_tools = [get_weather]
    return create_react_agent(
        model=model,
        tools=weather_tools,
        name="weather_expert",
        prompt="你是一个专业的天气助手，擅长天气查询和气候信息。请帮助用户获取准确的天气信息，并提供相关建议。"
    )

def build_supervisor_workflow():
    """构建Supervisor工作流"""
    print("🏗️ 正在构建Supervisor工作流...")
    
    # 创建专门的智能体
    research_agent = create_research_agent()
    math_agent = create_math_agent()
    weather_agent = create_weather_agent()
    
    # 创建自定义handoff工具（可选）
    custom_tools = [
        create_handoff_tool(
            agent_name="research_expert",
            name="assign_to_research",
            description="将任务分配给研究专家，用于信息查询、知识搜索、公司信息等任务"
        ),
        create_handoff_tool(
            agent_name="math_expert", 
            name="assign_to_math",
            description="将任务分配给数学专家，用于数学计算、公式求解、数值分析等任务"
        ),
        create_handoff_tool(
            agent_name="weather_expert",
            name="assign_to_weather", 
            description="将任务分配给天气专家，用于天气查询、气候信息、出行建议等任务"
        )
    ]
    
    # 创建supervisor工作流
    workflow = create_supervisor(
        agents=[research_agent, math_agent, weather_agent],
        model=model,
        tools=custom_tools,
        prompt="""你是一个智能团队主管，管理三个专业专家：

1. **研究专家 (research_expert)**: 擅长信息搜索、知识查询、公司信息等
2. **数学专家 (math_expert)**: 擅长数学计算、公式求解、数值分析等  
3. **天气专家 (weather_expert)**: 擅长天气查询、气候信息、出行建议等

根据用户的问题，智能选择最合适的专家来处理任务。确保：
- 每个专家都专注于自己的专业领域
- 提供清晰的任务分配说明
- 如果需要多个专家的协作，按顺序分配任务

请使用相应的工具将任务分配给合适的专家。""",
        add_handoff_messages=True,  # 添加handoff消息到历史记录
        handoff_tool_prefix="assign_to"  # 自定义工具前缀
    )
    
    print("✅ Supervisor工作流构建完成！")
    return workflow.compile()

def run_supervisor_workflow_example():
    """运行Supervisor工作流示例"""
    print("=" * 60)
    print("🚀 LangGraph Supervisor工作流示例")
    print("=" * 60)
    
    # 构建工作流
    app = build_supervisor_workflow()
    
    # 测试用例
    test_cases = [
        "请帮我搜索关于人工智能的最新发展",
        "计算 (15 * 8 + 23) / 4 的结果",
        "查询北京和上海的天气情况",
        "什么是机器学习？请详细解释",
        "计算 2^10 + 3^3 - 5*7",
        "获取苹果公司的基本信息",
        "查询杭州的天气，适合出行吗？",
        "计算圆的面积，半径是5"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"测试用例 {i}: {query}")
        print(f"{'='*50}")
        
        try:
            # 执行工作流
            result = app.invoke({
                "messages": [HumanMessage(content=query)]
            })
            
            # 显示结果
            print("\n📋 处理结果:")
            for msg in result["messages"]:
                if hasattr(msg, 'name') and msg.name:
                    print(f"🤖 {msg.name}: {msg.content}")
                else:
                    print(f"🤖 AI: {msg.content}")
                    
        except Exception as e:
            print(f"❌ 处理失败: {e}")

def run_interactive_example():
    """运行交互式示例"""
    print("=" * 60)
    print("🚀 LangGraph Supervisor交互式示例")
    print("=" * 60)
    print("💡 你可以询问以下类型的问题:")
    print("   - 信息查询: '什么是深度学习？'")
    print("   - 数学计算: '计算 25 * 16 + 8'")
    print("   - 天气查询: '查询上海的天气'")
    print("   - 公司信息: '获取微软公司的信息'")
    print("   - 输入 'quit' 退出")
    print("=" * 60)
    
    # 构建工作流
    app = build_supervisor_workflow()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 请输入你的问题: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
                
            if not user_input:
                continue
                
            print(f"\n🔄 正在处理: {user_input}")
            
            # 执行工作流
            result = app.invoke({
                "messages": [HumanMessage(content=user_input)]
            })
            
            # 显示结果
            print("\n📋 处理结果:")
            for msg in result["messages"]:
                if hasattr(msg, 'name') and msg.name:
                    print(f"🤖 {msg.name}: {msg.content}")
                else:
                    print(f"🤖 AI: {msg.content}")
                    
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 处理失败: {e}")

def run_streaming_example():
    """运行流式输出示例"""
    print("=" * 60)
    print("🚀 LangGraph Supervisor流式输出示例")
    print("=" * 60)
    
    # 构建工作流
    app = build_supervisor_workflow()
    
    # 测试查询
    query = "请帮我搜索关于人工智能的信息，并计算一下如果每天学习2小时，一年能学到多少知识"
    
    print(f"查询: {query}")
    print("\n🔄 流式输出:")
    print("-" * 40)
    
    try:
        # 流式执行
        for chunk in app.stream({
            "messages": [HumanMessage(content=query)]
        }):
            # 显示每个chunk的内容
            if "messages" in chunk:
                for msg in chunk["messages"]:
                    if hasattr(msg, 'name') and msg.name:
                        print(f"🤖 {msg.name}: {msg.content}")
                    else:
                        print(f"🤖 AI: {msg.content}")
            print("-" * 40)
                    
    except Exception as e:
        print(f"❌ 处理失败: {e}")

def main():
    """主函数"""
    print("🎯 LangGraph Supervisor工作流示例")
    print("=" * 60)
    
    # 检查API密钥
    if config.api_key == "your-openai-api-key":
        print("⚠️  请设置有效的OpenAI API密钥")
        print("   可以通过环境变量 OPENAI_API_KEY 设置")
        exit()
    
    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 运行预设测试用例")
    # print("2. 运行交互式示例")
    print("3. 运行流式输出示例")
    
    choice = input("请输入选择 (1, 2 或 3): ").strip()
    
    if choice == "1":
        run_supervisor_workflow_example()
    # elif choice == "2":
        # run_interactive_example()
    elif choice == "3":
        run_streaming_example()
    # else:
    #     print("无效选择，运行预设测试用例...")
    #     run_supervisor_workflow_example()

if __name__ == "__main__":
    main() 