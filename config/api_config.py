"""
API配置文件
智谱AI GLM-4 配置
注意：生产环境请通过环境变量或.env文件传入API Key，不要硬编码

使用方法：
  在运行前设置环境变量：export ZHIPU_API_KEY=your_real_api_key
  或在项目根目录创建 .env 文件并写入：ZHIPU_API_KEY=your_real_api_key
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 智谱AI (ZhipuAI) 配置
# 获取API Key: https://open.bigmodel.cn/
# ============================================================
ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "your_api_key_here")
ZHIPU_MODEL: str = "glm-4-flash"    # 使用glm-4-flash，稳定性好、延迟低
ZHIPU_MAX_TOKENS: int = 4096
ZHIPU_TEMPERATURE: float = 0.1      # 低温度，减少幻觉，保证输出稳定
LLM_MAX_RETRIES: int = 3            # LLM调用失败时的最大重试次数

# LLM请求超时（秒）
LLM_TIMEOUT: int = 60

# ============================================================
# 数据库配置
# ============================================================
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH: str = os.getenv(
    "IKEA_DB_PATH",
    os.path.join(_PROJECT_ROOT, "data", "ikea_parts.db"),
)

# ============================================================
# 输出目录配置
# ============================================================
BOM_OUTPUT_DIR: str = os.path.join(_PROJECT_ROOT, "output", "bom")
CAD_OUTPUT_DIR: str = os.path.join(_PROJECT_ROOT, "output", "cad")
MANUAL_OUTPUT_DIR: str = os.path.join(_PROJECT_ROOT, "output", "manual")
