#!/usr/bin/env python3
"""
LangMem 提示词优化示例
展示如何使用LangMem进行提示词优化
支持自定义模型配置
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain.embeddings import init_embeddings
from langchain.chat_models import init_chat_model
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

from langmem import (
    create_memory_store_manager,
    create_manage_memory_tool,
    create_search_memory_tool,
    create_prompt_optimizer
)

# 导入配置模块
import config
from config import ModelConfig, custom_config
from config import logger


class LangMemDemo:
    """LangMem演示类 - 专注于提示词优化"""
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """
        初始化LangMem演示
        
        Args:
            model_config: 模型配置对象，如果为None则使用默认配置
        """
        try:
            # 设置默认模型配置
            if model_config is None:
                model_config = custom_config
            
            self.model_config = model_config
            logger.info(f"初始化LangMem演示，使用模型配置: {model_config.model_provider}:{model_config.model_name}")
            
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
            
            logger.info(f"嵌入模型初始化成功: {model_config.embedding_provider}:{model_config.embedding_model}")
            
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
            
            logger.info(f"聊天模型初始化成功: {model_config.model_provider}:{model_config.model_name}")
            
            # 获取嵌入模型的维度
            embedding_dims = model_config.get_embedding_dimensions()
            logger.info(f"嵌入维度: {embedding_dims}")
            
            # 设置内存存储
            self.store = InMemoryStore(
                index={
                    "dims": embedding_dims,
                    "embed": self.embeddings,
                }
            )

            
            # 创建内存工具
            self.memory_tools = [
                create_manage_memory_tool(namespace=("memories",), store=self.store),
                create_search_memory_tool(namespace=("memories",), store=self.store),
            ]
            
            # 创建带内存的智能体
            self.agent = create_react_agent(
                self.llm,  # 使用已初始化的聊天模型对象
                tools=self.memory_tools, 
                store=self.store, 
                checkpointer=InMemorySaver()
            )
            
            logger.info("智能体创建成功")
            
            print(f"✅ LangMem演示初始化完成")
            print(f"   聊天模型: {model_config.model_provider}:{model_config.model_name}")
            print(f"   嵌入模型: {model_config.embedding_provider}:{model_config.embedding_model}")
            print(f"   嵌入维度: {embedding_dims}")
            print(f"   存储: InMemoryStore")
            print(f"   命名空间: ('memories',)")
            
        except Exception as e:
            logger.error(f"LangMem演示初始化失败: {e}")
            raise Exception(f"初始化失败: {e}")
    
    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return {
            "chat_model": f"{self.model_config.model_provider}:{self.model_config.model_name}",
            "embedding_model": f"{self.model_config.embedding_provider}:{self.model_config.embedding_model}",
            "chat_base_url": self.model_config.base_url or "默认",
            "embedding_base_url": self.model_config.embedding_base_url or "默认",
            "embedding_dimensions": str(self.model_config.get_embedding_dimensions())
        }
    
    def save_optimized_prompt(self, original_prompt: str, optimized_prompt: str, scenario: str, 
                            optimization_type: str, trajectories: List, filename: str = None) -> str:
        """
        保存优化后的提示词
        
        Args:
            original_prompt: 原始提示词
            optimized_prompt: 优化后的提示词
            scenario: 场景类型
            optimization_type: 优化类型
            trajectories: 使用的轨迹
            filename: 文件名，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"optimized_prompt_{scenario}_{timestamp}.json"
            
            # 创建logs目录（如果不存在）
            logs_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            filepath = os.path.join(logs_dir, filename)
            
            # 准备保存的数据
            data = {
                "original_prompt": original_prompt,
                "optimized_prompt": optimized_prompt,
                "scenario": scenario,
                "optimization_type": optimization_type,
                "trajectories_count": len(trajectories),
                "optimization_timestamp": datetime.now().isoformat(),
                "model_info": self.get_model_info(),
                "analysis": self.analyze_trajectories(trajectories)
            }
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"优化提示词已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            error_msg = f"保存优化提示词失败: {e}"
            logger.error(error_msg)
            return ""
    
    def load_optimized_prompt(self, filepath: str) -> Dict[str, Any]:
        """
        加载优化后的提示词
        
        Args:
            filepath: 文件路径
            
        Returns:
            加载的数据
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"已加载优化提示词: {filepath}")
            return data
            
        except Exception as e:
            error_msg = f"加载优化提示词失败: {e}"
            logger.error(error_msg)
            return {}

    def optimize_prompt(self, base_prompt: str, trajectories: List, optimization_type: str = "metaprompt") -> str:
        """
        优化提示词
        
        Args:
            base_prompt: 基础提示词
            trajectories: 对话轨迹
            optimization_type: 优化类型 ("metaprompt", "reflection", "feedback")
            
        Returns:
            优化后的提示词
        """
        try:
            logger.info(f"开始优化提示词，类型: {optimization_type}")
            
            optimizer = create_prompt_optimizer(
                self.llm, # 使用已初始化的聊天模型对象
                kind=optimization_type,
                config={
                    "max_reflection_steps": 3, 
                    "min_reflection_steps": 1,
                    "reflection_threshold": 0.7
                }
            )
            
            updated_prompt = optimizer.invoke({
                "trajectories": trajectories,
                "prompt": base_prompt
            })
            logger.info(f"优化后的提示词: {updated_prompt}")
            logger.info("提示词优化完成")
            return updated_prompt
        except Exception as e:
            error_msg = f"优化提示词失败: {e}"
            logger.error(error_msg)
            return base_prompt
    
    def analyze_trajectories(self, trajectories: List) -> Dict[str, Any]:
        """
        分析对话轨迹
        
        Args:
            trajectories: 对话轨迹列表
            
        Returns:
            分析结果
        """
        try:
            logger.info("开始分析对话轨迹")
            
            total_trajectories = len(trajectories)
            avg_score = sum(traj[1].get("score", 0) for traj in trajectories) / total_trajectories
            high_score_count = sum(1 for traj in trajectories if traj[1].get("score", 0) > 0.8)
            
            analysis = {
                "total_trajectories": total_trajectories,
                "average_score": avg_score,
                "high_score_count": high_score_count,
                "high_score_percentage": (high_score_count / total_trajectories) * 100,
                "score_distribution": {
                    "excellent": sum(1 for traj in trajectories if traj[1].get("score", 0) >= 0.9),
                    "good": sum(1 for traj in trajectories if 0.7 <= traj[1].get("score", 0) < 0.9),
                    "fair": sum(1 for traj in trajectories if 0.5 <= traj[1].get("score", 0) < 0.7),
                    "poor": sum(1 for traj in trajectories if traj[1].get("score", 0) < 0.5)
                }
            }
            
            logger.info(f"轨迹分析完成: 平均分数 {avg_score:.2f}")
            return analysis
        except Exception as e:
            error_msg = f"分析轨迹失败: {e}"
            logger.error(error_msg)
            return {}
    
    def create_sample_trajectories(self, scenario: str = "general") -> List:
        """
        创建示例对话轨迹
        
        Args:
            scenario: 场景类型 ("general", "technical", "creative", "customer_service")
            
        Returns:
            对话轨迹列表
        """
        if scenario == "technical":
            return [
                (
                    [
                        {"role": "user", "content": "解释什么是RESTful API？"},
                        {"role": "assistant", "content": "RESTful API是一种基于REST架构风格的API设计..."}
                    ],
                    {"score": 0.85, "comment": "技术解释准确，但可以添加更多实际例子"}
                ),
                (
                    [
                        {"role": "user", "content": "什么是微服务架构？"},
                        {"role": "assistant", "content": "微服务架构是一种将应用程序构建为一组小型自治服务的架构模式..."}
                    ],
                    {"score": 0.92, "comment": "很好的解释，包含了优缺点和适用场景"}
                ),
                (
                    [
                        {"role": "user", "content": "Docker和虚拟机有什么区别？"},
                        {"role": "assistant", "content": "Docker使用容器化技术，而虚拟机使用虚拟化技术..."}
                    ],
                    {"score": 0.78, "comment": "基本正确，但可以更详细地解释技术差异"}
                )
            ]
        elif scenario == "creative":
            return [
                (
                    [
                        {"role": "user", "content": "写一个关于太空探索的短故事"},
                        {"role": "assistant", "content": "在遥远的未来，人类终于踏上了火星的土地..."}
                    ],
                    {"score": 0.88, "comment": "故事有创意，但可以增加更多情感元素"}
                ),
                (
                    [
                        {"role": "user", "content": "设计一个未来城市的标志"},
                        {"role": "assistant", "content": "这个标志融合了科技感和人文关怀..."}
                    ],
                    {"score": 0.95, "comment": "设计理念很好，描述生动具体"}
                )
            ]
        elif scenario == "customer_service":
            return [
                (
                    [
                        {"role": "user", "content": "我的订单还没有收到"},
                        {"role": "assistant", "content": "我理解您的担忧，让我帮您查询订单状态..."}
                    ],
                    {"score": 0.82, "comment": "回应及时，但可以提供更多解决方案"}
                ),
                (
                    [
                        {"role": "user", "content": "产品有质量问题"},
                        {"role": "assistant", "content": "非常抱歉给您带来不便，我们立即为您处理..."}
                    ],
                    {"score": 0.89, "comment": "态度诚恳，解决方案明确"}
                )
            ]
        else:  # general
            return [
                (
                    [
                        {"role": "user", "content": "什么是机器学习？"},
                        {"role": "assistant", "content": "机器学习是人工智能的一个分支，它使计算机能够在没有明确编程的情况下学习和改进..."}
                    ],
                    {"score": 0.85, "comment": "回答准确但可以更详细"}
                ),
                (
                    [
                        {"role": "user", "content": "解释一下深度学习"},
                        {"role": "assistant", "content": "深度学习是机器学习的一个子领域，使用多层神经网络来模拟人脑的学习过程..."}
                    ],
                    {"score": 0.92, "comment": "很好的解释，包含了具体例子"}
                ),
                (
                    [
                        {"role": "user", "content": "如何学习编程？"},
                        {"role": "assistant", "content": "学习编程可以从基础开始，选择一门入门语言如Python..."}
                    ],
                    {"score": 0.78, "comment": "建议实用，但可以更系统化"}
                )
            ]





def demo_continuous_optimization(model_config: Optional[ModelConfig] = None):
    """演示持续优化过程"""
    print("\n🔄 持续优化过程演示")
    print("=" * 50)
    
    demo = LangMemDemo(model_config=model_config)
    
    # 初始提示词
    initial_prompt = "你是一个AI助手"
    
    print(f"   初始提示词: {initial_prompt}")
    
    # 第一轮优化
    print("\n📝 第一轮优化（基础对话）")
    trajectories_round1 = demo.create_sample_trajectories("general")
    optimized_prompt_1 = demo.optimize_prompt(initial_prompt, trajectories_round1)
    print(f"   优化后: {optimized_prompt_1}")
    
    # 第二轮优化（基于第一轮结果）
    print("\n📝 第二轮优化（技术对话）")
    trajectories_round2 = demo.create_sample_trajectories("technical")
    optimized_prompt_2 = demo.optimize_prompt(optimized_prompt_1, trajectories_round2)
    print(f"   优化后: {optimized_prompt_2}")
    
    # 第三轮优化（基于前两轮结果）
    print("\n📝 第三轮优化（创意对话）")
    trajectories_round3 = demo.create_sample_trajectories("creative")
    optimized_prompt_3 = demo.optimize_prompt(optimized_prompt_2, trajectories_round3)
    print(f"   优化后: {optimized_prompt_3}")
    
    print("\n📊 优化演进过程:")
    print(f"   初始 → 第一轮 → 第二轮 → 第三轮")
    print(f"   基础 → 通用优化 → 技术优化 → 创意优化")
    
    print("\n✅ 持续优化演示完成！")


def main():
    """主函数"""
    print("🚀 LangMem 提示词优化演示")
    print("=" * 60)
    
    try:
        # 使用自定义配置
        print("\n🔧 使用自定义模型配置:")
        from config import custom_config
        
    

        # 持续优化过程演示
        demo_continuous_optimization(custom_config)
        
        print("\n✅ 所有演示完成！")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 