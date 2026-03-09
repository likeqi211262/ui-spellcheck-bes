# 界面截图功能更新

## 新增功能

### 1. 自动界面截图

在执行检查任务时，系统会自动对每个访问的界面进行截图。

**截图存储位置**: `reports/screenshots/`

**命名规则**: 
- 格式: `task{任务ID}_interface_{界面ID}_{时间戳}.png`
- 示例: `task1_interface_2_20240306_143025.png`

### 2. 报告中集成截图

HTML报告中新增了以下功能：

#### 界面截图展示
- 每个界面的错误详情页面都包含该界面的截图
- 截图以Base64格式嵌入HTML报告，确保报告可以独立查看
- 支持在浏览器中直接查看，无需额外文件

#### 改进的报告布局
- 按界面分组显示错误，便于查看每个界面的问题
- 界面卡片包含截图和该界面的所有错误
- 优化的视觉效果和错误标识

### 3. 前端截图查看

在界面配置页面，可以直接预览已采集的界面截图：
- 点击"查看截图"按钮查看大图
- 支持缩放查看

## 使用方法

### 1. 执行检查任务

创建并执行检查任务时，系统会自动截图：

```
1. 进入"任务管理"
2. 创建新任务
3. 任务执行过程中自动采集界面截图
4. 任务完成后生成报告
```

### 2. 查看截图

有多种方式查看界面截图：

**方式1：在报告中查看**
```
1. 任务完成后，点击"生成HTML报告"
2. 下载并打开报告
3. 每个界面详情中都包含截图
```

**方式2：在界面配置中查看**
```
1. 进入"界面配置"页面
2. 找到有截图的界面
3. 点击"查看截图"按钮
```

**方式3：直接访问API**
```
GET /api/screenshots/{interface_id}
需要认证Token
```

### 3. 报告示例

HTML报告包含以下内容：

```html
<!-- 界面截图部分 -->
<div class="screenshot-container">
    <h4>界面截图</h4>
    <img src="data:image/png;base64,{截图数据}" alt="界面截图">
</div>

<!-- 错误列表 -->
<table>
    <tr>
        <th>错误文本</th>
        <th>错误类型</th>
        <th>严重程度</th>
        <th>修正建议</th>
    </tr>
    <!-- 错误数据 -->
</table>
```

## 技术实现

### 后端实现

**1. 数据库更新**
- `InterfaceInfo` 表新增 `screenshot_path` 字段
- 存储每个界面的截图文件路径

**2. 截图采集**
```python
# backend/app/core/crawler.py
def take_interface_screenshot(self, interface_id, task_id):
    """采集界面截图"""
    screenshot_dir = os.path.join(settings.REPORT_OUTPUT_DIR, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    filename = f"task{task_id}_interface_{interface_id}_{timestamp}.png"
    filepath = os.path.join(screenshot_dir, filename)
    
    self.driver.save_screenshot(filepath)
    return filepath
```

**3. 报告生成**
```python
# backend/app/core/report_generator.py
def generate_html_report(self, task_id):
    """生成包含截图的HTML报告"""
    # 获取界面截图并转换为Base64
    for interface_data in interfaces_with_errors.values():
        if interface.screenshot_path:
            with open(interface.screenshot_path, 'rb') as f:
                img_data = f.read()
                interface_data['screenshot_base64'] = base64.b64encode(img_data)
    
    # 在HTML模板中嵌入截图
    template.render(interfaces_with_errors=interfaces_with_errors)
```

**4. API端点**
```python
# backend/app/api/screenshots.py
@router.get("/{interface_id}")
async def get_screenshot(interface_id):
    """获取界面截图"""
    return FileResponse(screenshot_path)
```

### 前端实现

**1. 界面列表展示截图**
```vue
<el-table-column label="截图">
  <el-button @click="viewScreenshot(row.id)">
    查看截图
  </el-button>
</el-table-column>
```

**2. 截图预览对话框**
```vue
<el-dialog v-model="screenshotDialogVisible" title="界面截图">
  <img :src="screenshotUrl" style="max-width: 100%">
</el-dialog>
```

## 配置说明

### 截图存储路径

在 `backend/.env` 中配置：
```env
REPORT_OUTPUT_DIR=./reports
```

截图将保存在 `{REPORT_OUTPUT_DIR}/screenshots/` 目录下。

### 截图分辨率

默认截图分辨率为 1920x1080，在 `crawler.py` 中设置：
```python
options.add_argument('--window-size=1920,1080')
```

### 注意事项

1. **存储空间**: 截图会占用磁盘空间，建议定期清理旧任务的截图
2. **权限**: 访问截图API需要认证Token
3. **格式**: 截图格式为PNG，确保清晰度
4. **报告大小**: 包含截图的HTML报告文件较大（每个截图约1-2MB）

## 性能优化建议

1. **定期清理**: 设置定时任务清理超过30天的截图
2. **压缩存储**: 可以考虑使用图片压缩减少存储空间
3. **按需加载**: 在报告中按需加载截图，避免一次性加载所有图片
4. **缩略图**: 为报告生成缩略图版本，点击后加载原图

## 更新日志

**v1.1.0 - 2024-03-06**
- ✨ 新增自动界面截图功能
- ✨ HTML报告中集成截图展示
- ✨ 前端界面配置页面支持截图预览
- 🐛 修复报告生成时的编码问题
- 💄 优化报告UI布局和样式
