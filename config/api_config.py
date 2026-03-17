"""
API配置文件
智谱AI GLM-4 配置及各模块输出路径配置

注意：请将 ZHIPU_API_KEY 设置为您在智谱AI平台申请的 API Key。
推荐做法：在项目根目录创建 .env 文件并写入：
    ZHIPU_API_KEY=your_actual_api_key
或直接在运行前设置环境变量：
    export ZHIPU_API_KEY=your_actual_api_key
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 项目根目录（自动计算，无需修改）
# ============================================================
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# 智谱AI (ZhipuAI) 配置
# ============================================================
ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "your_api_key_here")
ZHIPU_MODEL: str = "glm-4-flash"       # 使用glm-4-flash，稳定性好、延迟低
ZHIPU_MAX_TOKENS: int = 4096
ZHIPU_TEMPERATURE: float = 0.1          # 低温度，减少幻觉，保证输出稳定

# LLM请求超时（秒）
LLM_TIMEOUT: int = 60
# LLM请求失败时的最大重试次数
LLM_MAX_RETRIES: int = 3

# ============================================================
# 数据库路径配置
# ============================================================
DB_PATH: str = os.getenv(
    "IKEA_DB_PATH",
    os.path.join(_PROJECT_ROOT, "data", "ikea_parts.db")
)

# ============================================================
# 输出目录配置
# ============================================================
BOM_OUTPUT_DIR: str = os.getenv(
    "BOM_OUTPUT_DIR",
    os.path.join(_PROJECT_ROOT, "output", "bom")
)

CAD_OUTPUT_DIR: str = os.getenv(
    "CAD_OUTPUT_DIR",
    os.path.join(_PROJECT_ROOT, "output", "cad")
)

MANUAL_OUTPUT_DIR: str = os.getenv(
    "MANUAL_OUTPUT_DIR",
    os.path.join(_PROJECT_ROOT, "output", "manual")
)
