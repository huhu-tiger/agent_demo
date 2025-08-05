# -*- coding: utf-8 -*-

"""
测试智能家居安装项目调度系统API
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000"

def test_installation_task_api():
    """测试安装任务API接口"""
    
    # 测试用例
    test_cases = [
        {
            "name": "智能门锁安装",
            "task": "需要安装：3个智能门锁（客厅/主卧/次卧），2个网络摄像头（前门/后院）"
        },
        {
            "name": "智能灯泡安装", 
            "task": "安装智能灯泡：客厅5个，卧室3个，厨房2个"
        },
        {
            "name": "智能插座安装",
            "task": "安装智能插座：客厅2个，卧室1个，厨房1个"
        }
    ]
    
    print("开始测试智能家居安装项目调度系统API...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print("-" * 30)
        
        # 准备请求数据
        request_data = {
            "task": test_case["task"]
        }
        
        try:
            # 发送POST请求
            print(f"发送请求: {test_case['task']}")
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}/api/installation/task",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=60  # 设置60秒超时
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应时间: {response_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 请求成功!")
                print(f"响应消息: {result.get('message', 'N/A')}")
                print(f"任务结果状态: {result.get('task_result', {}).get('status', 'N/A')}")
                
                # 如果有任务结果，显示部分信息
                if result.get('task_result') and result['task_result'].get('messages'):
                    messages = result['task_result']['messages']
                    print(f"返回消息数量: {len(messages)}")
                    if messages:
                        print(f"最后一条消息: {messages[-1][:100]}...")
                        
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接错误: 无法连接到服务器，请确保API服务正在运行")
        except requests.exceptions.Timeout:
            print("❌ 请求超时: 服务器响应时间过长")
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
        
        print("-" * 30)
    
    print("\n测试完成!")
    print("=" * 50)

def test_health_check():
    """测试健康检查接口"""
    print("\n测试健康检查接口...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")

def test_examples_endpoint():
    """测试示例接口"""
    print("\n测试示例接口...")
    try:
        response = requests.get(f"{BASE_URL}/api/installation/examples")
        if response.status_code == 200:
            print("✅ 示例接口正常")
            examples = response.json().get('examples', [])
            print(f"可用示例数量: {len(examples)}")
            for i, example in enumerate(examples, 1):
                print(f"示例{i}: {example}")
        else:
            print(f"❌ 示例接口失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 示例接口异常: {str(e)}")

if __name__ == "__main__":
    print("智能家居安装项目调度系统API测试")
    print("请确保API服务正在运行: uvicorn fastapi_installation_system:app --host 0.0.0.0 --port 8000")
    print("=" * 50)
    
    # 测试健康检查
    # test_health_check()
    
    # 测试示例接口
    # test_examples_endpoint()
    
    # 测试主要功能
    test_installation_task_api() 