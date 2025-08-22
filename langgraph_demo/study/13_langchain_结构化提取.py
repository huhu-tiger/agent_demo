#!/usr/bin/env python3
"""
trustcall 风格：利用 LangChain 的 with_structured_output 实现结构化数据抽取

特点：
- 使用 Pydantic 定义结构化输出 Schema
- 使用 ChatOpenAI.with_structured_output 强制模型输出符合 Schema 的结构化结果
- 提供最小可运行示例：从日程文本中抽取会议数据

先决条件：
- 已安装依赖（在 study/requirements.txt 已包含）
- 配置环境变量 OPENAI_API_KEY（或通过 OpenAI 兼容网关的 base_url 与 api_key）

运行：
- python langgraph_demo/study/13_trustcall_demo.py
"""
from __future__ import annotations

import json
import os
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from langchain_openai import ChatOpenAI
import config
logger = config.logger
# 使用 config.py 中的 base_url/api_key/model 初始化兼容 OpenAI 协议的模型
# 注意：此处会将 config 的值写入环境变量，若需覆盖请在运行前设置 OPENAI_API_BASE/OPENAI_API_KEY
os.environ["OPENAI_API_BASE"] = config.base_url
os.environ["OPENAI_API_KEY"] = config.api_key
MODEL_NAME = config.model

# 初始化语言模型（显式传入 api_key/base_url，兼容自建网关或公有云服务）
llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.1,
    max_tokens=500,
    api_key=config.api_key,
    base_url=config.base_url,
)

# 添加详细的调试日志
logger.info(f"[配置] 模型名称: {MODEL_NAME}")
logger.info(f"[配置] API基础URL: {config.base_url}")
logger.info(f"[配置] API密钥: {config.api_key[:10]}..." if config.api_key else "None")

class Attendee(BaseModel):
    name: str = Field(description="参会人姓名，若缺失可用邮箱前缀代替")
    email: Optional[str] = Field(default=None, description="参会人邮箱，可为空")


class Meeting(BaseModel):
    title: str = Field(description="会议标题")
    company: str = Field(description="客户公司名称（外部公司）")
    attendees: List[Attendee] = Field(description="客户侧参会人列表（排除内部人员）")
    meeting_time: str = Field(description="会议时间，格式如 10:30 AM 或 14:00 等")


# 结构化输出 Schema（用于 LangChain 的 with_structured_output 抽取日程）
class CalendarData(BaseModel):
    meetings: List[Meeting] = Field(description="从日程文本中解析出的会议条目列表")


# trustcall 最小校验示例：若 foods 少于 3 个，将触发验证并通过重试自动修复
class Preferences(BaseModel):
    foods: List[str] = Field(description="喜欢的食物列表")

    @field_validator("foods")
    def at_least_three_foods(cls, v):
        if len(v) < 3:
            raise ValueError("Must have at least three favorite foods")
        return v


# trustcall 复杂结构示例用的 Schema：支持在 existing 基础上更新与插入
class Person(BaseModel):
    username: str = Field(description="人物姓名")
    notes: List[str] = Field(default_factory=list, description="爱好")
    age: Optional[int] = Field(default=None, description="年龄")
    gender: Optional[str] = Field(default=None, description="性别")
    phone: Optional[str] = Field(default=None, description="电话")
    email: Optional[str] = Field(default=None, description="邮箱")
    address: Optional[str] = Field(default=None, description="地址")
    company: Optional[str] = Field(default=None, description="公司")
    position: Optional[str] = Field(default=None, description="职位")


EXTRACTION_INSTRUCTION = """
从以下原始日程文本中抽取会议信息：

{text}

抽取要求：
- 你所在公司为示例公司：Tavily；因此 Tavily 为内部公司，外部公司为客户公司
- 只抽取客户公司的参会人（排除 @tavily.com、@internal.com 等内部域名）
- 每个会议需要包含：title、company、attendees（包含 name 与 email）、meeting_time（例如 09:00 AM）
- 严格按照目标 Schema 返回，不要输出额外说明
"""


def create_structured_extractor(model: str = "gpt-4o-mini"):
    """创建一个带结构化输出能力的 LLM 解析器。

    如果你走的是 OpenAI 兼容网关（自建或第三方），可通过设置环境变量：
    - OPENAI_API_KEY
    - OPENAI_BASE_URL（可选）
    """


    return llm.with_structured_output(CalendarData)


def extract_calendar_data(raw_text: str, model: str = "gpt-4o-mini") -> CalendarData:
    """调用 LLM 将非结构化日程文本抽取为 CalendarData。"""
    parser = create_structured_extractor(model=model)
    prompt = EXTRACTION_INSTRUCTION.format(text=raw_text)
    return parser.invoke(prompt)


def _demo_text() -> str:
    return (
        """
2025-08-21
09:30 上午 - 与 ACME 公司启动会
参会人：alice@acme.com（Alice）、bob@tavily.com（Bob）、tom@acme.com

11:00 上午 - 产品评审 | Contoso
参与者：jane@contoso.com（Jane Doe）、li@tavily.com、mark@contoso.com（Mark）

02:15 下午 - 每周同步 - Globex
访客：emily@globex.com、john@internal.com、kate@globex.com（Kate）
        """.strip()
    )


def lagnchian_llm_structured_output_main():
    """演示纯 LangChain 的结构化输出（with_structured_output）用于日程抽取。"""
    # 运行前检查环境变量，避免用户未配置时直接报错
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENAI_BASE_URL"):
        print(
            "未检测到 OPENAI_API_KEY；如使用 OpenAI 兼容网关，请设置 OPENAI_API_KEY（与可选的 OPENAI_BASE_URL）。\n"
            "示例跳过实际调用，仅展示将被解析的示例文本：\n"
        )
        print(_demo_text())
        return

    logger.info("[LangChain] 开始调用结构化输出...")
    try:
        data = extract_calendar_data(_demo_text())
        logger.info("[LangChain] 调用成功")
    except Exception as e:
        logger.error(f"[LangChain] 调用失败: {e}")
        logger.exception("[LangChain] 详细错误信息:")
        return
    # 结构日志
    try:
        logger.info("[LangChain] 返回类型: %s", type(data).__name__)
        logger.info("[LangChain] meetings 数量: %s", getattr(data, "meetings", []) and len(data.meetings))
        logger.info(
            "[LangChain] 返回结构(JSON):\n%s",
            json.dumps(json.loads(data.model_dump_json()), ensure_ascii=False, indent=2),
        )
    except Exception as e:
        logger.exception("[LangChain] 日志打印失败: %s", e)
    # 以 JSON 打印，便于查看结构
    # print(json.dumps(json.loads(data.model_dump_json()), ensure_ascii=False, indent=2))


def test_api_connection():
    """测试 API 连接是否正常"""
    logger.info("[测试] 开始测试 API 连接...")
    
    try:
        # 简单的测试调用
        response = llm.invoke("你好，请回复'连接成功'")
        logger.info(f"[测试] API 连接成功，响应: {response.content}")
        return True
    except Exception as e:
        logger.error(f"[测试] API 连接失败: {e}")
        logger.exception("[测试] 详细错误信息:")
        return False


if __name__ == "__main__":
    # 首先测试 API 连接
    if not test_api_connection():
        logger.error("API 连接失败，跳过所有测试")
        exit(1)
    
    lagnchian_llm_structured_output_main()

