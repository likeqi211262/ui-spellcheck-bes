from sqlalchemy.orm import Session
from app import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db(db: Session):
    db.query(models.SpellError).delete()
    db.query(models.TextElement).delete()
    db.query(models.CheckTask).delete()
    db.query(models.InterfaceInfo).delete()
    db.query(models.SpellRule).delete()
    db.query(models.SysUser).delete()
    db.query(models.SysRole).delete()
    db.commit()
    
    roles = [
        models.SysRole(id=1, role_name="admin", permissions="all", status=1),
        models.SysRole(id=2, role_name="tester", permissions="task:create,task:execute,report:view", status=1),
        models.SysRole(id=3, role_name="viewer", permissions="report:view", status=1),
    ]
    db.add_all(roles)
    
    hashed_password = pwd_context.hash("admin123")
    admin_user = models.SysUser(
        id=1,
        username="admin",
        password=hashed_password,
        role_id=1,
        status=1
    )
    db.add(admin_user)
    
    default_rules = [
        models.SpellRule(word="offer", word_type="industry", is_whitelist=1, remark="运营商专业术语", language="en"),
        models.SpellRule(word="360", word_type="industry", is_whitelist=1, remark="360界面专用术语", language="en"),
        models.SpellRule(word="bes", word_type="industry", is_whitelist=1, remark="Bes平台名称", language="en"),
        models.SpellRule(word="commerce", word_type="industry", is_whitelist=1, remark="Commerce系统名称", language="en"),
        models.SpellRule(word="username", word_type="common", is_whitelist=0, remark="常用词汇", language="en"),
        models.SpellRule(word="password", word_type="common", is_whitelist=0, remark="常用词汇", language="en"),
        models.SpellRule(word="login", word_type="common", is_whitelist=0, remark="常用词汇", language="en"),
        models.SpellRule(word="submit", word_type="common", is_whitelist=0, remark="常用词汇", language="en"),
        models.SpellRule(word="cancel", word_type="common", is_whitelist=0, remark="常用词汇", language="en"),
        models.SpellRule(word="确认", word_type="common", is_whitelist=0, remark="常用词汇", language="zh"),
        models.SpellRule(word="取消", word_type="common", is_whitelist=0, remark="常用词汇", language="zh"),
        models.SpellRule(word="登录", word_type="common", is_whitelist=0, remark="常用词汇", language="zh"),
        models.SpellRule(word="提交", word_type="common", is_whitelist=0, remark="常用词汇", language="zh"),
    ]
    db.add_all(default_rules)
    
    sample_interfaces = [
        models.InterfaceInfo(
            interface_name="操作员登录界面",
            interface_path="/admin/login",
            jump_rule="输入用户名密码后点击登录按钮",
            status=1,
            creator="system"
        ),
        models.InterfaceInfo(
            interface_name="用户登录界面",
            interface_path="/user/login",
            jump_rule="输入手机号和验证码后点击登录",
            status=1,
            creator="system"
        ),
        models.InterfaceInfo(
            interface_name="360界面",
            interface_path="/dashboard",
            jump_rule="登录后自动跳转",
            status=1,
            creator="system"
        ),
    ]
    db.add_all(sample_interfaces)
    
    db.commit()
    print("Database initialized successfully!")
    print("Default admin user: admin / admin123")
