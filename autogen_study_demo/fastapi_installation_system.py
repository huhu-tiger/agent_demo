# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Wed Mar 19 16:13:28 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, AsyncGenerator
import asyncio
import uvicorn
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import Swarm
from autogen_agentchat.conditions import HandoffTermination
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import HandoffMessage
from config import model_client as Ollama_model_client

# 定义请求模型
class InstallationRequest(BaseModel):
    task: str
    user_input: Optional[str] = None

# 定义响应模型
class InstallationResponse(BaseModel):
    success: bool
    message: str
    task_result: Optional[Dict] = None
    error: Optional[str] = None

# 定义工具函数
async def generate_installation_guide(device: str) -> str:
    """生成设备安装指南"""
    guides = {
        "智能门锁": "1. 定位安装位置\n2. 固定背板\n3. 安装锁体\n4. 调试电子部件",
        "网络摄像头": "1. 选择安装高度\n2. 固定支架\n3. 连接电源\n4. 配置无线网络",
        "智能灯泡": "1. 关闭电源\n2. 安装灯泡\n3. 连接智能控制器\n4. 测试功能"
    }
    return guides.get(device, "标准安装流程")

async def check_inventory(devices: List[str]) -> Dict[str, bool]:
    """检查设备库存"""
    inventory = {"智能门锁": True, "网络摄像头": False, "智能灯泡": True, "智能插座": True}
    return {d: inventory.get(d, False) for d in devices}

# 定义各角色智能体
def create_agents():
    """创建智能体实例"""
    project_manager = AssistantAgent(
        "project_manager",
        description="项目经理",
        model_client=Ollama_model_client,
        handoffs=["electrician", "network_engineer", "inventory_clerk"],
        system_message="""负责整体项目协调：
        1. 解析用户安装需求
        2. 分配任务给专业工程师
        3. 监控项目进度
        使用TERMINATE结束流程"""
    )

    electrician = AssistantAgent(
        "electrician",
        description="电工",
        model_client=Ollama_model_client,
        handoffs=["project_manager"],
        tools=[generate_installation_guide],
        system_message="""电气设备安装专家：
        1. 生成电气设备安装指南
        2. 处理电路改造需求
        完成工作后返回项目经理"""
    )

    network_engineer = AssistantAgent(
        "network_engineer",
        description="网络工程师",
        model_client=Ollama_model_client,
        handoffs=["project_manager"],
        system_message="""网络设备配置专家：
        1. 规划无线网络覆盖
        2. 配置智能设备联网
        完成工作后返回项目经理"""
    )

    inventory_clerk = AssistantAgent(
        "inventory_clerk",
        description="库存管理员",
        model_client=Ollama_model_client,
        handoffs=["project_manager"],
        tools=[check_inventory],
        system_message="""库存管理系统：
        1. 检查设备库存状态
        2. 生成备货清单
        完成检查后返回项目经理"""
    )
    
    return project_manager, electrician, network_engineer, inventory_clerk

# 创建Swarm团队
def create_installation_team():
    """创建安装团队"""
    project_manager, electrician, network_engineer, inventory_clerk = create_agents()
    
    max_messages_termination = MaxMessageTermination(max_messages=25)
    termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE") | max_messages_termination
    
    installation_team = Swarm(
        participants=[project_manager, electrician, network_engineer, inventory_clerk],
        termination_condition=termination
    )
    
    return installation_team

# 运行任务处理流程（流式输出）
async def run_team_stream_generator(task: str, user_input: Optional[str] = None) -> AsyncGenerator[str, None]:
    """运行团队任务流并生成流式输出"""
    installation_team = create_installation_team()
    
    # 发送开始消息
    yield f"data: {json.dumps({'type': 'start', 'message': '开始处理安装任务...'}, ensure_ascii=False)}\n\n"
    
    # 开始任务流
    async for event in installation_team.run_stream(task=task):
        # 处理每个事件
        if hasattr(event, 'content') and event.content:
            # 安全地处理内容，避免序列化错误
            content = event.content
            
            # 处理不同类型的内容
            if isinstance(content, str):
                # 如果是文本，直接使用
                processed_content = content
            elif isinstance(content, list):
                # 如果是列表，取第一个元素
                if len(content) > 0:
                    if isinstance(content[0], str):
                        processed_content = content[0]
                    else:
                        # 如果是对象，转换为字典
                        try:
                            processed_content = content[0].__dict__
                        except:
                            processed_content = {"message": "工具调用结果"}
                else:
                    processed_content = "空内容"
            elif hasattr(content, '__dict__'):
                # 如果是对象，转换为字典
                try:
                    processed_content = content.__dict__
                except:
                    processed_content = {"message": "对象内容"}
            else:
                # 其他情况，转换为字符串
                processed_content = str(content)
            
            # 发送进度消息
            progress_data = {
                'event_type': 'progress',
                'source': getattr(event, 'source', 'unknown'),
                'message_type': getattr(event, 'type', 'unknown'),
                'content': processed_content,
                'timestamp': asyncio.get_event_loop().time()
            }
            yield f"data: {json.dumps(progress_data, ensure_ascii=False)}\n\n"
    
    # 处理用户输入（如果需要）
    # if user_input:
    #     yield f"data: {json.dumps({'type': 'user_input', 'message': f'处理用户输入: {user_input}'}, ensure_ascii=False)}\n\n"
        
    #     async for event in installation_team.run_stream(
    #         HandoffMessage(source="user", target="project_manager", content=user_input)
    #     ):
    #         if hasattr(event, 'content') and event.content:
    #             # 安全地处理内容
    #             content = event.content
    #             if hasattr(content, '__dict__'):
    #                 try:
    #                     content = str(content)
    #                 except:
    #                     content = "工具调用结果"
                
    #             progress_data = {
    #                 'type': 'progress',
    #                 'agent': getattr(event, 'source', 'unknown'),
    #                 'content': content,
    #                 'timestamp': asyncio.get_event_loop().time()
    #             }
    #             yield f"data: {json.dumps(progress_data, ensure_ascii=False)}\n\n"
    
    # 发送完成消息
    yield f"data: {json.dumps({'type': 'complete', 'message': '任务处理完成'}, ensure_ascii=False)}\n\n"

# 运行任务处理流程（非流式，用于兼容）
async def run_team_stream(task: str, user_input: Optional[str] = None):
    """运行团队任务流"""
    installation_team = create_installation_team()
    
    # 开始任务
    task_result = await Console(installation_team.run_stream(task=task))
    
    # 处理用户输入（如果需要）
    if user_input:
        task_result = await installation_team.run_stream(
            HandoffMessage(source="user", target="project_manager", content=user_input)
        )
    
    # 检查是否需要用户输入
    while True:
        last_msg = task_result.messages[-1]
        if isinstance(last_msg, HandoffMessage) and last_msg.target == "user":
            # 如果需要用户输入，返回特殊状态
            return {
                "status": "needs_user_input",
                "message": "需要用户补充信息",
                "task_result": task_result,
                "last_message": last_msg
            }
        else:
            break
    
    return {
        "status": "completed",
        "task_result": task_result,
        "messages": [msg.content for msg in task_result.messages if hasattr(msg, 'content')]
    }

# 创建FastAPI应用
app = FastAPI(
    title="智能家居安装项目调度系统",
    description="基于AutoGen的多智能体协作系统，用于智能家居安装项目调度",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {"message": "智能家居安装项目调度系统API", "status": "running"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "installation_system"}

@app.post("/api/installation/task")
async def process_installation_task(request: InstallationRequest):
    """处理安装任务（流式输出）"""
    try:
        # 返回流式响应
        return StreamingResponse(
            run_team_stream_generator(request.task, request.user_input),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
    except Exception as e:
        # 如果出错，返回错误信息
        error_data = {
            "type": "error",
            "message": "任务处理失败",
            "error": str(e)
        }
        return StreamingResponse(
            iter([f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"]),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )

@app.post("/api/installation/task/sync", response_model=InstallationResponse)
async def process_installation_task_sync(request: InstallationRequest):
    """处理安装任务（同步响应，用于兼容）"""
    try:
        # 运行团队任务
        result = await run_team_stream(request.task, request.user_input)
        
        if result["status"] == "needs_user_input":
            return InstallationResponse(
                success=True,
                message="任务需要用户补充信息",
                task_result=result
            )
        else:
            return InstallationResponse(
                success=True,
                message="任务处理完成",
                task_result=result
            )
            
    except Exception as e:
        return InstallationResponse(
            success=False,
            message="任务处理失败",
            error=str(e)
        )

@app.post("/api/installation/continue", response_model=InstallationResponse)
async def continue_installation_task(request: InstallationRequest):
    """继续处理安装任务（当需要用户输入时）"""
    try:
        if not request.user_input:
            raise HTTPException(status_code=400, detail="需要提供用户输入")
        
        # 继续任务处理
        result = await run_team_stream(request.task, request.user_input)
        
        return InstallationResponse(
            success=True,
            message="任务继续处理完成",
            task_result=result
        )
        
    except Exception as e:
        return InstallationResponse(
            success=False,
            message="任务继续处理失败",
            error=str(e)
        )

@app.get("/api/installation/examples")
async def get_example_tasks():
    """获取示例任务"""
    examples = [
        "需要安装：3个智能门锁（客厅/主卧/次卧），2个网络摄像头（前门/后院）",
        "安装智能灯泡：客厅5个，卧室3个，厨房2个",
        "配置智能家居系统：包括智能门锁、摄像头、灯泡、插座等设备",
        "安装智能插座：客厅2个，卧室1个，厨房1个"
    ]
    return {"examples": examples}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 