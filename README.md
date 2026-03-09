# Commerce系统界面文本拼写检查工具

## 项目简介

这是一个用于Commerce系统界面文本拼写检查的Web工具，支持自动遍历界面、采集文本、拼写检查、生成报告等功能。

## 功能特性

- ✅ 自动遍历Web界面并采集文本
- ✅ 自动界面截图（新增）
- ✅ 多语言拼写检查（支持中英文）
- ✅ 可视化Web管理界面
- ✅ RESTful API接口
- ✅ 规则库管理（白名单、行业术语等）
- ✅ 多格式报告生成（HTML、Excel）
- ✅ 报告中集成界面截图（新增）
- ✅ 任务管理和进度监控
- ✅ 用户权限管理

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: SQLite
- **自动化**: Selenium + ChromeDriver
- **拼写检查**: pyspellchecker + language-tool-python
- **报告生成**: Jinja2 + OpenPyXL

### 前端
- **框架**: Vue 3
- **UI组件**: Element Plus
- **构建工具**: Vite

## 项目结构

```
commerce-spell-checker/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心功能模块
│   │   │   ├── spell_checker.py    # 拼写检查引擎
│   │   │   ├── crawler.py          # 界面遍历爬虫
│   │   │   └── report_generator.py # 报告生成器
│   │   ├── main.py            # FastAPI入口
│   │   ├── models.py          # 数据库模型
│   │   ├── schemas.py         # Pydantic模型
│   │   └── config.py          # 配置文件
│   ├── requirements.txt
│   └── init_db.py             # 数据库初始化脚本
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── utils/             # 工具函数
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── router.js
│   ├── package.json
│   └── vite.config.js
├── reports/                    # 生成的报告
│   └── screenshots/            # 界面截图（新增）
├── data/                       # SQLite数据库文件
├── logs/                       # 日志文件
├── start.bat                   # Windows启动脚本
└── start.sh                    # Linux/Mac启动脚本
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- Chrome浏览器（用于Selenium）

### 安装步骤

#### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 安装前端依赖

```bash
cd frontend
npm install
```

#### 3. 初始化数据库

```bash
cd backend
python init_db.py
```

### 启动服务

#### Windows

双击运行 `start.bat` 文件，或执行：

```bash
start.bat
```

#### Linux/Mac

```bash
chmod +x start.sh
./start.sh
```

#### 手动启动

**启动后端服务：**

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端服务：**

```bash
cd frontend
npm run dev
```

### 访问应用

- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 使用指南

### 1. 登录系统

使用默认账号登录系统。

### 2. 配置界面信息

1. 进入"界面配置"页面
2. 添加需要检查的界面信息（名称、访问路径等）
3. 设置界面状态为"启用"

### 3. 管理拼写规则

1. 进入"规则管理"页面
2. 添加专业术语到白名单（如"offer"、"360"等）
3. 管理通用词汇和自定义规则

### 4. 创建检查任务

1. 进入"任务管理"页面
2. 点击"创建检查任务"
3. 输入任务名称并选择检查范围
4. 任务将在后台自动执行

### 5. 查看报告

1. 任务完成后，点击"生成HTML报告"或"生成Excel"
2. HTML报告中包含界面截图，方便定位错误位置
3. 点击"下载报告"获取报告文件
4. 在"报告查看"页面可以查看详细的错误列表

**截图功能说明**（新增）：
- 执行任务时会自动对每个界面进行截图
- 截图保存在 `reports/screenshots/` 目录
- HTML报告中每个界面都包含对应的截图
- 可在"界面配置"页面直接预览截图

### 6. 标记修复

1. 在"报告查看"页面选择任务
2. 查看错误列表
3. 点击"标记修复"更新错误状态

## API接口文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要接口

#### 认证
- `POST /api/auth/token` - 用户登录获取token
- `GET /api/auth/me` - 获取当前用户信息

#### 任务管理
- `GET /api/tasks` - 获取任务列表
- `POST /api/tasks` - 创建检查任务
- `GET /api/tasks/{task_id}` - 获取任务详情
- `POST /api/tasks/{task_id}/generate-report` - 生成报告

#### 规则管理
- `GET /api/rules` - 获取规则列表
- `POST /api/rules` - 创建规则
- `PUT /api/rules/{rule_id}` - 更新规则
- `DELETE /api/rules/{rule_id}` - 删除规则

#### 界面管理
- `GET /api/interfaces` - 获取界面列表
- `POST /api/interfaces` - 创建界面配置
- `PUT /api/interfaces/{interface_id}` - 更新界面配置

#### 报告查看
- `GET /api/reports/errors` - 获取错误列表
- `PUT /api/reports/errors/{error_id}/fix` - 标记错误已修复
- `GET /api/reports/download/{task_id}` - 下载报告文件
- `GET /api/reports/statistics/{task_id}` - 获取统计信息

#### 截图管理（新增）
- `GET /api/screenshots/{interface_id}` - 获取界面截图

## 配置说明

### 后端配置

在 `backend/.env` 文件中配置：

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./data/spell_checker.db
REPORT_OUTPUT_DIR=./reports
LOG_DIR=./logs
```

### 前端配置

在 `frontend/vite.config.js` 中配置后端API地址：

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

## 注意事项

1. **ChromeDriver**: 首次运行时会自动下载ChromeDriver，需要网络连接
2. **拼写检查**: LanguageTool需要网络连接进行语法检查
3. **数据库**: 使用SQLite，数据存储在 `data/spell_checker.db` 文件中
4. **报告文件**: 生成的报告存储在 `reports/` 目录下

## 常见问题

### 1. ChromeDriver版本不匹配

确保Chrome浏览器版本与ChromeDriver版本匹配。程序会自动下载对应版本。

### 2. 语言工具连接失败

LanguageTool需要访问网络，如果网络受限，可以考虑使用离线模式或禁用语法检查功能。

### 3. 前端无法连接后端

检查后端服务是否正常运行，确认API地址配置正确。

## 优化建议

基于技术设计文档，本实现做了以下优化：

1. **简化数据库**: 使用SQLite替代MySQL，无需额外配置数据库服务
2. **支持多语言**: 增加了对中文拼写检查的支持
3. **简化部署**: 提供一键启动脚本，降低使用门槛
4. **模块化设计**: 核心功能独立模块，便于扩展和维护

## 扩展开发

### 添加新的拼写检查器

在 `backend/app/core/spell_checker.py` 中扩展 `SpellCheckEngine` 类。

### 添加新的报告格式

在 `backend/app/core/report_generator.py` 中添加新的生成方法。

### 自定义界面遍历逻辑

修改 `backend/app/core/crawler.py` 中的 `WebCrawler` 类。

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。
