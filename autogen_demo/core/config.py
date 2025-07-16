"""
Configuration loader for the multi-agent system.

This module loads environment variables from a .env file, performs necessary
substitutions, and makes them available as Python variables or sets them
back into the environment for other libraries like autogen to use.
"""
from dotenv import load_dotenv
import os
import string

# Load environment variables from .env file
load_dotenv()

# --- LLM Configurations ---
# The path to the OAI_CONFIG_LIST.json file is now defined in the .env file
# autogen will automatically use the OAI_CONFIG_LIST env var.

# --- API Configurations ---
BOCHAI_API_URL = os.getenv("BOCHAI_API_URL")
BOCHAI_API_KEY = os.getenv("BOCHAI_API_KEY")

SEARXNG_API_URL = os.getenv("SEARXNG_API_URL")

VISION_API_URL = os.getenv("VISION_API_URL")

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
print(222,LOG_LEVEL)

