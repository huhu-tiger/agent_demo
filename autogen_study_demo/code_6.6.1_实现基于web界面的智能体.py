
# -*- coding: utf-8 -*-

"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码 
Created on Thu Mar 20 15:56:48 2025
"""


# import nest_asyncio
# nest_asyncio.apply()


import asyncio
import streamlit as st
from autogen_agentchat.agents import AssistantAgent 
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os

from streamlit import error  # 假设正在使用Streamlit
from autogen_agentchat.teams import RoundRobinGroupChat



#设置模型客户端
# model_client = OpenAIChatCompletionClient(
#     model="gemini-2.0-flash",
#     api_key=os.getenv("GEMINI_API_KEY"),  # 确保在环境中设置了 GEMINI_API_KEY
# )

from config import model_client
# 创建 AssistantAgent，名为 "assistant"。
writer = AssistantAgent("assistant", model_client=model_client,
                        handoffs=["user"],
                       
                        system_message="""你是个智能助手。
                        你负责接收用户的问题，并根据问题进行回答。
                        
                        输出对问题分析的思考过程。如果用户的问题不明确，你可以向用户索要更多信息。
                        
                        任务完成时，回复'TERMINATE'。
                        
                        """, 
 
                    )

introducestr = """您好！我是智能助手。"""
termination = HandoffTermination(target="user_proxy") | TextMentionTermination("TERMINATE")   

# 解析task_result
def parseresult(task_result, lastagent="assistant"):
    if task_result is None:
        return "系统出现故障，请稍后。。。。\n\nTERMINATE"

    # 获取最后一个 TextMessage 的内容
    last_message = None
    merged_message = []
    found_last_sequence = False
    # 反向遍历 task_result.messages 列表
    for msg in reversed(task_result.messages):
        # 检查消息类型是否为 TextMessage 且来源是否为 Assistant
        if (
            msg.type == "TextMessage" or msg.type == "ToolCallRequestEvent" or msg.type == 'ThoughtEvent'
        ) and msg.source == lastagent:
           
            found_last_sequence = True
            strmsg = msg.content
            if isinstance(strmsg, str):
                if "</think>" in msg.content:
                    strmsg = strmsg.split("</think>")[-1]
            else:
                strmsg = eval(strmsg[0].arguments).get("message")
            if strmsg:
                merged_message.insert( 0, strmsg.strip()  )  # 将消息内容插入到列表开头以保持顺序
        else:
            # 如果已经找到了最后一段来自 Assistant 的消息序列并且当前消息不符合条件，则停止查找
            if found_last_sequence:
                break
    last_message = "可以再详细说说你的问题吗？\n\nTERMINATE"
    if found_last_sequence and merged_message:
        last_message = " ".join(merged_message)

    last_message = last_message.replace("TERMINATE", "").strip(" \n")
    return last_message

def main():
    st.title("智能助手系统") #定义主函数 main，设置网页标题为 "智能助手系统"

    # 初始化或重置 team
    if "team" not in st.session_state:
        st.session_state.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(st.session_state.event_loop)
        
        # 重新创建 team
        st.session_state.team  = RoundRobinGroupChat([writer],max_turns=1, termination_condition=termination)

        st.session_state.reset = False

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": introducestr})
        st.session_state.last_role = "assistant"

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.chat_input("Enter your message:")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        async def handle_message():
            print(f"该信息移交给：{st.session_state.last_role}")
            task = HandoffMessage(
                source="user", 
                target=st.session_state.last_role,
                content=user_input)
            
            task_result = await Console(st.session_state.team.run_stream(task=task))
            
            if task_result.messages[-1].type == "HandoffMessage":
                st.session_state.last_role = task_result.messages[-1].source
            else:
                st.session_state.last_role = "assistant"
            
            print(task_result)
            
            last_message = parseresult(task_result)
            
            if 'TERMINATE' in task_result.stop_reason:
                print("发现TERMINATE命令！关闭本轮聊天！")
                await st.session_state.team.reset()
                # 重新初始化 team
                del st.session_state.team
           
            st.session_state.messages.append({"role": "assistant", "content": last_message})

            with st.chat_message("assistant"):
                st.write(last_message)

        st.session_state.event_loop.run_until_complete(handle_message())

if __name__ == "__main__":

    main()
    ## streamlit run code_6.6.1_实现基于web界面的智能体.py