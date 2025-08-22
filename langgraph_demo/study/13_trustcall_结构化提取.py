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


def trustcall_llm_structured_output_main():
    """使用 trustcall 将偏好抽取为 Preferences，演示校验失败→自动修复。"""
    from trustcall import create_extractor

    logger.info("[trustcall] 开始创建提取器...")
    try:
        # 将 Preferences 作为"工具"绑定给 LLM，强制以结构化工具调用返回
        extractor = create_extractor(
            llm,
            tools=[Preferences],
            tool_choice="Preferences",
        )
        
        logger.info("[trustcall] 提取器创建成功")
    except Exception as e:
        logger.error(f"[trustcall] 提取器创建失败: {e}")
        logger.exception("[trustcall] 详细错误信息:")
        return

    logger.info("[trustcall] 开始调用提取器...")
    try:
        # 使用 messages 形式调用；少于 3 个食品将触发验证并自动补全
        result = extractor.invoke({"messages": [("user", "我喜欢苹果派和冰淇淋。")]})
        logger.info("[trustcall] 调用成功")
    except Exception as e:
        logger.error(f"[trustcall] 调用失败: {e}")
        logger.exception("[trustcall] 详细错误信息:")
        return

    # 结构日志
    try:
        logger.info("[trustcall-simple] keys: %s", list(result.keys()))
        logger.info(
            "[trustcall-simple] sizes => messages: %d, responses: %d, response_metadata: %d, attempts: %s",
            len(result.get("messages", [])),
            len(result.get("responses", [])),
            len(result.get("response_metadata", [])),
            result.get("attempts"),
        )
        msgs = result.get("messages", [])
        if msgs:
            last_msg = msgs[-1]
            tc = getattr(last_msg, "tool_calls", [])
            logger.info("[trustcall-simple] last_message type: %s, tool_calls: %d", type(last_msg).__name__, len(tc) if tc else 0)
    except Exception as e:
        logger.exception("[trustcall-simple] 日志打印失败: %s", e)

    try:
        pref = result["responses"][0]
        # 打印解析后的 Preferences JSON
        pretty = pref.model_dump_json(indent=2)
        logger.info("[trustcall-simple] Preferences(JSON):\n%s", pretty)
        print("trustcall Preferences result:")
        print(pretty)
    except Exception as e:
        logger.exception("trustcall 调用失败：%s", e)
        print("trustcall 调用失败：", e)


def trustcall_complex_schema_main():
    """参考 trustcall README 的 Complex schema 思路，演示在已有数据上更新并支持插入。
    文档参考：https://github.com/hinthornw/trustcall?tab=readme-ov-file#complex-schema
    """
    from trustcall import create_extractor

    logger.info("[trustcall-complex] 开始创建复杂模式提取器...")
    try:
        # 现有的人员记录（示例，索引将作为 json_doc_id 暗示顺序）
        # 注意：字段名必须与 Person 模型完全匹配
        existing_persons = [
            {
                "username": "Emma Thompson",
                "notes": [
                    "Loves hiking",
                    "Works in marketing",
                    "Has a dog named Max",
                ],
                "age": None,
                "gender": None,
                "phone": None,
                "email": None,
                "address": None,
                "company": None,
                "position": None,
            },
            {
                "username": "Michael Chen",
                "notes": [
                    "Great at problem-solving",
                    "Vegetarian",
                    "Plays guitar",
                ],
                "age": None,
                "gender": None,
                "phone": None,
                "email": None,
                "address": None,
                "company": None,
                "position": None,
            },
            {
                "username": "Sarah Johnson",
                "notes": [
                    "Has two kids",
                    "Loves gardening",
                    "Makes amazing cookies",
                ],
                "age": None,
                "gender": None,
                "phone": None,
                "email": None,
                "address": None,
                "company": None,
                "position": None,
            },
        ]

        conversation = (
            """
- Emma 提到昨晚带着她的新小狗（一只名叫 Sunny 的金毛寻回犬）散步。
- Michael 刚开始在一家初创公司担任数据科学家，并考虑转为纯素饮食。
- Sarah 的大儿子刚升入初中；她正专注于特殊教育，对教学充满热情。
- 我还认识了 Olivia Davis，她是一名 27 岁的平面设计师，热爱艺术与素描，周末在当地动物收容所做志愿者。
            """.strip()
        )

        # 将 Person 作为工具绑定，并开启 enable_inserts 允许创建新记录
        # existing 以 {SchemaName: 当前列表} 的形式传入，信号：在此基础上进行更新/插入
        extractor = create_extractor(
            llm,
            tools=[Person],
            tool_choice="Person",
            enable_inserts=True,
        )
        logger.info("[trustcall-complex] 提取器创建成功")
    except Exception as e:
        logger.error(f"[trustcall-complex] 提取器创建失败: {e}")
        logger.exception("[trustcall-complex] 详细错误信息:")
        return

    logger.info("[trustcall-complex] 开始调用提取器...")
    try:
        result = extractor.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"根据以下对话更新现有人员记录并创建新记录：\n\n{conversation}",
                    }
                ],
                "existing": {"Person": existing_persons},
            }
        )
        logger.info("[trustcall-complex] 调用成功")
    except Exception as e:
        logger.error(f"[trustcall-complex] 调用失败: {e}")
        logger.exception("[trustcall-complex] 详细错误信息:")
        return

    # 结构日志
    try:
        logger.info("[trustcall-complex] keys: %s", list(result.keys()))
        logger.info(
            "[trustcall-complex] sizes => messages: %d, responses: %d, response_metadata: %d, attempts: %s",
            len(result.get("messages", [])),
            len(result.get("responses", [])),
            len(result.get("response_metadata", [])),
            result.get("attempts"),
        )
    except Exception as e:
        logger.exception("[trustcall-complex] 日志打印失败: %s", e)

    print("Updated and new person records:")
    responses = result.get("responses", [])
    metas = result.get("response_metadata", [])
    for r, meta in zip(responses, metas):
        rid = meta.get("json_doc_id", "New")
        print(f"ID: {rid}")
        try:
            j = r.model_dump_json(indent=2)
            logger.info("[trustcall-complex] Person(JSON):\n%s", j)
            # print(j)
        except Exception:
            j = json.dumps(r, ensure_ascii=False, indent=2)
            logger.info("[trustcall-complex] Person(dictJSON):\n%s", j)
            # print(j)
        print()

def trustcall_extract_new_records_demo():
    """仅提取新记录：不给定 existing，直接从对话中抽取 Person 列表。"""
    from trustcall import create_extractor

    conversation = (
        """
- 我认识了 张爱玲，她是一名数据分析师，喜欢跑步、烘焙和旅行。
- 还有 李霞，他是后端工程师，周末喜欢打篮球和看电影。
        """.strip()
    )

    extractor = create_extractor(
        llm,
        tools=[Person],
        tool_choice="any",
    )

    result = extractor.invoke(
        {
            "messages": [
                (
                    "user",
                    f"请使用 Person 工具，从以下对话中提取人物记录。文本中可能包含多位人物：请为每位人物分别调用 Person 工具输出一条记录，勿合并；尽量补全姓名、职位/爱好等字段。\n\n{conversation}",
                )
            ]
        }
    )

    # 结构日志
    try:
        logger.info("[trustcall-new] : %s", result)
        logger.info(
            "[trustcall-new] sizes => messages: %d, responses: %d, response_metadata: %d, attempts: %s",
            len(result.get("messages", [])),
            len(result.get("responses", [])),
            len(result.get("response_metadata", [])),
            result.get("attempts"),
        )
    except Exception as e:
        logger.exception("[trustcall-new] 日志打印失败: %s", e)

    responses = result.get("responses", [])
    metas = result.get("response_metadata", [])

    # 简单预期人数（统计对话中以“- ”开头的条目，忽略备注行）
    expected_count = sum(1 for line in conversation.splitlines() if line.strip().startswith("- ") and "备注" not in line)

    # 若少于预期，追加一次更强提示重试
    if len(responses) < expected_count:
        retry_msg = (
            f"上文至少包含 {expected_count} 位人物。请为每位人物分别调用 Person 工具各输出一条记录，"
            "不要合并到同一条工具调用中；若某些字段缺失可留空或省略。"
        )
        result_retry = extractor.invoke({"messages": [("user", retry_msg)]})
        try:
            logger.info("[trustcall-new][retry] sizes => messages: %d, responses: %d", len(result_retry.get("messages", [])), len(result_retry.get("responses", [])))
        except Exception:
            pass
        # 若重试有返回，用重试结果替换
        if result_retry.get("responses"):
            responses = result_retry.get("responses", [])
            metas = result_retry.get("response_metadata", [])

    if not responses:
        print("trustcall 新记录提取失败：无响应")
        return
    for r, meta in zip(responses, metas or [{}] * len(responses)):
        rid = (meta or {}).get("json_doc_id", "New")
        print(f"ID: {rid}")
        try:
            j = r.model_dump_json(indent=2)
            logger.info("[trustcall-new] Person(JSON):\n%s", j)

        except Exception:
            j = json.dumps(r, ensure_ascii=False, indent=2)
            logger.info("[trustcall-new] Person(dictJSON):\n%s", j)

        print()

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
    

    # 填补记录，支持在已有数据上更新并支持插入
    trustcall_llm_structured_output_main()
    # 复杂结构示例，支持在已有数据上更新并支持插入
    # trustcall_complex_schema_main()

    # 提取新记录
    trustcall_extract_new_records_demo()
    
