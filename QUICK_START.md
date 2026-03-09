# 快速启动指南 - 截图功能

## 🚀 5分钟快速上手

### 步骤1: 安装依赖（首次运行）

```bash
# Windows
install.bat

# Linux/Mac
chmod +x install.sh && ./install.sh
```

### 步骤2: 启动服务

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### 步骤3: 访问系统

浏览器打开: http://localhost:3000

登录账号: `admin` / `admin123`

### 步骤4: 创建测试任务

1. 进入"界面配置"，添加测试界面（例如：https://www.baidu.com）
2. 进入"任务管理"，创建新任务
3. 等待任务执行完成（通常1-2分钟）
4. 点击"生成HTML报告"

### 步骤5: 查看截图

**在报告中查看**:
- 打开生成的HTML报告
- 每个界面都有截图展示

**在系统中查看**:
- 进入"界面配置"页面
- 点击"查看截图"按钮

## 📸 截图功能验证

### 自动验证脚本

```bash
cd backend
python test_screenshot.py
```

### 手动验证步骤

1. **检查数据库字段**
   ```bash
   cd backend
   python migrate_add_screenshot.py
   ```
   应该显示: `✅ 字段已存在`

2. **检查截图目录**
   ```bash
   # 查看是否有截图文件
   ls reports/screenshots/
   ```
   应该看到 `.png` 文件

3. **检查报告**
   - 打开HTML报告
   - 查看是否有图片显示
   - 检查图片是否清晰

## 🔧 常见问题

### Q1: 任务执行但没有截图？

**检查**:
- Chrome浏览器是否安装
- 是否能访问目标网站
- reports目录是否有写入权限

**解决**:
```bash
# 创建目录
mkdir -p reports/screenshots

# 设置权限（Linux/Mac）
chmod 755 reports/screenshots
```

### Q2: 报告中看不到图片？

**检查**:
- 浏览器控制台是否有错误
- 截图文件是否存在
- 报告文件大小（正常应大于1MB）

**解决**:
```bash
# 检查截图文件
ls -lh reports/screenshots/

# 重新生成报告
# 在系统中点击"生成HTML报告"
```

### Q3: 截图模糊或不完整？

**原因**:
- 页面加载未完成
- 网络延迟
- 页面响应式布局

**解决**:
- 检查网络连接
- 增加页面等待时间（修改crawler.py中的time.sleep）

## 💡 最佳实践

### 1. 测试界面选择

建议先测试简单界面：
- ✅ 百度首页: https://www.baidu.com
- ✅ 必应首页: https://www.bing.com
- ❌ 复杂单页应用（可能加载慢）

### 2. 任务配置

- 首次测试建议只检查1-2个界面
- 确认成功后再增加界面数量
- 建议在非高峰期执行大批量任务

### 3. 报告管理

- HTML报告包含截图，文件较大
- 建议按日期归档报告
- 定期清理过期报告和截图

## 📊 性能参考

### 单个界面
- 截图时间: 2-3秒
- 文本采集: 1-2秒
- 总耗时: 约5秒

### 10个界面
- 预计总耗时: 50-60秒
- 截图总大小: 约15-20MB

### 100个界面
- 预计总耗时: 8-10分钟
- 截图总大小: 约150-200MB
- 建议分批执行

## 🎯 下一步

### 探索更多功能

- [ ] 配置拼写规则库
- [ ] 添加专业术语白名单
- [ ] 自定义报告模板
- [ ] 设置定时任务

### 高级配置

**修改截图分辨率**:
```python
# backend/app/core/crawler.py
options.add_argument('--window-size=1920,1080')  # 修改这里
```

**修改等待时间**:
```python
# backend/app/core/crawler.py
time.sleep(2)  # 增加等待时间确保页面加载完成
```

## 📞 获取帮助

- 查看详细文档: `README.md`
- 截图功能说明: `SCREENSHOT_FEATURE.md`
- 更新日志: `UPDATE_LOG.md`
- API文档: http://localhost:8000/docs

---

**祝你使用愉快！** 🎉

如有问题，请查看日志文件: `logs/` 目录
