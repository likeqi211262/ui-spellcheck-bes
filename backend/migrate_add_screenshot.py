"""
数据库迁移脚本 - 添加screenshot_path字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.config import get_settings

settings = get_settings()

def migrate():
    print("=" * 60)
    print("数据库迁移 - 添加screenshot_path字段")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        print("\n检查字段是否存在...")
        
        if 'sqlite' in settings.DATABASE_URL:
            result = db.execute(text("PRAGMA table_info(interface_info)"))
            columns = [row[1] for row in result]
            
            if 'screenshot_path' not in columns:
                print("字段不存在，开始添加...")
                db.execute(text("ALTER TABLE interface_info ADD COLUMN screenshot_path VARCHAR(500)"))
                db.commit()
                print("✅ 字段添加成功！")
            else:
                print("✅ 字段已存在，无需迁移。")
        else:
            print("⚠️  非SQLite数据库，请手动执行以下SQL:")
            print("ALTER TABLE interface_info ADD COLUMN screenshot_path VARCHAR(500);")
    
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    print("\n迁移完成！")

if __name__ == "__main__":
    migrate()
