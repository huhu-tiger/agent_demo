#!/usr/bin/env python3
"""
直接Tag筛选演示脚本
展示如何直接基于Tag字段进行筛选，而不是先搜索所有再筛选
"""

import os
import sys
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import custom_config
from langgraph_demo.study.13_base_memory_demo import AdvancedMemoryDemo, MemoryItem


def demo_direct_tag_filtering():
    """演示直接Tag筛选功能"""
    
    print("🎯 直接Tag筛选演示")
    print("=" * 50)
    
    # 创建演示实例
    demo = AdvancedMemoryDemo(model_config=custom_config)
    
    # 添加测试记忆
    print("\n📝 添加测试记忆...")
    
    test_memories = [
        MemoryItem(
            content="我学会了Python编程",
            memory_type="learning",
            emotional_context="满足和成就感",
            importance=0.8,
            tags=["学习", "编程", "Python", "技能"],
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        ),
        MemoryItem(
            content="我学会了JavaScript编程",
            memory_type="learning",
            emotional_context="兴奋和自豪",
            importance=0.7,
            tags=["学习", "编程", "JavaScript", "技能"],
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        ),
        MemoryItem(
            content="我通过了编程考试",
            memory_type="achievement",
            emotional_context="兴奋和自豪",
            importance=0.9,
            tags=["成就", "考试", "编程", "成功"],
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
        ),
        MemoryItem(
            content="我和朋友吵架了",
            memory_type="conflict",
            emotional_context="沮丧和困惑",
            importance=0.6,
            tags=["冲突", "朋友", "情感"],
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        )
    ]
    
    for memory in test_memories:
        demo.add_advanced_memory(memory)
    
    print("\n🔍 1. 显示所有可用标签:")
    all_tags = demo.get_all_available_tags()
    print(f"   可用标签: {', '.join(all_tags)}")
    
    print("\n🔍 2. 直接Tag字段搜索:")
    print("   搜索标签: '编程'")
    tag_field_results = demo.search_by_tag_field("编程", limit=5)
    for i, memory in enumerate(tag_field_results, 1):
        print(f"   {i}. {memory['content']}")
        print(f"      匹配标签: {', '.join(memory['matched_tags'])}")
        print(f"      所有标签: {', '.join(memory['tags'])}")
        print(f"      相似度: {memory['score']:.3f}")
        print(f"      搜索类型: {memory['search_type']}")
    
    print("\n🔍 3. 直接Tag组合搜索:")
    print("   搜索标签: ['学习', '编程']")
    tag_direct_results = demo.search_by_tags_direct(["学习", "编程"], limit=5)
    for i, memory in enumerate(tag_direct_results, 1):
        print(f"   {i}. {memory['content']}")
        print(f"      匹配标签: {', '.join(memory['matched_tags'])}")
        print(f"      所有标签: {', '.join(memory['tags'])}")
        print(f"      相似度: {memory['score']:.3f}")
        print(f"      搜索类型: {memory['search_type']}")
    
    print("\n🔍 4. 对比：相似度搜索 vs 直接Tag筛选:")
    print("   相似度搜索 (使用'编程'作为查询):")
    similarity_results = demo.search_by_tags(["编程"], limit=3)
    for i, memory in enumerate(similarity_results, 1):
        print(f"   {i}. {memory['content']} (相似度: {memory['score']:.3f})")
    
    print("\n   直接Tag筛选 (使用'编程'作为标签):")
    tag_results = demo.search_by_tag_field("编程", limit=3)
    for i, memory in enumerate(tag_results, 1):
        print(f"   {i}. {memory['content']} (匹配标签: {', '.join(memory['matched_tags'])})")
    
    print("\n✅ 直接Tag筛选演示完成！")


if __name__ == "__main__":
    demo_direct_tag_filtering() 