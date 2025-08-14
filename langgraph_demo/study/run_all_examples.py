# -*- coding: utf-8 -*-
"""
LangGraph 学习示例 - 主运行文件
运行所有知识点的示例

作者: AI Assistant
来源: LangGraph 官方文档学习
"""

import os
import sys
import importlib
from typing import List

import config

# 获取日志器
logger = config.logger

# ============================================================================
# 示例列表
# ============================================================================

EXAMPLES = [
    {
        "name": "基础概念",
        "file": "01_basic_concepts",
        "description": "学习状态管理、节点定义、边连接等核心概念"
    },
    {
        "name": "条件路由", 
        "file": "02_conditional_routing",
        "description": "学习条件边、动态决策、路由函数"
    },
    {
        "name": "工具集成",
        "file": "03_tools_integration", 
        "description": "学习工具定义、工具调用、状态扩展"
    },
    {
        "name": "多智能体协作",
        "file": "04_multi_agent_collaboration",
        "description": "学习复杂状态管理、智能体协作、结果整合"
    },
    {
        "name": "高级特性",
        "file": "05_advanced_features",
        "description": "学习记忆管理、检查点、并行处理、错误处理"
    },
    {
        "name": "边类型详解",
        "file": "06_edge_types_demo",
        "description": "学习 add_edge 参数含义、直接边、条件边、并行边"
    }
]

# ============================================================================
# 运行函数
# ============================================================================

def run_example(example_file: str) -> bool:
    """
    运行单个示例
    
    Args:
        example_file: 示例文件名（不含扩展名）
        
    Returns:
        bool: 运行是否成功
    """
    try:
        logger.info(f"🚀 开始运行示例: {example_file}")
        
        # 动态导入模块
        module = importlib.import_module(example_file)
        
        # 查找并运行主函数
        if hasattr(module, 'test_basic_concepts'):
            module.test_basic_concepts()
        elif hasattr(module, 'test_conditional_routing'):
            module.test_conditional_routing()
        elif hasattr(module, 'test_tools_integration'):
            module.test_tools_integration()
        elif hasattr(module, 'test_multi_agent_collaboration'):
            module.test_multi_agent_collaboration()
        elif hasattr(module, 'test_advanced_features'):
            module.test_advanced_features()
        elif hasattr(module, 'test_edge_types'):
            module.test_edge_types()
        else:
            logger.warning(f"未找到主函数: {example_file}")
            return False
        
        logger.info(f"✅ 示例运行完成: {example_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ 运行示例失败 {example_file}: {e}")
        return False

def run_all_examples():
    """运行所有示例"""
    logger.info("🎓 LangGraph 学习示例 - 完整运行")
    logger.info(f"模型配置: {config.model}")
    logger.info(f"API 地址: {config.base_url}")
    logger.info("=" * 60)
    
    success_count = 0
    total_count = len(EXAMPLES)
    
    for i, example in enumerate(EXAMPLES, 1):
        logger.info(f"\n📚 示例 {i}/{total_count}: {example['name']}")
        logger.info(f"描述: {example['description']}")
        
        if run_example(example['file']):
            success_count += 1
        
        logger.info("-" * 40)
    
    # 总结
    logger.info(f"\n🎉 运行完成！")
    logger.info(f"成功: {success_count}/{total_count}")
    logger.info(f"成功率: {success_count/total_count*100:.1f}%")

def run_specific_example(example_name: str):
    """运行特定示例"""
    logger.info(f"🎯 运行特定示例: {example_name}")
    
    # 查找示例
    example = None
    for ex in EXAMPLES:
        if ex['name'] == example_name or ex['file'] == example_name:
            example = ex
            break
    
    if example:
        logger.info(f"找到示例: {example['name']}")
        logger.info(f"描述: {example['description']}")
        run_example(example['file'])
    else:
        logger.error(f"未找到示例: {example_name}")
        logger.info("可用示例:")
        for ex in EXAMPLES:
            logger.info(f"  - {ex['name']} ({ex['file']})")

def show_examples():
    """显示所有可用示例"""
    logger.info("📚 可用的 LangGraph 学习示例:")
    logger.info("=" * 60)
    
    for i, example in enumerate(EXAMPLES, 1):
        logger.info(f"{i}. {example['name']}")
        logger.info(f"   文件: {example['file']}.py")
        logger.info(f"   描述: {example['description']}")
        logger.info()

# ============================================================================
# 交互式运行
# ============================================================================

def interactive_run():
    """交互式运行"""
    logger.info("🎮 交互式 LangGraph 学习示例")
    logger.info("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 显示所有示例")
        print("2. 运行所有示例")
        print("3. 运行特定示例")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            show_examples()
        elif choice == "2":
            run_all_examples()
        elif choice == "3":
            show_examples()
            example_name = input("\n请输入示例名称或编号: ").strip()
            try:
                # 尝试按编号选择
                index = int(example_name) - 1
                if 0 <= index < len(EXAMPLES):
                    run_specific_example(EXAMPLES[index]['name'])
                else:
                    logger.error("无效的编号")
            except ValueError:
                # 按名称选择
                run_specific_example(example_name)
        elif choice == "4":
            logger.info("👋 再见！")
            break
        else:
            logger.warning("无效选择，请重新输入")

# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            run_all_examples()
        elif command == "list":
            show_examples()
        elif command == "interactive":
            interactive_run()
        else:
            run_specific_example(command)
    else:
        # 默认运行交互式模式
        interactive_run()

if __name__ == "__main__":
    main() 