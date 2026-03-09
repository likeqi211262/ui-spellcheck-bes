#!/bin/bash

echo "================================"
echo "Commerce拼写检查工具 - 启动脚本"
echo "================================"
echo ""

echo "[1/3] 初始化数据库..."
cd backend
python init_db.py
if [ $? -ne 0 ]; then
    echo "数据库初始化失败"
    exit 1
fi

echo ""
echo "[2/3] 启动后端服务..."
osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"'

echo ""
echo "[3/3] 启动前端服务..."
cd ../frontend
osascript -e 'tell application "Terminal" to do script "cd '$(pwd)' && npm run dev"'

echo ""
echo "================================"
echo "服务启动完成！"
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "前端界面: http://localhost:3000"
echo "默认账号: admin / admin123"
echo "================================"
