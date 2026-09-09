@echo off
chcp 65001 >nul
REM 四川旅游 - 一键启动脚本
REM 双击本文件即可启动 Flask 后端

cd /d "%~dp0backend"

REM 检查 .env 是否存在
if not exist ".env" (
    echo [警告] 未找到 backend\.env 文件
    echo 请先复制 .env.example 为 .env 并填入 AI_API_KEY
    echo.
)

echo ========================================
echo  四川旅游 后端启动中...
echo  访问地址: http://localhost:3000
echo  旅游助手: http://localhost:3000/travel-tips.html
echo  按 Ctrl+C 可停止
echo ========================================
echo.

python app.py

echo.
echo 服务已停止，按任意键关闭窗口
pause >nul
