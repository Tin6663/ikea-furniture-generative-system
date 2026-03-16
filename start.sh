#!/bin/bash
# ============================================================
# 宜家家具参数化设计系统 - 一键启动脚本（macOS / Linux）
# 使用方法: bash start.sh
# ============================================================

set -e

PYTHON=""
PIP=""

# ── 1. 检测 Python ───────────────────────────────────────────
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(sys.version_info.major)")
        if [ "$VER" = "3" ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ 未找到 Python 3，请先安装 Python 3.9+ (https://python.org)"
    exit 1
fi

echo "✅ Python: $($PYTHON --version)"

# ── 2. 检测 pip ──────────────────────────────────────────────
for cmd in pip3 pip; do
    if command -v "$cmd" &>/dev/null; then
        PIP="$cmd"
        break
    fi
done

if [ -z "$PIP" ]; then
    PIP="$PYTHON -m pip"
fi

# ── 3. 安装依赖 ──────────────────────────────────────────────
echo ""
echo "📦 正在检查并安装依赖库（首次运行较慢，约2-5分钟）..."
$PIP install -q zhipuai pydantic streamlit pandas requests httpx python-dotenv Jinja2 sniffio anyio cadquery 2>&1 | grep -E "(Successfully|already|ERROR|error)" || true
echo "✅ 依赖安装完成"

# ── 4. 初始化数据库 ──────────────────────────────────────────
echo ""
echo "🗄️  正在初始化宜家零件数据库..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
$PYTHON data/init_db.py
echo "✅ 数据库就绪"

# ── 5. 启动 WebUI ────────────────────────────────────────────
echo ""
echo "🚀 正在启动 WebUI..."
echo "   浏览器访问: http://localhost:8501"
echo "   按 Ctrl+C 停止服务"
echo ""

# 找 streamlit 可执行文件
STREAMLIT=""
for candidate in \
    "$($PYTHON -m site --user-base)/bin/streamlit" \
    "$(dirname $($PYTHON -c 'import sys; print(sys.executable)'))/streamlit" \
    "streamlit"; do
    if command -v "$candidate" &>/dev/null 2>&1; then
        STREAMLIT="$candidate"
        break
    fi
done

if [ -z "$STREAMLIT" ]; then
    # 兜底：用 python -m streamlit
    $PYTHON -m streamlit run app.py --server.port 8501
else
    "$STREAMLIT" run app.py --server.port 8501
fi
