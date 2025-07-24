"""
@author: 代码医生工作室

@来源: 图书《AI Agent开发：做与学 ——AutoGen 入门与进阶》配套代码    
"""

from openai import OpenAI

base_url="http://localhost:11434/v1"
model="deepseek-r1:7b"
api_key=  "Not-required" # 对于本地模型，API密钥不是必需的


def basic_customer_service(query: str) -> str:
    """
    基础的智能客服函数，处理常见问题并调用大模型生成回答。

    Args:
        query: 用户提出的问题。

    Returns:
        str: 针对用户问题的回答。
    """
    common_questions = {
        "退货政策": "支持7天无理由退货，请保留原始包装。",
        "运费": "国内订单满99元包邮。"
    }
    # 检查是否为常见问题
    if query in common_questions:
        return common_questions[query]
    else:
        # 调用OpenAI接口（示例使用Ollama本地模型）
        # 注意：这里假设已经正确配置了OpenAI的API密钥，并且Ollama服务正在运行。
        # 如果使用本地模型，需要设置base_url指向本地服务的地址和端口。
        client = OpenAI(api_key=api_key, base_url=base_url)
        prompt =  f"用户提问：{query}"
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': prompt} ],
            stream=False
        )

        return response.choices[0].message.content.strip()


# 测试
print(basic_customer_service("退货政策"))  # 输出预设答案
print(basic_customer_service("推荐一款笔记本电脑"))  # 调用大模型生成回答

