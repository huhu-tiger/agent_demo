# -*- coding: utf-8 -*-

"""
Mem0AI 基本功能测试脚本
用于验证 Mem0AI 是否正确安装和配置
"""

import asyncio
import sys

async def test_mem0ai_import():
    """测试 Mem0AI 导入"""
    try:
        from mem0 import Memory
        print("✅ Mem0AI 导入成功")
        return True
    except ImportError as e:
        print(f"❌ Mem0AI 导入失败: {e}")
        print("请运行: pip install mem0ai>=0.1.0")
        return False

async def test_memory_initialization():
    """测试内存初始化"""
    try:
        from mem0 import Memory
        memory = Memory()
        print("✅ 内存初始化成功")
        return memory
    except Exception as e:
        print(f"❌ 内存初始化失败: {e}")
        return None

async def test_basic_operations(memory):
    """测试基本操作"""
    if not memory:
        return False
    
    try:
        # 测试添加记忆
        print("测试添加记忆...")
        result = await memory.add("测试记忆内容", user_id="test_user")
        print(f"✅ 添加记忆成功: {result}")
        
        # 测试搜索记忆
        print("测试搜索记忆...")
        results = await memory.search("测试", user_id="test_user", limit=5)
        print(f"✅ 搜索记忆成功: {results}")
        
        return True
    except Exception as e:
        print(f"❌ 基本操作测试失败: {e}")
        return False

async def test_autogen_integration():
    """测试 AutoGen 集成"""
    try:
        from autogen_agentchat.agents import AssistantAgent
        from mem0 import Memory
        
        memory_client = Memory()
        assistant_agent = AssistantAgent(
            name="test_agent",
            memory=[memory_client],
        )
        print("✅ AutoGen 集成测试成功")
        return True
    except Exception as e:
        print(f"❌ AutoGen 集成测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 Mem0AI 功能测试")
    print("=" * 40)
    
    # 测试导入
    if not await test_mem0ai_import():
        sys.exit(1)
    
    # 测试初始化
    memory = await test_memory_initialization()
    if not memory:
        sys.exit(1)
    
    # 测试基本操作
    if not await test_basic_operations(memory):
        print("⚠️  基本操作测试失败，可能是网络或API配置问题")
    
    # 测试 AutoGen 集成
    if not await test_autogen_integration():
        print("⚠️  AutoGen 集成测试失败")
    
    print("\n✅ 测试完成！")
    print("\n如果所有测试都通过，说明 Mem0AI 已正确配置。")
    print("如果某些测试失败，请检查网络连接和API配置。")

if __name__ == "__main__":
    asyncio.run(main()) 