#!/usr/bin/env python3
"""
Tag筛选功能测试脚本
演示如何基于Tag列进行筛选，而不是相似度搜索
"""

import os
import sys
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from config import custom_config
from langgraph_demo.study.13_base_memory_demo import AdvancedMemoryDemo, MemoryItem


def test_tag_filtering():
    """测试Tag筛选功能"""
    
    print("🧪 Tag筛选功能测试")
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
    
    print("\n🔍 2. 精确Tag筛选测试:")
    print("   搜索标签: ['编程']")
    exact_results = demo.search_by_tags_exact(["编程"], limit=5)
    for i, memory in enumerate(exact_results, 1):
        print(f"   {i}. {memory['content']}")
        print(f"      匹配标签: {', '.join(memory['matched_tags'])}")
        print(f"      所有标签: {', '.join(memory['tags'])}")
        print(f"      重要性: {memory['importance']:.2f}")
    
    print("\n🔍 3. 部分Tag匹配测试:")
    print("   搜索标签: ['学习']")
    partial_results = demo.search_by_tags_partial(["学习"], limit=5)
    for i, memory in enumerate(partial_results, 1):
        print(f"   {i}. {memory['content']}")
        print(f"      匹配标签: {', '.join(memory['matched_tags'])}")
        print(f"      所有标签: {', '.join(memory['tags'])}")
        print(f"      重要性: {memory['importance']:.2f}")
    
    print("\n🔍 4. 多条件筛选测试:")
    print("   条件: 标签包含'编程' 且 重要性>=0.7")
    filtered_results = demo.filter_memories_by_criteria(
        tags=["编程"],
        min_importance=0.7,
        limit=5
    )
    for i, memory in enumerate(filtered_results, 1):
        print(f"   {i}. {memory['content']}")
        print(f"      标签: {', '.join(memory['tags'])}")
        print(f"      重要性: {memory['importance']:.2f}")
        print(f"      情感: {memory['emotional_context']}")
    
    print("\n🔍 5. 对比：相似度搜索 vs Tag筛选:")
    print("   相似度搜索 (使用'编程'作为查询):")
    similarity_results = demo.search_by_tags(["编程"], limit=3)
    for i, memory in enumerate(similarity_results, 1):
        print(f"   {i}. {memory['content']} (相似度: {memory['score']:.3f})")
    
    print("\n   Tag精确筛选 (使用'编程'作为标签):")
    tag_results = demo.search_by_tags_exact(["编程"], limit=3)
    for i, memory in enumerate(tag_results, 1):
        print(f"   {i}. {memory['content']} (匹配标签: {', '.join(memory['matched_tags'])})")
    
    print("\n✅ Tag筛选测试完成！")


if __name__ == "__main__":
    test_tag_filtering() 