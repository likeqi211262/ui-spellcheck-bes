@echo off
echo ================================
echo 安装Commerce拼写检查工具依赖
echo ================================
echo.

echo [1/2] 安装后端依赖...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 后端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2/2] 安装前端依赖...
cd ..\frontend
npm install
if %errorlevel% neq 0 (
    echo 前端依赖安装失败
    pause
    exit /b 1
)

echo.
echo ================================
echo 依赖安装完成！
echo 运行 start.bat 启动服务
echo ================================
pause
