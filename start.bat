@echo off
REM ============================================================
REM 宜家家具参数化设计系统 - 一键启动脚本（Windows）
REM 使用方法: 双击 start.bat 或在命令行运行
REM ============================================================

echo.
echo ========================================
echo   IKEA 家具参数化设计系统 CS10
echo ========================================
echo.

REM ── 1. 检测 Python ──────────────────────────────────────────
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] 检测到 Python:
python --version

REM ── 2. 安装依赖 ──────────────────────────────────────────────
echo.
echo [1/3] 正在安装依赖（首次约2-5分钟）...
pip install -q zhipuai pydantic streamlit pandas requests httpx python-dotenv Jinja2 sniffio anyio cadquery
IF %ERRORLEVEL% NEQ 0 (
    echo [警告] 部分依赖安装失败，尝试继续...
)
echo [OK] 依赖安装完成

REM ── 3. 初始化数据库 ──────────────────────────────────────────
echo.
echo [2/3] 正在初始化零件数据库...
python data\init_db.py
IF %ERRORLEVEL% NEQ 0 (
    echo [错误] 数据库初始化失败
    pause
    exit /b 1
)
echo [OK] 数据库就绪

REM ── 4. 启动 WebUI ────────────────────────────────────────────
echo.
echo [3/3] 正在启动 WebUI...
echo 浏览器访问: http://localhost:8501
echo 按 Ctrl+C 停止服务
echo.

python -m streamlit run app.py --server.port 8501
pause
