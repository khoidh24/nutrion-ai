"""
Configuration module for AI Agent.
Supports multiple LLM providers: Deepseek, Claude, OpenAI
"""

import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMProvider(Enum):
    """Supported LLM providers"""
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"
    OPENAI = "openai"


@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: LLMProvider
    api_key: str
    model: str
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7


# Provider-specific configurations
PROVIDER_CONFIGS = {
    LLMProvider.DEEPSEEK: {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
    },
    LLMProvider.CLAUDE: {
        "base_url": "https://api.anthropic.com/v1",
        "default_model": "claude-3-5-sonnet-20241022",
    },
    LLMProvider.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
    },
}


def get_llm_config(provider: str = None) -> LLMConfig:
    """
    Get LLM configuration from environment variables.
    
    Environment variables:
    - MODEL_API_KEY: API key for the selected provider
    - LLM_PROVIDER: Provider name (deepseek, claude, openai). Default: deepseek
    - LLM_MODEL: Model name (optional, uses provider default if not set)
    - LLM_MAX_TOKENS: Max tokens for response (default: 4096)
    - LLM_TEMPERATURE: Temperature for generation (default: 0.7)
    """
    # Get provider from env or parameter
    provider_name = provider or os.getenv("LLM_PROVIDER", "deepseek").lower()
    
    try:
        llm_provider = LLMProvider(provider_name)
    except ValueError:
        raise ValueError(f"Unsupported provider: {provider_name}. "
                        f"Supported: {[p.value for p in LLMProvider]}")
    
    # Get API key
    api_key = os.getenv("MODEL_API_KEY")
    if not api_key:
        raise ValueError("MODEL_API_KEY environment variable is required")
    
    # Get provider config
    provider_config = PROVIDER_CONFIGS[llm_provider]
    
    return LLMConfig(
        provider=llm_provider,
        api_key=api_key,
        model=os.getenv("LLM_MODEL", provider_config["default_model"]),
        base_url=provider_config["base_url"],
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    )


# Web search configuration
SEARCH_CONFIG = {
    "serper_api_key": os.getenv("SERPER_API_KEY"),  # For Google Search via Serper
    "max_results": int(os.getenv("SEARCH_MAX_RESULTS", "5")),
}


# Paths - support both normal run and PyInstaller exe
import sys
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(__file__)

PROMPTS_DIR = os.path.join(BASE_DIR, "knowledge_base", "prompts")
TEMPLATES_DIR = os.path.join(BASE_DIR, "knowledge_base", "templates")


def get_system_prompt() -> str:
    """Load system prompt from file"""
    prompt_path = os.path.join(PROMPTS_DIR, "SYSTEM_PROMPT.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def get_template(name: str) -> str:
    """Load template by name"""
    template_path = os.path.join(TEMPLATES_DIR, f"{name}.md")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()
