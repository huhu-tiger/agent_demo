"""
Configuration loader for the multi-agent system.

This module loads environment variables from a .env file, performs necessary
substitutions, and makes them available as Python variables or sets them
back into the environment for other libraries like autogen to use.
"""
from dotenv import load_dotenv
import os
import string

# Load environment variables from .env file in the project root
load_dotenv()

# --- API Endpoints ---
BOCHAI_URL = os.getenv("BOCHAI_API_URL")
SEARXNG_URL = os.getenv("SEARXNG_API_URL")
VISION_URL = os.getenv("VISION_API_URL")

# --- API Tokens & Base URLs ---
QWEN_TOKEN = os.getenv("QWEN_PLUS_TOKEN")
DEEPSEEK_TOKEN = os.getenv("DEEPSEEK_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

def _setup_autogen_config():
    """
    Loads the OAI_CONFIG_LIST template, substitutes variables,
    and sets the final JSON string as an environment variable.
    """
    template_str = os.getenv("OAI_CONFIG_LIST_TEMPLATE")
    
    if not template_str:
        return

    # Create a dictionary of variables to substitute
    # Fallback to empty strings if a variable is not set
    substitutions = {
        "QWEN_PLUS_TOKEN": QWEN_TOKEN or "",
        "DEEPSEEK_API_KEY": DEEPSEEK_TOKEN or "",
        "QWEN_BASE_URL": QWEN_BASE_URL or "",
        "DEEPSEEK_BASE_URL": DEEPSEEK_BASE_URL or "",
    }
    
    # Use string.Template for safe substitution
    template = string.Template(template_str)
    final_config_str = template.substitute(substitutions)
    
    # Set the final, resolved JSON string as the OAI_CONFIG_LIST env var
    # so that autogen's config_list_from_json can find and use it.
    os.environ["OAI_CONFIG_LIST"] = final_config_str

# Run the setup function when the module is imported
_setup_autogen_config() 