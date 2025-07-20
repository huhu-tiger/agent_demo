from typing import Iterator
import sys
from pathlib import Path
from agno.agent import Agent
from agno.run.response import RunResponse, RunResponseEvent, RunResponseContentEvent, RunEvent
from agno.models.openai import OpenAIChat
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow
# 确保可以导入config模块
current_dir = Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

import config  # 使用绝对导入
from config import model_config_manager  # 导入模型配置管理器

print(model_config_manager.models)
model_name="Qwen3-235B"
reasoning_model_name="deepseek-r1"
class CacheWorkflow(Workflow):
    # Purely descriptive, not used by the workflow
    description: str = "A workflow that caches previous outputs"

    # Add agents or teams as attributes on the workflow
    agent = Agent(model=OpenAIChat(
        id=model_config_manager.models[model_name].model_name,  # 模型ID
        name=model_config_manager.models[model_name].model_name,  # 模型名称
        api_key=model_config_manager.models[model_name].api_key,  # API密钥
        base_url=model_config_manager.models[model_name].url,  # API基础URL
        role_map={        
            "system": "system",
            "user": "user",
            "assistant": "assistant",
            "tool": "tool",
            "model": "assistant"
            }
    ),)

    # Write the logic in the `run()` method
    def run(self, message: str) -> Iterator[RunResponseEvent]:
        logger.info(f"Checking cache for '{message}'")
        # Check if the output is already cached
        if (cached_content := self.session_state.get(message)):
            logger.info(f"Cache hit for '{message}'")
            # 产出一个 RunResponseContentEvent，模拟流式输出
            yield 
            (
                run_id=self.run_id,
                content=cached_content,
            )
            return

        logger.info(f"Cache miss for '{message}'")
        # Run the agent and yield the response
        yield from self.agent.run(message, stream=True)

        # Cache the output after response is yielded
        self.session_state[message] = self.agent.run_response.content


if __name__ == "__main__":
    workflow = CacheWorkflow()
    # Run workflow (this is takes ~1s)
    response = workflow.run(message="Tell me a joke.")
    # Print the response
    pprint_run_response(response, markdown=True, show_time=True)
    # Run workflow again (this is immediate because of caching)
    response = workflow.run(message="Tell me a joke.")
    # Print the response
    pprint_run_response(response, markdown=True, show_time=True)
