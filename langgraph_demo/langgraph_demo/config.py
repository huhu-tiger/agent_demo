

from dataclasses import dataclass
from typing import Dict

@dataclass
class ModelConfig:
    url: str
    api_key: str
    model_name: str 
    model_type: str

@dataclass
class ModelConfigManager:
    model_configs: Dict[str, ModelConfig]




