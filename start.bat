@echo off
echo ================================
echo Commerce拼写检查工具 - 启动脚本
echo ================================
echo.

echo [1/4] 数据库迁移...
cd backend
python migrate_add_screenshot.py
if %errorlevel% neq 0 (
    echo 数据库迁移失败
    pause
    exit /b 1
)

echo.
echo [2/4] 初始化数据库...
python init_db.py
if %errorlevel% neq 0 (
    echo 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo [3/4] 启动后端服务...
start cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [4/4] 启动前端服务...
start cmd /k "cd frontend && npm run dev"

echo.
echo ================================
echo 服务启动完成！
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 前端界面: http://localhost:3000
echo 默认账号: admin / admin123
echo 
echo 新功能：界面截图已集成到报告中！
echo ================================
pause
