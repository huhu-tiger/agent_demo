"""
LangGraph 分层多智能体示例 (使用 create_supervisor)

这个示例展示了如何使用 langgraph-supervisor 库构建分层多智能体系统：
- 顶层Supervisor: 管理多个团队
- 团队级Supervisor: 管理团队内的专门智能体
- 专门智能体: 执行具体任务

主要特点：
1. 使用 create_supervisor 构建层级结构
2. 团队级别的任务分配
3. 专门智能体的协作
4. 分层消息传递
"""

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
logger = config.logger
# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key

# 初始化LLM模型
model = ChatOpenAI(
    model=config.model,
    temperature=0.1,
    max_tokens=1000
)

# 设置LangGraph配置，关闭并行处理
import os
os.environ["LANGGRAPH_DISABLE_PARALLEL"] = "true"
os.environ["LANGGRAPH_DISABLE_CONCURRENCY"] = "true"

logger.info("🔧 已禁用LangGraph并行处理功能")
logger.info("   - LANGGRAPH_DISABLE_PARALLEL=true")
logger.info("   - LANGGRAPH_DISABLE_CONCURRENCY=true")

# ==================== 工具函数定义 ====================

@tool
def search_web(query: str) -> str:
    """搜索网络信息"""
    logger.info(f"🔍 工具调用: search_web(query='{query}')")
    
    search_results = {
        "人工智能": "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。主要技术包括机器学习、深度学习、自然语言处理等。",
        "机器学习": "机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。主要算法包括监督学习、无监督学习、强化学习等。",
        "深度学习": "深度学习是机器学习的一个分支，使用多层神经网络来模拟人脑的学习过程。在图像识别、语音识别、自然语言处理等领域取得了突破性进展。",
        "自然语言处理": "自然语言处理是人工智能的一个重要分支，致力于让计算机理解、解释和生成人类语言。应用包括机器翻译、情感分析、问答系统等。",
        "计算机视觉": "计算机视觉是人工智能的一个分支，致力于让计算机理解和分析视觉信息。应用包括图像识别、目标检测、人脸识别等。",
        "苹果公司": "苹果公司（Apple Inc.）。参与了人工智能的前沿研究，如Siri、Face ID等。",
    }
    
    # 首先尝试从预设结果中查找
    if query in search_results:
        result = search_results[query]
        logger.info(f"🔍 工具结果: search_web (预设) -> {result[:100]}...")
        print(f"🔍 搜索工具: 查询 '{query}' -> {result[:100]}...")
        return result
    
    # 如果没有找到，使用LLM生成内容
    # logger.info(f"🔍 未找到预设结果，使用LLM生成关于 '{query}' 的内容")
    print(f"🔍 搜索工具: 查询 '{query}' -> 使用LLM生成内容...")
    
    try:
        # 使用LLM生成相关内容
        prompt = f"""请提供关于"{query}"的详细、准确的信息。请包括以下方面：
1. 基本定义和概念
2. 主要特点或技术要点
3. 应用领域或实际用途
4. 相关的发展趋势或重要性

请用中文回答，内容要详细、专业且易于理解。"""
        
        # 调用LLM生成内容
        from langchain_core.messages import HumanMessage
        response = model.invoke([HumanMessage(content=prompt)])
        
        result = response.content
        logger.info(f"🔍 工具结果: search_web (LLM生成) -> {result[:100]}...")
        print(f"🔍 搜索工具: 查询 '{query}' -> {result[:100]}...")
        
        return result
        
    except Exception as e:
        error_msg = f"LLM生成内容失败: {str(e)}"
        logger.error(f"🔍 {error_msg}")
        print(f"🔍 搜索工具: 查询 '{query}' -> {error_msg}")
        return f"抱歉，无法获取关于'{query}'的信息。错误: {str(e)}"

@tool
def get_company_info(company: str) -> str:
    """获取公司信息"""
    logger.info(f"🏢 工具调用: get_company_info(company='{company}')")
    
    company_data = {
        "苹果公司": "苹果公司（Apple Inc.）是一家总部位于美国加利福尼亚州的跨国科技公司，主要产品包括iPhone、iPad、Mac、Apple Watch等。",
        "谷歌": "谷歌（Google）是Alphabet公司的子公司，是全球最大的搜索引擎公司，主要业务包括搜索、广告、云计算、人工智能等。",
        "微软": "微软公司（Microsoft Corporation）是一家总部位于美国的跨国科技公司，主要产品包括Windows操作系统、Office办公软件、Azure云服务等。",
        "亚马逊": "亚马逊（Amazon）是全球最大的电子商务公司之一，业务涵盖电商、云计算、人工智能、物流等多个领域。",
        "特斯拉": "特斯拉（Tesla）是一家专注于电动汽车、能源存储和太阳能板的公司，致力于推动可持续能源的发展。"
    }
    
    # 首先尝试从预设结果中查找
    if company in company_data:
        result = company_data[company]
        logger.info(f"🏢 工具结果: get_company_info (预设) -> {result[:100]}...")
        print(f"🏢 公司信息工具: 查询 '{company}' -> {result[:100]}...")
        return result
    
    # 如果没有找到，使用LLM生成内容
    # logger.info(f"🏢 未找到预设结果，使用LLM生成关于 '{company}' 的公司信息")
    print(f"🏢 公司信息工具: 查询 '{company}' -> 使用LLM生成内容...")
    
    try:
        # 使用LLM生成相关内容
        prompt = f"""请提供关于"{company}"公司的详细、准确的信息。请包括以下方面：
1. 公司基本信息和背景
2. 主要业务和产品
3. 市场地位和影响力
4. 技术实力和创新能力
5. 财务状况和发展前景

请用中文回答，内容要详细、专业且客观。如果信息不确定，请说明。"""
        
        # 调用LLM生成内容
        from langchain_core.messages import HumanMessage
        response = model.invoke([HumanMessage(content=prompt)])
        
        result = response.content
        logger.info(f"🏢 工具结果: get_company_info (LLM生成) -> {result[:100]}...")
        print(f"🏢 公司信息工具: 查询 '{company}' -> {result[:100]}...")
        
        return result
        
    except Exception as e:
        error_msg = f"LLM生成内容失败: {str(e)}"
        logger.error(f"🏢 {error_msg}")
        print(f"🏢 公司信息工具: 查询 '{company}' -> {error_msg}")
        return f"抱歉，无法获取关于'{company}'的公司信息。错误: {str(e)}"

@tool
def calculate_math(expression: str) -> str:
    """计算数学表达式"""
    logger.info(f"🧮 工具调用: calculate_math(expression='{expression}')")
    
    try:
        allowed_chars = set('0123456789+-*/(). ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            output = f"计算结果: {expression} = {result}"
            logger.info(f"🧮 工具结果: calculate_math -> {output}")
            print(f"🧮 数学计算工具: {expression} -> {result}")
            return output
        else:
            output = "表达式包含不允许的字符"
            logger.warning(f"🧮 工具错误: calculate_math -> {output}")
            print(f"🧮 数学计算工具: 错误 - {output}")
            return output
    except Exception as e:
        output = f"计算错误: {str(e)}"
        logger.error(f"🧮 工具异常: calculate_math -> {output}")
        print(f"🧮 数学计算工具: 异常 - {output}")
        return output

@tool
def get_weather(location: str) -> str:
    """获取指定地点的天气信息"""
    logger.info(f"🌤️ 工具调用: get_weather(location='{location}')")
    
    weather_data = {
        "北京": "晴天，温度25°C，湿度60%",
        "上海": "多云，温度28°C，湿度70%",
        "广州": "雨天，温度30°C，湿度80%",
        "深圳": "晴天，温度29°C，湿度65%",
        "杭州": "多云，温度26°C，湿度65%",
        "成都": "阴天，温度24°C，湿度70%"
    }
    
    result = weather_data.get(location, f"无法获取{location}的天气信息")
    logger.info(f"🌤️ 工具结果: get_weather -> {result}")
    print(f"🌤️ 天气查询工具: {location} -> {result}")
    
    return result

@tool
def write_document(content: str, title: str) -> str:
    """创建文档"""
    logger.info(f"📝 工具调用: write_document(title='{title}', content='{content[:50]}...')")
    
    result = f"已创建文档 '{title}'，内容：{content}"
    logger.info(f"📝 工具结果: write_document -> {result[:100]}...")
    print(f"📝 文档创建工具: '{title}' -> 已创建")
    
    return result

@tool
def edit_document(content: str, suggestions: str) -> str:
    """编辑文档"""
    logger.info(f"✏️ 工具调用: edit_document(suggestions='{suggestions[:50]}...', content='{content[:50]}...')")
    
    result = f"根据建议 '{suggestions}' 编辑了文档，新内容：{content}"
    logger.info(f"✏️ 工具结果: edit_document -> {result[:100]}...")
    print(f"✏️ 文档编辑工具: 根据建议编辑 -> 已完成")
    
    return result

@tool
def create_chart(data: str, chart_type: str) -> str:
    """创建图表"""
    logger.info(f"📊 工具调用: create_chart(chart_type='{chart_type}', data='{data[:50]}...')")
    
    result = f"已创建 {chart_type} 类型的图表，数据：{data}"
    logger.info(f"📊 工具结果: create_chart -> {result[:100]}...")
    print(f"📊 图表创建工具: {chart_type} 类型图表 -> 已创建")
    
    return result

# ==================== 第一层：专门智能体 ====================

def create_research_agents():
    """创建研究团队智能体"""
    print("🔍 创建研究团队智能体...")
    logger.info("开始创建研究团队智能体...")
    
    # 搜索专家
    logger.info("创建搜索专家智能体...")
    search_expert = create_react_agent(
        model=model,
        tools=[search_web],
        name="search_expert",
        prompt="你是一个专业的搜索专家，擅长信息检索和知识查询。请帮助用户找到准确、详细的信息。"
    )
    logger.info("搜索专家智能体创建完成")
    
    # 公司分析师
    # logger.info("创建公司分析师智能体...")
    # company_analyst = create_react_agent(
    #     model=model,
    #     tools=[get_company_info],
    #     name="company_analyst",
    #     prompt="你是一个专业的公司分析师，擅长公司信息分析和市场研究。请提供详细的公司分析报告。"
    # )
    # logger.info("公司分析师智能体创建完成")
    
    logger.info("研究团队智能体创建完成，共创建 1 个智能体")
    return [search_expert]

def create_math_agents():
    """创建数学团队智能体"""
    print("🧮 创建数学团队智能体...")
    logger.info("开始创建数学团队智能体...")
    
    # 计算专家
    logger.info("创建计算专家智能体...")
    calculation_expert = create_react_agent(
        model=model,
        tools=[calculate_math],
        name="calculation_expert",
        prompt="你是一个专业的计算专家，擅长各种数学计算和公式求解。请帮助用户解决数学问题，并解释计算过程。"
    )
    logger.info("计算专家智能体创建完成")
    
    logger.info("数学团队智能体创建完成，共创建 1 个智能体")
    return [calculation_expert]

def create_weather_agents():
    """创建天气团队智能体"""
    print("🌤️ 创建天气团队智能体...")
    logger.info("开始创建天气团队智能体...")
    
    # 天气专家
    logger.info("创建天气专家智能体...")
    weather_expert = create_react_agent(
        model=model,
        tools=[get_weather],
        name="weather_expert",
        prompt="你是一个专业的天气专家，擅长天气查询和气候信息分析。请帮助用户获取准确的天气信息，并提供相关建议。"
    )
    logger.info("天气专家智能体创建完成")
    
    logger.info("天气团队智能体创建完成，共创建 1 个智能体")
    return [weather_expert]

def create_writing_agents():
    """创建写作团队智能体"""
    print("✍️ 创建写作团队智能体...")
    logger.info("开始创建写作团队智能体...")
    
    # 文档编写专家
    logger.info("创建文档编写专家智能体...")
    document_writer = create_react_agent(
        model=model,
        tools=[write_document, edit_document],
        name="document_writer",
        prompt="你是一个专业的文档编写专家，擅长创建和编辑各种类型的文档。请帮助用户创建高质量的内容。"
    )
    logger.info("文档编写专家智能体创建完成")
    
    # 图表制作专家
    logger.info("创建图表制作专家智能体...")
    chart_maker = create_react_agent(
        model=model,
        tools=[create_chart],
        name="chart_maker",
        prompt="你是一个专业的图表制作专家，擅长创建各种类型的图表和可视化。请帮助用户制作清晰、美观的图表。"
    )
    logger.info("图表制作专家智能体创建完成")
    
    logger.info("写作团队智能体创建完成，共创建 2 个智能体")
    return [document_writer, chart_maker]

# ==================== 第二层：团队级Supervisor ====================

def create_research_team_supervisor():
    """创建研究团队Supervisor"""
    print("🏗️ 创建研究团队Supervisor...")
    logger.info("开始创建研究团队Supervisor...")
    
    research_agents = create_research_agents()
    logger.info("研究团队智能体创建完成，开始创建handoff工具...")
    
    # 创建团队级handoff工具
    logger.info("创建研究团队handoff工具...")
    research_tools = [
        create_handoff_tool(
            agent_name="search_expert",
            name="assign_to_search",
            description="将任务分配给搜索专家，用于信息检索、知识查询等任务"
        ),
        # create_handoff_tool(
        #     agent_name="company_analyst",
        #     name="assign_to_analyst",
        #     description="获取指定公司的详细信息"
        # )
    ]
    logger.info("研究团队handoff工具创建完成，共创建 1 个工具")
    
    # 创建研究团队Supervisor
    logger.info("创建研究团队Supervisor...")
    research_team = create_supervisor(
        agents=research_agents,
        model=model,
        tools=research_tools,
        prompt="""你是研究团队的负责人，管理两个专业专家：

1. **搜索专家 (search_expert)**: 擅长信息检索、知识查询、网络搜索等

根据任务需求，智能选择最合适的专家来处理。确保：
- 信息查询类任务分配给搜索专家
- 公司分析类任务分配给公司分析师
- 提供清晰的任务分配说明
- 避免循环调用，每个任务只分配给一个专家

请使用相应的工具将任务分配给合适的专家。""",
        add_handoff_messages=True,
        handoff_tool_prefix="assign_to",
        checkpointer=None,  # 禁用检查点，确保串行执行
        recursion_limit=30  # 增加递归限制
    )
    
    logger.info("研究团队Supervisor创建完成，开始编译...")
    compiled_team = research_team.compile(name="research_team")
    logger.info("研究团队Supervisor编译完成")
    
    return compiled_team

def create_math_team_supervisor():
    """创建数学团队Supervisor"""
    print("🏗️ 创建数学团队Supervisor...")
    logger.info("开始创建数学团队Supervisor...")
    
    math_agents = create_math_agents()
    logger.info("数学团队智能体创建完成，开始创建handoff工具...")
    
    # 创建团队级handoff工具
    logger.info("创建数学团队handoff工具...")
    math_tools = [
        create_handoff_tool(
            agent_name="calculation_expert",
            name="assign_to_calculator",
            description="将任务分配给计算专家，用于数学计算、公式求解、数值分析等任务"
        )
    ]
    logger.info("数学团队handoff工具创建完成，共创建 1 个工具")
    
    # 创建数学团队Supervisor
    logger.info("创建数学团队Supervisor...")
    math_team = create_supervisor(
        agents=math_agents,
        model=model,
        tools=math_tools,
        prompt="""你是数学团队的负责人，管理计算专家：

**计算专家 (calculation_expert)**: 擅长各种数学计算、公式求解、数值分析等

根据任务需求，将数学相关的任务分配给计算专家。确保：
- 提供清晰的计算要求
- 解释计算过程和结果
- 处理复杂的数学表达式

请使用相应的工具将任务分配给计算专家。""",
        add_handoff_messages=True,
        handoff_tool_prefix="assign_to",
        checkpointer=None  # 禁用检查点，确保串行执行
    )
    
    logger.info("数学团队Supervisor创建完成，开始编译...")
    compiled_team = math_team.compile(name="math_team")
    logger.info("数学团队Supervisor编译完成")
    
    return compiled_team

def create_weather_team_supervisor():
    """创建天气团队Supervisor"""
    print("🏗️ 创建天气团队Supervisor...")
    logger.info("开始创建天气团队Supervisor...")
    
    weather_agents = create_weather_agents()
    logger.info("天气团队智能体创建完成，开始创建handoff工具...")
    
    # 创建团队级handoff工具
    logger.info("创建天气团队handoff工具...")
    weather_tools = [
        create_handoff_tool(
            agent_name="weather_expert",
            name="assign_to_weather",
            description="将任务分配给天气专家，用于天气查询、气候信息、出行建议等任务"
        )
    ]
    logger.info("天气团队handoff工具创建完成，共创建 1 个工具")
    
    # 创建天气团队Supervisor
    logger.info("创建天气团队Supervisor...")
    weather_team = create_supervisor(
        agents=weather_agents,
        model=model,
        tools=weather_tools,
        prompt="""你是天气团队的负责人，管理天气专家：

**天气专家 (weather_expert)**: 擅长天气查询、气候信息分析、出行建议等

根据任务需求，将天气相关的任务分配给天气专家。确保：
- 提供准确的天气信息
- 分析气候趋势
- 给出出行建议

请使用相应的工具将任务分配给天气专家。""",
        add_handoff_messages=True,
        handoff_tool_prefix="assign_to",
        checkpointer=None  # 禁用检查点，确保串行执行
    )
    
    logger.info("天气团队Supervisor创建完成，开始编译...")
    compiled_team = weather_team.compile(name="weather_team")
    logger.info("天气团队Supervisor编译完成")
    
    return compiled_team

def create_writing_team_supervisor():
    """创建写作团队Supervisor"""
    print("🏗️ 创建写作团队Supervisor...")
    logger.info("开始创建写作团队Supervisor...")
    
    writing_agents = create_writing_agents()
    logger.info("写作团队智能体创建完成，开始创建handoff工具...")
    
    # 创建团队级handoff工具
    logger.info("创建写作团队handoff工具...")
    writing_tools = [
        create_handoff_tool(
            agent_name="document_writer",
            name="assign_to_writer",
            description="将任务分配给文档编写专家，用于文档创建、内容编辑、报告撰写等任务"
        ),
        create_handoff_tool(
            agent_name="chart_maker",
            name="assign_to_chart_maker",
            description="将任务分配给图表制作专家，用于图表创建、数据可视化、图形设计等任务"
        )
    ]
    logger.info("写作团队handoff工具创建完成，共创建 2 个工具")
    logger.info(f"写作团队工具列表: {[tool.name for tool in writing_tools]}")
    
    # 创建写作团队Supervisor
    logger.info("创建写作团队Supervisor...")
    writing_team = create_supervisor(
        agents=writing_agents,
        model=model,
        tools=writing_tools,
        prompt="""你是写作团队的负责人，管理两个专业专家：

1. **文档编写专家 (document_writer)**: 擅长文档创建、内容编辑、报告撰写等
2. **图表制作专家 (chart_maker)**: 擅长图表创建、数据可视化、图形设计等

根据任务需求，智能选择最合适的专家来处理。确保：
- 文档编写类任务分配给文档编写专家
- 图表制作类任务分配给图表制作专家
- 提供清晰的任务要求和指导
- 避免循环调用，每个任务只分配给一个专家

请使用相应的工具将任务分配给合适的专家。""",
        add_handoff_messages=True,
        handoff_tool_prefix="assign_to",
        checkpointer=None,  # 禁用检查点，确保串行执行
        recursion_limit=30  # 增加递归限制
    )
    
    logger.info("写作团队Supervisor创建完成，开始编译...")
    compiled_team = writing_team.compile(name="writing_team")
    logger.info("写作团队Supervisor编译完成")
    
    return compiled_team

# ==================== 第三层：顶层Supervisor ====================

def create_top_level_supervisor():
    """创建顶层Supervisor"""
    print("🏗️ 创建顶层Supervisor...")
    logger.info("开始创建顶层Supervisor...")
    
    # 创建各个团队
    logger.info("开始创建各个专业团队...")
    research_team = create_research_team_supervisor()
    logger.info("研究团队创建完成")
    
    math_team = create_math_team_supervisor()
    logger.info("数学团队创建完成")
    
    weather_team = create_weather_team_supervisor()
    logger.info("天气团队创建完成")
    
    writing_team = create_writing_team_supervisor()
    logger.info("写作团队创建完成")
    
    logger.info("所有专业团队创建完成，开始创建顶层handoff工具...")
    
    # 创建顶层handoff工具
    logger.info("创建顶层handoff工具...")
    top_level_tools = [
        create_handoff_tool(
            agent_name="research_team",
            name="assign_to_research_team",
            description="将任务分配给研究团队，用于信息查询、知识搜索、公司分析等任务"
        ),
        create_handoff_tool(
            agent_name="math_team",
            name="assign_to_math_team",
            description="将任务分配给数学团队，用于数学计算、公式求解、数值分析等任务"
        ),
        create_handoff_tool(
            agent_name="weather_team",
            name="assign_to_weather_team",
            description="将任务分配给天气团队，用于天气查询、气候信息、出行建议等任务"
        ),
        create_handoff_tool(
            agent_name="writing_team",
            name="assign_to_writing_team",
            description="将任务分配给写作团队，用于文档编写、图表制作、内容创作等任务"
        )
    ]
    logger.info("顶层handoff工具创建完成，共创建 4 个工具")
    logger.info(f"顶层工具列表: {[tool.name for tool in top_level_tools]}")
    
    # 创建顶层Supervisor
    logger.info("创建顶层Supervisor...")
    top_level = create_supervisor(
        agents=[research_team, math_team, weather_team, writing_team],
        model=model,
        tools=top_level_tools,
        prompt="""你是整个智能体系统的总负责人，管理四个专业团队：

1. **研究团队 (research_team)**: 擅长信息查询、知识搜索、公司分析等
2. **数学团队 (math_team)**: 擅长数学计算、公式求解、数值分析等
3. **天气团队 (weather_team)**: 擅长天气查询、气候信息、出行建议等
4. **写作团队 (writing_team)**: 擅长文档编写、图表制作、内容创作等

根据用户的需求，智能选择最合适的团队来处理任务。确保：
- 每个团队都专注于自己的专业领域
- 提供清晰的任务分配说明
- 如果需要多个团队的协作，按顺序分配任务
- 优先考虑任务的核心需求
- 避免循环调用，每个任务只分配给一个团队处理

经验:
1. 咨询检索类任务，优先分配给 research_team
2. 数学类任务，分配给 math_team
3. 天气类任务，分配给 weather_team
4. 编写文档类任务，分配给 writing_team
5. 避免同时分配给多个团队，防止循环调用

请使用相应的工具将任务分配给合适的团队。""",
        add_handoff_messages=True,
        handoff_tool_prefix="assign_to",
        checkpointer=None,  # 禁用检查点，确保串行执行
        recursion_limit=50  # 增加递归限制
    )
    
    logger.info("顶层Supervisor创建完成，开始生成可视化图表...")
    
    # 可视化工作流程图
    from show_graph import show_workflow_graph
    
    # 生成工作流图的 PNG 格式，用于文档和演示
    # 可以根据需要选择不同的格式：
    # - formats=['md']: 只生成 Markdown 文件
    # - formats=['mmd']: 只生成 Mermaid 代码文件  
    # - formats=['png']: 只生成 PNG 图片
    # - formats=['png', 'md', 'mmd']: 生成多种格式
    show_workflow_graph(top_level, "分层多智能体工作流", logger, "分层多智能体模式演示", formats=['png'])
    
    logger.info("可视化图表生成完成，开始编译顶层Supervisor...")
    compiled_system = top_level.compile(name="hierarchical_system")
    logger.info("顶层Supervisor编译完成，分层系统构建完成")
    
    return compiled_system

# ==================== 运行示例 ====================

def validate_tool_configuration():
    """验证工具配置是否正确"""
    logger.info("🔍 开始验证工具配置...")
    
    try:
        # 创建各个团队并验证工具
        research_team = create_research_team_supervisor()
        math_team = create_math_team_supervisor()
        weather_team = create_weather_team_supervisor()
        writing_team = create_writing_team_supervisor()
        
        # 创建顶层Supervisor
        top_level = create_top_level_supervisor()
        
        logger.info("✅ 工具配置验证完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 工具配置验证失败: {e}")
        logger.exception("详细错误信息:")
        return False

def print_debug_info(chunk, chunk_count):
    """打印详细的调试信息"""
    print(f"\n🔍 DEBUG - 数据块 {chunk_count} 详细信息:")
    print("=" * 60)
    
    # 打印chunk的所有键值对
    print("📋 数据块键值对:")
    for key, value in chunk.items():
        if isinstance(value, list):
            print(f"   {key}: 列表，长度 {len(value)}")
        elif isinstance(value, dict):
            print(f"   {key}: 字典，键数量 {len(value)}")
        else:
            print(f"   {key}: {type(value).__name__} = {value}")
    
    # 如果有messages，显示详细信息
    if "messages" in chunk:
        print(f"\n📨 消息详细信息:")
        for i, msg in enumerate(chunk["messages"], 1):
            print(f"\n   消息 {i}:")
            print(f"     类型: {type(msg).__name__}")
            print(f"     内容长度: {len(str(msg.content))} 字符")
            
            # 显示所有属性
            print(f"     所有属性:")
            for attr_name in dir(msg):
                if not attr_name.startswith('_'):
                    try:
                        attr_value = getattr(msg, attr_name)
                        if not callable(attr_value):
                            print(f"       {attr_name}: {attr_value}")
                    except:
                        pass
    
    print("-" * 60)

def print_complete_result(result, title="处理结果"):
    """打印完整的结果信息"""
    print(f"\n📋 {title}:")
    print("=" * 60)
    
    # 打印完整的result字典结构
    print("🔍 完整结果结构:")
    for key, value in result.items():
        if key == "messages":
            print(f"📨 {key}: {len(value)} 条消息")
        else:
            print(f"📋 {key}: {value}")
    
    print("\n📨 详细消息内容:")
    print("-" * 40)
    
    message_count = 0
    team_executions = {}
    
    for msg in result["messages"]:
        message_count += 1
        print(f"\n📝 消息 {message_count}:")
        print(f"   类型: {type(msg).__name__}")
        
        if hasattr(msg, 'name') and msg.name:
            print(f"   发送者: {msg.name}")
            print(f"   内容: {msg.content}")
            logger.info(f"消息 {message_count}: {msg.name} -> {msg.content}")
            
            # 统计团队执行情况
            if msg.name in team_executions:
                team_executions[msg.name] += 1
            else:
                team_executions[msg.name] = 1
        else:
            print(f"   发送者: AI")
            print(f"   内容: {msg.content}")
            logger.info(f"消息 {message_count}: AI -> {msg.content}")
        
        # 打印消息的其他属性
        for attr in ['type', 'additional_kwargs', 'response_metadata']:
            if hasattr(msg, attr):
                value = getattr(msg, attr)
                if value:
                    print(f"   {attr}: {value}")
    
    print("-" * 40)
    print(f"✅ 共处理 {message_count} 条消息")
    
    # 显示团队执行统计
    if team_executions:
        print("\n📊 团队执行统计:")
        logger.info("团队执行统计:")
        for team, count in team_executions.items():
            print(f"   {team}: {count} 次执行")
            logger.info(f"   {team}: {count} 次执行")
    
    return message_count, team_executions

def run_hierarchical_example():
    """运行分层示例"""
    print("=" * 60)
    print("🚀 LangGraph 分层多智能体示例")
    print("=" * 60)
    
    logger.info("开始构建分层多智能体系统...")
    
    # 构建分层系统
    hierarchical_system = create_top_level_supervisor()
    
    logger.info("分层系统构建完成，开始执行测试用例...")
    
    # 测试用例 - 简化为单一任务，避免循环调用
    test_cases = [
        "搜索关于人工智能的信息,并创建一个综合分析报告",
        # "获取苹果公司的基本信息",
        # "计算 2^10 + 3^3 - 5*7"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🧪 测试用例 {i}: {query}")
        print(f"{'='*60}")
        
        logger.info(f"开始执行测试用例 {i}: {query}")
        
        try:
            print(f"\n🔄 正在处理查询: {query}")
            logger.info(f"调用分层系统处理查询: {query}")
            
            # 执行分层系统
            result = hierarchical_system.invoke({
                "messages": [HumanMessage(content=query)],
                "stream_mode":"values"
            })
            
            logger.info(f"测试用例 {i} 执行完成，开始显示结果")
            
            # 使用专门的函数打印完整结果
            message_count, team_executions = print_complete_result(result, f"测试用例 {i} 完整处理结果")
            logger.info(f"测试用例 {i} 完成，共处理 {message_count} 条消息")
                    
        except Exception as e:
            error_msg = f"❌ 测试用例 {i} 处理失败: {e}"
            print(error_msg)
            logger.error(f"测试用例 {i} 处理失败: {e}")
            logger.exception("详细错误信息:")
            
            # 如果是工具调用错误，提供更详细的诊断信息
            if "is not a valid tool" in str(e):
                print("\n🔍 工具调用错误诊断:")
                print("   这通常是由于以下原因之一:")
                print("   1. 工具名称不匹配")
                print("   2. 工具未正确注册")
                print("   3. 层级结构中的工具作用域问题")
                print("   4. 智能体配置错误")
                print("\n   建议:")
                print("   - 检查工具名称是否正确")
                print("   - 验证智能体配置")
                print("   - 确认层级结构设置")
                print("   - 运行工具配置验证 (选项4)")

def run_streaming_example():
    """运行流式输出示例"""
    print("=" * 60)
    print("🚀 LangGraph 分层系统流式输出示例 (DEBUG模式)")
    print("=" * 60)
    
    logger.info("开始构建分层系统用于流式输出...")
    
    # 构建分层系统
    hierarchical_system = create_top_level_supervisor()
    
    # 测试查询 - 简化为单一任务，避免循环调用
    query = "请帮我搜索关于人工智能的信息"
    
    print(f"查询: {query}")
    logger.info(f"流式查询: {query}")
    print("\n🔄 流式输出 (stream_mode=debug):")
    print("🔍 DEBUG模式将显示详细的执行过程和完整内容")
    print("-" * 60)
    
    try:
        chunk_count = 0
        team_executions = {}
        all_messages = []
        
        # 流式执行
        for chunk in hierarchical_system.stream({
            "messages": [HumanMessage(content=query)],
            "stream_mode":"debug"
        }):
            chunk_count += 1
            logger.info(f"收到第 {chunk_count} 个数据块")
            
            # 调用debug信息显示函数
            print_debug_info(chunk, chunk_count)
            
            # 显示每个chunk的完整内容 (debug模式)
            print(f"\n🔍 DEBUG - 数据块 {chunk_count} 完整信息:")
            print("=" * 60)
            
            # 打印chunk的完整结构
            print("🔍 数据块结构:")
            for key, value in chunk.items():
                if key == "messages":
                    print(f"📨 {key}: {len(value)} 条消息")
                    all_messages.extend(value)
                else:
                    print(f"📋 {key}: {value}")
            
            if "messages" in chunk:
                print(f"\n📨 数据块 {chunk_count} 详细消息:")
                for i, msg in enumerate(chunk["messages"], 1):
                    print(f"\n📝 消息 {i}:")
                    print(f"   类型: {type(msg).__name__}")
                    
                    if hasattr(msg, 'name') and msg.name:
                        print(f"   发送者: {msg.name}")
                        print(f"   内容: {msg.content}")
                        logger.info(f"数据块 {chunk_count} - 消息 {i}: {msg.name} -> {msg.content}")
                        
                        # 统计团队执行情况
                        if msg.name in team_executions:
                            team_executions[msg.name] += 1
                        else:
                            team_executions[msg.name] = 1
                    else:
                        print(f"   发送者: AI")
                        print(f"   内容: {msg.content}")
                        logger.info(f"数据块 {chunk_count} - 消息 {i}: AI -> {msg.content}")
                    
                    # 打印消息的其他属性 (debug模式)
                    print("   属性信息:")
                    for attr in ['type', 'additional_kwargs', 'response_metadata']:
                        if hasattr(msg, attr):
                            value = getattr(msg, attr)
                            if value:
                                print(f"     {attr}: {value}")
                    
                    # 打印消息的完整内容 (debug模式)
                    print(f"   完整内容:")
                    print(f"     {msg.content}")
            else:
                print(f"📦 数据块 {chunk_count} 内容: {chunk}")
                logger.info(f"数据块 {chunk_count}: {chunk}")
            
            print("-" * 60)
        
        logger.info(f"流式输出完成，共处理 {chunk_count} 个数据块")
        print(f"\n✅ 流式输出完成，共处理 {chunk_count} 个数据块")
        
        # 显示最终汇总 (debug模式)
        print(f"\n📊 DEBUG - 最终汇总:")
        print("=" * 40)
        print(f"   总数据块数: {chunk_count}")
        print(f"   总消息数: {len(all_messages)}")
        
        # 显示所有消息的统计信息
        print(f"\n📋 消息类型统计:")
        message_types = {}
        for msg in all_messages:
            msg_type = type(msg).__name__
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        for msg_type, count in message_types.items():
            print(f"   {msg_type}: {count} 条")
        
        # 显示团队执行统计
        if team_executions:
            print(f"\n📊 团队执行统计:")
            logger.info("团队执行统计:")
            for team, count in team_executions.items():
                print(f"   {team}: {count} 次执行")
                logger.info(f"   {team}: {count} 次执行")
        
        print("=" * 40)
                    
    except Exception as e:
        error_msg = f"❌ 流式处理失败: {e}"
        print(error_msg)
        logger.error(f"流式处理失败: {e}")
        logger.exception("详细错误信息:")
        
        # 如果是工具调用错误，提供更详细的诊断信息
        if "is not a valid tool" in str(e):
            print("\n🔍 工具调用错误诊断:")
            print("   这通常是由于以下原因之一:")
            print("   1. 工具名称不匹配")
            print("   2. 工具未正确注册")
            print("   3. 层级结构中的工具作用域问题")
            print("   4. 智能体配置错误")
            print("\n   建议:")
            print("   - 检查工具名称是否正确")
            print("   - 验证智能体配置")
            print("   - 确认层级结构设置")
            print("   - 运行工具配置验证 (选项4)")



def main():
    """主函数"""
    print("🎯 LangGraph 分层多智能体示例")
    print("=" * 60)
    
    logger.info("启动分层多智能体示例程序")
    
    # 检查API密钥
    if config.api_key == "your-openai-api-key":
        error_msg = "⚠️  请设置有效的OpenAI API密钥"
        print(error_msg)
        print("   可以通过环境变量 OPENAI_API_KEY 设置")
        logger.error("API密钥未设置，程序退出")
        exit()
    
    logger.info("API密钥检查通过")
    
    # 选择运行模式
    # print("\n请选择运行模式:")
    # print("1. 运行预设测试用例")
    # print("2. 运行流式输出示例")
    # print("3. 验证工具配置")
    
    # choice = input("请输入选择 (1, 2 或 3): ").strip()
    # logger.info(f"用户选择运行模式: {choice}")
    
    # if choice == "1":
    #     logger.info("开始运行预设测试用例")
    run_hierarchical_example()
    # elif choice == "2":
    logger.info("开始运行流式输出示例")
    # run_streaming_example()
    # elif choice == "3":
    #     logger.info("开始验证工具配置")
    #     validate_tool_configuration()
    # else:
    #     logger.warning(f"无效选择: {choice}，默认运行预设测试用例")
    #     print("无效选择，运行预设测试用例...")
    #     run_hierarchical_example()
    
    logger.info("程序执行完成")

if __name__ == "__main__":
    main()
