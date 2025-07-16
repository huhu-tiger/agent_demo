"""
Configuration loader for the multi-agent system.

This module loads environment variables from a .env file and makes them
available as Python variables.
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env file in the project root
load_dotenv()

# --- API Endpoints ---
BOCHAI_URL = os.getenv("BOCHAI_API_URL")
SEARXNG_URL = os.getenv("SEARXNG_API_URL")
VISION_URL = os.getenv("VISION_API_URL")

# --- API Tokens ---
QWEN_TOKEN = os.getenv("QWEN_PLUS_TOKEN") 