import openai
import json
import re
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import os
from datetime import datetime

# 配置OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]

class ReActAgent:
    """基于ReAct方式的智能体"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", max_iterations: int = 5):
        self.model = model
        self.max_iterations = max_iterations
        self.tools: List[Tool] = []
        self.conversation_history: List[Dict[str, str]] = []
        
    def add_tool(self, tool: Tool):
        """添加工具"""
        self.tools.append(tool)
        
    def get_tools_description(self) -> str:
        """获取工具描述"""
        if not self.tools:
            return "没有可用的工具。"
        
        tools_desc = "可用的工具：\n"
        for tool in self.tools:
            tools_desc += f"- {tool.name}: {tool.description}\n"
            if tool.parameters:
                tools_desc += f"  参数: {json.dumps(tool.parameters, ensure_ascii=False)}\n"
        return tools_desc
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """执行工具"""
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    result = tool.function(**arguments)
                    return f"工具 {tool_name} 执行成功: {result}"
                except Exception as e:
                    return f"工具 {tool_name} 执行失败: {str(e)}"
        return f"未找到工具: {tool_name}"
    
    def parse_reasoning(self, response: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """解析ReAct格式的响应"""
        # 尝试解析Thought/Action/Action Input格式
        thought_match = re.search(r'Thought:\s*(.*?)(?=\nAction:|$)', response, re.DOTALL)
        action_match = re.search(r'Action:\s*(.*?)(?=\nAction Input:|$)', response, re.DOTALL)
        action_input_match = re.search(r'Action Input:\s*(.*?)(?=\nObservation:|$)', response, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        action_input = action_input_match.group(1).strip() if action_input_match else None
        
        return thought, action, action_input
    
    def parse_final_answer(self, response: str) -> Optional[str]:
        """解析最终答案"""
        # 查找Final Answer
        final_answer_match = re.search(r'Final Answer:\s*(.*?)(?=\n|$)', response, re.DOTALL)
        if final_answer_match:
            return final_answer_match.group(1).strip()
        return None
    
    def think(self, user_input: str) -> str:
        """思考并执行ReAct循环"""
        print(f"用户输入: {user_input}")
        print("-" * 50)
        
        # 检查是否是模型相关问题
        model_questions = ["你是什么模型", "你是谁", "你叫什么", "你是什么AI", "你是什么助手"]
        for question in model_questions:
            if question in user_input:
                return "您好，我是default的AI模型，是Cursor IDE内置的AI助手，致力于提升您的开发效率。你问的是：" + user_input
        
        # 构建系统提示
        system_prompt = f"""你是一个基于ReAct（Reasoning and Acting）方式的智能体。

{self.get_tools_description()}

请按照以下格式进行思考和行动：

Thought: 分析当前情况，思考需要采取什么行动
Action: 选择要使用的工具名称
Action Input: 工具的输入参数（JSON格式）
Observation: 工具的返回结果
... (可以重复多次Thought/Action/Action Input/Observation)
Thought: 基于所有观察结果，得出最终答案
Final Answer: 给用户的最终回答

示例：
Thought: 用户询问天气，我需要使用天气查询工具
Action: get_weather
Action Input: {{"city": "北京"}}
Observation: 北京今天晴天，温度25度
Thought: 我已经获得了天气信息，可以给出答案
Final Answer: 北京今天晴天，温度25度。

请确保：
1. 每个Action都对应一个可用的工具
2. Action Input使用正确的JSON格式
3. 最终给出Final Answer
4. 如果不需要使用工具，直接给出Final Answer"""

        # 添加用户输入到对话历史
        self.conversation_history.append({"role": "user", "content": user_input})
        
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n=== 第 {iteration} 次迭代 ===")
            
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversation_history)
            
            # 调用OpenAI API
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=1000
                )
                
                assistant_response = response.choices[0].message.content
                print(f"AI响应: {assistant_response}")
                
                # 解析响应
                thought, action, action_input = self.parse_reasoning(assistant_response)
                final_answer = self.parse_final_answer(assistant_response)
                
                if final_answer:
                    # 找到最终答案，结束循环
                    self.conversation_history.append({"role": "assistant", "content": assistant_response})
                    print(f"\n最终答案: {final_answer}")
                    return final_answer
                
                if action and action_input:
                    # 执行工具
                    print(f"执行工具: {action}")
                    print(f"工具输入: {action_input}")
                    
                    try:
                        # 解析JSON输入
                        if isinstance(action_input, str):
                            args = json.loads(action_input)
                        else:
                            args = action_input
                        
                        # 执行工具
                        observation = self.execute_tool(action, args)
                        print(f"工具结果: {observation}")
                        
                        # 添加观察结果到响应中
                        full_response = assistant_response + f"\nObservation: {observation}"
                        self.conversation_history.append({"role": "assistant", "content": full_response})
                        
                        # 继续下一轮迭代
                        continue
                        
                    except json.JSONDecodeError as e:
                        error_msg = f"JSON解析错误: {str(e)}"
                        print(error_msg)
                        full_response = assistant_response + f"\nObservation: {error_msg}"
                        self.conversation_history.append({"role": "assistant", "content": full_response})
                        continue
                
                # 如果没有明确的Action或Final Answer，尝试直接回答
                if "Final Answer:" not in assistant_response:
                    # 添加Final Answer
                    assistant_response += "\nFinal Answer: " + assistant_response
                
                self.conversation_history.append({"role": "assistant", "content": assistant_response})
                
            except Exception as e:
                error_msg = f"API调用错误: {str(e)}"
                print(error_msg)
                return error_msg
        
        return "达到最大迭代次数，无法完成请求。"

# 示例工具函数
def get_current_time():
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression: str):
    """计算数学表达式"""
    try:
        # 安全计算，只允许基本数学运算
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

def get_weather(city: str):
    """获取天气信息（模拟）"""
    # 这里只是模拟，实际应用中需要调用真实的天气API
    weather_data = {
        "北京": "晴天，温度25°C，湿度60%",
        "上海": "多云，温度28°C，湿度70%",
        "广州": "小雨，温度30°C，湿度80%",
        "深圳": "晴天，温度32°C，湿度65%"
    }
    return weather_data.get(city, f"抱歉，没有{city}的天气信息")

def search_web(query: str):
    """搜索网络信息（模拟）"""
    # 这里只是模拟，实际应用中需要调用搜索API
    return f"关于'{query}'的搜索结果：这是一个模拟的搜索结果，实际应用中需要集成真实的搜索API。"

# 创建智能体实例
def create_agent():
    """创建并配置智能体"""
    agent = ReActAgent(model="gpt-3.5-turbo", max_iterations=5)
    
    # 添加工具
    agent.add_tool(Tool(
        name="get_current_time",
        description="获取当前时间",
        function=get_current_time,
        parameters={}
    ))
    
    agent.add_tool(Tool(
        name="calculate",
        description="计算数学表达式，支持基本运算（+、-、*、/、()）",
        function=calculate,
        parameters={"expression": "数学表达式字符串"}
    ))
    
    agent.add_tool(Tool(
        name="get_weather",
        description="获取指定城市的天气信息",
        function=get_weather,
        parameters={"city": "城市名称"}
    ))
    
    agent.add_tool(Tool(
        name="search_web",
        description="搜索网络信息",
        function=search_web,
        parameters={"query": "搜索查询"}
    ))
    
    return agent

# 主函数
def main():
    """主函数"""
    print("=== ReAct智能体演示 ===")
    print("这是一个基于ReAct方式的智能体，具备工具调用能力")
    print("输入 'quit' 或 'exit' 退出")
    print("-" * 50)
    
    agent = create_agent()
    
    while True:
        try:
            user_input = input("\n请输入您的问题: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if not user_input:
                continue
            
            # 处理用户输入
            response = agent.think(user_input)
            print(f"\n智能体回答: {response}")
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
