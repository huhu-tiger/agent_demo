"""
LangGraph Swarm 架构示例

本示例演示了如何使用 LangGraph Swarm 构建多智能体协作系统。
包含以下功能：
1. 多个专业智能体的定义
2. 智能体之间的切换机制
3. 状态管理和记忆
4. 流式输出和可视化
"""

import os
import uuid
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
from langgraph.types import interrupt, Command
from langchain_core.messages import ToolMessage
import sys

# 配置相关导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 设置 OpenAI API 环境变量
os.environ["OPENAI_API_BASE"] = config.base_url  # API 基础URL
os.environ["OPENAI_API_KEY"] = config.api_key    # API 密钥

# 初始化语言模型
model = ChatOpenAI(
    model=config.model,
    temperature=0.1,
    max_tokens=1000
)

# 模拟数据存储
USER_DATA = {
    "user_123": {
        "name": "张三",
        "preferences": ["技术", "编程", "AI"],
        "subscription": "premium"
    }
}

BOOKINGS = {
    "user_123": {
        "flights": [],
        "hotels": [],
        "activities": []
    }
}

# 模拟航班数据
FLIGHTS = [
    {
        "id": "FL001",
        "from": "北京",
        "to": "上海",
        "airline": "中国国航",
        "departure": "2024-01-15 10:00",
        "arrival": "2024-01-15 12:00",
        "price": 800
    },
    {
        "id": "FL002", 
        "from": "北京",
        "to": "广州",
        "airline": "南方航空",
        "departure": "2024-01-15 14:00",
        "arrival": "2024-01-15 17:00",
        "price": 1200
    }
]

# 模拟酒店数据
HOTELS = [
    {
        "id": "HT001",
        "name": "北京希尔顿酒店",
        "location": "北京朝阳区",
        "price": 800,
        "rating": 4.5
    },
    {
        "id": "HT002",
        "name": "上海外滩华尔道夫酒店",
        "location": "上海黄浦区",
        "price": 1500,
        "rating": 4.8
    }
]

# 模拟活动数据
ACTIVITIES = [
    {
        "id": "AC001",
        "name": "故宫博物院参观",
        "location": "北京",
        "duration": "3小时",
        "price": 60
    },
    {
        "id": "AC002",
        "name": "外滩夜景游船",
        "location": "上海",
        "duration": "2小时", 
        "price": 120
    }
]


# ==================== 工具函数定义 ====================

def search_flights(from_city: str, to_city: str, date: str) -> List[Dict[str, Any]]:
    """
    搜索航班信息
    
    Args:
        from_city: 出发城市
        to_city: 到达城市
        date: 日期 (YYYY-MM-DD)
        
    Returns:
        符合条件的航班列表
    """
    # 模拟搜索逻辑
    available_flights = []
    for flight in FLIGHTS:
        if flight["from"] == from_city and flight["to"] == to_city:
            available_flights.append(flight)
    
    if not available_flights:
        return [{"message": f"抱歉，没有找到从 {from_city} 到 {to_city} 的航班"}]
    
    return available_flights


def book_flight(flight_id: str, user_id: str) -> str:
    """
    预订航班
    
    Args:
        flight_id: 航班ID
        user_id: 用户ID
        
    Returns:
        预订结果
    """
    flight = next((f for f in FLIGHTS if f["id"] == flight_id), None)
    if not flight:
        return "错误：航班不存在"
    
    if user_id not in BOOKINGS:
        BOOKINGS[user_id] = {"flights": [], "hotels": [], "activities": []}
    
    BOOKINGS[user_id]["flights"].append(flight)
    return f"成功预订航班：{flight['from']} -> {flight['to']}，航班号：{flight['airline']}"


def search_hotels(location: str, check_in: str, check_out: str) -> List[Dict[str, Any]]:
    """
    搜索酒店信息
    
    Args:
        location: 城市名称
        check_in: 入住日期
        check_out: 退房日期
        
    Returns:
        符合条件的酒店列表
    """
    available_hotels = []
    for hotel in HOTELS:
        if location in hotel["location"]:
            available_hotels.append(hotel)
    
    if not available_hotels:
        return [{"message": f"抱歉，在 {location} 没有找到合适的酒店"}]
    
    return available_hotels


def book_hotel(hotel_id: str, user_id: str, check_in: str, check_out: str) -> str:
    """
    预订酒店
    
    Args:
        hotel_id: 酒店ID
        user_id: 用户ID
        check_in: 入住日期
        check_out: 退房日期
        
    Returns:
        预订结果
    """
    hotel = next((h for h in HOTELS if h["id"] == hotel_id), None)
    if not hotel:
        return "错误：酒店不存在"
    
    if user_id not in BOOKINGS:
        BOOKINGS[user_id] = {"flights": [], "hotels": [], "activities": []}
    
    booking_info = {
        **hotel,
        "check_in": check_in,
        "check_out": check_out
    }
    BOOKINGS[user_id]["hotels"].append(booking_info)
    return f"成功预订酒店：{hotel['name']}，入住：{check_in}，退房：{check_out}"


def search_activities(location: str) -> List[Dict[str, Any]]:
    """
    搜索活动信息
    
    Args:
        location: 城市名称
        
    Returns:
        符合条件的活动列表
    """
    available_activities = []
    for activity in ACTIVITIES:
        if location in activity["location"]:
            available_activities.append(activity)
    
    if not available_activities:
        return [{"message": f"抱歉，在 {location} 没有找到合适的活动"}]
    
    return available_activities


def book_activity(activity_id: str, user_id: str, date: str) -> str:
    """
    预订活动
    
    Args:
        activity_id: 活动ID
        user_id: 用户ID
        date: 活动日期
        
    Returns:
        预订结果
    """
    activity = next((a for a in ACTIVITIES if a["id"] == activity_id), None)
    if not activity:
        return "错误：活动不存在"
    
    if user_id not in BOOKINGS:
        BOOKINGS[user_id] = {"flights": [], "hotels": [], "activities": []}
    
    booking_info = {
        **activity,
        "date": date
    }
    BOOKINGS[user_id]["activities"].append(booking_info)
    return f"成功预订活动：{activity['name']}，日期：{date}"


def get_user_info(user_id: str) -> Dict[str, Any]:
    """
    获取用户信息
    
    Args:
        user_id: 用户ID
        
    Returns:
        用户信息
    """
    return USER_DATA.get(user_id, {
        "name": "未知用户",
        "preferences": [],
        "subscription": "basic"
    })


def get_user_bookings(user_id: str) -> Dict[str, Any]:
    """
    获取用户预订信息
    
    Args:
        user_id: 用户ID
        
    Returns:
        用户预订信息
    """
    return BOOKINGS.get(user_id, {"flights": [], "hotels": [], "activities": []})


# ==================== 人工交互确认工具 ====================

def get_user_input(prompt: str) -> str:
    """
    获取用户输入
    
    Args:
        prompt: 提示信息
    
    Returns:
        用户输入的字符串
    """
    print(f"\n{'='*50}")
    print(f"🤖 系统提示: {prompt}")
    print(f"{'='*50}")
    
    while True:
        try:
            user_input = input("👤 请输入: ").strip()
            if user_input:
                return user_input
            else:
                print("❌ 输入不能为空，请重新输入")
        except KeyboardInterrupt:
            print("\n⚠️ 检测到 Ctrl+C，程序退出")
            exit(0)
        except EOFError:
            print("\n⚠️ 检测到 EOF，程序退出")
            exit(0)


def confirm_flight_params_interrupt(from_city: str = None, to_city: str = None, date: str = None, tool_call_id: str = None) -> Command:
    """
    使用 interrupt 机制确认航班搜索参数
    
    Args:
        from_city: 出发城市
        to_city: 到达城市
        date: 日期
        tool_call_id: 工具调用ID
        
    Returns:
        Command 对象，包含用户输入的参数
    """
    # 总是使用 interrupt 来确认参数，无论是否已有参数
    current_params = {
        "from_city": from_city or "",
        "to_city": to_city or "",
        "date": date or ""
    }
    
    missing_params = []
    if not from_city:
        missing_params.append("出发城市")
    if not to_city:
        missing_params.append("到达城市")
    if not date:
        missing_params.append("日期")
    
    # 总是触发中断来确认参数
    if missing_params:
        message = f"请提供以下缺失的航班搜索参数：{', '.join(missing_params)}"
    else:
        message = f"请确认航班搜索参数：从 {from_city} 到 {to_city}，日期：{date}"
    
    # 使用 interrupt 暂停执行，等待用户输入
    interrupt_data = {
        "message": message,
        "required_params": missing_params,
        "current_params": current_params,
        "format_hint": "请分别告诉我：出发城市、到达城市、出行日期（格式：YYYY-MM-DD）"
    }
    
    # 调用 interrupt 函数暂停执行
    user_input = interrupt(interrupt_data)
    
    # 解析用户输入（简单解析，实际应用中可能需要更复杂的解析）
    parts = user_input.split('，')
    if len(parts) >= 3:
        new_from_city = parts[0].strip()
        new_to_city = parts[1].strip()
        new_date = parts[2].strip()
    else:
        # 如果解析失败，返回原始输入
        new_from_city = from_city or user_input
        new_to_city = to_city or user_input
        new_date = date or user_input
    
    # 创建 ToolMessage
    tool_message = ToolMessage(
        content=f"已确认航班参数：从 {new_from_city} 到 {new_to_city}，日期：{new_date}",
        tool_call_id=tool_call_id,
        name="confirm_flight_params_interrupt"
    )
    
    return Command(
        update={
            "flight_params": {
                "from_city": new_from_city,
                "to_city": new_to_city,
                "date": new_date
            },
            "messages": [tool_message]
        }
    )


def confirm_hotel_params_interrupt(city: str = None, check_in: str = None, check_out: str = None, tool_call_id: str = None) -> Command:
    """
    使用 interrupt 机制确认酒店搜索参数
    
    Args:
        city: 城市
        check_in: 入住日期
        check_out: 退房日期
        tool_call_id: 工具调用ID
        
    Returns:
        Command 对象，包含用户输入的参数
    """
    # 总是使用 interrupt 来确认参数，无论是否已有参数
    current_params = {
        "city": city or "",
        "check_in": check_in or "",
        "check_out": check_out or ""
    }
    
    missing_params = []
    if not city:
        missing_params.append("城市")
    if not check_in:
        missing_params.append("入住日期")
    if not check_out:
        missing_params.append("退房日期")
    
    # 总是触发中断来确认参数
    if missing_params:
        message = f"请提供以下缺失的酒店搜索参数：{', '.join(missing_params)}"
    else:
        message = f"请确认酒店搜索参数：城市 {city}，入住：{check_in}，退房：{check_out}"
    
    # 使用 interrupt 暂停执行，等待用户输入
    interrupt_data = {
        "message": message,
        "format_hint": "请分别告诉我：城市、入住日期、退房日期（格式：YYYY-MM-DD）"
    }
    
    # 调用 interrupt 函数暂停执行
    user_input = interrupt(interrupt_data)
    
    # 解析用户输入
    parts = user_input.split('，')
    if len(parts) >= 3:
        new_city = parts[0].strip()
        new_check_in = parts[1].strip()
        new_check_out = parts[2].strip()
    else:
        new_city = city or user_input
        new_check_in = check_in or user_input
        new_check_out = check_out or user_input
    
    # 创建 ToolMessage
    tool_message = ToolMessage(
        content=f"已确认酒店参数：城市 {new_city}，入住：{new_check_in}，退房：{new_check_out}",
        tool_call_id=tool_call_id,
        name="confirm_hotel_params_interrupt"
    )
    
    return Command(
        update={
            "hotel_params": {
                "city": new_city,
                "check_in": new_check_in,
                "check_out": new_check_out
            },
            "messages": [tool_message]
        }
    )


def confirm_activity_params_interrupt(city: str = None, date: str = None, tool_call_id: str = None) -> Command:
    """
    使用 interrupt 机制确认活动搜索参数
    
    Args:
        city: 城市
        date: 日期
        tool_call_id: 工具调用ID
        
    Returns:
        Command 对象，包含用户输入的参数
    """
    # 总是使用 interrupt 来确认参数，无论是否已有参数
    current_params = {
        "city": city or "",
        "date": date or ""
    }
    
    missing_params = []
    if not city:
        missing_params.append("城市")
    if not date:
        missing_params.append("日期")
    
    # 总是触发中断来确认参数
    if missing_params:
        message = f"请提供以下缺失的活动搜索参数：{', '.join(missing_params)}"
    else:
        message = f"请确认活动搜索参数：城市 {city}，日期：{date}"
    
    # 使用 interrupt 暂停执行，等待用户输入
    interrupt_data = {
        "message": message,
        "format_hint": "请分别告诉我：城市、活动日期（格式：YYYY-MM-DD）"
    }
    
    # 调用 interrupt 函数暂停执行
    user_input = interrupt(interrupt_data)
    
    # 解析用户输入
    parts = user_input.split('，')
    if len(parts) >= 2:
        new_city = parts[0].strip()
        new_date = parts[1].strip()
    else:
        new_city = city or user_input
        new_date = date or user_input
    
    # 创建 ToolMessage
    tool_message = ToolMessage(
        content=f"已确认活动参数：城市 {new_city}，日期：{new_date}",
        tool_call_id=tool_call_id,
        name="confirm_activity_params_interrupt"
    )
    
    return Command(
        update={
            "activity_params": {
                "city": new_city,
                "date": new_date
            },
            "messages": [tool_message]
        }
    )


# ==================== 智能体切换工具 ====================

# 创建智能体切换工具
transfer_to_flight_agent = create_handoff_tool(
    agent_name="flight_agent",
    description="切换到航班预订智能体，可以搜索和预订航班。"
)

transfer_to_hotel_agent = create_handoff_tool(
    agent_name="hotel_agent", 
    description="切换到酒店预订智能体，可以搜索和预订酒店。"
)

transfer_to_activity_agent = create_handoff_tool(
    agent_name="activity_agent",
    description="切换到活动预订智能体，可以搜索和预订旅游活动。"
)

transfer_to_assistant_agent = create_handoff_tool(
    agent_name="assistant_agent",
    description="切换到主助手智能体，可以处理一般查询和协调其他智能体。"
)


# ==================== 智能体定义 ====================

# 主助手智能体
assistant_agent = create_react_agent(
    model,
    tools=[
        transfer_to_flight_agent,
        transfer_to_hotel_agent, 
        transfer_to_activity_agent,
        get_user_info,
        get_user_bookings
    ],
    prompt="""你是一个智能旅行助手，专门帮助用户规划旅行。
    
    你的职责包括：
    1. 理解用户的旅行需求
    2. 根据需求切换到相应的专业智能体（航班、酒店、活动）
    3. 提供旅行建议和协调服务
    4. 查看用户的预订信息
    
    当用户需要预订航班时，请切换到 flight_agent
    当用户需要预订酒店时，请切换到 hotel_agent  
    当用户需要预订活动时，请切换到 activity_agent
    
    请始终保持友好和专业的服务态度。""",
    name="assistant_agent"
)

# 航班预订智能体
flight_agent = create_react_agent(
    model,
    tools=[
        confirm_flight_params_interrupt,
        search_flights,
        book_flight,
        transfer_to_hotel_agent,
        transfer_to_activity_agent,
        transfer_to_assistant_agent
    ],
    prompt="""你是一个专业的航班预订智能体。
    
    你的职责包括：
    1. 确认航班搜索参数（出发城市、到达城市、日期）
    2. 搜索航班信息
    3. 帮助用户预订航班
    4. 提供航班相关建议
    
    重要：当用户询问航班预订时，你必须首先调用 confirm_flight_params_interrupt 工具来确认参数。
    不要直接询问用户，而是使用工具来处理参数确认。
    只有在获得完整的参数后，才进行航班搜索。
    
    当用户完成航班预订后，可以建议他们预订酒店或活动。
    如果需要切换到其他智能体，请使用相应的切换工具。
    
    请提供准确和有用的航班信息。""",
    name="flight_agent"
)

# 酒店预订智能体
hotel_agent = create_react_agent(
    model,
    tools=[
        confirm_hotel_params_interrupt,
        search_hotels,
        book_hotel,
        transfer_to_flight_agent,
        transfer_to_activity_agent,
        transfer_to_assistant_agent
    ],
    prompt="""你是一个专业的酒店预订智能体。
    
    你的职责包括：
    1. 确认酒店搜索参数（城市、入住日期、退房日期）
    2. 搜索酒店信息
    3. 帮助用户预订酒店
    4. 提供酒店相关建议
    
    重要：当用户询问酒店预订时，你必须首先调用 confirm_hotel_params_interrupt 工具来确认参数。
    不要直接询问用户，而是使用工具来处理参数确认。
    只有在获得完整的参数后，才进行酒店搜索。
    
    当用户完成酒店预订后，可以建议他们预订航班或活动。
    如果需要切换到其他智能体，请使用相应的切换工具。
    
    请提供准确和有用的酒店信息。""",
    name="hotel_agent"
)

# 活动预订智能体
activity_agent = create_react_agent(
    model,
    tools=[
        confirm_activity_params_interrupt,
        search_activities,
        book_activity,
        transfer_to_flight_agent,
        transfer_to_hotel_agent,
        transfer_to_assistant_agent
    ],
    prompt="""你是一个专业的旅游活动预订智能体。
    
    你的职责包括：
    1. 确认活动搜索参数（城市、日期）
    2. 搜索旅游活动信息
    3. 帮助用户预订活动
    4. 提供活动相关建议
    
    重要：当用户询问活动预订时，你必须首先调用 confirm_activity_params_interrupt 工具来确认参数。
    不要直接询问用户，而是使用工具来处理参数确认。
    只有在获得完整的参数后，才进行活动搜索。
    
    当用户完成活动预订后，可以建议他们预订航班或酒店。
    如果需要切换到其他智能体，请使用相应的切换工具。
    
    请提供准确和有用的活动信息。""",
    name="activity_agent"
)


# ==================== Swarm 构建 ====================

def create_travel_swarm():
    """
    创建旅行预订 Swarm 系统
    """
    print("正在创建旅行预订 Swarm 系统...")
    
    # 创建 Swarm
    swarm = create_swarm(
        agents=[
            assistant_agent,
            flight_agent,
            hotel_agent,
            activity_agent
        ],
        default_active_agent="assistant_agent"  # 默认从主助手开始
    )
    
    # 设置检查点保存器（用于状态管理）
    checkpointer = InMemorySaver()
    
    # 编译 Swarm
    app = swarm.compile(checkpointer=checkpointer)
    
    print("Swarm 系统创建完成！")
    return app


# ==================== 流式输出工具 ====================

def print_stream(stream):
    """
    打印流式输出
    
    Args:
        stream: 流式输出对象
    """
    for ns, update in stream:
        print(f"\n=== 命名空间: {ns} ===")
        
        for node, node_updates in update.items():
            if node_updates is None:
                continue

            if isinstance(node_updates, (dict, tuple)):
                node_updates_list = [node_updates]
            elif isinstance(node_updates, list):
                node_updates_list = node_updates
            else:
                raise ValueError(f"未知的更新类型: {node_updates}")

            for node_updates in node_updates_list:
                print(f"\n--- 节点: {node} ---")
                
                if isinstance(node_updates, tuple):
                    print(node_updates)
                    continue
                    
                # 查找消息键
                messages_key = next(
                    (k for k in node_updates.keys() if "messages" in k), None
                )
                
                if messages_key is not None:
                    # 打印最后一条消息
                    last_message = node_updates[messages_key][-1]
                    print(f"消息: {last_message.content}")
                else:
                    print(f"更新: {node_updates}")

        print("\n" + "="*50 + "\n")


# ==================== 演示函数 ====================

def demo_agent_switching():
    """
    演示智能体切换功能（支持中断和人工交互）
    """
    print("\n=== 智能体切换演示（支持中断） ===")
    print("=" * 40)
    
    # 创建 Swarm
    app = create_travel_swarm()
    
    # 生成唯一的会话ID
    thread_id = str(uuid.uuid4())
    config_dict = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": "user_123"
        }
    }
    
    print(f"会话ID: {thread_id}")
    
    # 演示智能体切换（全部需要中断确认）
    scenarios = [
        "我想预订航班",  # 缺少所有参数
        "预订北京到上海的航班",  # 缺少日期参数
        "我想预订酒店",  # 缺少所有参数
        "预订上海的活动"  # 缺少日期参数
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n场景 {i}: {scenario}")
        print("-" * 30)
        
        try:
            # 执行工作流
            result = app.invoke(
                {
                    "messages": [
                        {"role": "user", "content": scenario}
                    ]
                },
                config=config_dict
            )
            
            # 检查是否有中断
            if "__interrupt__" in result:
                print("⏸️ 检测到中断，等待人工输入...")
                print(f"中断信息: {result['__interrupt__']}")
                
                # 处理中断信息（可能是列表或字典）
                interrupt_data = result['__interrupt__']
                if isinstance(interrupt_data, list) and len(interrupt_data) > 0:
                    # 如果是列表，取第一个元素
                    interrupt_info = interrupt_data[0]
                    if hasattr(interrupt_info, 'value'):
                        # 如果是 Interrupt 对象，获取其 value
                        message = interrupt_info.value.get('message', '请提供缺失的参数')
                    else:
                        # 如果是字典
                        message = interrupt_info.get('message', '请提供缺失的参数')
                elif isinstance(interrupt_data, dict):
                    # 如果是字典
                    message = interrupt_data.get('message', '请提供缺失的参数')
                else:
                    message = '请提供缺失的参数'
                
                # 获取用户输入
                user_input = get_user_input(message)
                
                print(f"🔄 用户输入: {user_input}")
                
                # 使用 Command 恢复执行
                resume_command = Command(resume=user_input)
                print(f"📝 恢复命令: {resume_command}")
                
                result = app.invoke(resume_command, config=config_dict)
                
                # 输出最终结果
                print("✅ 工作流执行完成")
                if 'messages' in result:
                    last_message = result['messages'][-1]
                    print(f"最终响应: {last_message.content}")
            else:
                print("✅ 工作流执行完成（无中断）")
                if 'messages' in result:
                    last_message = result['messages'][-1]
                    print(f"最终响应: {last_message.content}")
                    
        except Exception as e:
            print(f"❌ 执行过程中出现错误: {e}")
            import traceback
            traceback.print_exc()


def interactive_demo():
    """
    交互式演示函数，测试参数确认功能
    """
    print("\n=== 交互式参数确认演示 ===")
    print("=" * 40)
    
    # 创建 Swarm
    app = create_travel_swarm()
    
    # 生成唯一的会话ID
    thread_id = str(uuid.uuid4())
    config_dict = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": "user_123"
        }
    }
    
    print(f"会话ID: {thread_id}")
    print("现在您可以与系统交互，测试参数确认功能。")
    print("尝试输入缺少参数的问题，比如：")
    print("- '我想预订航班'")
    print("- '预订酒店'")
    print("- '我想参加活动'")
    print("输入 'quit' 退出\n")
    
    while True:
        try:
            user_input = input("您: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
                
            if not user_input:
                continue
                
            print("\n系统响应:")
            print("-" * 30)
            
            # 流式输出响应
            for chunk in app.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config_dict,
                subgraphs=True
            ):
                for node, node_updates in chunk.items():
                    if node == "__end__":
                        continue
                        
                    if isinstance(node_updates, (dict, tuple)):
                        node_updates_list = [node_updates]
                    elif isinstance(node_updates, list):
                        node_updates_list = node_updates
                    else:
                        continue

                    for node_updates in node_updates_list:
                        if isinstance(node_updates, tuple):
                            continue
                            
                        # 查找消息键
                        messages_key = next(
                            (k for k in node_updates.keys() if "messages" in k), None
                        )
                        
                        if messages_key is not None:
                            # 打印最后一条消息
                            last_message = node_updates[messages_key][-1]
                            print(f"{last_message.content}")
            
            print("-" * 30 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    """
    主函数
    """
    print("LangGraph Swarm 架构示例（全中断模式）")
    print("=" * 50)
    
    try:
        # 演示智能体切换功能（支持中断）
        demo_agent_switching()
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
