#!/usr/bin/env python3
"""
LangGraph InMemoryStore 高级示例
展示多向量索引、复杂记忆结构和高级搜索功能
支持自定义模型配置
"""

import os
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import traceback

from langchain.embeddings import init_embeddings
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

import config
from config import ModelConfig

# 获取日志器
logger = config.logger


@dataclass
class MemoryItem:
    """记忆项数据结构"""
    content: str
    memory_type: str
    emotional_context: str
    importance: float  # 重要性评分 0-1
    tags: List[str]
    created_at: str
    last_accessed: str
    access_count: int = 0


class AdvancedMemoryDemo:
    """高级记忆演示类"""
    
    def __init__(
        self, 
        model_config: Optional[ModelConfig] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        初始化高级演示类
        
        Args:
            model_config: 模型配置对象
            openai_api_key: OpenAI API密钥（向后兼容）
        """
        # 设置默认模型配置
        if model_config is None:
            model_config = ModelConfig()
        
        # 如果提供了openai_api_key，设置到配置中
        if openai_api_key:
            model_config.api_key = openai_api_key
            model_config.embedding_api_key = openai_api_key
        
        self.model_config = model_config
        
        # 初始化嵌入模型
        embedding_config = model_config.get_embedding_config()
        if embedding_config:
            # 使用自定义配置初始化嵌入模型
            if model_config.embedding_provider == "openai":
                self.embeddings = init_embeddings(
                    f"openai:{model_config.embedding_model}",
                    **embedding_config
                )
            else:
                # 支持其他提供商
                self.embeddings = init_embeddings(
                    f"{model_config.embedding_provider}:{model_config.embedding_model}",
                    **embedding_config
                )
        else:
            # 使用默认配置
            self.embeddings = init_embeddings(f"{model_config.embedding_provider}:{model_config.embedding_model}")
        
        # 初始化聊天模型
        chat_config = model_config.get_chat_model_config()
        if chat_config:
            # 使用自定义配置初始化聊天模型
            if model_config.model_provider == "openai":
                self.llm = init_chat_model(
                    f"openai:{model_config.model_name}",
                    **chat_config
                )
            else:
                # 支持其他提供商
                self.llm = init_chat_model(
                    f"{model_config.model_provider}:{model_config.model_name}",
                    **chat_config
                )
        else:
            # 使用默认配置
            self.llm = init_chat_model(f"{model_config.model_provider}:{model_config.model_name}")
        
        # 获取嵌入模型的维度
        embedding_dims = model_config.get_embedding_dimensions()
        
        # 创建带有多向量索引的InMemoryStore
        self.store = InMemoryStore(
            index={
                "embed": self.embeddings,
                "dims": embedding_dims,
                "fields": ["content", "emotional_context", "tags"],  # 多字段索引
                "tag_index": {  # 专门的tag索引
                    "type": "exact_match",
                    "field": "tags"
                }
            }
        )
        
        # 创建检查点保存器
        self.checkpointer = InMemorySaver()
        
        # 构建图
        self.graph = self._build_graph()
        
        # 用户配置
        self.config = {
            "configurable": {
                "thread_id": "advanced_demo",
                "user_id": "demo_user",
            }
        }
    
    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return {
            "chat_model": f"{self.model_config.model_provider}:{self.model_config.model_name}",
            "embedding_model": f"{self.model_config.embedding_provider}:{self.model_config.embedding_model}",
            "chat_base_url": self.model_config.base_url or "默认",
            "embedding_base_url": self.model_config.embedding_base_url or "默认",
            "embedding_dimensions": str(self.model_config.get_embedding_dimensions())
        }
    
    def _extract_emotional_keywords(self, message: str) -> List[str]:
        """
        从消息中提取情感关键词
        
        Args:
            message: 用户消息
            
        Returns:
            情感关键词列表
        """
        # 情感关键词映射
        emotional_keywords = {
            "积极情感": ["开心", "高兴", "快乐", "兴奋", "满足", "自豪", "满意", "愉快", "喜悦", "激动"],
            "消极情感": ["难过", "悲伤", "沮丧", "失望", "愤怒", "焦虑", "担心", "害怕", "痛苦", "绝望"],
            "中性情感": ["平静", "冷静", "中性", "一般", "普通", "正常"],
            "惊讶": ["惊讶", "震惊", "意外", "没想到", "出乎意料"],
            "困惑": ["困惑", "迷茫", "不解", "疑惑", "不明白"]
        }
        
        # 检测消息中的情感关键词
        detected_emotions = []
        for emotion_type, keywords in emotional_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    detected_emotions.append(keyword)
                    break  # 每个情感类型只取第一个匹配的关键词
        
        logger.info(f"从消息 '{message}' 中检测到情感关键词: {detected_emotions}")
        return detected_emotions
    
    def _build_graph(self):
        """构建高级LangGraph工作流"""
        
        def advanced_chat_with_memory(state, *, store: BaseStore):
            """高级记忆聊天节点"""
            logger.info(f"advanced_chat_with_memory: {state}")
            user_id = "demo_user"
            namespace = (user_id, "advanced_memories")
            
            # 基于用户最后一条消息进行多维度搜索
            last_message = state["messages"][-1].content
            logger.info(f"处理用户消息: {last_message}")
            
            # 搜索内容相关的记忆
            content_results = store.search(
                namespace, 
                query=last_message, 
                limit=3
            )
            
            # 搜索情感相关的记忆 - 使用情感关键词
            emotional_keywords = self._extract_emotional_keywords(last_message)
            if emotional_keywords:
                emotional_query = " ".join(emotional_keywords)
                emotional_results = store.search(
                    namespace, 
                    query=emotional_query, 
                    limit=2
                )
            else:
                # 如果没有检测到情感关键词，使用原始消息
                emotional_results = store.search(
                    namespace, 
                    query=last_message, 
                    limit=2
                )
            
            # 构建记忆上下文
            memories = []
            seen_memories = set()
            
            # 处理内容相关记忆
            for item in content_results:
                if item.key not in seen_memories:
                    memory_data = item.value
                    similarity_score = item.score
                    memories.append({
                        "content": memory_data.get("content", ""),
                        "emotional_context": memory_data.get("emotional_context", ""),
                        "importance": memory_data.get("importance", 0.5),
                        "tags": memory_data.get("tags", []),
                        "score": similarity_score,
                        "search_type": "内容相关"
                    })
                    seen_memories.add(item.key)
                    logger.info(f"找到内容相关记忆: {memory_data.get('content', '')} (相似度: {similarity_score:.3f})")
            
            # 处理情感相关记忆
            for item in emotional_results:
                if item.key not in seen_memories:
                    memory_data = item.value
                    similarity_score = item.score
                    memories.append({
                        "content": memory_data.get("content", ""),
                        "emotional_context": memory_data.get("emotional_context", ""),
                        "importance": memory_data.get("importance", 0.5),
                        "tags": memory_data.get("tags", []),
                        "score": similarity_score,
                        "search_type": "情感相关"
                    })
                    seen_memories.add(item.key)
                    logger.info(f"找到情感相关记忆: {memory_data.get('content', '')} (相似度: {similarity_score:.3f})")
            
            # 按重要性排序记忆
            memories.sort(key=lambda x: x["importance"], reverse=True)
            
            # 构建记忆上下文
            memory_context = ""
            if memories:
                memory_context = "\n## 相关记忆:\n"
                for i, memory in enumerate(memories[:3], 1):
                    memory_context += f"{i}. 内容: {memory['content']}\n"
                    memory_context += f"   情感: {memory['emotional_context']}\n"
                    memory_context += f"   标签: {', '.join(memory['tags'])}\n"
                    memory_context += f"   重要性: {memory['importance']:.2f}\n"
                    memory_context += f"   相似度: {memory['score']:.3f}\n"
                    memory_context += f"   搜索类型: {memory['search_type']}\n\n"
            
            logger.info(f"memory_context: {memory_context}")
            
            # 检查是否需要存储新记忆
            if "记住" in last_message or "remember" in last_message.lower():
                # 提取要记住的内容
                memory_content = last_message.replace("记住", "").replace("remember", "").strip()
                if memory_content:
                    # 分析情感和重要性
                    analysis_prompt = f"""
分析以下内容的可能情感状态和重要性：
内容: {memory_content}

请以JSON格式返回：
{{
    "emotional_context": "情感描述",
    "importance": 0.8,
    "tags": ["标签1", "标签2"]
}}
"""
                    
                    try:
                        analysis_response = self.llm.invoke([
                            {"role": "user", "content": analysis_prompt}
                        ])
                        # 这里简化处理，实际应该解析JSON
                        emotional_context = "中性"
                        importance = 0.7
                        tags = ["用户记忆"]
                    except:
                        emotional_context = "中性"
                        importance = 0.7
                        tags = ["用户记忆"]
                    
                    memory_id = str(uuid.uuid4())
                    now = datetime.now().isoformat()
                    
                    store.put(
                        namespace,
                        memory_id,
                        {
                            "content": memory_content,
                            "emotional_context": emotional_context,
                            "importance": importance,
                            "tags": tags,
                            "created_at": now,
                            "last_accessed": now,
                            "access_count": 1
                        }
                    )
                    memory_context += f"已记住: {memory_content}\n"
                    logger.info(f"存储新记忆: {memory_content}")
            
            # 构建系统提示
            system_prompt = f"""你是一个高级AI助手，具有情感感知和记忆管理能力。{memory_context}

请用中文回复用户的问题。考虑记忆的情感上下文和重要性。
如果用户询问情感相关的问题，请基于情感记忆回答。
如果用户要求记住什么，请分析内容的情感状态和重要性。"""
            
            try:
                # 调用LLM
                logger.info("开始调用LLM...")
                response = self.llm.invoke(
                    [
                        {"role": "system", "content": system_prompt},
                        *state["messages"]
                    ]
                )
                logger.info(f"系统提示词: {system_prompt}")
                logger.info(f"用户输入: {state['messages']}")
                logger.info(f"LLM调用成功，响应类型: {type(response)}")
                logger.info(f"LLM响应内容: {response.content if hasattr(response, 'content') else response}")
                
                return {"messages": [response]}
                
            except Exception as e:
                logger.error(f"LLM调用失败: {e}")
                logger.error(f"LLM错误详情: {traceback.format_exc()}")
                # 返回错误消息
                error_response = AIMessage(content=f"抱歉，模型调用失败: {str(e)}")
                return {"messages": [error_response]}
        
        # 构建图
        builder = StateGraph(MessagesState)
        builder.add_node("advanced_chat", advanced_chat_with_memory)
        builder.add_edge(START, "advanced_chat")
        
        return builder.compile(
            checkpointer=self.checkpointer,
            store=self.store
        )
    
    def add_advanced_memory(self, memory_item: MemoryItem) -> str:
        """
        添加高级记忆
        
        Args:
            memory_item: 记忆项对象
            
        Returns:
            记忆ID
        """
        memory_id = str(uuid.uuid4())
        namespace = ("demo_user", "advanced_memories")
        
        # 转换为字典
        memory_dict = asdict(memory_item)
        
        self.store.put(namespace, memory_id, memory_dict)
        
        print(f"✅ 已添加高级记忆: {memory_item.content}")
        print(f"   情感: {memory_item.emotional_context}")
        print(f"   重要性: {memory_item.importance:.2f}")
        print(f"   标签: {', '.join(memory_item.tags)}")
        
        return memory_id
    
    def search_by_emotion(self, emotion_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        按情感搜索记忆
        
        Args:
            emotion_query: 情感查询
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        namespace = ("demo_user", "advanced_memories")
        results = self.store.search(namespace, query=emotion_query, limit=limit)
        
        memories = []
        for item in results:
            memories.append({
                "id": item.key,
                "content": item.value.get("content", ""),
                "emotional_context": item.value.get("emotional_context", ""),
                "importance": item.value.get("importance", 0.5),
                "tags": item.value.get("tags", []),
                "score": item.score,
                "search_type": "情感搜索",
                "created_at": item.value.get("created_at", ""),
                "access_count": item.value.get("access_count", 0)
            })
        
        # 按相似度排序
        memories.sort(key=lambda x: x["score"], reverse=True)
        return memories
    
    def search_by_tags(self, tags: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        按标签搜索记忆
        
        Args:
            tags: 标签列表
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        namespace = ("demo_user", "advanced_memories")
        # 使用标签作为查询
        query = " ".join(tags)
        results = self.store.search(namespace, query=query, limit=limit)
        
        memories = []
        for item in results:
            item_tags = item.value.get("tags", [])
            # 检查是否有匹配的标签
            if any(tag in item_tags for tag in tags):
                memories.append({
                    "id": item.key,
                    "content": item.value.get("content", ""),
                    "emotional_context": item.value.get("emotional_context", ""),
                    "importance": item.value.get("importance", 0.5),
                    "tags": item_tags,
                    "score": item.score,
                    "search_type": "标签搜索",
                    "created_at": item.value.get("created_at", ""),
                    "access_count": item.value.get("access_count", 0)
                })
        
        # 按相似度排序
        memories.sort(key=lambda x: x["score"], reverse=True)
        return memories
    
    def search_by_tags_direct(self, tags: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        直接基于tag字段进行搜索（不是先搜索所有再筛选）
        
        Args:
            tags: 要搜索的标签列表
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        namespace = ("demo_user", "advanced_memories")
        
        # 使用tag作为查询词，专门搜索tags字段
        results = self.store.search(
            namespace, 
            query=" ".join(tags),  # 使用标签组合作为查询
            limit=limit
        )
        
        memories = []
        for item in results:
            item_tags = item.value.get("tags", [])
            # 检查是否有匹配的标签
            matched_tags = [tag for tag in tags if tag in item_tags]
            if matched_tags:  # 只返回有匹配标签的记忆
                memories.append({
                    "id": item.key,
                    "content": item.value.get("content", ""),
                    "emotional_context": item.value.get("emotional_context", ""),
                    "importance": item.value.get("importance", 0.5),
                    "tags": item_tags,
                    "matched_tags": matched_tags,
                    "score": item.score,
                    "search_type": "Tag直接搜索",
                    "created_at": item.value.get("created_at", ""),
                    "access_count": item.value.get("access_count", 0)
                })
        
        # 按重要性排序
        memories.sort(key=lambda x: x["importance"], reverse=True)
        return memories[:limit]
    
    def search_by_tag_field(self, tag: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        基于单个tag字段进行精确搜索
        
        Args:
            tag: 要搜索的标签
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        namespace = ("demo_user", "advanced_memories")
        
        # 使用tag作为查询词
        results = self.store.search(
            namespace, 
            query=tag,
            limit=limit
        )
        
        memories = []
        for item in results:
            item_tags = item.value.get("tags", [])
            # 检查是否包含指定的标签
            if tag in item_tags:
                memories.append({
                    "id": item.key,
                    "content": item.value.get("content", ""),
                    "emotional_context": item.value.get("emotional_context", ""),
                    "importance": item.value.get("importance", 0.5),
                    "tags": item_tags,
                    "matched_tags": [tag],
                    "score": item.score,
                    "search_type": "Tag字段搜索",
                    "created_at": item.value.get("created_at", ""),
                    "access_count": item.value.get("access_count", 0)
                })
        
        # 按重要性排序
        memories.sort(key=lambda x: x["importance"], reverse=True)
        return memories[:limit]
    
    def search_by_tags_exact(self, tags: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        按标签精确筛选（不是相似度）
        
        Args:
            tags: 要搜索的标签列表
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        namespace = ("demo_user", "advanced_memories")
        
        # 获取所有记忆
        all_results = self.store.search(namespace, query="", limit=100)
        
        memories = []
        for item in all_results:
            item_tags = item.value.get("tags", [])
            # 检查是否有匹配的标签
            matched_tags = [tag for tag in tags if tag in item_tags]
            if matched_tags:  # 只返回有匹配标签的记忆
                memories.append({
                    "id": item.key,
                    "content": item.value.get("content", ""),
                    "emotional_context": item.value.get("emotional_context", ""),
                    "importance": item.value.get("importance", 0.5),
                    "tags": item_tags,
                    "matched_tags": matched_tags,
                    "score": item.score,
                    "search_type": "Tag精确筛选",
                    "created_at": item.value.get("created_at", ""),
                    "access_count": item.value.get("access_count", 0)
                })
        
        # 按重要性排序
        memories.sort(key=lambda x: x["importance"], reverse=True)
        return memories[:limit]
    
    def search_by_tags_partial(self, partial_tag: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        按标签部分匹配筛选
        
        Args:
            partial_tag: 部分标签
            limit: 结果数量限制
            
        Returns:
            搜索结果列表
        """
        namespace = ("demo_user", "advanced_memories")
        
        # 获取所有记忆
        all_results = self.store.search(namespace, query="", limit=100)
        
        memories = []
        for item in all_results:
            item_tags = item.value.get("tags", [])
            # 检查是否有部分匹配的标签
            matched_tags = [tag for tag in item_tags if partial_tag in tag]
            if matched_tags:  # 只返回有匹配标签的记忆
                memories.append({
                    "id": item.key,
                    "content": item.value.get("content", ""),
                    "emotional_context": item.value.get("emotional_context", ""),
                    "importance": item.value.get("importance", 0.5),
                    "tags": item_tags,
                    "matched_tags": matched_tags,
                    "score": item.score,
                    "search_type": "Tag部分匹配",
                    "created_at": item.value.get("created_at", ""),
                    "access_count": item.value.get("access_count", 0)
                })
        
        # 按重要性排序
        memories.sort(key=lambda x: x["importance"], reverse=True)
        return memories[:limit]
    
    def filter_memories_by_criteria(self, 
                                  tags: Optional[List[str]] = None,
                                  emotional_context: Optional[str] = None,
                                  importance_min: Optional[float] = None,
                                  importance_max: Optional[float] = None,
                                  memory_type: Optional[str] = None,
                                  limit: int = 10) -> List[Dict[str, Any]]:
        """
        按多个条件筛选记忆
        
        Args:
            tags: 标签列表
            emotional_context: 情感上下文
            importance_min: 最小重要性
            importance_max: 最大重要性
            memory_type: 记忆类型
            limit: 结果数量限制
            
        Returns:
            筛选结果列表
        """
        namespace = ("demo_user", "advanced_memories")
        
        # 获取所有记忆
        all_results = self.store.search(namespace, query="", limit=100)
        
        memories = []
        for item in all_results:
            memory_data = item.value
            
            # 检查标签条件
            if tags:
                item_tags = memory_data.get("tags", [])
                if not any(tag in item_tags for tag in tags):
                    continue
            
            # 检查情感条件
            if emotional_context:
                item_emotional = memory_data.get("emotional_context", "")
                if emotional_context.lower() not in item_emotional.lower():
                    continue
            
            # 检查重要性条件
            importance = memory_data.get("importance", 0.5)
            if importance_min is not None and importance < importance_min:
                continue
            if importance_max is not None and importance > importance_max:
                continue
            
            # 检查记忆类型条件
            if memory_type:
                item_type = memory_data.get("memory_type", "")
                if memory_type.lower() not in item_type.lower():
                    continue
            
            memories.append({
                "id": item.key,
                "content": memory_data.get("content", ""),
                "emotional_context": memory_data.get("emotional_context", ""),
                "importance": importance,
                "tags": memory_data.get("tags", []),
                "memory_type": memory_data.get("memory_type", ""),
                "score": item.score,
                "search_type": "多条件筛选",
                "created_at": memory_data.get("created_at", ""),
                "access_count": memory_data.get("access_count", 0)
            })
        
        # 按重要性排序
        memories.sort(key=lambda x: x["importance"], reverse=True)
        return memories[:limit]
    
    def get_all_available_tags(self) -> List[str]:
        """
        获取所有可用的标签
        
        Returns:
            标签列表
        """
        namespace = ("demo_user", "advanced_memories")
        
        # 获取所有记忆
        all_results = self.store.search(namespace, query="", limit=100)
        
        all_tags = set()
        for item in all_results:
            tags = item.value.get("tags", [])
            all_tags.update(tags)
        
        return sorted(list(all_tags))
    
    def get_high_importance_memories(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        获取高重要性记忆
        
        Args:
            threshold: 重要性阈值
            
        Returns:
            高重要性记忆列表
        """
        namespace = ("demo_user", "advanced_memories")
        # 获取所有记忆
        all_results = self.store.search(namespace, query="", limit=100)
        
        high_importance = []
        for item in all_results:
            importance = item.value.get("importance", 0.5)
            if importance >= threshold:
                high_importance.append({
                    "id": item.key,
                    "content": item.value.get("content", ""),
                    "emotional_context": item.value.get("emotional_context", ""),
                    "importance": importance,
                    "tags": item.value.get("tags", []),
                    "score": item.score,
                    "created_at": item.value.get("created_at", ""),
                    "access_count": item.value.get("access_count", 0)
                })
        
        # 按重要性排序
        high_importance.sort(key=lambda x: x["importance"], reverse=True)
        return high_importance
    
    def chat(self, message: str) -> str:
        """
        与AI助手聊天
        
        Args:
            message: 用户消息
            
        Returns:
            AI回复
        """
        logger.info(f"开始聊天，用户消息: {message}")
        response_content = ""
        
        try:
            result = self.graph.invoke(
                {"messages": [HumanMessage(content=message)]},
                self.config,
            )
            logger.info(f"llm result: {result}")
            response_content = result["messages"][-1].content
                
            return response_content
            
        except Exception as e:
            logger.error(f"聊天过程中出现错误: {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            return f"抱歉，聊天过程中出现错误: {str(e)}"
    
    def list_all_advanced_memories(self) -> List[Dict[str, Any]]:
        """
        列出所有高级记忆
        
        Returns:
            所有记忆的列表
        """
        namespace = ("demo_user", "advanced_memories")
        results = self.store.search(namespace, query="", limit=100)
        
        memories = []
        for item in results:
            memories.append({
                "id": item.key,
                "content": item.value.get("content", ""),
                "emotional_context": item.value.get("emotional_context", ""),
                "importance": item.value.get("importance", 0.5),
                "tags": item.value.get("tags", []),
                "score": item.score,
                "created_at": item.value.get("created_at", ""),
                "access_count": item.value.get("access_count", 0)
            })
        
        # 按重要性排序
        memories.sort(key=lambda x: x["importance"], reverse=True)
        return memories


def main():
    """主函数 - 演示高级InMemoryStore功能"""
    
    print("🚀 LangGraph 高级 InMemoryStore 演示")
    print("=" * 50)
    
    print("\n🔧 模型配置演示...")
    
    # 使用自定义配置
    print("\n1. 使用自定义模型配置:")
    from config import custom_config
    
    # 创建高级演示实例
    demo = AdvancedMemoryDemo(model_config=custom_config)
    
    # 获取模型信息
    model_info = demo.get_model_info()
    print(f"   聊天模型: {model_info['chat_model']}")
    print(f"   嵌入模型: {model_info['embedding_model']}")
    print(f"   聊天API地址: {model_info['chat_base_url']}")
    print(f"   嵌入API地址: {model_info['embedding_base_url']}")
    print(f"   嵌入维度: {model_info['embedding_dimensions']}")
    
    print("\n📝 2. 添加高级记忆...")
    
    # 创建不同类型的记忆
    memories = [
        MemoryItem(
            content="我通过了重要的考试",
            memory_type="achievement",
            emotional_context="兴奋和自豪",
            importance=0.9,
            tags=["成就", "考试", "成功"],
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        ),
        MemoryItem(
            content="我和朋友吵架了",
            memory_type="conflict",
            emotional_context="沮丧和困惑",
            importance=0.7,
            tags=["冲突", "朋友", "情感"],
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        ),
        MemoryItem(
            content="我学会了新的编程技能",
            memory_type="learning",
            emotional_context="满足和成就感",
            importance=0.8,
            tags=["学习", "编程", "技能"],
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        ),
        MemoryItem(
            content="我失去了心爱的宠物",
            memory_type="loss",
            emotional_context="悲伤和怀念",
            importance=0.95,
            tags=["失去", "宠物", "悲伤"],
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        )
    ]
    
    # 添加记忆
    for memory in memories:
        demo.add_advanced_memory(memory)
    
    print("\n🔍 3. 高级搜索演示...")
    
    # 按情感搜索
    print("\n搜索积极情感的记忆:")
    positive_memories = demo.search_by_emotion("兴奋 自豪 满足", limit=3)
    for memory in positive_memories:
        print(f"  - {memory['content']} (情感: {memory['emotional_context']}, 重要性: {memory['importance']:.2f}, 相似度: {memory['score']:.3f}, 搜索类型: {memory['search_type']})")
    
    # 按标签搜索（相似度搜索）
    print("\n按标签相似度搜索:")
    learning_memories = demo.search_by_tags(["学习", "技能"], limit=3)
    for memory in learning_memories:
        print(f"  - {memory['content']} (标签: {', '.join(memory['tags'])}, 相似度: {memory['score']:.3f}, 搜索类型: {memory['search_type']})")
    
    # 直接Tag搜索（不是先搜索所有再筛选）
    print("\n直接Tag搜索（基于tag字段）:")
    direct_tag_memories = demo.search_by_tag_field("编程", limit=3)
    for memory in direct_tag_memories:
        print(f"  - {memory['content']}")
        print(f"     匹配标签: {', '.join(memory['matched_tags'])}")
        print(f"     所有标签: {', '.join(memory['tags'])}")
        print(f"     相似度: {memory['score']:.3f}")
        print(f"     搜索类型: {memory['search_type']}")
    
    # 直接Tag筛选（使用filter）
    print("\n直接Tag筛选（使用标签组合查询）:")
    filter_tag_memories = demo.search_by_tags_direct(["学习", "编程"], limit=3)
    for memory in filter_tag_memories:
        print(f"  - {memory['content']}")
        print(f"     匹配标签: {', '.join(memory['matched_tags'])}")
        print(f"     所有标签: {', '.join(memory['tags'])}")
        print(f"     相似度: {memory['score']:.3f}")
        print(f"     搜索类型: {memory['search_type']}")
    
    # 对比：传统相似度搜索 vs 直接Tag筛选
    print("\n对比：传统相似度搜索 vs 直接Tag筛选:")
    print("传统相似度搜索 (使用'编程'作为查询):")
    similarity_results = demo.search_by_tags(["编程"], limit=3)
    for i, memory in enumerate(similarity_results, 1):
        print(f"  {i}. {memory['content']} (相似度: {memory['score']:.3f})")
    
    print("\n直接Tag筛选 (使用'编程'作为标签):")
    tag_results = demo.search_by_tag_field("编程", limit=3)
    for i, memory in enumerate(tag_results, 1):
        print(f"  {i}. {memory['content']} (匹配标签: {', '.join(memory['matched_tags'])})")
    
    # 按标签精确筛选（不是相似度）
    print("\n按标签精确筛选（非相似度）:")
    exact_tag_memories = demo.search_by_tags_exact(["学习", "编程"], limit=3)
    for memory in exact_tag_memories:
        print(f"  - {memory['content']}")
        print(f"     匹配标签: {', '.join(memory['matched_tags'])}")
        print(f"     所有标签: {', '.join(memory['tags'])}")
        print(f"     重要性: {memory['importance']:.2f}")
        print(f"     搜索类型: {memory['search_type']}")
    
    # 获取高重要性记忆
    print("\n高重要性记忆 (重要性 >= 0.8):")
    high_importance = demo.get_high_importance_memories(threshold=0.8)
    for memory in high_importance:
        print(f"  - {memory['content']} (重要性: {memory['importance']:.2f})")
    
    print("\n💬 4. ========================高级聊天演示===========================")
    
    # 测试情感感知对话
    print("\n用户: 记住我今天很开心")
    response = demo.chat("记住我今天很开心")
    logger.info(f"AI: {response}")
    
    print("\n用户: 我最近有什么让我感到兴奋的事情吗？")
    response = demo.chat("我最近有什么让我感到兴奋的事情吗？")
    logger.info(f"AI: {response}")
    
    print("\n用户: 我最重要的记忆是什么？")
    response = demo.chat("我最重要的记忆是什么？")
    logger.info(f"AI: {response}")
    
    print("\n📋 5. 列出所有高级记忆...")
    all_memories = demo.list_all_advanced_memories()
    for i, memory in enumerate(all_memories, 1):
        print(f"  {i}. {memory['content']}")
        print(f"     情感: {memory['emotional_context']}")
        print(f"     重要性: {memory['importance']}")
        print(f"     标签: {', '.join(memory['tags'])}")
        print(f"     相似度: {memory['score']}")
        print(f"     访问次数: {memory['access_count']}")
        print(f"     创建时间: {memory['created_at']}")
        print()
    
    print("\n✅ 高级演示完成！")


if __name__ == "__main__":
    main() 