"""
API配置文件
智谱AI GLM-4 配置
注意：生产环境请通过环境变量或.env文件传入API Key，不要硬编码
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 智谱AI (ZhipuAI) 配置
# ============================================================
ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "your_api_key_here")
ZHIPU_MODEL: str = "glm-4.7"        # 使用glm-4.7，稳定性好、延迟低
ZHIPU_MAX_TOKENS: int = 4096
ZHIPU_TEMPERATURE: float = 0.1           # 低温度，减少幻觉，保证输出稳定

# LLM请求超时（秒）
LLM_TIMEOUT: int = 60