"""
测试截图功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models
from app.core.crawler import WebCrawler

def test_screenshot():
    db = SessionLocal()
    
    try:
        interfaces = db.query(models.InterfaceInfo).filter(
            models.InterfaceInfo.status == 1
        ).limit(1).all()
        
        if not interfaces:
            print("没有找到启用的界面，创建测试界面...")
            test_interface = models.InterfaceInfo(
                interface_name="测试界面",
                interface_path="https://www.baidu.com",
                status=1,
                creator="system"
            )
            db.add(test_interface)
            db.commit()
            db.refresh(test_interface)
            interfaces = [test_interface]
        
        crawler = WebCrawler(db, headless=False)
        
        try:
            print("初始化浏览器...")
            crawler.init_driver()
            
            for interface in interfaces:
                print(f"\n访问界面: {interface.interface_name}")
                print(f"路径: {interface.interface_path}")
                
                text_elements, screenshot_path = crawler.crawl_interface(
                    interface.id,
                    interface.interface_path,
                    task_id=1
                )
                
                print(f"采集到 {len(text_elements)} 个文本元素")
                
                if screenshot_path:
                    print(f"✅ 截图成功: {screenshot_path}")
                    if os.path.exists(screenshot_path):
                        file_size = os.path.getsize(screenshot_path)
                        print(f"   文件大小: {file_size} bytes")
                    else:
                        print(f"   ⚠️  文件不存在")
                else:
                    print(f"❌ 截图失败")
                
                print("\n采集的文本示例:")
                for i, elem in enumerate(text_elements[:5]):
                    print(f"  {i+1}. [{elem.element_type}] {elem.text_content[:50]}")
                
                break
        
        finally:
            print("\n关闭浏览器...")
            crawler.close_driver()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("截图功能测试")
    print("=" * 60)
    test_screenshot()
    print("\n测试完成！")
