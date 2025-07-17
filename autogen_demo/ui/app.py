"""
智能多体协作研究报告生成系统前端界面
"""
import gradio as gr
import requests
import time
import threading
import queue
import json

# API配置
API_URL_GENERATE = "http://localhost:8000/generate_report"
API_URL_LOGS = "http://localhost:8000/agent_logs"
API_URL_MODELS = "http://localhost:8000/models"

# 消息队列，用于存储日志和报告
log_queue = queue.Queue()
report_queue = queue.Queue()

def get_available_models():
    """获取可用模型列表"""
    try:
        response = requests.get(API_URL_MODELS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"available_models": [], "default_model": None}

def stream_agent_logs():
    """从后端获取智能体日志的生成器函数"""
    try:
        while True:
            response = requests.get(API_URL_LOGS)
            if response.status_code == 200:
                data = response.json()
                for log in data["logs"]:
                    yield log + "\n"
            time.sleep(2)  # 每2秒轮询一次
    except Exception as e:
        yield f"日志获取错误: {e}\n"

def generate_report_and_stream(topic: str, date_range: str, model_name: str):
    """
    向后端API发送报告生成请求并流式处理结果
    """
    def log_producer():
        """生产日志和报告的线程函数"""
        log_queue.put("▶️ 请求已发送到后端服务器...\n")
        
        try:
            # 准备请求数据
            request_data = {
                "topic": topic,
                "filters": {"date_range": date_range} if date_range else None
            }
            
            # 发送请求到后端API
            log_queue.put(f"🔍 正在为主题「{topic}」生成研究报告...\n")
            response = requests.post(API_URL_GENERATE, json=request_data, timeout=600)
            response.raise_for_status()
            data = response.json()
            
            # 处理响应
            log_queue.put("✅ 后端处理完成\n")
            log_queue.put(f"⏱️ 处理耗时: {data['execution_time']:.2f} 秒\n")
            log_queue.put(f"📄 报告状态: {data['message']}\n")
            
            # 将报告放入报告队列
            report_queue.put(data['report_markdown'])

        except requests.exceptions.Timeout:
            error_msg = "❌ 请求超时，报告生成时间过长"
            log_queue.put(f"{error_msg}\n")
            report_queue.put("## 报告生成失败\n\n生成过程超时，请稍后重试或尝试简化主题。")
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"❌ 后端服务返回错误: HTTP {e.response.status_code}"
            log_queue.put(f"{error_msg}\n")
            report_queue.put(f"## 报告生成失败\n\n{error_msg}")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ 连接后端服务失败: {e}"
            log_queue.put(f"{error_msg}\n")
            report_queue.put(f"## 报告生成失败\n\n无法连接到后端服务，请确认服务器是否正常运行。")
            
        except Exception as e:
            error_msg = f"❌ 处理过程中发生未知错误: {e}"
            log_queue.put(f"{error_msg}\n")
            report_queue.put(f"## 报告生成失败\n\n处理过程中发生未知错误。")
            
        finally:
            log_queue.put(None)  # 结束日志流的哨兵值

    # 创建并启动日志生产线程
    log_thread = threading.Thread(target=log_producer)
    log_thread.start()

    # 处理日志输出
    logs_output = ""
    report_content = "## 正在生成报告，请稍候...\n\n报告生成可能需要几分钟时间，取决于主题复杂度。"
    
    agent_status = [
        "🔄 规划智能体：正在分析主题...",
        "🔄 搜索智能体 BC：等待任务分配...",
        "🔄 搜索智能体 SX：等待任务分配...",
        "🔄 视觉智能体：等待图像分析任务...",
        "🔄 表格智能体：等待数据分析任务...",
        "🔄 报告智能体：等待素材整合..."
    ]
    
    # 模拟智能体状态更新的计数器
    status_counter = 0
    last_status_update = time.time()
    
    while True:
        try:
            # 更新智能体状态（模拟）
            current_time = time.time()
            if current_time - last_status_update >= 3:  # 每3秒更新一次状态
                if status_counter == 0:
                    agent_status[0] = "✅ 规划智能体：已完成主题分析"
                elif status_counter == 1:
                    agent_status[1] = "✅ 搜索智能体 BC：已完成信息检索"
                elif status_counter == 2:
                    agent_status[2] = "✅ 搜索智能体 SX：已完成图片搜索"
                elif status_counter == 3:
                    agent_status[3] = "✅ 视觉智能体：已完成图像分析"
                elif status_counter == 4:
                    agent_status[4] = "✅ 表格智能体：已完成数据分析"
                elif status_counter == 5:
                    agent_status[5] = "✅ 报告智能体：报告生成完毕"
                
                status_counter = (status_counter + 1) % 6
                last_status_update = current_time
            
            # 生成智能体状态HTML
            status_html = "<div style='margin-bottom:20px;'>\n"
            status_html += "<h3>智能体状态</h3>\n"
            status_html += "<ul>\n"
            for status in agent_status:
                status_html += f"<li>{status}</li>\n"
            status_html += "</ul>\n</div>\n\n"
            
            # 尝试从日志队列获取消息
            try:
                log_item = log_queue.get(timeout=0.5)
                if log_item is None:  # 检测到哨兵值
                    break
                logs_output += log_item
            except queue.Empty:
                pass
            
            # 尝试从报告队列获取报告
            try:
                report_item = report_queue.get_nowait()
                report_content = report_item
            except queue.Empty:
                pass
                
            # 将智能体状态添加到报告内容前面
            combined_output = status_html + report_content
            
            # 返回更新后的日志和报告
            yield logs_output, combined_output

        except Exception as e:
            logs_output += f"❌ UI更新过程中出错: {e}\n"
            yield logs_output, f"## 报告生成过程中出错\n\n{e}"
            break
    
    # 等待日志线程结束
    log_thread.join()
    
    # 最终更新，确保显示最新状态
    try:
        final_report = report_queue.get_nowait()
        report_content = final_report
    except queue.Empty:
        pass
        
    # 报告完成后，所有智能体状态都显示为已完成
    for i in range(len(agent_status)):
        if "🔄" in agent_status[i]:
            agent_status[i] = agent_status[i].replace("🔄", "✅").replace("等待任务分配...", "任务已完成").replace("正在分析主题...", "已完成主题分析")
    
    # 最终状态HTML
    final_status_html = "<div style='margin-bottom:20px;'>\n"
    final_status_html += "<h3>智能体状态</h3>\n"
    final_status_html += "<ul>\n"
    for status in agent_status:
        final_status_html += f"<li>{status}</li>\n"
    final_status_html += "</ul>\n</div>\n\n"
    
    combined_output = final_status_html + report_content
    yield logs_output, combined_output


def build_ui():
    """构建Gradio UI界面"""
    # 获取可用模型
    models_info = get_available_models()
    model_names = models_info.get("available_models", [])
    default_model = models_info.get("default_model")
    if not model_names:
        model_names = ["deepseek-v3", "qwen-plus", "qwen-vl", "deepseek-r1"]
    
    with gr.Blocks(
        title="智能多体协作研究报告生成系统",
        theme="soft",
        css="""
        .gradio-container {background-color: #f7f7f7}
        .report-container {min-height: 500px; border: 1px solid #ddd; padding: 10px; border-radius: 5px; background-color: white}
        .logs-container {font-family: monospace; background-color: #2b2b2b; color: #f8f8f2; padding: 15px; border-radius: 5px}
        """
    ) as demo:
        gr.Markdown("# 🤖 智能多体协作研究报告生成系统")
        gr.Markdown(
            "输入研究主题，多智能体系统将自动搜集信息、分析数据，并生成一份专业的研究报告。"
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                topic_input = gr.Textbox(
                    label="研究主题",
                    placeholder="例如：生成式AI在企业中的应用趋势",
                )
                
                with gr.Row():
                    date_range_input = gr.Textbox(
                        label="日期范围（可选）",
                        placeholder="例如：2024-01-01~2024-12-31",
                        scale=3
                    )
                    model_dropdown = gr.Dropdown(
                        label="使用模型",
                        choices=model_names,
                        value=default_model or model_names[0] if model_names else None,
                        scale=2
                    )
                
                start_button = gr.Button("开始生成报告", variant="primary", size="lg")

        with gr.Row():
            # 左侧：报告生成进度和结果
            with gr.Column(scale=3, elem_classes="report-container"):
                gr.Markdown("### 研究报告")
                report_output = gr.Markdown()
            
            # 右侧：实时日志
            with gr.Column(scale=2, elem_classes="logs-container"):
                gr.Markdown("### 实时日志")
                log_output = gr.Textbox(
                    label="",
                    lines=25,
                    max_lines=50,
                    interactive=False,
                    autoscroll=True,
                    elem_classes="logs-output"
                )
        
        # 下载按钮
        with gr.Row():
            download_button = gr.Button("📥 下载报告(Markdown)", variant="secondary")
        
        # 事件处理
        start_button.click(
            fn=generate_report_and_stream,
            inputs=[topic_input, date_range_input, model_dropdown],
            outputs=[log_output, report_output]
        )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="0.0.0.0", share=True)
