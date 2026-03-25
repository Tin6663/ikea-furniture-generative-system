"""
API配置文件
智谱AI GLM-4 配置 & 本地数据库路径
注意：生产环境请通过环境变量或 .env 文件传入敏感信息
"""

import os
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# 数据库路径配置
# ============================================================
# 允许通过环境变量 DB_PATH 覆盖，默认使用仓库内 data/ikea_parts.db
DB_PATH: str = os.getenv("DB_PATH", os.path.join(PROJECT_ROOT, "data", "ikea_parts.db"))

# ============================================================
# 输出目录配置
# ============================================================
OUTPUT_ROOT = os.getenv("OUTPUT_ROOT", os.path.join(PROJECT_ROOT, "output"))
BOM_OUTPUT_DIR = os.getenv("BOM_OUTPUT_DIR", os.path.join(OUTPUT_ROOT, "bom"))
CAD_OUTPUT_DIR = os.getenv("CAD_OUTPUT_DIR", os.path.join(OUTPUT_ROOT, "cad"))
MANUAL_OUTPUT_DIR = os.getenv("MANUAL_OUTPUT_DIR", os.path.join(OUTPUT_ROOT, "manual"))

# ============================================================
# 智谱AI (ZhipuAI) 配置
# ============================================================
ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "your_api_key_here")
ZHIPU_MODEL: str = os.getenv("ZHIPU_MODEL", "glm-4.7")  # 默认稳定版本
ZHIPU_MAX_TOKENS: int = int(os.getenv("ZHIPU_MAX_TOKENS", "4096"))
ZHIPU_TEMPERATURE: float = float(os.getenv("ZHIPU_TEMPERATURE", "0.1"))  # 低温度，减少幻觉

# LLM请求超时与重试
LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))
LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
