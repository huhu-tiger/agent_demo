# -*- coding: utf-8 -*-
"""
测试模型工具选择功能
"""

import os
import sys
sys.path.append('.')

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import config

# 设置环境变量
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 初始化语言模型
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,
    max_tokens=1000
)

def test_model_question_detection():
    """测试模型问题检测"""
    print("🧪 测试模型问题检测")
    print("=" * 50)
    
    test_questions = [
        "你是什么模型？",
        "你是谁？",
        "你叫什么名字？",
        "请解释什么是机器学习",
        "查询北京的天气",
        "计算 2 + 3"
    ]
    
    for question in test_questions:
        print(f"\n问题: {question}")
        
        # 构建判断提示
        prompt = f"""
请判断以下问题是否是询问AI模型身份、能力或个人信息的问题。
如果是，请回答"MODEL_QUESTION"；如果不是，请回答"NOT_MODEL_QUESTION"。

问题：{question}

回答：
"""
        
        try:
            # 调用大模型进行判断
            messages = [HumanMessage(content=prompt)]
            response = llm.invoke(messages)
            
            print(f"模型判断: {response.content.strip()}")
            
            # 检查是否是模型问题
            if "MODEL_QUESTION" in response.content:
                standard_answer = f"您好，我是default的AI模型，是Cursor IDE内置的AI助手，致力于提升您的开发效率。你问的是：{question}"
                print(f"标准回答: {standard_answer}")
            else:
                print("不是模型问题，使用其他工具处理")
                
        except Exception as e:
            print(f"错误: {e}")

def test_tool_selection():
    """测试工具选择"""
    print("\n\n🔧 测试工具选择")
    print("=" * 50)
    
    test_questions = [
        "你是什么模型？",
        "查询北京的天气怎么样",
        "请帮我计算 15 * 3 + 10",
        "搜索关于人工智能的信息",
        "翻译 hello 这个单词",
        "请解释什么是机器学习"
    ]
    
    for question in test_questions:
        print(f"\n问题: {question}")
        
        # 构建工具选择提示
        tool_selection_prompt = f"""
请分析以下用户问题，并选择最合适的工具来处理。

可用工具：
1. get_weather - 天气查询工具
2. calculate_math - 数学计算工具
3. search_web - 网络搜索工具
4. translate_text - 文本翻译工具
5. ask_llm - 大语言模型问答工具
6. analyze_text - 文本分析工具
7. get_model_info - 模型信息工具

用户问题：{question}

请根据问题的内容，选择最合适的工具。如果问题涉及多个方面，可以选择多个工具。
请只回答工具名称，用逗号分隔，例如：get_weather,calculate_math

回答：
"""
        
        try:
            # 调用大模型进行工具选择
            messages = [HumanMessage(content=tool_selection_prompt)]
            response = llm.invoke(messages)
            
            print(f"选择的工具: {response.content.strip()}")
            
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    test_model_question_detection()
    test_tool_selection() 