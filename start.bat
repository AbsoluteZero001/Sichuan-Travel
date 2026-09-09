@echo off
chcp 65001 >nul
REM 四川旅游 - 一键启动脚本
REM 双击本文件即可启动 Flask 后端
REM 适配新电脑：自动检测 Python、缺失依赖时自动安装

cd /d "%~dp0backend"

REM ---- 1. 检测 Python（依次尝试 python / py 启动器；不用 python3，Win 上是商店占位符）----
set "PY_CMD="
python --version >nul 2>&1 && set "PY_CMD=python"
if not defined PY_CMD (
    py -3 --version >nul 2>&1 && set "PY_CMD=py -3"
)
if not defined PY_CMD (
    echo [错误] 未检测到 Python，请先安装 Python 3.x
    echo 安装时请勾选 "Add Python to PATH"，下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo [信息] 检测到 Python:
%PY_CMD% --version

REM ---- 2. 检查 .env 是否存在 ----
if not exist ".env" (
    echo [警告] 未找到 backend\.env 文件
    echo 请先复制 .env.example 为 .env 并填入 AI_API_KEY
    echo.
)

REM ---- 3. 检查依赖，缺失则自动安装 ----
%PY_CMD% -c "import flask, flask_cors, mysql.connector, jwt, docx, openai, dotenv" >nul 2>&1
if errorlevel 1 (
    echo [信息] 首次运行，正在自动安装依赖（requirements.txt），请稍候...
    %PY_CMD% -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络后手动执行:
        echo        %PY_CMD% -m pip install -r "%~dp0requirements.txt"
        echo.
        pause
        exit /b 1
    )
    echo [信息] 依赖安装完成。
)

echo ========================================
echo  四川旅游 后端启动中...
echo  访问地址: http://localhost:3000
echo  旅游助手: http://localhost:3000/travel-tips.html
echo  按 Ctrl+C 可停止
echo ========================================
echo.

%PY_CMD% app.py

echo.
echo 服务已停止，按任意键关闭窗口
pause >nul
