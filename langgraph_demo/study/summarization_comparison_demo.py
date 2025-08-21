#!/usr/bin/env python3
"""
摘要前后内容对比演示
专门展示LangMem摘要功能的效果
"""

import os
import sys
from typing import List, Dict, Any
from datetime import datetime
import uuid

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langmem.short_term import summarize_messages, RunningSummary

import config
from config import logger


def add_message_ids(messages: List[BaseMessage]) -> List[BaseMessage]:
    """为消息添加ID字段"""
    for message in messages:
        if not hasattr(message, 'id') or message.id is None:
            message.id = str(uuid.uuid4())
    return messages


def print_messages_summary(messages: List[BaseMessage], title: str = "消息内容"):
    """打印消息内容的详细摘要信息"""
    print(f"\n📋 {title}:")
    print("=" * 60)
    
    total_chars = 0
    total_messages = len(messages)
    
    for i, message in enumerate(messages, 1):
        if hasattr(message, "content"):
            content = message.content
            if isinstance(content, str):
                chars = len(content)
                total_chars += chars
                print(f"消息{i} ({chars}字符):")
                print(f"  内容: {content}")
                print()
            elif isinstance(content, list):
                # 处理多模态内容
                for j, item in enumerate(content):
                    if hasattr(item, "text"):
                        text = item.text
                        chars = len(text)
                        total_chars += chars
                        print(f"消息{i}-{j+1} ({chars}字符):")
                        print(f"  内容: {text}")
                        print()
            else:
                content_str = str(content)
                chars = len(content_str)
                total_chars += chars
                print(f"消息{i} ({chars}字符):")
                print(f"  内容: {content_str}")
                print()
        elif isinstance(message, dict) and "content" in message:
            content = message["content"]
            chars = len(content)
            total_chars += chars
            print(f"消息{i} ({chars}字符):")
            print(f"  内容: {content}")
            print()
        else:
            print(f"消息{i}: 无法解析内容")
    
    print(f"📊 统计信息:")
    print(f"   消息数量: {total_messages}")
    print(f"   总字符数: {total_chars}")
    print(f"   平均字符数: {total_chars // total_messages if total_messages > 0 else 0}")
    print("=" * 60)


def safe_token_counter(messages: List[BaseMessage]) -> int:
    """安全的token计数器"""
    try:
        total_chars = 0
        for message in messages:
            if hasattr(message, "content"):
                content = message.content
                if isinstance(content, str):
                    total_chars += len(content)
                else:
                    total_chars += len(str(content))
        
        # 粗略估算：每4字符一个token
        return max(1, total_chars // 4)
    except Exception:
        return 1


def demo_summarization_comparison():
    """演示摘要前后对比"""
    print("🎯 LangMem摘要前后对比演示")
    print("=" * 60)
    
    # 创建模型
    model = ChatOpenAI(
        model=config.model,
        temperature=0.1,
        openai_api_base=config.base_url,
        openai_api_key=config.api_key
    )
    
    summarization_model = model.bind(max_tokens=128)
    
    # 创建长对话历史
    conversation_history = [
        SystemMessage(content="你是一个专业的AI助手，专门回答关于人工智能和机器学习的问题。请用中文回答，并保持专业性和准确性。"),
        HumanMessage(content="你好，我想了解一下人工智能的发展历史。人工智能这个概念最早是在什么时候提出的？"),
        AIMessage(content="人工智能的发展历史可以追溯到1950年代。1950年，艾伦·图灵提出了著名的图灵测试，这被认为是人工智能研究的开端。1956年，在达特茅斯会议上，约翰·麦卡锡首次提出了'人工智能'这个术语，标志着人工智能作为一个独立学科的正式诞生。"),
        HumanMessage(content="能详细说说机器学习的发展阶段吗？从最早的符号主义到现在的深度学习，每个阶段都有什么特点？"),
        AIMessage(content="机器学习的发展经历了几个重要阶段：1. 符号主义时期（1950-1980）：基于逻辑和规则，使用符号推理方法。2. 连接主义时期（1980-2000）：基于神经网络，模拟人脑神经元连接。3. 统计学习时期（2000-2010）：基于统计学方法，如支持向量机、随机森林等。4. 深度学习时期（2010至今）：基于深度神经网络，在大数据和强大计算能力支持下取得突破。"),
        HumanMessage(content="深度学习是什么时候兴起的？为什么深度学习在2010年代突然变得这么重要？"),
        AIMessage(content="深度学习的概念可以追溯到1940年代，但真正的兴起是在2010年代。2012年，AlexNet在ImageNet竞赛中的突破性表现标志着深度学习时代的开始。深度学习在2010年代变得重要的原因包括：1. 大数据时代的到来提供了充足的训练数据。2. GPU等硬件的发展提供了强大的计算能力。3. 算法的改进，如ReLU激活函数、Dropout正则化等。4. 开源框架的普及，如TensorFlow、PyTorch等。"),
        HumanMessage(content="神经网络的历史可以追溯到什么时候？最早的神经网络模型是什么样的？"),
        AIMessage(content="神经网络的历史可以追溯到1943年，当时Warren McCulloch和Walter Pitts提出了第一个数学模型来模拟神经元的工作方式。1957年，Frank Rosenblatt发明了感知器（Perceptron），这是第一个能够学习的神经网络模型。感知器是一个单层神经网络，只能解决线性可分的问题。1969年，Marvin Minsky和Seymour Papert指出了感知器的局限性，导致神经网络研究进入低谷期。直到1980年代，反向传播算法的提出才重新激活了神经网络研究。"),
        HumanMessage(content="能讲讲图灵测试吗？这个测试是如何判断一个机器是否具有智能的？"),
        AIMessage(content="图灵测试是由艾伦·图灵在1950年提出的，用于判断机器是否具有智能的测试方法。测试的基本思想是：如果一个人在与机器对话时，无法判断对方是人还是机器，那么就可以认为这台机器具有智能。具体测试过程是：测试者通过文字与两个对象（一个人类，一个机器）进行对话，但不知道哪个是人类哪个是机器。如果测试者无法准确判断，或者判断错误率超过50%，那么这台机器就通过了图灵测试。图灵测试的意义在于它提供了一个客观的、可操作的智能定义，虽然它也有局限性，但至今仍是人工智能领域的重要概念。"),
        HumanMessage(content="什么是专家系统？专家系统在人工智能发展史上扮演了什么角色？"),
        AIMessage(content="专家系统是人工智能的一个重要分支，它是一种基于知识的计算机程序，能够模拟人类专家在特定领域的推理和决策过程。专家系统主要由知识库、推理机和用户界面组成。知识库存储领域专家的知识和经验，推理机根据知识库中的规则进行推理，用户界面提供人机交互功能。专家系统在1970-1980年代非常流行，代表性的系统包括DENDRAL（化学分析）、MYCIN（医疗诊断）、XCON（计算机配置）等。专家系统在人工智能发展史上扮演了重要角色：1. 证明了基于知识的推理方法的有效性。2. 推动了知识表示和推理技术的发展。3. 为后来的机器学习方法奠定了基础。4. 在特定领域取得了实际应用的成功。"),
        HumanMessage(content="自然语言处理的发展历程是怎样的？从最早的规则方法到现在的大语言模型，经历了哪些重要阶段？"),
        AIMessage(content="自然语言处理的发展历程可以分为几个重要阶段：1. 规则方法时期（1950-1980）：基于语言学规则和手工编写的语法规则，如Chomsky的转换生成语法。2. 统计方法时期（1980-2010）：基于概率统计和机器学习方法，如隐马尔可夫模型、条件随机场等。3. 神经网络时期（2010-2017）：使用神经网络进行语言建模，如Word2Vec、RNN、LSTM等。4. 预训练模型时期（2017-2020）：如BERT、GPT等预训练语言模型的出现。5. 大语言模型时期（2020至今）：如GPT-3、ChatGPT、GPT-4等大规模语言模型，在理解和生成能力上取得了突破性进展。每个阶段都有其特点和贡献，推动了自然语言处理技术的不断进步。"),
        HumanMessage(content="计算机视觉的发展历史如何？从最早的图像处理到现在的高级视觉理解，有哪些关键技术突破？"),
        AIMessage(content="计算机视觉的发展历史可以分为几个重要阶段：1. 早期图像处理（1960-1980）：主要关注低层图像处理，如边缘检测、图像滤波等。2. 特征工程时期（1980-2000）：手工设计特征，如SIFT、HOG等特征描述子。3. 机器学习时期（2000-2010）：使用机器学习方法进行图像分类和识别，如支持向量机、随机森林等。4. 深度学习时期（2010-2020）：深度卷积神经网络的出现，如AlexNet、VGG、ResNet等，在图像识别任务上取得了突破性进展。5. 高级视觉理解时期（2020至今）：如目标检测、图像分割、视觉问答等高级任务，以及多模态模型的兴起。关键技术突破包括：卷积神经网络、注意力机制、Transformer架构、自监督学习等。"),
        HumanMessage(content="强化学习是什么时候提出的？强化学习与其他机器学习方法有什么不同？"),
        AIMessage(content="强化学习的概念可以追溯到1950年代，但真正的发展是在1980年代。1957年，Richard Bellman提出了动态规划方法，为强化学习奠定了基础。1989年，Chris Watkins提出了Q-learning算法，这是强化学习的重要里程碑。强化学习与其他机器学习方法的主要区别在于：1. 学习方式：强化学习通过与环境交互来学习，而不是从标注数据中学习。2. 目标：强化学习的目标是最大化长期累积奖励，而不是最小化预测误差。3. 探索与利用：强化学习需要在探索新策略和利用已知策略之间平衡。4. 时序性：强化学习考虑时序决策问题，当前决策会影响未来的状态和奖励。强化学习在游戏、机器人控制、自动驾驶等领域取得了重要应用。"),
        HumanMessage(content="能详细解释一下监督学习和无监督学习的区别吗？它们各自适用于什么场景？")
    ]
    
    # 为消息添加ID
    conversation_history = add_message_ids(conversation_history)
    
    print_messages_summary(conversation_history, "原始对话历史")
    
    # 计算原始token数
    original_tokens = safe_token_counter(conversation_history)
    print(f"\n🔢 原始对话Token数: {original_tokens}")
    
    # 进行摘要
    print("\n🔄 开始摘要处理...")
    print("-" * 40)
    
    try:
        summarization_result = summarize_messages(
            conversation_history,
            running_summary=None,  # 没有之前的摘要
            token_counter=safe_token_counter,
            model=summarization_model,
            max_tokens=512,  # 最大总token数
            max_tokens_before_summary=256,  # 触发摘要的token阈值
            max_summary_tokens=128  # 摘要最大token数
        )
        
        print("✅ 摘要处理完成!")
        
        # 打印摘要结果
        print("\n📋 摘要结果:")
        print("-" * 40)
        
        if summarization_result.running_summary:
            logger.info(f"运行摘要: {summarization_result.running_summary.summary}")
            logger.info(f"摘要字符数: {len(summarization_result.running_summary.summary)}")
            logger.info(f"摘要Token数: {safe_token_counter([SystemMessage(content=summarization_result.running_summary.summary)])}")
        

        print_messages_summary(summarization_result.messages, "摘要后的消息")
        
        # 计算摘要后的token数
        summarized_tokens = safe_token_counter(summarization_result.messages)
        print(f"\n🔢 摘要后Token数: {summarized_tokens}")
        
        # 计算压缩比
        compression_ratio = (1 - summarized_tokens / original_tokens) * 100
        print(f"\n📊 压缩效果:")
        print(f"   原始Token数: {original_tokens}")
        print(f"   摘要后Token数: {summarized_tokens}")
        print(f"   压缩比例: {compression_ratio:.1f}%")
        print(f"   Token节省: {original_tokens - summarized_tokens}")
        
        # 测试摘要质量
        print(f"\n🧪 摘要质量测试:")
        print("-" * 40)
        
        # 使用摘要后的消息进行对话
        test_message = HumanMessage(content="基于我们之前的讨论，你能总结一下人工智能发展的主要里程碑吗？")
        test_message.id = str(uuid.uuid4())  # 添加ID
        
        # 构建包含摘要的完整消息
        if summarization_result.running_summary:
            summary_message = SystemMessage(content=f"对话摘要: {summarization_result.running_summary.summary}")
            summary_message.id = str(uuid.uuid4())  # 添加ID
            # test_messages = [summary_message] + summarization_result.messages + [test_message]
            test_messages = [summary_message] + [test_message]
        else:
            test_messages = summarization_result.messages + [test_message]
        
        print("使用摘要后的上下文进行回答...")
        response = model.invoke(test_messages)
        print(f"回答: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 摘要处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_progressive_summarization():
    """演示渐进式摘要过程"""
    print("\n🎯 渐进式摘要过程演示")
    print("=" * 60)
    
    # 创建模型
    model = ChatOpenAI(
        model=config.model,
        temperature=0.1,
        openai_api_base=config.base_url,
        openai_api_key=config.api_key
    )
    
    summarization_model = model.bind(max_tokens=128)
    
    # 模拟渐进式对话
    conversation_stages = [
        # 第1阶段：基础对话
        [
            SystemMessage(content="你是一个有用的AI助手"),
            HumanMessage(content="你好，请介绍一下自己"),
            AIMessage(content="你好！我是一个AI助手，很高兴为您服务。我可以帮助您解答各种问题，包括技术、科学、历史、文学等各个领域。请随时向我提问！")
        ],
        
        # 第2阶段：添加更多对话
        [
            SystemMessage(content="你是一个有用的AI助手"),
            HumanMessage(content="你好，请介绍一下自己"),
            AIMessage(content="你好！我是一个AI助手，很高兴为您服务。我可以帮助您解答各种问题，包括技术、科学、历史、文学等各个领域。请随时向我提问！"),
            HumanMessage(content="什么是机器学习？"),
            AIMessage(content="机器学习是人工智能的一个子领域，它使计算机能够在没有明确编程的情况下学习和改进。机器学习算法通过分析数据来识别模式，并使用这些模式来做出预测或决策。主要类型包括监督学习、无监督学习和强化学习。")
        ],
        
        # 第3阶段：继续扩展
        [
            SystemMessage(content="你是一个有用的AI助手"),
            HumanMessage(content="你好，请介绍一下自己"),
            AIMessage(content="你好！我是一个AI助手，很高兴为您服务。我可以帮助您解答各种问题，包括技术、科学、历史、文学等各个领域。请随时向我提问！"),
            HumanMessage(content="什么是机器学习？"),
            AIMessage(content="机器学习是人工智能的一个子领域，它使计算机能够在没有明确编程的情况下学习和改进。机器学习算法通过分析数据来识别模式，并使用这些模式来做出预测或决策。主要类型包括监督学习、无监督学习和强化学习。"),
            HumanMessage(content="深度学习是什么？"),
            AIMessage(content="深度学习是机器学习的一个分支，它使用多层神经网络来模拟人脑的学习过程。深度学习模型能够自动学习数据的层次化表示，在图像识别、自然语言处理、语音识别等领域取得了突破性进展。常见的深度学习架构包括卷积神经网络(CNN)、循环神经网络(RNN)和Transformer等。"),
            HumanMessage(content="计算机视觉的发展历史如何？从最早的图像处理到现在的高级视觉理解，有哪些关键技术突破？"),
            AIMessage(content="计算机视觉的发展历史可以分为几个重要阶段：1. 早期图像处理（1960-1980）：主要关注低层图像处理，如边缘检测、图像滤波等。2. 特征工程时期（1980-2000）：手工设计特征，如SIFT、HOG等特征描述子。3. 机器学习时期（2000-2010）：使用机器学习方法进行图像分类和识别，如支持向量机、随机森林等。4. 深度学习时期（2010-2020）：深度卷积神经网络的出现，如AlexNet、VGG、ResNet等，在图像识别任务上取得了突破性进展。5. 高级视觉理解时期（2020至今）：如目标检测、图像分割、视觉问答等高级任务，以及多模态模型的兴起。关键技术突破包括：卷积神经网络、注意力机制、Transformer架构、自监督学习等。"),
            HumanMessage(content="强化学习是什么时候提出的？强化学习与其他机器学习方法有什么不同？"),
            AIMessage(content="强化学习的概念可以追溯到1950年代，但真正的发展是在1980年代。1957年，Richard Bellman提出了动态规划方法，为强化学习奠定了基础。1989年，Chris Watkins提出了Q-learning算法，这是强化学习的重要里程碑。强化学习与其他机器学习方法的主要区别在于：1. 学习方式：强化学习通过与环境交互来学习，而不是从标注数据中学习。2. 目标：强化学习的目标是最大化长期累积奖励，而不是最小化预测误差。3. 探索与利用：强化学习需要在探索新策略和利用已知策略之间平衡。4. 时序性：强化学习考虑时序决策问题，当前决策会影响未来的状态和奖励。强化学习在游戏、机器人控制、自动驾驶等领域取得了重要应用。"),
            HumanMessage(content="能详细解释一下监督学习和无监督学习的区别吗？它们各自适用于什么场景？")
        ]
    ]
    
    running_summary = None
    
    for stage, messages in enumerate(conversation_stages, 1):
        print(f"\n🔄 第{stage}阶段对话:")
        print("-" * 40)
        
        # 为消息添加ID
        messages = add_message_ids(messages)
        
        # 打印当前消息
        print_messages_summary(messages, f"第{stage}阶段消息")
        
        # 计算当前token数
        current_tokens = safe_token_counter(messages)
        print(f"当前Token数: {current_tokens}")
        
        # 如果有运行摘要，显示它
        if running_summary:
            print(f"\n📝 当前运行摘要: {running_summary.summary}")
            print(f"摘要字符数: {len(running_summary.summary)}")
        
        # 进行摘要
        try:
            summarization_result = summarize_messages(
                messages,
                running_summary=running_summary,
                token_counter=safe_token_counter,
                model=summarization_model,
                max_tokens=512,
                max_tokens_before_summary=256,
                max_summary_tokens=128
            )
            
            # 更新运行摘要
            if summarization_result.running_summary:
                running_summary = summarization_result.running_summary
                print(f"\n✅ 第{stage}阶段摘要完成:")
                print(f"   新摘要: {running_summary.summary}")
                print(f"   摘要字符数: {len(running_summary.summary)}")
            else:
                print(f"\n✅ 第{stage}阶段无需摘要")
            
            # 显示摘要后的消息
            if summarization_result.messages != messages:
                print(f"\n📋 摘要后的消息:")
                print_messages_summary(summarization_result.messages, f"第{stage}阶段摘要后")
                
                summarized_tokens = safe_token_counter(summarization_result.messages)
                compression_ratio = (1 - summarized_tokens / current_tokens) * 100
                print(f"压缩比例: {compression_ratio:.1f}%")
            
        except Exception as e:
            print(f"❌ 第{stage}阶段摘要失败: {e}")
    
    print(f"\n✅ 渐进式摘要演示完成!")


def main():
    """主函数"""
    print("🚀 LangMem摘要前后对比演示")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 演示1：摘要前后对比
    if demo_summarization_comparison():
        print("\n✅ 摘要前后对比演示完成")
        
        # 演示2：渐进式摘要
        demo_progressive_summarization()
        
        print("\n🎉 所有演示完成！")
    else:
        print("\n❌ 摘要演示失败")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main() 