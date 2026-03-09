from sqlalchemy import Column, BigInteger, VARCHAR, TEXT, TINYINT, INT, DATETIME
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class InterfaceInfo(Base):
    __tablename__ = "interface_info"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    interface_name = Column(VARCHAR(100), nullable=False)
    interface_path = Column(VARCHAR(255), nullable=False)
    parent_id = Column(BigInteger, nullable=True)
    jump_rule = Column(TEXT, nullable=True)
    status = Column(TINYINT, nullable=False, default=1)
    screenshot_path = Column(VARCHAR(500), nullable=True)
    create_time = Column(DATETIME, server_default=func.now())
    update_time = Column(DATETIME, server_default=func.now(), onupdate=func.now())
    creator = Column(VARCHAR(50), nullable=False, default="system")
    
    text_elements = relationship("TextElement", back_populates="interface")


class TextElement(Base):
    __tablename__ = "text_element"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    interface_id = Column(BigInteger, nullable=False, index=True)
    element_path = Column(VARCHAR(500), nullable=False)
    text_content = Column(TEXT, nullable=False)
    element_type = Column(VARCHAR(50), nullable=False)
    collect_time = Column(DATETIME, server_default=func.now())
    collect_status = Column(TINYINT, nullable=False, default=1)
    
    interface = relationship("InterfaceInfo", back_populates="text_elements")
    spell_errors = relationship("SpellError", back_populates="text_element")


class SpellRule(Base):
    __tablename__ = "spell_rule"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    word = Column(VARCHAR(100), nullable=False, unique=True, index=True)
    word_type = Column(VARCHAR(50), nullable=False, default="common")
    is_whitelist = Column(TINYINT, nullable=False, default=0)
    remark = Column(VARCHAR(255), nullable=True)
    language = Column(VARCHAR(10), nullable=False, default="en")
    create_time = Column(DATETIME, server_default=func.now())
    update_time = Column(DATETIME, server_default=func.now(), onupdate=func.now())


class SpellError(Base):
    __tablename__ = "spell_error"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    element_id = Column(BigInteger, nullable=False, index=True)
    error_text = Column(VARCHAR(500), nullable=False)
    correct_suggest = Column(TEXT, nullable=True)
    error_type = Column(VARCHAR(50), nullable=False)
    severity_level = Column(TINYINT, nullable=False, default=2)
    check_time = Column(DATETIME, server_default=func.now())
    is_fixed = Column(TINYINT, nullable=False, default=0)
    fixed_time = Column(DATETIME, nullable=True)
    
    text_element = relationship("TextElement", back_populates="spell_errors")


class CheckTask(Base):
    __tablename__ = "check_task"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    task_name = Column(VARCHAR(100), nullable=False)
    task_status = Column(TINYINT, nullable=False, default=0)
    start_time = Column(DATETIME, nullable=True)
    end_time = Column(DATETIME, nullable=True)
    check_scope = Column(VARCHAR(255), nullable=False, default="all")
    error_count = Column(INT, nullable=True, default=0)
    executor = Column(VARCHAR(50), nullable=False, default="system")
    report_path = Column(VARCHAR(255), nullable=True)
    error_msg = Column(TEXT, nullable=True)


class SysUser(Base):
    __tablename__ = "sys_user"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(VARCHAR(50), nullable=False, unique=True, index=True)
    password = Column(VARCHAR(100), nullable=False)
    role_id = Column(BigInteger, nullable=False, default=3)
    status = Column(TINYINT, nullable=False, default=1)
    create_time = Column(DATETIME, server_default=func.now())


class SysRole(Base):
    __tablename__ = "sys_role"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    role_name = Column(VARCHAR(50), nullable=False, unique=True)
    permissions = Column(TEXT, nullable=True)
    status = Column(TINYINT, nullable=False, default=1)


class SysLog(Base):
    __tablename__ = "sys_log"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    log_type = Column(VARCHAR(50), nullable=False)
    operator = Column(VARCHAR(50), nullable=True)
    operation_desc = Column(VARCHAR(255), nullable=False)
    request_param = Column(TEXT, nullable=True)
    ip_address = Column(VARCHAR(50), nullable=True)
    create_time = Column(DATETIME, server_default=func.now())
    error_detail = Column(TEXT, nullable=True)
