# -*- coding: utf-8 -*-

"""
测试智能家居安装项目调度系统流式API
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000"

def test_streaming_installation_task():
    """测试流式安装任务API"""
    
    # 测试用例
    test_cases = [
        {
            "name": "智能门锁安装",
            "task": "需要安装：3个智能门锁（客厅/主卧/次卧），2个网络摄像头（前门/后院）"
        },
        {
            "name": "智能灯泡安装", 
            "task": "安装智能灯泡：客厅5个，卧室3个，厨房2个"
        }
    ]
    
    print("开始测试智能家居安装项目调度系统流式API...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print("-" * 40)
        
        # 准备请求数据
        request_data = {
            "task": test_case["task"]
        }
        
        try:
            print(f"发送请求: {test_case['task']}")
            print("开始接收流式响应...")
            print("-" * 30)
            
            # 发送POST请求并处理流式响应
            response = requests.post(
                f"{BASE_URL}/api/installation/task",
                json=request_data,
                headers={"Content-Type": "application/json"},
                stream=True,  # 启用流式传输
                timeout=120  # 设置120秒超时
            )
            
            if response.status_code == 200:
                print("✅ 流式连接建立成功!")
                
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        # 解码并解析SSE数据
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                data_str = line_str[6:]  # 移除 'data: ' 前缀
                                data = json.loads(data_str)
                                
                                # 根据消息类型处理
                                event_type = data.get('event_type', data.get('type', 'unknown'))
                                
                                if event_type == 'start':
                                    print(f"🚀 {data.get('message', '')}")
                                elif event_type == 'progress':
                                    source = data.get('source', 'unknown')
                                    message_type = data.get('message_type', 'unknown')
                                    content = data.get('content', '')
                                    
                                    # 处理内容显示
                                    if isinstance(content, dict):
                                        content_str = str(content)
                                    else:
                                        content_str = str(content)
                                    
                                    print(f"🤖 [{source}] ({message_type}) {content_str[:100]}{'...' if len(content_str) > 100 else ''}")
                                elif event_type == 'user_input':
                                    print(f"👤 {data.get('message', '')}")
                                elif event_type == 'complete':
                                    print(f"✅ {data.get('message', '')}")
                                elif event_type == 'error':
                                    print(f"❌ 错误: {data.get('message', '')}")
                                    if data.get('error'):
                                        print(f"   详情: {data.get('error', '')}")
                                else:
                                    print(f"📝 {data}")
                                    
                            except json.JSONDecodeError as e:
                                print(f"⚠️ JSON解析错误: {e}")
                                print(f"原始数据: {line_str}")
                            except Exception as e:
                                print(f"⚠️ 处理错误: {e}")
                
                print("-" * 30)
                print("✅ 流式响应处理完成!")
                
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接错误: 无法连接到服务器，请确保API服务正在运行")
        except requests.exceptions.Timeout:
            print("❌ 请求超时: 服务器响应时间过长")
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
        
        print("-" * 40)
    
    print("\n测试完成!")
    print("=" * 60)

def test_sync_api_compatibility():
    """测试同步API兼容性"""
    print("\n测试同步API兼容性...")
    
    request_data = {
        "task": "安装智能插座：客厅2个，卧室1个"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/installation/task/sync",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 同步API测试成功!")
            print(f"响应: {result.get('message', 'N/A')}")
        else:
            print(f"❌ 同步API测试失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 同步API测试异常: {str(e)}")

if __name__ == "__main__":
    print("智能家居安装项目调度系统流式API测试")
    print("请确保API服务正在运行: uvicorn fastapi_installation_system:app --host 0.0.0.0 --port 8000")
    print("=" * 60)
    
    # 测试流式API
    test_streaming_installation_task()
    
    # 测试同步API兼容性
    # test_sync_api_compatibility() 