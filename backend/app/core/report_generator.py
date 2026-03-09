import os
import base64
from datetime import datetime
from typing import List, Dict
from jinja2 import Template
from openpyxl import Workbook
from sqlalchemy.orm import Session
from app import models
from app.config import get_settings

settings = get_settings()


class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.output_dir = settings.REPORT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_html_report(self, task_id: int, include_fixed: bool = False) -> str:
        task = self.db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
        if not task:
            return None
        
        query = self.db.query(models.SpellError).join(models.TextElement).join(models.InterfaceInfo)
        
        if task.check_scope != "all":
            interface_ids = [int(x) for x in task.check_scope.split(",") if x.strip()]
            query = query.filter(models.TextElement.interface_id.in_(interface_ids))
        
        if not include_fixed:
            query = query.filter(models.SpellError.is_fixed == 0)
        
        errors = query.all()
        
        stats = {
            'total_errors': len(errors),
            'by_severity': {},
            'by_type': {},
            'by_interface': {}
        }
        
        for error in errors:
            severity = error.severity_level
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            
            error_type = error.error_type
            stats['by_type'][error_type] = stats['by_type'].get(error_type, 0) + 1
            
            interface_name = error.text_element.interface.interface_name
            stats['by_interface'][interface_name] = stats['by_interface'].get(interface_name, 0) + 1
        
        interfaces_with_errors = {}
        for error in errors:
            interface = error.text_element.interface
            if interface.id not in interfaces_with_errors:
                interfaces_with_errors[interface.id] = {
                    'interface': interface,
                    'errors': [],
                    'screenshot_base64': None
                }
            interfaces_with_errors[interface.id]['errors'].append(error)
        
        for interface_data in interfaces_with_errors.values():
            interface = interface_data['interface']
            if interface.screenshot_path and os.path.exists(interface.screenshot_path):
                try:
                    with open(interface.screenshot_path, 'rb') as img_file:
                        img_data = img_file.read()
                        interface_data['screenshot_base64'] = base64.b64encode(img_data).decode('utf-8')
                except Exception as e:
                    print(f"Failed to read screenshot {interface.screenshot_path}: {str(e)}")
        
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>拼写检查报告 - {{ task.task_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        h2 { color: #666; margin-top: 30px; }
        h3 { color: #4CAF50; margin-top: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .severity-high { color: red; font-weight: bold; }
        .severity-medium { color: orange; }
        .severity-low { color: blue; }
        .stats { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .screenshot-container { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #fafafa; }
        .screenshot-img { max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; }
        .interface-section { margin: 30px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px; background-color: white; }
        .error-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 10px; }
        .badge-high { background-color: #ffebee; color: #c62828; }
        .badge-medium { background-color: #fff3e0; color: #ef6c00; }
        .badge-low { background-color: #e3f2fd; color: #1976d2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>拼写检查报告</h1>
        <div class="stats">
            <p><strong>任务名称:</strong> {{ task.task_name }}</p>
            <p><strong>执行人:</strong> {{ task.executor }}</p>
            <p><strong>开始时间:</strong> {{ task.start_time }}</p>
            <p><strong>结束时间:</strong> {{ task.end_time }}</p>
            <p><strong>错误总数:</strong> {{ stats.total_errors }}</p>
        </div>
        
        <h2>错误统计</h2>
        <p><strong>按严重程度:</strong></p>
        <ul>
            {% for severity, count in stats.by_severity.items() %}
            <li>严重程度 {{ severity }}: {{ count }} 个错误</li>
            {% endfor %}
        </ul>
        
        <p><strong>按错误类型:</strong></p>
        <ul>
            {% for error_type, count in stats.by_type.items() %}
            <li>{{ error_type }}: {{ count }} 个错误</li>
            {% endfor %}
        </ul>
        
        <h2>界面截图与错误详情</h2>
        {% for interface_id, interface_data in interfaces_with_errors.items() %}
        <div class="interface-section">
            <h3>{{ interface_data.interface.interface_name }} 
                <span class="error-badge badge-{% if interface_data.errors|length > 5 %}high{% elif interface_data.errors|length > 2 %}medium{% else %}low{% endif %}">
                    {{ interface_data.errors|length }} 个错误
                </span>
            </h3>
            <p><strong>界面路径:</strong> {{ interface_data.interface.interface_path }}</p>
            
            {% if interface_data.screenshot_base64 %}
            <div class="screenshot-container">
                <h4>界面截图</h4>
                <img src="data:image/png;base64,{{ interface_data.screenshot_base64 }}" alt="界面截图" class="screenshot-img">
            </div>
            {% else %}
            <div class="screenshot-container">
                <p style="color: #999; font-style: italic;">暂无截图</p>
            </div>
            {% endif %}
            
            <h4>错误列表</h4>
            <table>
                <tr>
                    <th>ID</th>
                    <th>错误文本</th>
                    <th>错误类型</th>
                    <th>严重程度</th>
                    <th>修正建议</th>
                    <th>检查时间</th>
                </tr>
                {% for error in interface_data.errors %}
                <tr>
                    <td>{{ error.id }}</td>
                    <td>{{ error.error_text }}</td>
                    <td>{{ error.error_type }}</td>
                    <td class="severity-{% if error.severity_level == 3 %}high{% elif error.severity_level == 2 %}medium{% else %}low{% endif %}">
                        {% if error.severity_level == 3 %}高{% elif error.severity_level == 2 %}中{% else %}低{% endif %}
                    </td>
                    <td>{{ error.correct_suggest }}</td>
                    <td>{{ error.check_time }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endfor %}
        
        <h2>完整错误明细</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>界面</th>
                <th>错误文本</th>
                <th>错误类型</th>
                <th>严重程度</th>
                <th>修正建议</th>
                <th>检查时间</th>
            </tr>
            {% for error in errors %}
            <tr>
                <td>{{ error.id }}</td>
                <td>{{ error.text_element.interface.interface_name }}</td>
                <td>{{ error.error_text }}</td>
                <td>{{ error.error_type }}</td>
                <td class="severity-{% if error.severity_level == 3 %}high{% elif error.severity_level == 2 %}medium{% else %}low{% endif %}">
                    {% if error.severity_level == 3 %}高{% elif error.severity_level == 2 %}中{% else %}低{% endif %}
                </td>
                <td>{{ error.correct_suggest }}</td>
                <td>{{ error.check_time }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            task=task,
            errors=errors,
            stats=stats,
            interfaces_with_errors=interfaces_with_errors
        )
        
        filename = f"report_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        task.report_path = filepath
        self.db.commit()
        
        return filepath
    
    def generate_excel_report(self, task_id: int, include_fixed: bool = False) -> str:
        task = self.db.query(models.CheckTask).filter(models.CheckTask.id == task_id).first()
        if not task:
            return None
        
        query = self.db.query(models.SpellError).join(models.TextElement).join(models.InterfaceInfo)
        
        if task.check_scope != "all":
            interface_ids = [int(x) for x in task.check_scope.split(",") if x.strip()]
            query = query.filter(models.TextElement.interface_id.in_(interface_ids))
        
        if not include_fixed:
            query = query.filter(models.SpellError.is_fixed == 0)
        
        errors = query.all()
        
        wb = Workbook()
        ws = wb.active
        ws.title = "拼写错误报告"
        
        headers = ["ID", "界面名称", "元素路径", "错误文本", "上下文", "错误类型", "严重程度", "修正建议", "检查时间", "是否修复"]
        ws.append(headers)
        
        for error in errors:
            ws.append([
                error.id,
                error.text_element.interface.interface_name,
                error.text_element.element_path,
                error.error_text,
                error.text_element.text_content,
                error.error_type,
                error.severity_level,
                error.correct_suggest or "",
                str(error.check_time),
                "是" if error.is_fixed == 1 else "否"
            ])
        
        filename = f"report_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        wb.save(filepath)
        
        task.report_path = filepath
        self.db.commit()
        
        return filepath
