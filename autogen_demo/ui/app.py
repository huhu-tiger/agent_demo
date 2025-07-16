"""
Gradio user interface for the multi-agent report generation system.
"""
import gradio as gr
import requests
import time
import threading
import queue

API_URL = "http://localhost:8000/generate_report"

# A queue to hold log messages
log_queue = queue.Queue()

def stream_logs():
    """Generator function to yield logs from the queue."""
    while True:
        try:
            log_message = log_queue.get(timeout=10)  # Wait for 10 seconds
            if log_message is None:  # Sentinel value to stop the stream
                break
            yield log_message
        except queue.Empty:
            # This allows the thread to check for the stop condition
            pass

def generate_report_and_logs(topic: str, date_range: str):
    """
    Makes a request to the backend API to generate a report and streams logs.
    """
    # Start the log streaming in a separate thread
    # This is a simplified placeholder. A robust solution would use WebSockets.
    def log_producer():
        # In a real implementation, you would connect to a WebSocket or SSE stream from the server.
        # Here, we simulate logs.
        log_queue.put("▶️ Request sent to backend...\n")
        
        try:
            response = requests.post(API_URL, json={"topic": topic}, timeout=600)
            response.raise_for_status()
            data = response.json()
            
            log_queue.put("✅ Backend process finished.\n")
            log_queue.put(f"📄 Report Status: {data['message']}\n")
            
            # Put the final report into the queue as well, to be handled by the main function
            log_queue.put(data['report_markdown'])

        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Error connecting to backend: {e}"
            log_queue.put(error_msg)
            log_queue.put(error_msg) # Send it again to update the report panel
        finally:
            log_queue.put(None) # Sentinel to stop the log streamer

    # Use a generator to yield updates to the UI
    log_thread = threading.Thread(target=log_producer)
    log_thread.start()

    log_output = ""
    final_report = "Generating... please wait."
    while True:
        try:
            item = log_queue.get(timeout=610) # Timeout slightly longer than request timeout
            if item is None:
                break
            
            # If it looks like a report, it's the final output
            if item.startswith("# Research Report"):
                final_report = item
            else: # Otherwise, it's a log message
                log_output += item
            
            yield log_output, final_report

        except queue.Empty:
            final_report = "Error: The generation process timed out."
            break
    
    log_thread.join()
    yield log_output, final_report


def build_ui():
    """Builds the Gradio UI."""
    with gr.Blocks(
        title="Intelligent Research Report Generator",
        theme="soft",
        css=".gradio-container {background-color: #f5f5f5}",
    ) as demo:
        gr.Markdown("# 🤖 Intelligent Research Report Generator")
        gr.Markdown(
            "Enter a topic below and the multi-agent system will generate a research report for you."
        )

        with gr.Row():
            with gr.Column(scale=3):
                topic_input = gr.Textbox(
                    label="Research Topic",
                    placeholder="e.g., The future of Generative AI in enterprise",
                )
                date_range_input = gr.Textbox(
                    label="Date Range (Optional)",
                    placeholder="e.g., 2024-01-01~2024-12-31",
                )
                start_button = gr.Button("Generate Report", variant="primary")

                gr.Markdown("---")
                report_output = gr.Markdown(label="Generated Report")

            with gr.Column(scale=2):
                log_output = gr.Textbox(
                    label="实时日志 (Live Logs)",
                    lines=30,
                    interactive=False,
                    autoscroll=True,
                )

        start_button.click(
            fn=generate_report_and_logs,
            inputs=[topic_input, date_range_input],
            outputs=[log_output, report_output],
        )

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch()
